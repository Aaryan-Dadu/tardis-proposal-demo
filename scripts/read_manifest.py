import json
from pathlib import Path

manifest = Path("generated/setup-generation-manifest.json")
selected: list[str] = []
if manifest.exists():
    rows = json.loads(manifest.read_text(encoding="utf-8"))
    for row in rows:
        path = row.get("setup_yaml") if isinstance(row, dict) else None
        if isinstance(path, str) and path.strip() and Path(path).exists():
            selected.append(path)

out = Path("generated/setup-yaml-paths.txt")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(sorted(set(selected))) + "\n", encoding="utf-8")
print(f"setup_yaml candidates: {len(set(selected))}")