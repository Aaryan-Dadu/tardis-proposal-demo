# Approach-4 Complete Flow Validation

This guide walks through the **entire approach-4 pipeline** step-by-step with validation checkpoints.

**Goal**: Verify every stage works correctly before relying on the system  
**Time**: ~30-40 minutes for full flow (excluding Azure if not configured)  
**Prerequisites**: 
- Git repository set up locally
- GitHub Actions enabled
- (Optional) Azure VM with conda for server testing

---

## Phase 1: Local Setup (5 minutes)

### 1.1 Verify Project Structure

```bash
cd /path/to/tardis-proposal-demo

# Check all required directories exist
ls -d .github scripts server setups templates envs

# Verify key files
ls -la .github/workflows/prototype-approach-4.yml
ls -la server/run_on_azure_example.sh
ls -la scripts/{detect_changed,generate_setup,create_sanity,run_setup_yaml_sanity,create_server_queue,build_gallery}.py
```

**Expected output**:
```
.github/
scripts/
server/
setups/
templates/
envs/
(all present)
```

### 1.2 Verify Python Syntax

```bash
# Test all Python scripts compile
python -m py_compile scripts/*.py server/*.py

# Should complete with no output (= success)
```

### 1.3 Verify YAML Validity

```bash
# Check workflow YAML
python -c "import yaml; yaml.safe_load(open('.github/workflows/prototype-approach-4.yml'))"
echo "✓ Workflow YAML valid"

# Check environment files
for f in envs/*.yml; do
  python -c "import yaml; yaml.safe_load(open('$f'))" && echo "✓ $f valid"
done

# Check example setup.yaml
python -c "import yaml; yaml.safe_load(open('setups/2026/GSOC_2026_Paper/setup.yaml'))"
echo "✓ setup.yaml valid"
```

---

## Phase 2: Push Test Config (5 minutes)

### 2.1 Create Test Config

```bash
# Create test directory
mkdir -p setups/2026/test-flow

# Create minimal TARDIS config for testing
cat > setups/2026/test-flow/test_config.yml << 'EOF'
# Minimal test TARDIS config
# Based on tardis-proposal-demo example

simulation:
  seed: 23                             # For reproducibility
  iterations: 3                        # Light for testing
  
photosphere:
  t_inner: 8000 K
  velocity: 10000 km/s

abundances_section:
  label: photosphere
  filetype: txt
  filename: kurucz_1000_layers.txt

abundances:
  Ni: 0.5
  Fe: 0.3
  Co: 0.2

structure:
  filetype: Artis
  filename: artis_structures.txt

montecarlo:
  seed: 23
  no_of_packets: 10
  iterations: 3
  no_of_virtual_packets: 1
  last_no_of_packets: 10

plasma:
  ionization: dilute_lte
  excitation: dilute_lte
  radiative_rates_type: dilute

supernova:
  luminosity_wavelength_start: 3480 Angstrom
  luminosity_wavelength_end: 9215 Angstrom
  time_of_explosion: 55283 d

spectrum:
  start: 3480 Angstrom
  end: 9215 Angstrom
  num: 2000
EOF
```

**Alternative**: Use existing example config
```bash
cp setups/2026/GSOC_2026_Paper/tardis_example.yml setups/2026/test-flow/test_config.yml
```

### 2.2 Stage and Commit

```bash
# Add to git
git add setups/2026/test-flow/test_config.yml

# Verify git sees the change
git status
# Should show: "new file: setups/2026/test-flow/test_config.yml"

# Commit
git commit -m "Test: Add config for approach-4 flow validation"

# Verify commit
git log -1 --oneline
# Should show: "Test: Add config for approach-4 flow validation"
```

### 2.3 Push to Main

```bash
# Push to GitHub
git push origin main

# Verify push succeeded
git log -1 --oneline origin/main
# Should show your commit
```

---

## Phase 3: Monitor CI Execution (15-30 minutes)

### 3.1 View Workflow Run

```bash
# Option 1: GitHub Web UI
# Go to: https://github.com/<you>/<repo>/actions
# Find: "approach-4-incremental-config-pipeline"
# Click latest run

# Option 2: From terminal (with gh CLI)
gh run list --workflow=prototype-approach-4.yml --limit=1
```

### 3.2 Monitor Each Stage

**Expected stages in order** (check each completes ✅):

1. **Checkout repository** (~10s)
   - Clone repo at head commit

2. **Set up conda environment** (~30s)
   - conda-incubator/setup-miniconda@v3
   - Activate: tardis-gsoc-approach-4-ci
   - Log in CI artifacts should show python + pyyaml + git installed

3. **Resolve diff refs** (~5s)
   - Determines what changed
   - For `push:main` (your scenario):
     - base_ref = previous commit
     - head_ref = current commit
   - Output: resolved refs to next step

4. **Detect changed configs** (~10s)
   - ✅ Should find: `setups/2026/test-flow/test_config.yml`
   - Output: `generated/changed-configs.json`
   - Content: should list your new config file

