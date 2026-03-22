# Approach-4 Quick Start Guide

## Overview

Approach-4 is a GitHub Actions-based CI/CD pipeline for TARDIS configuration processing:

```
Your Config → Commit → GitHub Actions CI  → Sanity Check → Azure Server → Notebook → Gallery
              (detect) (detect changes)     (validate)      (simulate)    (generate) (publish)
```

## Quick Start (5 minutes)

### 1. Add a TARDIS Configuration

Create or modify a TARDIS config in the `setups/` directory:

```bash
# Example
mkdir -p setups/2026/my-new-setup
cat > setups/2026/my-new-setup/tardis_example.yml << 'EOF'
# Your TARDIS config here
photosphere:
  # ... config content
EOF
```

### 2. Commit and Push

```bash
git add setups/2026/my-new-setup/tardis_example.yml
git commit -m "Add new TARDIS configuration for paper"
git push origin main
```

### 3. Watch CI Pipeline

- Visit: **Actions** tab in GitHub
- Workflow: "approach-4-incremental-config-pipeline"
- Stages:
  1. ✅ **Detect changed configs** – finds your new config
  2. ✅ **Generate setup.yaml** – infers TARDIS version
  3. ✅ **Create sanity configs** – lightweight test version
  4. ✅ **Run sanity tests** – validates syntax
  5. ✅ **Create server queue** – queues passed configs
  6. (Optional) Azure server execution – runs full simulation

### 4. View Results

**CI Artifacts**:
- Click workflow run → Artifacts → `approach-4-ci-artifacts`
- Files:
  - `changed-configs.json` – detected configs
  - `setup-generation-manifest.json` – generated setup.yaml paths
  - `sanity-results.json` – ✅ pass / ❌ fail
  - `server-queue.json` – configs queued for Azure

**Generated Gallery** (if Azure is configured):
- Visit: GitHub Pages (Settings → Pages)
- Shows generated notebooks per config

## Project Structure

```
.
├── .github/workflows/
│   └── prototype-approach-4.yml          # Main CI workflow
├── envs/
│   ├── ci-environment.yml                # Install on GitHub Actions
│   └── server-environment.yml            # Install on Azure VM
├── scripts/
│   ├── detect_changed_configs.py         # Find changed YAML files
│   ├── generate_setup_yamls.py           # Create per-config setup.yaml
│   ├── create_sanity_configs.py          # Lightweight test versions
│   ├── run_setup_yaml_sanity.py          # Run sanity checks
│   ├── create_server_queue.py            # Filter passed → server
│   ├── build_gallery.py                  # Generate HTML gallery
│   └── plot_from_config.py               # Generate plots from config
├── server/
│   ├── setup_env_from_setup_yaml.py      # Create conda env from setup.yaml
│   ├── process_server_queue.py           # Execute notebooks on server
│   ├── run_notebook_for_config.py        # Papermill notebook execution
│   └── run_on_azure_example.sh           # Server orchestration script
├── setups/
│   ├── README.md                         # Config structure guide
│   └── 2026/
│       └── GSOC_2026_Paper/
│           ├── setup.yaml                # Environment spec (auto-generated)
│           └── tardis_example.yml        # Your config here
├── templates/
│   └── config_report_template.ipynb      # Parameterized notebook template
├── docs/
│   ├── README.md                         # Project overview
│   ├── ENVIRONMENTS.md                   # Three-tier environment model
│   ├── SERVER_SETUP.md                   # Azure VM setup
│   └── QUICK_START.md                    # This file
└── .gitignore                             # Excludes generated outputs

Generated (not committed):
- generated/                              # CI scratch directory
- out/                                    # Server output notebooks
- docs-site/                              # Gallery HTML
```

## Configuration Format

Each config needs a `setup.yaml` (auto-generated, but you can customize):

```yaml
setup_format_version: approach-4-v1
environment:
  lockfile_url: https://raw.githubusercontent.com/tardis-sn/tardisbase/refs/heads/master/conda-linux-64.lock
  channels:
    - conda-forge
  extra_packages:
    - pyyaml
    - matplotlib
tardis:
  requested_ref: release-latest      # or specific tag like "2024.06.09"
  conda_spec: tardis-sn              # or "tardis-sn=2024.06.09"
config:
  path: setups/2026/GSOC_2026_Paper/tardis_example.yml
  atom_data: kurucz_cd23_chianti_H_He_latest
```

