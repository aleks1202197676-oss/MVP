from __future__ import annotations
import os, yaml
from core.run_registry import new_run_id, ensure_run_folders
from core.llm_bundle import build_llm_bundle

def load_cfg(path="config/hub.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def main():
    cfg = load_cfg()
    run_id = new_run_id(cfg["hub"]["run_id_format"])
    folders = ensure_run_folders(cfg["hub"]["output_root"], run_id)

    # Здесь место для вызова отдельных пайплайнов.
    # По умолчанию это заглушка — ты подключишь существующие скрипты.
    print(f"[RUN] {run_id}")
    print(f"[OUT] latest={folders['latest']} history={folders['history']}")

    # LLM bundle
    if cfg.get("llm_bundle", {}).get("enabled", True):
        zip_path = os.path.join(folders["latest"], f"LLM_BUNDLE_{run_id}.zip")
        files = build_llm_bundle(zip_path,
                                 include_globs=cfg["llm_bundle"]["include_globs"],
                                 exclude_globs=cfg["llm_bundle"].get("exclude_globs", []),
                                 max_files=int(cfg["llm_bundle"].get("max_files", 40)))
        print(f"[LLM] bundle={zip_path} files={len(files)}")

if __name__ == "__main__":
    main()
