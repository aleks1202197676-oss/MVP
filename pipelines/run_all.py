from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import yaml

from core.llm_bundle import build_llm_bundle
from core.run_registry import ensure_run_folders, new_run_id
from pipelines.health.import_samsung_health import main as run_health
from pipelines.models.solve_equation_model import main as run_models


def load_cfg(path: str = "config/hub.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_ai_contract(cfg: dict, run_id: str, folders: dict[str, str]) -> tuple[str, str]:
    contract_latest = Path("data/ai_contract/latest")
    contract_latest.mkdir(parents=True, exist_ok=True)

    bundle_path = contract_latest / "latest_bundle.zip"
    bundle_files = build_llm_bundle(
        str(bundle_path),
        include_globs=cfg["llm_bundle"]["include_globs"],
        exclude_globs=cfg["llm_bundle"].get("exclude_globs", []),
        max_files=int(cfg["llm_bundle"].get("max_files", 40)),
    )

    manifest = {
        "run_id": run_id,
        "generated_at": dt.datetime.now().isoformat(),
        "outputs_latest": folders["latest"],
        "outputs_history": folders["history"],
        "bundle_path": str(bundle_path).replace("\\", "/"),
        "bundle_file_count": len(bundle_files),
    }
    manifest_path = contract_latest / "run_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(manifest_path), str(bundle_path)


def main() -> None:
    cfg = load_cfg()
    run_id = new_run_id(cfg["hub"]["run_id_format"])
    folders = ensure_run_folders(cfg["hub"]["output_root"], run_id)

    if cfg.get("pipelines", {}).get("health", {}).get("enabled", False):
        run_health(
            inbox=cfg["pipelines"]["health"]["inputs"]["samsung_export_drop"],
            out=cfg["pipelines"]["health"]["outputs"]["latest_folder"],
        )

    if cfg.get("pipelines", {}).get("models", {}).get("enabled", False):
        run_models(
            spec=cfg["pipelines"]["models"]["inputs"]["model_spec"],
            out=cfg["pipelines"]["models"]["outputs"]["latest_folder"],
        )

    manifest_path, bundle_path = write_ai_contract(cfg, run_id, folders)

    print(f"[RUN] {run_id}")
    print(f"[OUT] latest={folders['latest']} history={folders['history']}")
    print(f"[AI_CONTRACT] manifest={manifest_path}")
    print(f"[AI_CONTRACT] bundle={bundle_path}")


if __name__ == "__main__":
    main()
