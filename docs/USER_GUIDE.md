# 👩‍💻 User Guide (How to Use)

## 1) Trigger a run

Choose one:
- Push config changes under `setups/` to `main`
- Run `approach-4-incremental-config-pipeline` manually from Actions

## 2) What happens automatically

- Changed configs are detected
- `setup.yaml` is generated per config
- CI sanity runs execute reduced validation
- Valid configs are queued for server execution
- Server runs full notebook generation
- CI pulls generated notebooks/gallery and commits them

## 3) Where to check results

- Execution status: GitHub Actions run logs
- Notebook status details: `out/notebook-manifest.json`
- Generated notebook files: `out/.../*.ipynb`
- Rendered gallery: `docs-site/index.html`

## 4) Interpreting failures

Read each manifest row:
- `status`: `ok` or `failed`
- `reason`: setup or notebook execution failure type
- `stderr_tail`: last traceback chunk for debugging

## 5) Local gallery build

From repo root:

```bash
python scripts/build_gallery.py --manifest out/notebook-manifest.json --output-dir docs-site
```

## 6) Local preview

Open `docs-site/index.html` in browser (or use a local static server).

## 7) Common pitfalls

- Running scripts from the wrong directory (use repo root)
- Missing secrets blocks dispatch
- Stale server checkout (handled by startup restore+pull)
