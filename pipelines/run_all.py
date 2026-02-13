from __future__ import annotations

import json
from pathlib import Path

import yaml

from core.compiled_memory import update_project_state, write_compiled_memory
from core.llm_bundle import build_llm_bundle
from core.run_registry import ensure_run_folders, new_run_id
from pipelines.finance import run_finance_pipeline
from pipelines.finance_mvp import run_finance_mvp_pipeline


def load_cfg(path: str = "config/hub.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def apply_project_state_overrides(cfg: dict, state_path: str = "contracts/meta/project_state.yml") -> dict:
    path = Path(state_path)
    if not path.exists():
        return cfg

    state = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    override_enabled = state.get("pipelines", {}).get("finance_mvp", {}).get("enabled")
    if isinstance(override_enabled, bool):
        cfg.setdefault("pipelines", {}).setdefault("finance_mvp", {})["enabled"] = override_enabled
    return cfg


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
    finance_mvp_enabled = bool(cfg.get("pipelines", {}).get("finance_mvp", {}).get("enabled", False))
    if finance_mvp_enabled:
        include.extend(bundle_cfg.get("include_when_finance_mvp_enabled", []))
    return include


def main() -> None:
    cfg = load_cfg()
    cfg = apply_project_state_overrides(cfg)
    run_id = new_run_id(cfg["hub"]["run_id_format"])
    ensure_run_folders(cfg["hub"]["output_root"], run_id)

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

    finance_enabled = bool(cfg.get("pipelines", {}).get("finance", {}).get("enabled", False))
    finance_mvp_enabled = bool(cfg.get("pipelines", {}).get("finance_mvp", {}).get("enabled", False))

    if finance_enabled:
        finance_report_path = run_finance_pipeline(cfg=cfg, run_id=run_id)
        key_artifacts.append(str(finance_report_path))

    if finance_mvp_enabled:
        finance_mvp_report_path = run_finance_mvp_pipeline(cfg=cfg, run_id=run_id)
        key_artifacts.append(str(finance_mvp_report_path))

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
