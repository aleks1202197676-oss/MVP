from __future__ import annotations

import json
import os
import shutil

import yaml

from core.llm_bundle import build_llm_bundle
from core.run_registry import ensure_run_folders, new_run_id
from pipelines.finance.run_finance import main as run_finance


def load_cfg(path: str = "config/hub.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    cfg = load_cfg()
    run_id = new_run_id(cfg["hub"]["run_id_format"])
    folders = ensure_run_folders(cfg["hub"]["output_root"], run_id)

    manifest: dict[str, object] = {
        "run_id": run_id,
        "pipelines": {},
        "bundle": None,
    }

    finance_cfg = cfg.get("pipelines", {}).get("finance", {})
    if finance_cfg.get("enabled", False):
        inputs = finance_cfg.get("inputs", {})
        out_dir = finance_cfg.get("outputs", {}).get("latest_folder", "data/outputs/latest/finance")
        files = run_finance(
            config_path=inputs.get("finance_config", "config/finance_config.yml"),
            data_root=inputs.get("data_root", "data/raw/finance"),
            out_dir=out_dir,
        )
        manifest["pipelines"]["finance"] = {
            "enabled": True,
            "output_dir": out_dir,
            "files": files,
        }

    if cfg.get("llm_bundle", {}).get("enabled", True):
        zip_path = os.path.join(folders["latest"], "latest_bundle.zip")
        files = build_llm_bundle(
            zip_path,
            include_globs=cfg["llm_bundle"]["include_globs"],
            exclude_globs=cfg["llm_bundle"].get("exclude_globs", []),
            max_files=int(cfg["llm_bundle"].get("max_files", 200)),
        )
        manifest["bundle"] = {"path": zip_path, "files": files}
        print(f"[LLM] bundle={zip_path} files={len(files)}")

    manifest_path = os.path.join(folders["latest"], "run_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    ai_contract_latest = os.path.join("data", "ai_contract", "latest")
    os.makedirs(ai_contract_latest, exist_ok=True)
    shutil.copy2(manifest_path, os.path.join(ai_contract_latest, "run_manifest.json"))
    if manifest.get("bundle") and isinstance(manifest["bundle"], dict):
        bundle_path = str(manifest["bundle"].get("path", ""))
        if bundle_path and os.path.exists(bundle_path):
            shutil.copy2(bundle_path, os.path.join(ai_contract_latest, "latest_bundle.zip"))
    print(f"[RUN] {run_id}")
    print(f"[OUT] latest={folders['latest']} history={folders['history']}")
    print(f"[MANIFEST] {manifest_path}")


if __name__ == "__main__":
    main()
