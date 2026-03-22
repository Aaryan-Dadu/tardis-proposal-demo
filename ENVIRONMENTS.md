# Approach-4 Environment Architecture

This document explains how conda environments are used in approach-4, aligned with [TARDIS installation.rst](https://tardis-sn.readthedocs.io/en/latest/installation.html).

## Three-Tier Environment Model

Approach-4 uses three distinct types of conda environments, each with a specific purpose:

### Tier 1: CI Orchestration Environment (`ci-environment.yml`)

**Location**: GitHub Actions runners  
**Created in workflow step**: "Set up conda environment"  
**Used for**: Config detection, setup.yaml generation, sanity check validation

**Installed packages**:
- `python=3.13` – Match TARDIS requires-python baseline
- `git` – Version control
- `gitpython` – Programmatic git operations (detect changed configs)
- `pyyaml` – Parse YAML config files and setup.yaml
- `requests` – Download lockfiles

**Key property**: Lightweight, no TARDIS installation, no simulation dependencies.

### Tier 2: Server Control Environment (`server-environment.yml`)

**Location**: Azure VM or local test server  
**Created in script**: `server/run_on_azure_example.sh`  
**Used for**: Orchestrate per-config environment creation and notebook execution pipeline

**Installed packages**:
- `python=3.13` – Match TARDIS requires-python baseline
- `gitpython` – Clone/pull repos on server
- `papermill>=2.3.0` – Execute parameterized notebooks
- `nbconvert>=6.0` – Convert notebooks to HTML
- `jupyterlab>=3.0` – Jupyter infrastructure
- `matplotlib>=3.3` – Plotting utilities
- `numpy` – Numerical operations
- `pyyaml` – Parse setup.yaml configuration
- `requests` – Resource downloads

**Key property**: Manages the orchestration pipeline, not used for TARDIS simulations directly.

### Tier 3: Per-Config Simulation Environment (created from `setup.yaml` + lockfile)

**Location**: Azure VM (one per config variant)  
**Created in script**: `server/setup_env_from_setup_yaml.py`  
**Used for**: Run TARDIS simulations and generate plots

**Installation flow** (follows [TARDIS installation.rst](https://tardis-sn.readthedocs.io/en/latest/installation.html#install-with-lockfiles)):

1. **Download lockfile**:
   ```bash
   wget https://raw.githubusercontent.com/tardis-sn/tardisbase/refs/heads/master/conda-{platform}.lock
   ```

2. **Create base environment from lockfile** (reproducible):
   ```bash
   conda create --name tardis-config-variant --file conda-{platform}.lock
   ```

3. **Install extra packages**:
   ```bash
   conda install -n tardis-config-variant pyyaml matplotlib jupyterlab nbconvert papermill
   ```

4. **Install TARDIS from specified version**:
   ```bash
   conda install -n tardis-config-variant tardis-sn={version}
   # or fallback to latest if version unavailable
   conda install -n tardis-config-variant tardis-sn
   ```

**Why this design**:
- ✅ **Reproducibility**: Lockfile pins all transitive dependencies
- ✅ **TARDIS version flexibility**: Can install any TARDIS version on top of lockfile base
- ✅ **Isolation**: Each config gets its own environment, no cross-contamination
- ✅ **Alignment with official docs**: Follows [TARDIS installation best practices](https://tardis-sn.readthedocs.io/en/latest/installation.html#install-with-lockfiles)

## Configuration Format: `setup.yaml`

Each configuration directory contains `setup.yaml` specifying the environment requirements:

```yaml
setup_format_version: approach-4-v1
environment:
  name: tardis-config-env
  lockfile_url: https://raw.githubusercontent.com/tardis-sn/tardisbase/refs/heads/master/conda-linux-64.lock
  override_channels: true
  channels:
    - conda-forge
  extra_packages:
    - pyyaml
    - matplotlib
    - jupyterlab
    - nbconvert
    - papermill
tardis:
  requested_ref: release-latest  # or specific version tag
  conda_spec: tardis-sn          # conda install spec
config:
  path: path/to/config.yml
  atom_data: kurucz_cd23_chianti_H_He_latest.h5
```

## Environment Resolution Logic

**CI workflow detects changes** → **Generates setup.yaml** → **Server creates per-config environment** → **Runs simulation** → **Generates notebook**

### Conda Version Inference

`generate_setup_yamls.py` infers TARDIS version from config metadata:

```python
# Check for version in config (in this order):
# 1. Top-level key: tardis_version
# 2. Metadata key: tardis_version
# 3. Git tag of config file
# If no version found: use release-latest
```

### Lockfile Handling

`setup_env_from_setup_yaml.py` implements:
- ✅ Conda TOS auto-acceptance (non-interactive for cloud VMs)
- ✅ Explicit channel configuration (conda-forge-first)
- ✅ Lockfile download with retry logic
- ✅ Version spec fallback (if exact spec fails, use generic `tardis-sn`)

## Benefits of This Architecture

1. **Separation of concerns**: CI scripts, server orchestration, and TARDIS simulation are isolated
2. **No cross-contamination**: Each config variant has independent environment
3. **Reproducibility**: Lockfile + version spec ensures identical setups
4. **Scalability**: Server can handle multiple simultaneous per-config environments
5. **Official alignment**: Follows TARDIS-recommended installation flow
6. **Non-interactive automation**: Works on cloud VMs without user input (Anaconda TOS auto-acceptance)

## Troubleshooting

### "conda: command not found" on server
- Ensure Miniconda/Anaconda is installed at standard location (e.g., `~/miniconda3`)
- Or set `CONDA_BIN=/path/to/conda` in `run_on_azure_example.sh`

### "Python version mismatch" in per-config environments
- Update lockfile URL in `setup.yaml` to latest tardisbase
- TARDIS typically supports Python 3.8+; lockfile should have compatible version

### "Anaconda TOS error"
- Script auto-accepts via `conda tos accept --override-channels`
- If it fails, manually run once on server: `conda tos accept`

### Per-config environment creation hangs
- Check internet connectivity (lockfile download)
- Verify conda channels are accessible from server
- Try running with `set -x` to see verbose output

## Next Steps

1. ✅ Environments are now fully specified per TARDIS installation.rst
2. ⏳ Configure GitHub secrets for Azure deployment (see [SERVER_SETUP.md](SERVER_SETUP.md))
3. ⏳ Test with real config variant to validate end-to-end pipeline
