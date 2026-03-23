from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path


HTML_TEMPLATE = """<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>TARDIS Approach-4 Notebook Gallery</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1rem; }}
    .card {{ border: 1px solid #ddd; border-radius: 8px; padding: 1rem; }}
    .muted {{ color: #666; font-size: 0.9rem; }}
  </style>
</head>
<body>
  <h1>TARDIS Approach-4 Notebook Gallery</h1>
  <p class=\"muted\">Prototype view for generated notebooks per committed config.</p>
  <div class=\"grid\">{cards}</div>
</body>
</html>
"""


def card_html(row: dict) -> str:
    config = str(row.get("config", ""))
    notebook = str(row.get("notebook", ""))
    status = str(row.get("status", "unknown"))
    reason = str(row.get("reason", ""))
    notebook_exists = bool(row.get("notebook_exists", False))

    config_link = f"../{config}"
    notebook_link = f"../{notebook}"
    config_name = Path(config).name if config else "(missing config)"

    notebook_line = (
        f"<p><a href='{escape(notebook_link)}'>Notebook (.ipynb)</a></p>"
        if notebook_exists
        else "<p class='muted'>Notebook unavailable (run failed or file missing)</p>"
    )

    status_line = f"<p class='muted'>Status: {escape(status)}</p>"
    reason_line = f"<p class='muted'>Reason: {escape(reason)}</p>" if reason and reason != "ok" else ""

    return (
        "<div class='card'>"
        f"<h3>{escape(config_name)}</h3>"
        f"<p class='muted'>{escape(config)}</p>"
        f"<p><a href='{escape(config_link)}'>Config file</a></p>"
        f"{notebook_line}"
        f"{status_line}"
        f"{reason_line}"
        "</div>"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build static notebook gallery page.")
    parser.add_argument("--manifest", default="out/notebook-manifest.json")
    parser.add_argument("--output-dir", default="docs-site")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    rows = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else []

    cards = "\n".join(card_html(row) for row in rows)
    html = HTML_TEMPLATE.format(cards=cards or "<p>No notebooks generated yet.</p>")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "index.html").write_text(html, encoding="utf-8")
    print(f"Gallery written to {output_dir / 'index.html'}")


if __name__ == "__main__":
    main()
