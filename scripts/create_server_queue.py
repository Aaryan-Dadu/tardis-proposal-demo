from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Create queue payload for server execution.")
    parser.add_argument("--sanity-results", default="generated/sanity-results.json")
    parser.add_argument("--output", default="generated/server-queue.json")
    args = parser.parse_args()

    rows = json.loads(Path(args.sanity_results).read_text(encoding="utf-8"))
    queue = [row for row in rows if row.get("sanity_passed")]

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(queue, indent=2) + "\n", encoding="utf-8")
    print(f"Queued {len(queue)} config(s) for server execution")


if __name__ == "__main__":
    main()
