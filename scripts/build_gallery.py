from __future__ import annotations

import argparse
import json
import shutil
from collections import Counter
from html import escape
from pathlib import Path

import nbformat
from nbconvert import HTMLExporter


HTML_TEMPLATE = """<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>TARDIS Proposal Prototype Notebook Gallery</title>
  <style>
    :root {{
      --page-bg: #f5f8ff;
      --surface: #ffffff;
      --surface-muted: #f8fbff;
      --surface-border: #d6e2f3;
      --text-main: #1f2a44;
      --text-muted: #617392;
      --brand: #2e5ca0;
      --brand-soft: #eaf2ff;
      --ok: #19723a;
      --ok-bg: #e8f7ed;
      --fail: #b0273a;
      --fail-bg: #fdeef1;
      --shadow: 0 10px 24px rgba(31, 42, 68, 0.08);
    }}

    * {{ box-sizing: border-box; }}
    body {{
      font-family: "Segoe UI", Roboto, Arial, sans-serif;
      margin: 0;
      color: var(--text-main);
      background: linear-gradient(180deg, #eef5ff 0%, var(--page-bg) 250px);
    }}

    .container {{
      max-width: 1240px;
      margin: 0 auto;
      padding: 1.75rem 1.2rem 2rem;
    }}

    .hero {{
      background: var(--surface);
      border: 1px solid var(--surface-border);
      border-radius: 16px;
      box-shadow: var(--shadow);
      padding: 1.15rem 1.25rem;
      margin-bottom: 0.95rem;
    }}

    h1 {{
      margin: 0;
      color: #183969;
      font-size: 1.55rem;
      letter-spacing: 0.01em;
    }}

    .subtitle {{
      margin: 0.38rem 0 0;
      color: var(--text-muted);
      font-size: 0.95rem;
    }}

    .summary {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.55rem;
      margin-top: 0.9rem;
    }}

    .pill {{
      border: 1px solid var(--surface-border);
      background: var(--brand-soft);
      color: var(--brand);
      font-weight: 700;
      font-size: 0.82rem;
      border-radius: 999px;
      padding: 0.28rem 0.7rem;
    }}
    .pill.ok {{ background: var(--ok-bg); color: var(--ok); border-color: #bfe7c9; }}
    .pill.fail {{ background: var(--fail-bg); color: var(--fail); border-color: #f2c1cb; }}

    .overview {{
      margin-top: 0.9rem;
      background: var(--surface-muted);
      border: 1px solid var(--surface-border);
      border-radius: 12px;
      padding: 0.75rem 0.85rem;
    }}

    .overview h2 {{
      margin: 0;
      font-size: 0.95rem;
      color: #214376;
    }}

    .overview-grid {{
      margin-top: 0.55rem;
      display: grid;
      gap: 0.35rem;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    }}

    .overview-item {{
      font-size: 0.84rem;
      color: #4e648a;
      background: #fff;
      border: 1px solid var(--surface-border);
      border-radius: 8px;
      padding: 0.42rem 0.55rem;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .controls {{
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 0.7rem;
      margin-top: 0.9rem;
      align-items: center;
    }}

    .search {{
      width: 100%;
      border: 1px solid var(--surface-border);
      border-radius: 10px;
      padding: 0.58rem 0.72rem;
      font-size: 0.9rem;
      color: var(--text-main);
      background: #fff;
    }}

    .filter-row {{
      display: flex;
      gap: 0.4rem;
      flex-wrap: wrap;
    }}

    .chip {{
      border: 1px solid var(--surface-border);
      background: #fff;
      color: var(--text-muted);
      border-radius: 999px;
      padding: 0.34rem 0.62rem;
      font-size: 0.8rem;
      cursor: pointer;
      font-weight: 600;
    }}
    .chip.active {{
      background: var(--brand);
      border-color: var(--brand);
      color: #fff;
    }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(460px, 1fr));
      gap: 0.85rem;
      align-items: start;
      margin-top: 0.95rem;
    }}

    .card {{
      border: 1px solid var(--surface-border);
      border-radius: 14px;
      padding: 0.9rem;
      background: var(--surface);
      box-shadow: var(--shadow);
    }}

    .card-top {{
      display: flex;
      justify-content: space-between;
      gap: 0.7rem;
      align-items: center;
    }}

    .card-title {{
      margin: 0;
      font-size: 1rem;
      color: #173764;
      word-break: break-word;
    }}

    .status-badge {{
      border-radius: 999px;
      padding: 0.2rem 0.56rem;
      font-size: 0.74rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.02em;
      border: 1px solid;
      white-space: nowrap;
    }}
    .status-ok {{ color: var(--ok); background: var(--ok-bg); border-color: #bfe7c9; }}
    .status-failed {{ color: var(--fail); background: var(--fail-bg); border-color: #f2c1cb; }}

    .path {{
      margin: 0.28rem 0 0.62rem;
      color: var(--text-muted);
      font-size: 0.86rem;
      word-break: break-word;
    }}

    .meta {{
      display: grid;
      grid-template-columns: 108px 1fr;
      gap: 0.3rem 0.62rem;
      font-size: 0.82rem;
      color: #566f96;
      margin-bottom: 0.65rem;
    }}

    .meta .label {{ font-weight: 700; color: #35588e; }}

    .actions {{
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
      margin-top: 0.25rem;
    }}

    .btn {{
      display: inline-flex;
      align-items: center;
      border: 1px solid var(--surface-border);
      border-radius: 8px;
      padding: 0.4rem 0.68rem;
      background: #fff;
      color: var(--brand);
      text-decoration: none;
      font-weight: 700;
      font-size: 0.82rem;
      cursor: pointer;
    }}
    .btn:hover {{ border-color: #b9cce8; background: #f7fbff; }}
    .btn.primary {{ background: var(--brand); color: #fff; border-color: var(--brand); }}

    .reason {{
      margin-top: 0.6rem;
      border: 1px dashed #f2c2cc;
      border-radius: 8px;
      background: #fff6f8;
      color: #8e2e3f;
      padding: 0.5rem 0.58rem;
      font-size: 0.81rem;
    }}

    .hidden {{ display: none !important; }}

    .preview-panel {{
      margin-top: 0.95rem;
      border: 1px solid var(--surface-border);
      border-radius: 14px;
      background: var(--surface);
      box-shadow: var(--shadow);
      overflow: hidden;
      max-width: 1180px;
      margin-left: auto;
      margin-right: auto;
    }}

    .preview-head {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 0.7rem;
      padding: 0.65rem 0.8rem;
      border-bottom: 1px solid var(--surface-border);
      background: var(--surface-muted);
    }}

    .preview-title {{
      margin: 0;
      font-size: 0.92rem;
      color: #264a7e;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .preview-frame {{
      width: 100%;
      height: 620px;
      border: 0;
      background: #fff;
    }}

    .empty-panel {{
      padding: 0.8rem;
      color: var(--text-muted);
      font-size: 0.86rem;
      background: #fbfdff;
    }}

    @media (max-width: 980px) {{
      .controls {{ grid-template-columns: 1fr; }}
      .grid {{ grid-template-columns: 1fr; }}
      .preview-frame {{ height: 500px; }}
      .meta {{ grid-template-columns: 95px 1fr; }}
    }}
  </style>
</head>
<body>
  <div class=\"container\">
    <section class=\"hero\">
      <h1>TARDIS Proposal Prototype Notebook Gallery</h1>
      <p class=\"subtitle\">Rendered notebook outputs with quick in-page preview and full notebook navigation.</p>
      <div class=\"summary\">{summary}</div>
      <div class=\"overview\">
        <h2>Notebook Configurations Overview</h2>
        <div class=\"overview-grid\">{overview}</div>
      </div>
      <div class=\"controls\">
        <input id=\"searchInput\" class=\"search\" type=\"search\" placeholder=\"Search by config name, folder, or path...\" />
        <div class=\"filter-row\" role=\"group\" aria-label=\"Status filters\">
          <button class=\"chip active\" data-filter=\"all\" type=\"button\">All</button>
          <button class=\"chip\" data-filter=\"ok\" type=\"button\">Successful</button>
          <button class=\"chip\" data-filter=\"failed\" type=\"button\">Failed</button>
        </div>
      </div>
    </section>

    <section id=\"previewPanel\" class=\"preview-panel hidden\" aria-live=\"polite\">
      <div class=\"preview-head\">
        <p id=\"previewTitle\" class=\"preview-title\">Notebook Quick Preview</p>
        <div class=\"actions\">
          <a id=\"previewOpenNew\" class=\"btn\" href=\"#\" target=\"_blank\" rel=\"noopener\">Open Full Notebook View</a>
          <button id=\"previewClose\" class=\"btn\" type=\"button\">Close Preview</button>
        </div>
      </div>
      <iframe id=\"previewFrame\" class=\"preview-frame\" loading=\"lazy\"></iframe>
    </section>

    <div class=\"grid\">{cards}</div>
  </div>

  <script>
    (() => {{
      const cards = [...document.querySelectorAll('[data-card]')];
      const searchInput = document.getElementById('searchInput');
      const chips = [...document.querySelectorAll('.chip')];
      const previewPanel = document.getElementById('previewPanel');
      const previewFrame = document.getElementById('previewFrame');
      const previewTitle = document.getElementById('previewTitle');
      const previewOpenNew = document.getElementById('previewOpenNew');
      const previewClose = document.getElementById('previewClose');

      let activeFilter = 'all';

      const applyFilters = () => {{
        const query = (searchInput?.value || '').toLowerCase().trim();
        cards.forEach((card) => {{
          const status = (card.dataset.status || '').toLowerCase();
          const text = (card.dataset.search || '').toLowerCase();
          const statusOk = activeFilter === 'all' || status === activeFilter;
          const textOk = !query || text.includes(query);
          card.classList.toggle('hidden', !(statusOk && textOk));
        }});
      }};

      const showPreview = (url, title, fullUrl) => {{
        if (!url) return;
        previewFrame.src = url;
        previewOpenNew.href = fullUrl || url;
        previewTitle.textContent = `Quick Preview: ${{title}}`;
        previewPanel.classList.remove('hidden');
        previewPanel.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
      }};

      const hidePreview = () => {{
        previewPanel.classList.add('hidden');
        previewFrame.src = '';
        previewOpenNew.href = '#';
      }};

      document.querySelectorAll('[data-preview-url]').forEach((btn) => {{
        btn.addEventListener('click', () => {{
          const url = btn.getAttribute('data-preview-url') || '';
          const fullUrl = btn.getAttribute('data-full-url') || '';
          const title = btn.getAttribute('data-preview-title') || 'Notebook';
          showPreview(url, title, fullUrl);
        }});
      }});

      previewClose?.addEventListener('click', hidePreview);

      searchInput?.addEventListener('input', applyFilters);
      chips.forEach((chip) => {{
        chip.addEventListener('click', () => {{
          chips.forEach((c) => c.classList.remove('active'));
          chip.classList.add('active');
          activeFilter = chip.dataset.filter || 'all';
          applyFilters();
        }});
      }});
    }})();
  </script>
</body>
</html>
"""