5. **Generate per-config setup.yaml** (~5s)
   - ✅ Should create: `setups/2026/test-flow/setup.yaml`
   - Content: lockfile URL, TARDIS spec, config path, atom data
   - Check: path matches actual config location

6. **Create lightweight sanity configs** (~5s)
   - ✅ Should create: `generated/sanity-configs/setups/2026/test-flow/test_config.yml`
   - Content: same as original but with reduced iterations
   - Check: `no_of_packets ≤ 10`, `iterations ≤ 5`

7. **Run setup.yaml sanity tests** (~5-20 minutes) ⏱️ **LONGEST STAGE**
   - ✅ Creates conda environment from lockfile
   - ✅ Downloads lockfile (200MB)
   - ✅ Installs TARDIS
   - ✅ Runs simulation on sanity config
   - ✅ Generates plots
   - Output: `generated/sanity-results.json`
   - **Check**: Look for `"sanity_passed": true`

8. **Create server queue payload** (~5s)
   - Filters to only `sanity_passed: true` configs
   - Output: `generated/server-queue.json`
   - If sanity failed → queue will be empty

9. **Upload CI artifacts** (~10s)
   - Uploads to Actions artifacts
   - Files: changed-configs.json, setup-generation-manifest.json, 
     sanity-manifest.json, sanity-results.json, server-queue.json
   - Download: Click workflow → Artifacts tab

10. **Configure SSH & Dispatch** (⏸️ SKIPPED if no Azure secrets)
    - Would setup SSH key
    - Would upload queue to Azure
    - Would trigger server script
    - **Status**: "Server dispatch skipped: set AZURE_SERVER_HOST..." → Normal if secrets not set

11. **Build gallery preview** (~5s)
    - Creates `docs-site/index.html`
    - Won't have notebooks yet (Azure creates those)
    - Upload artifact: approach-4-pages-preview

### 3.3 Download and Inspect Artifacts

```bash
# From Actions tab (GitHub Web):
# 1. Click workflow run
# 2. Artifacts section
# 3. Download "approach-4-ci-artifacts" ZIP

# Extract and inspect
unzip approach-4-ci-artifacts.zip
cd generated

# Verify each file
ls -lah *.json

# Check changed configs
jq . changed-configs.json
# Should contain: "setups/2026/test-flow/test_config.yml"

# Check setup generation
jq . setup-generation-manifest.json
# Should show: config path, setup_yaml path, atom_data

# Check sanity results
jq . sanity-results.json
# Should show: "sanity_passed": true (or false if simulation failed)

# Check server queue (if sanity passed)
jq . server-queue.json
# Should contain your config if sanity_passed
# Empty if sanity failed
```

### 3.4 Validate Sanity Results

```bash
# In sanity-results.json, check your config:
jq '.[] | select(.config | contains("test-flow"))' sanity-results.json

# Expected output:
{
  "config": "setups/2026/test-flow/test_config.yml",
  "setup_yaml": "setups/2026/test-flow/setup.yaml",
  "sanity_config": "generated/sanity-configs/setups/2026/test-flow/test_config.yml",
  "tardis_conda_spec": "tardis-sn",
  "atom_data": "kurucz_cd23_chianti_H_He_latest",
  "sanity_passed": true  # ← The critical check
}

# If sanity_passed: false, view workflow logs for error
```

---

## Phase 4: Optional Azure Server Execution (depends on setup)

### 4.1 Check Pre-requisites

```bash
# Do you have these GitHub secrets configured?
# Settings → Secrets and variables → Actions

# Required:
# ✅ AZURE_SERVER_HOST
# ✅ AZURE_SERVER_USER
# ✅ AZURE_SSH_PRIVATE_KEY
# ✅ AZURE_SERVER_REPO_PATH

# If NOT set, server dispatch will be SKIPPED (this is OK for testing)
```

### 4.2 Check CI Logs for Dispatch Status

**If secrets set**:
```
Log: "Configure SSH for Azure dispatch"
└─ SSH key configured ✅

Log: "Dispatch queue to Azure server"
└─ Queue uploaded via SCP ✅
└─ Server script executed via SSH ✅
```

**If secrets NOT set**:
```
Log: "Server dispatch skipped notice"
└─ "Azure dispatch skipped: set AZURE_SERVER_HOST..."
└─ This is normal for development 👍
```

### 4.3 If Server Executed: Verify Server Outputs

```bash
# SSH to your Azure VM
ssh -i /path/to/key.pem azureuser@<ip>

# Check outputs exist
cd /path/to/repo
ls -la out/
# Should contain: notebook-manifest.json, <config-folder>/, ...

# Check notebooks generated
find out -name "*.ipynb"
# Example expected: out/test-flow/test_config.ipynb

# Check manifest
cat out/notebook-manifest.json | jq .
# Should show status: "ok" if completed, "failed" if error

# Check gallery updated
cat docs-site/index.html | grep "test-flow"
# Should find your config in HTML
```

