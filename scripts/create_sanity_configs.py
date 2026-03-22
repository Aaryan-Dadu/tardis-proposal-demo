from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml


def make_lightweight_config(input_path: Path, output_path: Path) -> None:
    if input_path.suffix.lower() == ".csvy":
        output_path.write_text(input_path.read_text(encoding="utf-8"), encoding="utf-8")
        return

    data = yaml.safe_load(input_path.read_text(encoding="utf-8")) or {}
    montecarlo = data.setdefault("montecarlo", {})

    no_of_packets = float(montecarlo.get("no_of_packets", 10))
    montecarlo["no_of_packets"] = min(no_of_packets, 10)

    virtual_packets = float(montecarlo.get("no_of_virtual_packets", 4))
    montecarlo["no_of_virtual_packets"] = min(virtual_packets, 4)

    montecarlo["last_no_of_packets"] = 20

    iterations = float(montecarlo.get("iterations", 5))
    montecarlo["iterations"] = min(iterations, 5)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create lightweight sanity configs.")
    parser.add_argument("--setup-manifest", default="generated/setup-generation-manifest.json")
    parser.add_argument("--output", default="generated/sanity-manifest.json")
    parser.add_argument("--sanity-dir", default="generated/sanity-configs")
    args = parser.parse_args()

    rows = json.loads(Path(args.setup_manifest).read_text(encoding="utf-8"))
    sanity_dir = Path(args.sanity_dir)
    out_rows = []

    for row in rows:
        config_path = Path(row["config"])
        sanity_path = sanity_dir / config_path
        make_lightweight_config(config_path, sanity_path)
        out_rows.append(
            {
                **row,
                "sanity_config": str(sanity_path),
            }
        )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(out_rows, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {len(out_rows)} sanity config(s)")


if __name__ == "__main__":
    main()
