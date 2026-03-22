# Approach-4 Server Setup & Complete Flow

**Status**: `main` branch only (PRs skip server dispatch - good!)  
**Architecture**: Lockfile-first (per TARDIS installation.rst)  
**Platform**: Azure VM or any Linux/macOS with conda installed

---

## Table of Contents

1. [What's Expected on Server](#whats-expected-on-server) – minimal requirements
2. [What's Available (CI Provides)](#whats-available-ci-provides) – what CI sends
3. [Server Components](#server-components) – what code runs where
4. [Setup Instructions](#setup-instructions) – step-by-step
5. [Complete End-to-End Flow](#complete-end-to-end-flow) – validation walkthrough
6. [Troubleshooting](#troubleshooting) – debugging guide

---

## What's Expected on Server

### Minimal Server Requirements

The server must have **ONE thing**:

✅ **Conda (Miniconda or Anaconda)**
- Expected path: `$HOME/miniconda3/bin/conda` (or Anaconda/mambaforge)
- Must be executable
- Must have internet access (to download lockfiles and packages)
- Recent version (supports `conda tos accept` command)

That's it. No pre-installed TARDIS, no pre-built environments.

### Optional but Recommended

💡 **Git repo cloned** at a consistent path  
- Makes `AZURE_SERVER_REPO_PATH` simpler  
- Path can be anything, e.g., `/home/azureuser/tardis-approach-4`

💡 **Sufficient disk space**
- Each config environment: ~500MB–2GB
- Typical simulation run: output files ~100MB–500MB
- Rule of thumb: 10GB minimum for testing, 50GB+ for production

### NOT Required
- ❌ TARDIS pre-installed
- ❌ Pre-built conda environments
- ❌ Atom data downloaded in advance
- ❌ Any development tools or compilers (conda provides them)

---

## What's Available (CI Provides)

When CI dispatches to your server, it **sends exactly**:

### 1. Queue File (`generated/server-queue.json`)

**What it is**: JSON payload with configs that passed sanity checks

**What it contains**:
```json
[
  {
    "config": "setups/2026/GSOC_2026_Paper/tardis_example.yml",
    "setup_yaml": "setups/2026/GSOC_2026_Paper/setup.yaml",
    "atom_data": "kurucz_cd23_chianti_H_He_latest",
    "tardis_conda_spec": "tardis-sn",
    "sanity_passed": true
  }
]
```

**Why it matters**: 
- Only configs that passed lightweight CI sanity checks
- Ready to run full simulations
- Includes everything needed for environment setup

### 2. Server Control Script (`server/run_on_azure_example.sh`)

**What it does** (in order):
1. ✅ Validates conda binary exists
2. ✅ Creates control environment (a4-control) from hardcoded spec
3. ✅ Runs orchestration script inside control env
4. ✅ Manages all per-config environment creation
5. ✅ Executes notebooks for each config
6. ✅ Builds gallery page

**Control Environment Spec** (hardcoded in script):
```bash
"$CONDA_BIN" create -y -n "$CONTROL_ENV_NAME" python=3.13 pyyaml
```

Why minimal? Because only this script needs to run orchestration code—the actual TARDIS simulations run in separate per-config environments created from lockfiles.

### 3. Orchestration Scripts (`server/*.py`)

All Python scripts are provided by CI via repo sync. No pre-installation needed.

---

## Server Components

### Architecture Diagram

```
GitHub Actions CI (ubuntu-latest)
        ↓ [sanity checks]
        ↓ [creates queue]
        ↓ [SSH dispatch]
        ↓
    Azure Server
        ↓
 [control env] ← a4-control (python + pyyaml)
        ├→ process_server_queue.py
        │       ↓
        │   [for each config]
        │       ├→ setup_env_from_setup_yaml.py
        │       │    ├→ Download lockfile from URL
        │       │    ├→ `conda create --file lockfile`
        │       │    ├→ `conda install tardis-sn=<version>`
        │       │    ├→ `conda install extra_packages`  ← a4-config-env
        │       │    └→ Verify TARDIS imports
        │       │
        │       └→ run_notebook_for_config.py
        │            └→ Papermill execute notebook
        │                └→ Output: out/<config-folder>/<name>.ipynb
        │
        └→ build_gallery.py
             └→ docs-site/index.html
```

### Scripts Deep-Dive

#### `server/setup_env_from_setup_yaml.py`

**Purpose**: Create conda environment from `setup.yaml` (one per config)

**Flow**:
```
Input: setup.yaml file
  ↓
1. Validate setup.yaml format
   └─ Check: environment.lockfile_url exists
   └─ Check: tardis.conda_spec exists
  ↓
2. Resolve conda binary (check standard paths)
  ↓
3. Accept Anaconda TOS non-interactively
   └─ Essential for unattended VMs
  ↓
4. Download lockfile from URL
   └─ Example: https://raw.githubusercontent.com/tardis-sn/tardisbase/.../conda-linux-64.lock
   └─ Save to temp file
  ↓
5. Create environment from lockfile
   └─ `conda create -y -n a4-GSOC-2026-Paper --file /tmp/lockfile`
  ↓
6. Install TARDIS from setup.yaml spec
   └─ `conda install -n a4-GSOC-2026-Paper tardis-sn=<version>`
   └─ Fallback to `tardis-sn` (latest) if specific version fails
  ↓
7. Install extra packages (matplotlib, papermill, etc.)
   └─ `conda install -n a4-GSOC-2026-Paper pyyaml matplotlib jupyterlab nbconvert papermill`
  ↓
8. Verify installation
   └─ `conda run -n a4-<name> python -c "import tardis; print(tardis.__version__)"`
  ↓
Output: Fully configured environment ready for simulations
        Outputs JSON with env name, conda binary, TARDIS version
```

**Key Features**:
- ✅ **Lockfile-first** (reproducible base)
- ✅ **TARDIS version flexible** (can install any version on top of lockfile)
- ✅ **Per-config isolation** (separate env for each config)
- ✅ **Non-interactive TOS** (works on headless VMs)
- ✅ **Fallback support** (if exact version not in conda-forge, use latest)

#### `server/process_server_queue.py`

**Purpose**: Main orchestration—iterate through queue and execute notebooks

**Flow**:
```
Input: generated/server-queue.json
  ↓
For each config in queue:
  1. Setup environment
     └─ Call setup_env_from_setup_yaml.py
  2. Generate notebook
     └─ Call run_notebook_for_config.py with config params
  3. Record result
     └─ Append to notebook-manifest.json
  ↓
Output: out/notebook-manifest.json
        out/<config-folder>/<config-name>.ipynb (for each config)
        Manifest format:
        [
          {
            "config": "path/to/config.yml",
            "notebook": "out/path/to/config.ipynb",
            "setup_yaml": "path/to/setup.yaml",
            "env_name": "a4-config-name",
            "status": "ok" | "failed"
          }
        ]
```

#### `server/run_notebook_for_config.py`

**Purpose**: Execute Papermill template with config-specific parameters

**Flow**:
```
Input: --config <path>, --atom-data <id>, --output-notebook <path>
  ↓
1. Load template notebook
   └─ templates/config_report_template.ipynb
   └─ Contains Parameter cell with config_path=None, atom_data="default"
  ↓
2. Inject parameters via Papermill
   └─ config_path: <the config file path>
   └─ atom_data: <kurucz_cd23_chianti_H_He_latest>
  ↓
3. Execute notebook in conda environment
   └─ All cells run in order
   └─ TARDIS simulation runs here
   └─ Plots generated here
  ↓
Output: Completed notebook written to out/<config-folder>/<name>.ipynb
```

**Template Design** (config_report_template.ipynb):
```python
# Cell 1 (Parameters - injected by Papermill)
config_path = None  # Will be set to actual path
atom_data = "kurucz_cd23_chianti_H_He_latest"  # Can override

# Cell 2+
from tardis import run_tardis
config = Configuration.from_yaml(config_path)  # Uses injected path
sim = run_tardis(config, atom_data=atom_data)
# ... plot generation ...
```

#### `server/run_on_azure_example.sh`

**Purpose**: Entry point script called by CI via SSH

**What it does**:
```bash
1. Validate conda binary exists at $CONDA_BIN
2. Create control environment:
  conda create -y -n a4-control python=3.13 pyyaml
3. Call orchestration:
   conda run -n a4-control python server/process_server_queue.py \
     --queue generated/server-queue.json \
     --output-root out \
     --conda-bin $CONDA_BIN
4. Build gallery:
   conda run -n a4-control python scripts/build_gallery.py \
     --manifest out/notebook-manifest.json \
     --output-dir docs-site
5. Exit with success/failure
```

**Environment Variables** (customizable):
```bash
CONDA_BIN=/home/azureuser/miniconda3/bin/conda    # Path to conda
QUEUE_PATH=generated/server-queue.json             # Where to find queue
OUT_ROOT=out                                       # Where to store outputs
CONTROL_ENV_NAME=a4-control                        # Control env name
```

---

## Setup Instructions

### Step 1: Prepare Azure VM

```bash
# 1a. Create VM (any Linux/macOS with SSH access)
# 1b. SSH in
ssh -i your-key.pem azureuser@<ip-address>

# 1c. Install Miniconda (if not already present)
# Check if conda exists:
which conda
# or
~/miniconda3/bin/conda --version

# If not installed:
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p ~/miniconda3
```

### Step 2: Clone Repository

```bash
# Option A: Use SSH (requires GitHub key setup)
cd /home/azureuser
git clone git@github.com:<you>/<your-repo>.git tardis-approach-4
cd tardis-approach-4

# Option B: Use HTTPS
cd /home/azureuser
git clone https://github.com/<you>/<your-repo>.git tardis-approach-4
cd tardis-approach-4
```

### Step 3: Verify Setup

```bash
# Test conda binary
~/miniconda3/bin/conda --version
# Should output: conda 24.x.x or similar

# Test conda tos accept (needed for automation)
~/miniconda3/bin/conda tos accept

# Test SSH connectivity (from your local machine)
ssh -i /path/to/key.pem azureuser@<ip-address> "echo 'SSH works!'"

# Verify repo is accessible
ssh -i /path/to/key.pem azureuser@<ip-address> "ls -la /home/azureuser/tardis-approach-4"
```

### Step 4: Configure GitHub Secrets

In your GitHub repo, Settings → Secrets and variables → Actions:

```
AZURE_SERVER_HOST=57.158.25.120
AZURE_SERVER_USER=azureuser
AZURE_SSH_PRIVATE_KEY=<paste content of private key file>
AZURE_SERVER_REPO_PATH=/home/azureuser/tardis-approach-4
```

**How to get private key content**:
```bash
# On your local machine
cat ~/.ssh/azure_key  # or wherever your private key is
# Copy the entire output (-----BEGIN RSA PRIVATE KEY----- to -----END)
# Paste into GitHub secret as plain text
```

### Step 5: Test the Connection

Push a commit to main and watch GitHub Actions:
1. Workflow runs on ubuntu-latest (CI)
2. If dispatch secrets are set correctly:
   - Workflow will SSH to Azure
   - Execute server script
   - Results in Actions → "approach-4-ci-artifacts" (always)
   - Results in Azure server `out/` folder (if successful)

---

## Complete End-to-End Flow

### Flow Diagram with Times

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Developer: Commits config to main branch                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ GitHub Actions: "approach-4-incremental-config-pipeline"                    │
│                                                                             │
│ Job: detect-and-sanity (on ubuntu-latest, timeout 60 min)                  │
│ ═══════════════════════════════════════════════════════════════════════════│
│                                                                             │
│ [~1 min] Set up conda environment                                           │
│          └─ conda-incubator/setup-miniconda@v3                              │
│          └─ Activate: tardis-gsoc-approach-4-ci                             │
│          └─ Install: python=3.13, pyyaml, git, requests                     │
│                                                                             │
│ [~1 min] Resolve diff refs                                                 │
│          └─ if push: use before → HEAD                                      │
│          └─ else: use origin/main → HEAD                                    │
│          └─ (PR detection commented out to avoid server spam)               │
│                                                                             │
│ [~2 min] Detect changed configs                                             │
│          └─ Run: scripts/detect_changed_configs.py                          │
│          └─ Git diff base_ref → head_ref                                    │
│          └─ Filter: only *.yml, *.yaml, *.csvy                              │
│          └─ Output: generated/changed-configs.json                          │
│                                                                             │
│ [~1 min] Generate per-config setup.yaml                                     │
│          └─ Run: scripts/generate_setup_yamls.py                            │
│          └─ For each changed config:                                        │
│          │   ├─ Infer TARDIS version from metadata                          │
│          │   ├─ Create setup.yaml with lockfile URL                         │
│          │   └─ Write next to config file                                   │
│          └─ Output: generated/setup-generation-manifest.json                │
│                                                                             │
│ [~2 min] Create lightweight sanity configs                                  │
│          └─ Run: scripts/create_sanity_configs.py                           │
│          └─ For each config (COPY with reduced params):                     │
│          │   ├─ no_of_packets: min(original, 10)                            │
│          │   ├─ iterations: min(original, 5)                                │
│          │   └─ Other params: match original                                │
│          └─ Output: generated/sanity-configs/                               │
│                                                                             │
│ [~5-20 min] Run setup.yaml sanity tests ⏱️                                  │
│          └─ Run: scripts/run_setup_yaml_sanity.py                           │
│          └─ For each config:                                                │
│          │   ├─ Call: setup_env_from_setup_yaml.py                          │
│          │   │   ├─ Download lockfile (.lock file, ~200MB)                  │
│          │   │   ├─ `conda create --file lockfile` (~2 min, cached)         │
│          │   │   ├─ `conda install tardis-sn` (~2 min)                      │
│          │   │   ├─ `conda install extra_packages` (~30s)                   │
│          │   │   └─ Verify `import tardis`                                  │
│          │   │                                                              │
│          │   └─ Call: plot_from_config.py                                   │
│          │       ├─ Load sanity config                                      │
│          │       ├─ `tardis.run_tardis()` on light config (~1-3 min)        │
│          │       ├─ Generate 2 plot types (SDEC, LIV)                       │
│          │       ├─ Each with real & virtual packets (4 total)              │
│          │       └─ Output: generated/sanity-plots/                         │
│          │                                                                  │
│          └─ Output: generated/sanity-results.json                           │
│             Example: {"config": "...", "sanity_passed": true/false}         │
│                                                                             │
│ [~1 min] Create server queue payload                                        │
│          └─ Run: scripts/create_server_queue.py                             │
│          └─ Filter: only configs with sanity_passed=true                    │
│          └─ Output: generated/server-queue.json                             │
│                                                                             │
│ [~1 min] Upload CI artifacts                                                │
│          └─ Upload to Actions:                                              │
│          │  ├─ changed-configs.json                                         │
│          │  ├─ setup-generation-manifest.json                               │
│          │  ├─ sanity-manifest.json                                         │
│          │  ├─ sanity-results.json                                          │
│          │  └─ server-queue.json                                            │
│          └─ Download from Actions tab → "approach-4-ci-artifacts"           │
│                                                                             │
│ [~2 min] Configure SSH & Dispatch to Azure (IF secrets set)                 │
│          └─ IF secrets.AZURE_SERVER_HOST != '':                             │
│          ├─ Setup SSH key                                                  │
│          ├─ ssh-keyscan server host                                         │
│          ├─ scp server-queue.json to server                                 │
│          ├─ ssh: cd repo && bash server/run_on_azure_example.sh             │
│          └─ Wait for completion ⏱️                                           │
│                                                                             │
│ [~1 min] Build gallery preview                                              │
│          └─ Run: scripts/build_gallery.py                                   │
│          └─ Reads: out/notebook-manifest.json (if exists)                   │
│          └─ Output: docs-site/index.html                                    │
│          └─ Upload artifact: approach-4-pages-preview                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
                    [CI completes in 10-45 min total]
                    (depending on config complexity)
                                    ↓
                 ┌──────────────────────────────────────┐
                 │ Main Branch (sanity ✅)              │
                 │ → Server runs full simulations       │
                 │ → Notebooks generated                │
                 │ → Gallery publishable                │
                 │                                      │
                 │ PR Branch                            │
                 │ → Sanity passed ✅                   │
                 │ → Server dispatch SKIPPED            │
                 │ → Can merge with confidence          │
                 └──────────────────────────────────────┘
```

### Timeline Details

```
Total CI time: 10-45 minutes

Breakdown:
├─ Setup: ~1 min (conda env creation)
├─ Detect configs: ~1 min (git diff, filter)
├─ Generate setup.yaml: ~1 min (YAML parsing)
├─ Create sanity configs: ~1 min (copy + modify)
├─ Sanity checks: ~5-20 min ← VARIABLE (# configs × per-config time)
│  └─ Per config: env setup (3-5 min) + simulation (1-3 min) = 4-8 min
├─ Create queue: ~1 min (JSON filtering)
├─ Upload artifacts: ~1 min
├─ SSH dispatch (IF enabled): ~2 min (key setup, scp, trigger)
└─ Gallery build: ~1 min

Azure Server time (IF dispatched): 10-120+ minutes
├─ Per config: env creation (3-5 min) + full simulation (5-60 min)
└─ Gallery build: ~1 min
```

---

##  Validation Checklist: Step-by-Step Verification

### Local Developer Testing

```bash
# 1. Create a test config
mkdir -p setups/2026/test-config
cat > setups/2026/test-config/tardis_example.yml << 'EOF'
# Minimal TARDIS config
photosphere:
  t_inner: 9000 K
# ... add actual config content
EOF

# 2. Add to git
git add setups/2026/test-config/
git commit -m "Test config for approach-4"

# 3. Push to main (or test branch)
git push origin main
```

### GitHub Actions Verification

1. **Watch workflow run**:
   - Go to Actions tab
   - Find "approach-4-incremental-config-pipeline" run
   - Wait for "detect-and-sanity" job to complete

2. **Check each stage**:
   - ✅ "Set up conda environment" → Conda created
   - ✅ "Resolve diff refs" → Diff refs resolved
   - ✅ "Detect changed configs" → Test config detected
   - ✅ "Generate per-config setup.yaml" → setup.yaml created
   - ✅ "Create lightweight sanity configs" → Sanity config created
   - ✅ "Run setup.yaml sanity tests" → Simulations run
   - ✅ "Create server queue payload" → Queue created
   - ✅ "Upload CI artifacts" → Artifacts available
   - ⚠️ "Configure SSH" → SKIPPED if no secrets
   - ⚠️ "Dispatch queue" → SKIPPED if no secrets
   - ℹ️ "Server dispatch skipped notice" → If secrets missing

3. **Download artifacts**:
   - Click workflow run
   - Artifacts → "approach-4-ci-artifacts"
   - Download ZIP
   - Check `server-queue.json` contains your test config

### Server Verification (IF secrets configured)

```bash
# 1. SSH to server
ssh -i /path/to/key.pem azureuser@<ip>

# 2. Check if server script ran
cd /home/azureuser/tardis-approach-4
ls -la out/
# Should contain: notebook-manifest.json, <config-folder>/, ...

# 3. Check notebooks generated
find out -name "*.ipynb"
# Example: out/test-config/test-config.ipynb

# 4. Check gallery
ls -la docs-site/
cat docs-site/index.html | grep -c "config"  # Should see your config

# 5. Check environments created
~/miniconda3/bin/conda env list | grep a4-
# Example:
# a4-control              /path/to/miniconda3/envs/a4-control
# a4-test-config          /path/to/miniconda3/envs/a4-test-config
```

---

## Troubleshooting

### Problem: "Conda binary not found"

**Error in server logs**:
```
Conda binary not found at /home/azureuser/miniconda3/bin/conda
```

**Solution**:
1. SSH to server, check where conda is:
   ```bash
   which conda
   find ~ -name conda -type f 2>/dev/null
   ```
2. Either:
   - Install Miniconda at standard location, OR
   - Set `CONDA_BIN` env var in dispatch SSH command

### Problem: "conda Create failed"

**Error in server logs**:
```
RuntimeError: Lockfile download failed
```

**Causes & Solutions**:
- ✅ Check lockfile URL in setup.yaml is valid
- ✅ Check server has internet access (can you curl the URL?)
- ✅ Check TARDIS conda channel reachable
- ✅ Re-download lockfile, push new config

### Problem: "TARDIS import fails"

**Error in server logs**:
```
ImportError: No module named tardis
```

**Causes**:
- ✅ TARDIS install didn't complete (check conda.log)
- ✅ Wrong conda spec in setup.yaml (typo in version?)
- ✅ conda-forge doesn't have that version

**Solution**:
- Check what was installed: `conda run -n a4-<config> conda list tardis`
- Update setup.yaml to simpler spec: `tardis: {conda_spec: "tardis-sn"}` (latest)

### Problem: "SSH dispatch fails"

**Error in GitHub Actions**:
```
ssh_exchange_identification: read: Connection reset by peer
```

**Causes**:
- ✅ IP address wrong in AZURE_SERVER_HOST
- ✅ SSH key wrong (doesn't match server's authorized_keys)
- ✅ SSH port not open (usually 22, check firewall)
- ✅ Server down or unreachable

**Solution**:
```bash
# Test SSH locally
ssh -i /path/to/key.pem azureuser@<ip-address> "echo 'Test'"
# Should output: Test

# If fails:
# 1. Check IP (ping <ip>)
# 2. Check key matches server (~/.ssh/authorized_keys)
# 3. Check firewall allows port 22
# 4. Check server is running (aws/azure console)
```

### Problem: "Gallery not updating"

**Issue**: Generated HTML not showing newest notebooks

**Causes**:
- ✅ Notebook-manifest.json out of sync
- ✅ Notebooks in `out/` not found
- ✅ Gallery script wasn't called

**Solution**:
```bash
# Check manifest exists and is recent
ls -la out/notebook-manifest.json
cat out/notebook-manifest.json | jq .

# Check notebooks exist
find out -name "*.ipynb" | head -5

# Re-run locally
python scripts/build_gallery.py --manifest out/notebook-manifest.json --output-dir docs-site
```

### Problem: "Sanity tests pass, but server simulation fails"

This is normal! Sanity runs on reduced packets/iterations.  
Full simulation may hit memory limits, invalid physics, etc.

**Debugging**:
1. Check server logs for specific error
2. Look at notebooks in `out/<config>/` for error traceback
3. Adjust setup.yaml: maybe config needs different TARDIS version
4. Or reduce initial conditions (fewer packets, shorter time domain)

---

## Reference: Environment Resolution Flow

```
setup.yaml provided by CI
        ↓
setup_env_from_setup_yaml.py
        ├─ Parse: environment.lockfile_url
        ├─ Parse: tardis.conda_spec
        ├─ Parse: environment.extra_packages
        ├─ Parse: config.path
        └─ Parse: config.atom_data
        ↓
Create conda environment:
        ├─ Download: lockfile from URL
        ├─ Create: `conda create -n a4-<name> --file <lockfile>`
        ├─ Install: `conda install -n a4-<name> <tardis_spec>`
        ├─ Install: `conda install -n a4-<name> <extra_packages>`
        └─ Verify: python -c "import tardis; print(__version__)"
        ↓
Environment ready for Papermill
        ├─ Contains: base packages (lockfile)
        ├─ Contains: TARDIS (specified version)
        ├─ Contains: Jupyter infrastructure
        └─ Contains: plotting libraries
        ↓
Execute notebook in environment
        ├─ Papermill injects: config_path, atom_data
        ├─ Notebook imports: tardis, Configuration, SDECPlotter, etc.
        ├─ Notebook runs: run_tardis(config, atom_data=...)
        └─ Notebook outputs: plots, figures, results
        ↓
Output: Completed notebook
```

---

## Summary

| Aspect | Details |
|--------|---------|
| **Server Requirement** | Just conda + internet + repo |
| **CI Provides** | setup.yaml, queue.json, Python scripts |
| **Flow** | CI detects → sanity checks → queues → server setup env → runs notebook → gallery |
| **Per Config** | Separate conda env from lockfile for each config |
| **Safety** | PR dispatch disabled—only main branch to server |
| **Time** | CI: 10-45 min, Server: 10-120+ min (depends on simulation complexity) |
| **Scale** | Can handle multiple configs in queue (sequential or future: parallel) |

**Everything is designed to be minimal, reproducible, and safe.** ✅