---

## Phase 5: Cleanup and Validation (2 minutes)

### 5.1 Remove Test Config

```bash
# Remove test files (optional - can keep for future reference)
git rm setups/2026/test-flow/test_config.yml
git commit -m "Cleanup: Remove test config"
git push origin main
```

### 5.2 Verify Complete Flow Worked

Create summary:
```bash
echo "=== Approach-4 Flow Validation Complete ==="
echo ""
echo "✅ Phase 1: Local setup verified"
echo "✅ Phase 2: Test config created and committed"
echo "✅ Phase 3: CI workflow executed successfully"
echo "   ├─ Changed configs detected"
echo "   ├─ setup.yaml generated"
echo "   ├─ Sanity configs created"
echo "   ├─ Sanity tests passed"
echo "   ├─ Server queue created"
echo "   └─ Artifacts uploaded"
echo ""
if [ -d "out/" ]; then
  echo "✅ Phase 4: Server execution completed"
  echo "   ├─ Notebooks generated"
  echo "   └─ Gallery built"
else
  echo "⏸️ Phase 4: Server execution skipped (ok for development)"
fi
echo ""
echo "✅ Phase 5: Validation complete"
echo ""
echo "=== System Ready ==="
```

---

## Common Validation Failures & Solutions

| Issue | Check | Solution |
|-------|-------|----------|
| Config not detected | CI logs: "Detect changed configs" shows 0 | Ensure file is `.yml`/`.yaml`, added to git, committed |
| Setup generation fails | CI logs: "Generate per-config setup.yaml" | Check YAML syntax: `yamllint` |
| Sanity test fails | CI logs: "Run setup.yaml sanity tests" error | Check TARDIS config validity, maybe too few packets |
| Server dispatch fails | CI logs: "Configure SSH" shows error | Check GitHub secrets are set correctly |
| Notebooks not generating | Server logs | Check server conda path, atom data available |
| Gallery empty | `docs-site/index.html` no entries | Check notebook-manifest.json created on server |

---

## Flow Validation Matrix

```
Expected vs Actual:

Stage                           Expected              Actual  Status
─────────────────────────────────────────────────────────────────────
1. Checkout                     ✅ Repo cloned         [?]   
2. Conda setup                  ✅ CI env created      [?]
3. Diff resolution              ✅ Refs resolved       [?]
4. Detect configs               ✅ Config found        [?]
5. Generate setup.yaml          ✅ setup.yaml created  [?]
6. Create sanity configs        ✅ Sanity files made   [?]
7. Run sanity tests             ✅ Tests completed     [?]
8. Create queue                 ✅ queue.json made     [?]
9. Upload artifacts             ✅ Artifacts uploaded  [?]
10. SSH dispatch (if enabled)   ⏸️ Skipped or ✅ OK   [?]
11. Build gallery               ✅ index.html created  [?]

Server (if dispatch enabled):

Stage                           Expected              Actual  Status
─────────────────────────────────────────────────────────────────────
1. Receive queue                ✅ queue.json received [?]
2. Create control env           ✅ a4-control created  [?]
3. Process configs              ✅ Loop started        [?]
4. Setup env from setup.yaml    ✅ Config env created  [?]
5. Run notebook for config      ✅ Notebook executed   [?]
6. Generate manifest            ✅ Notebook added      [?]
7. Build gallery                ✅ index.html built    [?]
```

Fill in [?] as you proceed through validation.

---

## Success Criteria (All must pass ✅)

- [ ] Git detects your test config change
- [ ] CI runs all stages without error
- [ ] Sanity tests pass and config queued
- [ ] Artifacts downloadable from Actions
- [ ] Changed configs JSON contains your file
- [ ] setup.yaml generated correctly
- [ ] sanity-results.json shows `true`
- [ ] server-queue.json not empty (if sanity passed)
- [ ] (Optional) Server notebooks generated
- [ ] (Optional) Gallery shows your config

**If all ✅, system is working correctly!**

---

## Next Steps

1. Add real TARDIS configs to `setups/2026/`
2. Commit and let CI process them
3. (Optional) Enable server dispatch for production runs
4. Monitor outputs in Actions artifacts
5. Use GitHub Pages to publish gallery

---

## Timeline for Reference

```
Total: ~30-40 minutes (including sanity checks)
│
├─ Setup & prep: 5 min
├─ Push & wait: 1 min (just for git)
├─ CI execution: 
│  ├─ Setup & detect: 2 min
│  ├─ Generate: 2 min
│  ├─ Sanity tests: 10-20 min ← Variable
│  ├─ Queue & artifacts: 2 min
│  └─ Gallery build: 1 min
└─ Inspect & cleanup: 2-5 min

If Azure enabled:
  + Server execution: 15-60 min (depends on simulation complexity)
```
