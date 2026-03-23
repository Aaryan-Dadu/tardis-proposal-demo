from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Create queue payload for server execution.")
    parser.add_argument("--sanity-results", default="generated/sanity-results.json")
    parser.add_argument("--setup-manifest", default="generated/setup-generation-manifest.json")
    parser.add_argument("--output", default="generated/server-queue.json")
    args = parser.parse_args()

    sanity_path = Path(args.sanity_results)
    setup_manifest_path = Path(args.setup_manifest)

    if sanity_path.exists():
        rows = json.loads(sanity_path.read_text(encoding="utf-8"))
        queue = [row for row in rows if row.get("sanity_passed")]
        source = "sanity-results"
    elif setup_manifest_path.exists():
        queue = json.loads(setup_manifest_path.read_text(encoding="utf-8"))
        source = "setup-generation-manifest"
    else:
        queue = []
        source = "none"

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(queue, indent=2) + "\n", encoding="utf-8")
    print(f"Queued {len(queue)} config(s) for server execution (source: {source})")


if __name__ == "__main__":
    main()
