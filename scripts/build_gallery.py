from __future__ import annotations

import argparse
import json
from pathlib import Path


HTML_TEMPLATE = """<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>TARDIS Approach-4 Notebook Gallery</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 2rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1rem; }
    .card { border: 1px solid #ddd; border-radius: 8px; padding: 1rem; }
    .muted { color: #666; font-size: 0.9rem; }
  </style>
</head>
<body>
  <h1>TARDIS Approach-4 Notebook Gallery</h1>
  <p class=\"muted\">Prototype view for generated notebooks per committed config.</p>
  <div class=\"grid\">{cards}</div>
</body>
</html>
"""


def card_html(config: str, notebook: str) -> str:
    config_link = f"../{config}"
    notebook_link = f"../{notebook}"
    return (
        "<div class='card'>"
        f"<h3>{Path(config).name}</h3>"
        f"<p class='muted'>{config}</p>"
        f"<p><a href='{config_link}'>Config file</a></p>"
        f"<p><a href='{notebook_link}'>Notebook (.ipynb)</a></p>"
        "</div>"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build static notebook gallery page.")
    parser.add_argument("--manifest", default="out/notebook-manifest.json")
    parser.add_argument("--output-dir", default="docs-site")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    rows = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else []

    cards = "\n".join(card_html(row["config"], row["notebook"]) for row in rows)
    html = HTML_TEMPLATE.format(cards=cards or "<p>No notebooks generated yet.</p>")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "index.html").write_text(html, encoding="utf-8")
    print(f"Gallery written to {output_dir / 'index.html'}")


if __name__ == "__main__":
    main()
