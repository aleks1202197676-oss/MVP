from __future__ import annotations

import datetime as dt
from pathlib import Path

import yaml


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _sorted_unique(items: list[str]) -> list[str]:
    return sorted(set(items))


def write_compiled_memory(run_id: str, key_artifacts: list[str]) -> dict[str, str]:
    meta_dir = Path("contracts/meta")
    meta_dir.mkdir(parents=True, exist_ok=True)

    artifacts = _sorted_unique(key_artifacts)
    generated_at = _utc_now()

    md_path = meta_dir / "COMPILED_MEMORY.md"
    yml_path = meta_dir / "COMPILED_MEMORY.yml"

    md_lines = [
        "# COMPILED MEMORY",
        "",
        f"- generated_at: {generated_at}",
        f"- last_green_run: {run_id}",
        "",
        "## Key artifacts",
    ]
    md_lines.extend(f"- `{artifact}`" for artifact in artifacts)
    md_lines.append("")

    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    payload = {
        "generated_at": generated_at,
        "last_green_run": run_id,
        "artifacts": artifacts,
    }
    yml_path.write_text(yaml.safe_dump(payload, sort_keys=True, allow_unicode=True), encoding="utf-8")

    return {"md": str(md_path), "yml": str(yml_path)}


def update_project_state(run_id: str, key_artifacts: list[str]) -> str:
    state_path = Path("contracts/meta/project_state.yml")
    state_path.parent.mkdir(parents=True, exist_ok=True)

    current = {}
    if state_path.exists():
        current = yaml.safe_load(state_path.read_text(encoding="utf-8")) or {}

    current["version"] = int(current.get("version", 1))
    current["project"] = current.get("project", "MVP")
    current["last_green_run"] = run_id
    current["key_artifacts"] = _sorted_unique(key_artifacts)

    state_path.write_text(yaml.safe_dump(current, sort_keys=True, allow_unicode=True), encoding="utf-8")
    return str(state_path)
