from __future__ import annotations

import json
from pathlib import Path

import yaml

from core.compiled_memory import update_project_state, write_compiled_memory
from core.llm_bundle import build_llm_bundle
from core.run_registry import ensure_run_folders, new_run_id
from pipelines.finance import run_finance_pipeline


def load_cfg(path: str = "config/hub.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def build_manifest(run_id: str, bundle_path: str, key_artifacts: list[str]) -> str:
    manifest_path = Path("run_manifest.json")
    payload = {
        "bundle_path": bundle_path,
        "key_artifacts": sorted(set(key_artifacts)),
        "run_id": run_id,
    }
    manifest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return str(manifest_path)


def _bundle_include_globs(cfg: dict) -> list[str]:
    bundle_cfg = cfg.get("bundle", {})
    include = list(bundle_cfg.get("include_globs", []))
    finance_enabled = bool(cfg.get("pipelines", {}).get("finance", {}).get("enabled", False))
    if finance_enabled:
        include.extend(bundle_cfg.get("include_when_finance_enabled", []))
    return include


def main() -> None:
    cfg = load_cfg()
    run_id = new_run_id(cfg["hub"]["run_id_format"])
    ensure_run_folders(cfg["hub"]["output_root"], run_id)

    finance_cfg = cfg.get("pipelines", {}).get("finance", {})
    if finance_cfg.get("enabled", False):
        finance_output_dir = finance_cfg.get("outputs", {}).get("latest_folder", "data/outputs/latest/finance")
        finance_outputs = run_finance_pipeline(output_dir=finance_output_dir)
        print(f"[FINANCE] generated {len(finance_outputs)} files")

    bundle_cfg = cfg.get("bundle", {})
    if not bundle_cfg.get("enabled", True):
        print("[BUNDLE] disabled")
        return

    bundle_path = bundle_cfg["output_path"]
    key_artifacts = [
        "contracts/meta/START_HERE.md",
        "contracts/meta/project_state.yml",
        "contracts/meta/COMPILED_MEMORY.md",
        "pipelines/run_all.py",
        "START_HERE.md",
    ]

    write_compiled_memory(run_id=run_id, key_artifacts=key_artifacts)
    update_project_state(run_id=run_id, key_artifacts=key_artifacts)
    build_manifest(run_id=run_id, bundle_path=bundle_path, key_artifacts=key_artifacts)

    files = build_llm_bundle(
        zip_path=bundle_path,
        include_globs=_bundle_include_globs(cfg),
        exclude_globs=bundle_cfg.get("exclude_globs", []),
    )

    print(f"[RUN] {run_id}")
    print(f"[BUNDLE] {bundle_path}")
    print(f"[FILES] {len(files)}")


if __name__ == "__main__":
    main()
