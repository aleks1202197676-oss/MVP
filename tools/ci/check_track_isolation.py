from __future__ import annotations

import argparse
import fnmatch
import subprocess
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class RuleSet:
    forbidden_patterns: tuple[str, ...]
    reason: str


RULES: dict[str, RuleSet] = {
    "PR-F": RuleSet(
        forbidden_patterns=(
            ".github/workflows/**",
            "tools/operator/**",
            "memory_pack/**",
        ),
        reason="PR-F не должен менять CI/operator/memory_pack области.",
    ),
    "PR-A": RuleSet(
        forbidden_patterns=(
            "pipelines/finance*",
            "contracts/finance*",
            "data/raw/finance*",
            "outputs/latest/finance*",
        ),
        reason="PR-A не должен менять finance доменные области.",
    ),
    "PR-G": RuleSet(
        forbidden_patterns=(
            "data/raw/**",
            "outputs/latest/**",
            "contracts/finance*",
            "pipelines/finance*",
            "tools/operator/**",
            "memory_pack/**",
        ),
        reason="PR-G для gatekeeper/CI не должен менять продуктовые данные и finance домен без явного allowlist.",
    ),
}


def _git_changed_files(base_ref: str, head_ref: str) -> list[str]:
    cmd = ["git", "diff", "--name-only", f"{base_ref}...{head_ref}"]
    result = subprocess.run(cmd, check=True, text=True, capture_output=True)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _detect_track(pr_title: str, labels: list[str]) -> str | None:
    for token in [pr_title, *labels]:
        token_u = token.upper()
        if "PR-F" in token_u:
            return "PR-F"
        if "PR-A" in token_u:
            return "PR-A"
        if "PR-G" in token_u:
            return "PR-G"
    return None


def _match_patterns(path: str, patterns: tuple[str, ...]) -> list[str]:
    return [pattern for pattern in patterns if fnmatch.fnmatch(path, pattern)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Track isolation guard for pull requests.")
    parser.add_argument("--base", required=True, help="Base git ref/sha")
    parser.add_argument("--head", required=True, help="Head git ref/sha")
    parser.add_argument("--pr-title", default="", help="PR title")
    parser.add_argument("--labels", default="", help="Comma separated PR labels")
    parser.add_argument(
        "--allow",
        default="",
        help="Comma separated path prefixes that are allowed even if forbidden by track",
    )
    args = parser.parse_args()

    labels = [part.strip() for part in args.labels.split(",") if part.strip()]
    allow_prefixes = tuple(part.strip().rstrip("/") + "/" for part in args.allow.split(",") if part.strip())

    track = _detect_track(pr_title=args.pr_title, labels=labels)
    if not track:
        print("[track-isolation] Track не определен по title/labels; проверка пропущена.")
        return 0

    changed_files = _git_changed_files(base_ref=args.base, head_ref=args.head)
    print(f"[track-isolation] track={track}, changed_files={len(changed_files)}")

    rules = RULES.get(track)
    if not rules:
        print(f"[track-isolation] Для {track} нет правил; проверка пропущена.")
        return 0

    violations: list[tuple[str, list[str]]] = []
    for file_path in changed_files:
        if allow_prefixes and file_path.startswith(allow_prefixes):
            continue
        matched = _match_patterns(file_path, rules.forbidden_patterns)
        if matched:
            violations.append((file_path, matched))

    if not violations:
        print("[track-isolation] OK")
        return 0

    print("[track-isolation] FAIL")
    print(rules.reason)
    preview = violations[:20]
    for file_path, patterns in preview:
        print(f"  - {file_path}  (matched: {', '.join(patterns)})")
    if len(violations) > len(preview):
        print(f"  ... и еще {len(violations) - len(preview)} файлов")

    print("Подсказка: используйте --allow 'prefix1,prefix2' только для явно согласованных исключений.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
