from __future__ import annotations

import datetime as dt
import json
import os
import shutil
import subprocess
from pathlib import Path

import yaml

from core.llm_bundle import build_llm_bundle
from core.run_registry import ensure_run_folders, new_run_id
from pipelines.finance.run_finance import run_finance


CONFIG_PATH = "config/hub.yaml"
FINANCE_CONFIG_PATH = "config/finance_config.yml"
PROJECT_STATE_PATH = "contracts/meta/project_state.yml"


def load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def get_git_sha() -> str | None:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL)
            .strip()
            or None
        )
    except Exception:
        return None


def update_project_state(command: str, artifacts: dict[str, str]) -> None:
    state = load_yaml(PROJECT_STATE_PATH)
    root = state.setdefault("project_memory", {})
    root.setdefault("phase", "mvp")

    root["last_green_run"] = {
        "datetime": dt.datetime.now(dt.timezone.utc).isoformat(),
        "git_sha": get_git_sha(),
        "command": command,
        "key_artifacts": sorted(set(artifacts.values())),
    }
    root["artifacts_map"] = {
        "ai_contract_latest": "data/ai_contract/latest",
        "outputs_latest_finance": "data/outputs/latest/finance",
    }

    with open(PROJECT_STATE_PATH, "w", encoding="utf-8") as handle:
        yaml.safe_dump(state, handle, sort_keys=False, allow_unicode=True)


def main() -> None:
    cfg = load_yaml(CONFIG_PATH)
    finance_cfg = load_yaml(FINANCE_CONFIG_PATH)

    run_id = new_run_id(cfg["hub"].get("run_id_format", "%Y%m%d_%H%M%S"))
    folders = ensure_run_folders(cfg["hub"]["output_root"], run_id)

    artifacts: dict[str, str] = {}
    if finance_cfg.get("finance", {}).get("enabled", True):
        artifacts.update(run_finance(finance_cfg["finance"]["output_dir"]))

    manifest = {
        "run_id": run_id,
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "command": "python -m pipelines.run_all",
        "artifacts": artifacts,
    }

    manifest_path = Path(folders["latest"]) / "run_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    artifacts["run_manifest"] = str(manifest_path)

    update_project_state(manifest["command"], artifacts)

    bundle_path = Path("data/ai_contract/latest/latest_bundle.zip")
    files = build_llm_bundle(
        str(bundle_path),
        include_globs=cfg["llm_bundle"]["include_globs"],
        exclude_globs=cfg["llm_bundle"].get("exclude_globs", []),
        max_files=int(cfg["llm_bundle"].get("max_files", 500)),
    )

    ai_contract_latest = Path("data/ai_contract/latest")
    ai_contract_latest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(manifest_path, ai_contract_latest / "run_manifest.json")
    artifacts["latest_bundle"] = str(bundle_path)

    print(f"[RUN] {run_id}")
    print(f"[OUT] latest={folders['latest']} history={folders['history']}")
    print(f"[MANIFEST] {manifest_path}")
    print(f"[BUNDLE] {bundle_path} files={len(files)}")


if __name__ == "__main__":
    main()
