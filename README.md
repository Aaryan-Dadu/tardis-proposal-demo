# tardis-proposal-demo

Approach-4 prototype for incremental config processing with CI sanity checks and optional Azure server execution.

## Quick Links

📊 **[PROJECT_STATUS.md](PROJECT_STATUS.md)** – Complete project status & checklist  
🚀 **[QUICK_START.md](QUICK_START.md)** – Get started in 5 minutes  
🔍 **[FLOW_VALIDATION.md](FLOW_VALIDATION.md)** – Complete flow walkthrough (step-by-step)  
📖 **[SERVER_COMPLETE_SETUP.md](SERVER_COMPLETE_SETUP.md)** – Complete server setup guide  
🖥️ [SERVER_SETUP.md](SERVER_SETUP.md) – Azure VM quick reference  
⚙️ [ENVIRONMENTS.md](ENVIRONMENTS.md) – Three-tier conda model  
📋 [setups/README.md](setups/README.md) – Config format & structure  
🔍 [AUDIT_SUMMARY.md](AUDIT_SUMMARY.md) – Project audit & fixes

## Key Features

✅ **Automatic CI detection** – detects `.yml`, `.yaml`, `.csvy` files  
✅ **TARDIS version inference** – reads version from config metadata  
✅ **Lightweight sanity checks** – fast validation before server simulation  
✅ **Secure PR handling** – PRs skip server (avoid busy), only main branch dispatches  
✅ **Reproducible environments** – lockfile-first conda setup per installation.rst  
✅ **Optional Azure integration** – seamless CI→server handoff via SSH  
✅ **Per-config isolation** – each variant gets independent environment  
✅ **Parameterized notebooks** – Papermill injects config & atom data  
✅ **Gallery generation** – static HTML view of results

## Current Status

- **CI Workflow**: ✅ All stages working (detect → sanity → queue → dispatch)
- **PR Dispatch**: ⏸️ **Disabled** (commented out to prevent server overload from PRs)
- **Main Branch**: ✅ **Enabled for server dispatch** (if secrets configured)
- **Server Code**: ✅ Complete (setup_env, process queue, papermill execution)
- **Documentation**: ✅ Comprehensive (includes troubleshooting & validation)

## What Changed

- **PR detection commented out** in `.github/workflows/prototype-approach-4.yml`
  - Prevents server dispatch for every PR
  - Only `push:main` and `workflow_dispatch` trigger server
  - Keeps PR CI sanity checks (fast, no server load)