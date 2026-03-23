from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path

import nbformat
from nbconvert import HTMLExporter


HTML_TEMPLATE = """<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>TARDIS Approach-4 Notebook Gallery</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 2rem; background: #0b1020; color: #e8edf7; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 1rem; }}
    .card {{ border: 1px solid #2a3558; border-radius: 12px; padding: 1rem; background: #111935; }}
    .muted {{ color: #aeb9d6; font-size: 0.9rem; }}
    a {{ color: #8ec5ff; }}
    .ok {{ color: #8ce99a; }}
    .failed {{ color: #ff9ba5; }}
  </style>
</head>
<body>
  <h1>TARDIS Approach-4 Notebook Gallery</h1>
  <p class=\"muted\">Rendered notebook reports generated per config.</p>
  <div class=\"grid\">{cards}</div>
</body>
</html>
"""


def render_notebook_html(notebook_path: Path, output_dir: Path) -> str:
    notebook_rel = notebook_path.as_posix()
    safe_html_name = notebook_rel.replace("/", "__") + ".html"
    rendered_dir = output_dir / "notebooks"
    rendered_dir.mkdir(parents=True, exist_ok=True)
    rendered_file = rendered_dir / safe_html_name

    with notebook_path.open("r", encoding="utf-8") as fh:
        nb = nbformat.read(fh, as_version=4)

    exporter = HTMLExporter(template_name="lab")
    body, _ = exporter.from_notebook_node(nb)
    rendered_file.write_text(body, encoding="utf-8")
    return f"notebooks/{safe_html_name}"


def card_html(row: dict, output_dir: Path) -> str:
    config = str(row.get("config", ""))
    notebook = str(row.get("notebook", ""))
    status = str(row.get("status", "unknown"))
    reason = str(row.get("reason", ""))
    notebook_exists = bool(row.get("notebook_exists", False))

    config_link = f"../{config}"
    notebook_link = f"../{notebook}"
    config_name = Path(config).name if config else "(missing config)"

    rendered_html_link = ""
    if notebook_exists:
      notebook_path = Path(notebook)
      if notebook_path.exists():
        rendered_html_link = render_notebook_html(notebook_path, output_dir)

    notebook_line = (
      f"<p><a href='{escape(rendered_html_link)}'>Open rendered notebook</a></p><p><a href='{escape(notebook_link)}'>Raw notebook (.ipynb)</a></p>"
      if rendered_html_link
      else (
        f"<p><a href='{escape(notebook_link)}'>Raw notebook (.ipynb)</a></p>"
        if notebook_exists
        else "<p class='muted'>Notebook unavailable (run failed or file missing)</p>"
      )
    )

    status_class = "ok" if status == "ok" else "failed"
    status_line = f"<p class='muted'>Status: <span class='{status_class}'>{escape(status)}</span></p>"
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

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    cards = "\n".join(card_html(row, output_dir) for row in rows)
    html = HTML_TEMPLATE.format(cards=cards or "<p>No notebooks generated yet.</p>")
    (output_dir / "index.html").write_text(html, encoding="utf-8")
    print(f"Gallery written to {output_dir / 'index.html'}")


if __name__ == "__main__":
    main()