## Version Control

To specify a TARDIS version for your config, add to your `tardis_example.yml`:

```yaml
# Top-level key
tardis_version: "2024.06.09"

# OR in metadata
metadata:
  tardis_version: "2024.06.09"
```

If omitted, defaults to `release-latest`.

## Enable Azure Server Integration (Optional)

To run full simulations on Azure:

1. **Set up Azure VM** (see [SERVER_SETUP.md](SERVER_SETUP.md))
2. **Configure GitHub secrets**:
   - `AZURE_SERVER_HOST` – e.g., `57.158.25.120`
   - `AZURE_SERVER_USER` – e.g., `azureuser`
   - `AZURE_SSH_PRIVATE_KEY` – private key (as secret text)
   - `AZURE_SERVER_REPO_PATH` – e.g., `/home/azureuser/tardis-approach-4`
3. Commit → CI will auto-dispatch to Azure after sanity checks pass

## CI Pipeline Stages (in detail)

### Stage 1: Detect Changed Configs
```bash
git diff <base> <head> --name-only | grep -E '\.(yml|yaml|csvy)$'
```
- Finds config files changed in commit
- Output: `generated/changed-configs.json`

### Stage 2: Generate setup.yaml
- For each changed config, infers TARDIS version
- Creates `setup.yaml` next to config
- Includes lockfile URL, channels, TARDIS spec
- Output: `generated/setup-generation-manifest.json`

### Stage 3: Create Sanity Configs
- Copies each config with reduced parameters:
  - `no_of_packets: min(original, 10)`
  - `iterations: min(original, 5)`
- Fast test versions for CI (< 1 min)
- Output: `generated/sanity-configs/`

### Stage 4: Run Sanity Tests
- Creates conda env from setup.yaml
- Runs `plot_from_config.py` with sanity config
- Validates syntax and basic functionality
- Output: `generated/sanity-results.json` with ✅/❌ status

### Stage 5: Create Server Queue (if sanity pass)
- Filters results to only `sanity_passed: true`
- Creates `generated/server-queue.json`
- Payload ready for Azure dispatch

### Stage 6: Dispatch to Azure (if secrets configured)
- SSH upload `server-queue.json`
- Remote: `bash server/run_on_azure_example.sh`
- Server runs per-config notebooks
- Results in `out/` → gallery in `docs-site/`

## Troubleshooting

### Config not detected
- Ensure filename ends in `.yml`, `.yaml`, or `.csvy`
- Ensure committed to `main` branch
- Check "Detect changed configs" step in CI logs

### Sanity check fails
- Check error in "Run setup.yaml sanity tests" step
- Look for TARDIS config syntax errors
- Verify `atom_data` is valid identifier (e.g., `kurucz_cd23_chianti_H_He_latest`)

### Setup generation fails
- Check YAML syntax: `yamllint setups/2026/myconfig/tardis_example.yml`
- Verify no invalid YAML syntax

### Server dispatch fails
- Check GitHub secrets are set (see [SERVER_SETUP.md](SERVER_SETUP.md))
- Check Azure VM is up and running
- Check logs in "Dispatch queue to Azure server" step

### Gallery not updating
- Ensure `GitHub Pages` is enabled (Settings → Pages)
- Deploy from `main` branch, folder `/docs-site`
- Gallery builds only if configs pass sanity

## Links

- 📖 [ENVIRONMENTS.md](ENVIRONMENTS.md) – Three-tier conda model & lockfile flow
- 🖥️ [SERVER_SETUP.md](SERVER_SETUP.md) – Azure VM setup & deployment  
- ⚙️ [setups/README.md](setups/README.md) – Config format & structure
- 🚀 [.github/workflows/prototype-approach-4.yml](.github/workflows/prototype-approach-4.yml) – CI workflow

## Next Steps

1. ✅ Add a test config to `setups/2026/`
2. ✅ Commit and check CI pipeline passes
3. ✅ (Optional) Configure Azure for full simulations
4. ✅ Create variants of your config (fast, downbranch, etc.)

Happy TARDIS simulating! 🚀
