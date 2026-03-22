from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def run_git_diff(base_ref: str, head_ref: str) -> list[str]:
    cmd = ["git", "diff", "--name-only", f"{base_ref}...{head_ref}"]
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def is_config(path: str) -> bool:
    candidate = Path(path)
    suffix = candidate.suffix.lower()
    if suffix not in {".yml", ".yaml", ".csvy"}:
        return False

    parts = candidate.parts
    if not parts or parts[0] != "setups":
        return False

    if candidate.name == "setup.yaml":
        return False

    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect changed TARDIS config files.")
    parser.add_argument("--base-ref", default="origin/main")
    parser.add_argument("--head-ref", default="HEAD")
    parser.add_argument("--output", default="generated/changed-configs.json")
    args = parser.parse_args()

    changed = run_git_diff(args.base_ref, args.head_ref)
    configs = [path for path in changed if is_config(path)]

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "base_ref": args.base_ref,
        "head_ref": args.head_ref,
        "count": len(configs),
        "configs": sorted(configs),
    }
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Detected {len(configs)} changed config file(s)")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
