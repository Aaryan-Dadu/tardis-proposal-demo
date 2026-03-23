# 🚀 TARDIS Approach-4: Notebook Automation Pipeline

This repository automates end-to-end TARDIS notebook generation from committed setup configs.

## 🎯 Purpose

Build a reliable pipeline that:
- detects changed configs in CI
- sanity-validates changes quickly
- runs full notebook execution on a dedicated server
- syncs generated notebooks back into the repo
- publishes a browsable gallery with rendered previews

## 🧩 What this project includes

- CI orchestration workflow (`.github/workflows/prototype-approach-4.yml`)
- Server execution layer (`server/`)
- Setup/config tooling (`scripts/`)
- Generated output areas (`generated/`, `out/`, `docs-site/`)
- Static preview gallery for notebook browsing

## 📚 Documentation

All active docs are in `docs/`:

- 🧭 Main design doc: [docs/DESIGN.md](docs/DESIGN.md)
- 🏗️ Architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- 👩‍💻 User guide: [docs/USER_GUIDE.md](docs/USER_GUIDE.md)
- 🗂️ File purposes: [docs/FILE_PURPOSES.md](docs/FILE_PURPOSES.md)
- 🖥️ Server setup: [docs/SERVER_SETUP.md](docs/SERVER_SETUP.md)
- 🧪 Environment details: [docs/ENVIRONMENTS.md](docs/ENVIRONMENTS.md)
- 🔐 Secrets/security: [docs/SECRETS.md](docs/SECRETS.md)

## 📦 Outputs

- `out/` → notebooks + `notebook-manifest.json`
- `docs-site/` → rendered notebook gallery
- `generated/` → CI intermediate artifacts