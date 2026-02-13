#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
OPERATOR_DIR = ROOT / "tools" / "operator"
QUEUE_DIR = OPERATOR_DIR / "queue"
INBOX_DIR = QUEUE_DIR / "inbox"
PATCHES_DIR = QUEUE_DIR / "patches"
ARCHIVE_DIR = QUEUE_DIR / "archive"
LOGS_DIR = OPERATOR_DIR / "logs"
STOP_FILE = OPERATOR_DIR / "STOP"
EVENT_LOG = LOGS_DIR / "operator_events.jsonl"
STATE_FILE = LOGS_DIR / "processed_tasks.json"

DEFAULT_DENY_GLOBS = [".github/workflows/**"]


class OperatorError(RuntimeError):
    pass


@dataclass
class Task:
    task_id: str
    repo: str
    base_branch: str
    branch_name: str
    patch_file: str
    commands: list[str]
    allowlist_globs: list[str]
    pr_title: str
    pr_body: str
    mode: str
    source_file: Path


REQUIRED_FIELDS = {
    "task_id",
    "repo",
    "base_branch",
    "branch_name",
    "patch_file",
    "commands",
    "allowlist_globs",
    "pr_title",
    "pr_body",
}


def run(cmd: str | list[str], *, check: bool = True, capture_output: bool = True) -> subprocess.CompletedProcess:
    if isinstance(cmd, str):
        result = subprocess.run(cmd, cwd=ROOT, shell=True, text=True, capture_output=capture_output)
    else:
        result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=capture_output)
    if check and result.returncode != 0:
        raise OperatorError(f"Command failed ({result.returncode}): {cmd}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    return result


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_event(event: dict) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with EVENT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def load_processed() -> set[str]:
    if not STATE_FILE.exists():
        return set()
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return set(data.get("processed", []))
    except json.JSONDecodeError:
        return set()


def save_processed(processed: set[str]) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps({"processed": sorted(processed)}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_task(path: Path) -> Task:
    payload = json.loads(path.read_text(encoding="utf-8"))
    missing = REQUIRED_FIELDS - set(payload)
    if missing:
        raise OperatorError(f"Task {path.name} missing fields: {sorted(missing)}")
    if not isinstance(payload["commands"], list) or not all(isinstance(x, str) for x in payload["commands"]):
        raise OperatorError("commands must be list[str]")
    if not isinstance(payload["allowlist_globs"], list) or not all(isinstance(x, str) for x in payload["allowlist_globs"]):
        raise OperatorError("allowlist_globs must be list[str]")
    raw_mode = payload.get("mode", "auto")
    if raw_mode not in {"auto", "gh", "push_only"}:
        raise OperatorError("mode must be one of: auto, gh, push_only")

    payload["mode"] = raw_mode
    return Task(source_file=path, **payload)


def is_gh_ready() -> bool:
    gh_bin = run(["bash", "-lc", "command -v gh"], check=False)
    if gh_bin.returncode != 0:
        return False
    auth = run(["gh", "auth", "status"], check=False)
    return auth.returncode == 0


def resolve_mode(task_mode: str) -> str:
    if task_mode == "auto":
        return "gh" if is_gh_ready() else "push_only"
    return task_mode


def build_compare_url(task: Task) -> str:
    return f"https://github.com/{task.repo}/compare/{task.base_branch}...{task.branch_name}?expand=1"


def read_patch_touched_files(patch_path: Path) -> list[str]:
    touched: list[str] = []
    for line in patch_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("+++ b/"):
            touched.append(line[len("+++ b/") :].strip())
        elif line.startswith("--- a/"):
            touched.append(line[len("--- a/") :].strip())
    normalized = []
    for p in touched:
        if p == "/dev/null":
            continue
        normalized.append(p)
    return sorted(set(normalized))


def matches_any(path: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def enforce_allowlist(paths: Iterable[str], allowlist_globs: list[str], deny_globs: list[str]) -> None:
    denied = [p for p in paths if matches_any(p, deny_globs)]
    if denied:
        raise OperatorError(f"Patch touches denied paths: {denied}")
    outside = [p for p in paths if not matches_any(p, allowlist_globs)]
    if outside:
        raise OperatorError(f"Patch touches paths outside allowlist: {outside}")


def ensure_clean_tree() -> None:
    result = run(["git", "status", "--porcelain"], check=True)
    if result.stdout.strip():
        raise OperatorError("Working tree is not clean. Commit/stash changes before running operator.")


def process_task(task: Task) -> dict:
    patch_path = (ROOT / task.patch_file).resolve()
    if not patch_path.exists() or not patch_path.is_file():
        raise OperatorError(f"Patch file not found: {task.patch_file}")
    if not str(patch_path).startswith(str(PATCHES_DIR.resolve())):
        raise OperatorError("patch_file must be under tools/operator/queue/patches/")

    touched_from_patch = read_patch_touched_files(patch_path)
    enforce_allowlist(touched_from_patch, task.allowlist_globs, DEFAULT_DENY_GLOBS)

    ensure_clean_tree()

    mode = resolve_mode(task.mode)

    run(["git", "checkout", task.base_branch])
    run(["git", "checkout", "-B", task.branch_name, task.base_branch])

    run(["git", "apply", "--3way", "--index", str(patch_path)])

    staged = run(["git", "diff", "--cached", "--name-only"]).stdout.splitlines()
    enforce_allowlist(staged, task.allowlist_globs, DEFAULT_DENY_GLOBS)

    command_logs: list[dict] = []
    for cmd in task.commands:
        result = run(cmd, check=False)
        command_logs.append(
            {
                "command": cmd,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        )
        if result.returncode != 0:
            raise OperatorError(f"Task command failed: {cmd}")

    run(["git", "commit", "-m", f"operator: apply {task.task_id}"])
    commit_hash = run(["git", "rev-parse", "HEAD"]).stdout.strip()
    run(["git", "push", "-u", "origin", task.branch_name])

    next_action = ""
    pr_url = ""
    compare_url = build_compare_url(task)

    if mode == "gh":
        pr_create = run(
            [
                "gh",
                "pr",
                "create",
                "--base",
                task.base_branch,
                "--head",
                task.branch_name,
                "--title",
                task.pr_title,
                "--body",
                task.pr_body,
            ]
        )
        pr_url = pr_create.stdout.strip().splitlines()[-1] if pr_create.stdout.strip() else ""
        run(["gh", "pr", "merge", task.branch_name, "--auto", "--squash", "--delete-branch"])
        next_action = "PR created via gh and auto-merge enabled"
    else:
        next_action = (
            "Open compare URL and create PR manually. "
            "Optional: use GitHub Desktop (Current Branch -> Create Pull Request)."
        )

    return {
        "task_id": task.task_id,
        "commit_hash": commit_hash,
        "pr_url": pr_url,
        "compare_url": compare_url,
        "mode": mode,
        "next_action": next_action,
        "status": "success",
        "commands": command_logs,
    }


def archive_task(task: Task, suffix: str) -> None:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    target = ARCHIVE_DIR / f"{task.source_file.stem}.{suffix}.json"
    task.source_file.replace(target)


def main() -> int:
    parser = argparse.ArgumentParser(description="Local gh-based operator")
    parser.add_argument("--once", action="store_true", help="Process queue once and exit")
    parser.add_argument("--poll-interval", type=float, default=5.0, help="Queue poll interval in seconds")
    args = parser.parse_args()

    for d in [INBOX_DIR, PATCHES_DIR, ARCHIVE_DIR, LOGS_DIR]:
        d.mkdir(parents=True, exist_ok=True)

    processed = load_processed()

    while True:
        if STOP_FILE.exists():
            append_event({"ts": now_iso(), "status": "stopped", "reason": "STOP file exists"})
            return 0

        tasks = sorted(INBOX_DIR.glob("*.json"))
        for task_file in tasks:
            try:
                task = parse_task(task_file)
                if task.task_id in processed:
                    archive_task(task, "skipped")
                    append_event({"ts": now_iso(), "task_id": task.task_id, "status": "skipped", "reason": "already processed"})
                    continue

                append_event({"ts": now_iso(), "task_id": task.task_id, "status": "started"})
                result = process_task(task)
                processed.add(task.task_id)
                save_processed(processed)
                archive_task(task, "done")
                append_event({"ts": now_iso(), **result})
            except Exception as exc:  # noqa: BLE001 - top-level task guard
                append_event(
                    {
                        "ts": now_iso(),
                        "task_file": str(task_file.relative_to(ROOT)),
                        "status": "failed",
                        "error": str(exc),
                    }
                )
                if task_file.exists():
                    failed_target = ARCHIVE_DIR / f"{task_file.stem}.failed.json"
                    failed_target.parent.mkdir(parents=True, exist_ok=True)
                    task_file.replace(failed_target)
                run(["git", "reset", "--hard"], check=False)
                run(["git", "checkout", "-"], check=False)

        if args.once:
            return 0
        time.sleep(args.poll_interval)


if __name__ == "__main__":
    sys.exit(main())