def prettify_config_name(config_path: str) -> str:
    stem = Path(config_path).stem
    parts = [part for part in stem.replace("_", " ").replace("-", " ").split() if part]
    if not parts:
        return "Configuration"
    return " ".join(part.capitalize() for part in parts)


def render_notebook_html(notebook_path: Path, output_dir: Path) -> str:
    notebook_rel = notebook_path.as_posix()
    safe_html_name = notebook_rel.replace("/", "__") + ".html"
    rendered_dir = output_dir / "notebooks"
    rendered_dir.mkdir(parents=True, exist_ok=True)
    rendered_file = rendered_dir / safe_html_name

    with notebook_path.open("r", encoding="utf-8") as fh:
        nb = nbformat.read(fh, as_version=4)

    exporter = HTMLExporter(template_name="lab")
    exporter.exclude_input_prompt = True
    exporter.exclude_output_prompt = True
    body, _ = exporter.from_notebook_node(nb)
    rendered_file.write_text(body, encoding="utf-8")
    return f"notebooks/{safe_html_name}"


def render_full_notebook_view(rendered_html_link: str, title: str, output_dir: Path) -> str:
    safe_name = rendered_html_link.replace("/", "__") + "__viewer.html"
    viewers_dir = output_dir / "viewers"
    viewers_dir.mkdir(parents=True, exist_ok=True)
    viewer_file = viewers_dir / safe_name

    viewer_html = f"""<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{escape(title)} - Full Notebook View</title>
  <style>
    :root {{
      --reader-max: 1100px;
      --bg: #f3f7ff;
      --surface: #ffffff;
      --border: #d6e2f3;
      --text: #1f2a44;
      --muted: #5f7291;
      --brand: #2e5ca0;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: \"Segoe UI\", Roboto, Arial, sans-serif; background: var(--bg); color: var(--text); }}
    .top {{ display: flex; justify-content: space-between; align-items: center; gap: 0.75rem; padding: 0.7rem 0.9rem; border-bottom: 1px solid var(--border); background: var(--surface); position: sticky; top: 0; z-index: 2; }}
    .title-wrap {{ min-width: 0; }}
    .title {{ margin: 0; font-size: 0.95rem; color: #1b3f72; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    .subtitle {{ margin: 0.18rem 0 0; font-size: 0.78rem; color: var(--muted); }}
    .actions {{ display: inline-flex; gap: 0.38rem; align-items: center; flex-wrap: wrap; }}
    .btn {{ display: inline-flex; align-items: center; border: 1px solid var(--border); border-radius: 8px; padding: 0.34rem 0.58rem; text-decoration: none; color: var(--brand); background: #fff; font-size: 0.79rem; font-weight: 600; cursor: pointer; }}
    .btn.active {{ background: #eaf2ff; border-color: #b8cceb; }}
    .shell {{ max-width: var(--reader-max); margin: 0.8rem auto 1.1rem; border: 1px solid var(--border); border-radius: 12px; overflow: hidden; background: var(--surface); box-shadow: 0 10px 24px rgba(31,42,68,.08); }}
    .frame {{ width: 100%; height: calc(100vh - 120px); min-height: 620px; border: 0; background: #fff; }}
    body.wide .shell {{ max-width: 96vw; }}
    @media (max-width: 980px) {{ .frame {{ min-height: 500px; }} }}
  </style>
</head>
<body>
  <header class=\"top\">
    <div class=\"title-wrap\">
      <p class=\"title\">{escape(title)} — Full Notebook View</p>
      <p class=\"subtitle\">Reader layout optimized for notebook browsing</p>
    </div>
    <div class=\"actions\">
      <button id=\"normalBtn\" class=\"btn active\" type=\"button\">Normal Width</button>
      <button id=\"wideBtn\" class=\"btn\" type=\"button\">Wide Width</button>
      <a class=\"btn\" href=\"../{escape(rendered_html_link)}\" target=\"_blank\" rel=\"noopener\">Open Raw Render</a>
      <a class=\"btn\" href=\"../index.html\">Back to Gallery</a>
    </div>
  </header>
  <main class=\"shell\">
    <iframe class=\"frame\" src=\"../{escape(rendered_html_link)}\" loading=\"lazy\"></iframe>
  </main>
  <script>
    (() => {{
      const normalBtn = document.getElementById('normalBtn');
      const wideBtn = document.getElementById('wideBtn');
      normalBtn?.addEventListener('click', () => {{
        document.body.classList.remove('wide');
        normalBtn.classList.add('active');
        wideBtn?.classList.remove('active');
      }});
      wideBtn?.addEventListener('click', () => {{
        document.body.classList.add('wide');
        wideBtn.classList.add('active');
        normalBtn?.classList.remove('active');
      }});
    }})();
  </script>
</body>
</html>
"""

    viewer_file.write_text(viewer_html, encoding="utf-8")
    return f"viewers/{safe_name}"


