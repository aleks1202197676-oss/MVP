from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import yaml

from core.llm_bundle import build_llm_bundle
from core.run_registry import ensure_run_folders, new_run_id


def load_cfg(path: str = "config/hub.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def main() -> None:
    cfg = load_cfg()
    run_id = new_run_id(cfg["hub"]["run_id_format"])
    folders = ensure_run_folders(cfg["hub"]["output_root"], run_id)

    print(f"[RUN] {run_id}")
    print(f"[OUT] latest={folders['latest']} history={folders['history']}")

    llm_cfg = cfg.get("llm_bundle", {})
    if llm_cfg.get("enabled", True):
        zip_path = llm_cfg.get("zip_path", os.path.join(folders["latest"], f"LLM_BUNDLE_{run_id}.zip"))
        files = build_llm_bundle(
            zip_path=zip_path,
            include_globs=llm_cfg.get("include_globs", []),
            exclude_globs=llm_cfg.get("exclude_globs", []),
            max_files=int(llm_cfg.get("max_files", 5000)),
        )
        print(f"[LLM] bundle={zip_path} files={len(files)}")

        manifest_path = os.path.join(os.path.dirname(zip_path), "run_manifest.json")
        manifest = {
            "run_id": run_id,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "bundle_path": zip_path,
            "files_count": len(files),
            "files": files,
        }
        with open(manifest_path, "w", encoding="utf-8") as file:
            json.dump(manifest, file, ensure_ascii=False, indent=2)
        print(f"[LLM] manifest={manifest_path}")


if __name__ == "__main__":
    main()
