from __future__ import annotations

from pipelines.finance.export_finance import export_finance_outputs
from pipelines.finance.ingest_finance import read_finance_inputs
from pipelines.finance.simulate_finance import run_simulation


def main(config_path: str = "config/finance_config.yml", data_root: str = "data/raw/finance", out_dir: str = "data/outputs/latest/finance") -> list[str]:
    finance_inputs = read_finance_inputs(config_path=config_path, data_root=data_root)
    simulation = run_simulation(finance_inputs)
    paths = export_finance_outputs(simulation, out_dir=out_dir)
    print(f"[finance] exported {len(paths)} files -> {out_dir}")
    return paths


if __name__ == "__main__":
    main()
