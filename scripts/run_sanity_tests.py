from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def run_one_sanity(config_path: Path, atom_data: str) -> bool:
    cmd = [
        "python",
        "scripts/plot_from_config.py",
        str(config_path),
        "--atom-data",
        atom_data,
        "--output-dir",
        "generated/sanity-plots",
        "--output-prefix",
        config_path.stem,
    ]
    result = subprocess.run(cmd, check=False)
    return result.returncode == 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Run minimal sanity tests for changed configs.")
    parser.add_argument("--sanity-manifest", default="generated/sanity-manifest.json")
    parser.add_argument("--output", default="generated/sanity-results.json")
    args = parser.parse_args()

    rows = json.loads(Path(args.sanity_manifest).read_text(encoding="utf-8"))
    results = []

    for row in rows:
        ok = run_one_sanity(Path(row["sanity_config"]), row.get("atom_data", "kurucz_cd23_chianti_H_He_latest"))
        results.append({**row, "sanity_passed": ok})

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")

    failed = [r for r in results if not r["sanity_passed"]]
    print(f"Sanity passed: {len(results) - len(failed)}/{len(results)}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