def build_overview_html(rows: list[dict]) -> str:
    if not rows:
        return "<div class='overview-item'>No configuration records available.</div>"

    group_counter: Counter[str] = Counter()
    for row in rows:
        config = str(row.get("config", ""))
        parent = Path(config).parent.name if config else "unknown"
        group_counter[parent] += 1

    items = []
    for group_name, count in group_counter.most_common(8):
        items.append(
            f"<div class='overview-item'><strong>{escape(group_name)}</strong> · {count} config(s)</div>"
        )

    return "".join(items)


def card_html(row: dict, output_dir: Path) -> str:
    config = str(row.get("config", ""))
    notebook = str(row.get("notebook", ""))
    setup_yaml = str(row.get("setup_yaml", ""))
    env_name = str(row.get("env_name", ""))
    status = str(row.get("status", "unknown")).lower()
    reason = str(row.get("reason", ""))
    returncode = str(row.get("returncode", ""))
    notebook_exists = bool(row.get("notebook_exists", False))

    config_path = Path(config) if config else Path(".")
    config_link = f"../{config}" if config else "#"
    notebook_link = f"../{notebook}" if notebook else "#"

    config_title = prettify_config_name(config)
    config_label = config_path.name if config else "Unknown"
    config_group = config_path.parent.name if config else "unknown"

    rendered_html_link = ""
    full_view_link = ""
    if notebook_exists and notebook:
        notebook_path = Path(notebook)
        if notebook_path.exists():
            rendered_html_link = render_notebook_html(notebook_path, output_dir)
        full_view_link = render_full_notebook_view(rendered_html_link, config_label, output_dir)

    status_class = "ok" if status == "ok" else "failed"
    status_badge = "status-ok" if status == "ok" else "status-failed"

    actions_html = (
        (
            f"<div class='actions'>"
            f"<a class='btn primary' href='{escape(full_view_link)}' target='_blank' rel='noopener'>Open Full Notebook View</a>"
            f"<button class='btn' type='button' data-preview-url='{escape(rendered_html_link)}' data-full-url='{escape(full_view_link)}' data-preview-title='{escape(config_label)}'>Quick Preview</button>"
            f"<a class='btn' href='{escape(notebook_link)}'>Download .ipynb</a>"
            f"</div>"
        )
        if rendered_html_link
        else (
            f"<div class='actions'>"
            f"<a class='btn' href='{escape(notebook_link)}'>Download .ipynb</a>"
            f"</div><div class='preview-empty'>Rendered preview is unavailable for this entry.</div>"
            if notebook_exists
            else "<div class='preview-empty'>Notebook was not produced for this run.</div>"
        )
    )

    reason_html = (
        f"<div class='reason'><strong>Failure Reason:</strong> {escape(reason)}"
        + (f" (return code: {escape(returncode)})" if returncode and returncode != "0" else "")
        + "</div>"
        if status_class == "failed" and reason
        else ""
    )

    return (
        f"<article class='card' data-card='1' data-status='{escape(status_class)}' "
        f"data-search='{escape(config + ' ' + config_title + ' ' + config_group)}'>"
        f"<div class='card-top'>"
        f"<h3 class='card-title'>{escape(config_title)}</h3>"
        f"<span class='status-badge {status_badge}'>{escape(status_class)}</span>"
        f"</div>"
        f"<p class='path'>{escape(config)}</p>"
        f"<div class='meta'>"
        f"<span class='label'>Config File</span><span><a href='{escape(config_link)}'>{escape(config_label)}</a></span>"
        f"<span class='label'>Config Group</span><span>{escape(config_group)}</span>"
        f"<span class='label'>Setup YAML</span><span>{escape(Path(setup_yaml).name if setup_yaml else '-')}</span>"
        f"<span class='label'>Environment</span><span>{escape(env_name or '-')}</span>"
        f"</div>"
        f"{actions_html}"
        f"{reason_html}"
        f"</article>"
    )

def infer_config_from_notebook_path(notebook_path: Path) -> str:
    if notebook_path.parts and notebook_path.parts[0] == "out":
        relative = Path(*notebook_path.parts[1:])
    else:
        relative = notebook_path

    base = Path("setups") / relative.parent / f"{relative.stem}.yml"
    for candidate in (base, base.with_suffix(".yaml"), base.with_suffix(".csvy")):
        if candidate.exists():
            return candidate.as_posix()
    return base.as_posix()


def merge_manifest_with_discovered_notebooks(rows: list[dict], out_root: Path) -> list[dict]:
    if not out_root.exists():
        return rows

    normalized_rows = [row for row in rows if isinstance(row, dict)]
    existing_notebooks = {
        str(row.get("notebook", "")).replace("\\", "/")
        for row in normalized_rows
        if isinstance(row.get("notebook"), str)
    }

    discovered_entries: list[dict] = []
    for notebook in sorted(out_root.rglob("*.ipynb")):
        notebook_rel = notebook.as_posix()
        if notebook_rel in existing_notebooks:
            continue

        discovered_entries.append(
            {
                "config": infer_config_from_notebook_path(Path(notebook_rel)),
                "notebook": notebook_rel,
                "notebook_exists": True,
                "setup_yaml": "",
                "env_name": "",
                "status": "ok",
                "reason": "discovered_from_out",
                "returncode": 0,
                "stderr_tail": "",
            }
        )

    return normalized_rows + discovered_entries

def load_manifest_rows(manifest_path: Path) -> list[dict]:
    if not manifest_path.exists():
        return []

    raw = manifest_path.read_text(encoding="utf-8").strip()
    if not raw:
        return []

    try:
        loaded = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"Warning: invalid JSON in manifest {manifest_path}: {exc}")
        return []

    if isinstance(loaded, list):
        return [row for row in loaded if isinstance(row, dict)]

    print(f"Warning: manifest {manifest_path} is not a JSON list; ignoring content.")
    return []


def main() -> None:
    parser = argparse.ArgumentParser(description="Build static notebook gallery page.")
    parser.add_argument("--manifest", default="out/notebook-manifest.json")
    parser.add_argument("--output-dir", default="docs-site")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    rows = load_manifest_rows(manifest_path)
    rows = merge_manifest_with_discovered_notebooks(rows, Path("out"))

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rendered_dir = output_dir / "notebooks"
    viewers_dir = output_dir / "viewers"
    if rendered_dir.exists():
        shutil.rmtree(rendered_dir)
    if viewers_dir.exists():
      shutil.rmtree(viewers_dir)

    total = len(rows)
    ok_count = sum(1 for row in rows if str(row.get("status", "")).lower() == "ok")
    fail_count = total - ok_count
    summary_html = (
        f"<span class='pill'>Total: {total}</span>"
        f"<span class='pill ok'>Successful: {ok_count}</span>"
        f"<span class='pill fail'>Failed: {fail_count}</span>"
    )

    overview_html = build_overview_html(rows)
    cards = "\n".join(card_html(row, output_dir) for row in rows)

    html = HTML_TEMPLATE.format(
        summary=summary_html,
        overview=overview_html,
        cards=cards or "<article class='card'><p class='path'>No notebooks generated yet.</p></article>",
    )

    (output_dir / "index.html").write_text(html, encoding="utf-8")
    print(f"Gallery written to {output_dir / 'index.html'}")


if __name__ == "__main__":
    main()
