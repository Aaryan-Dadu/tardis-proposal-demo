# 🏗️ Implementation Architecture

## Component View

```mermaid
flowchart TB
  subgraph GH[GitHub Actions]
    CI[prototype-approach-4.yml]
    PAGES[deploy-gallery/static Pages workflows]
  end

  subgraph REPO[Repository]
    CFG[setups/** configs]
    GEN[generated/*.json]
    OUT[out/**]
    SITE[docs-site/**]
    SCRIPTS[scripts/*]
    SERVER[server/*]
  end

  subgraph VM[Azure VM]
    RUNNER[run_on_azure_example.sh]
    PROC[process_server_queue.py]
    PM[run_notebook_for_config.py]
  end

  CI --> GEN
  CI -->|scp queue| VM
  VM --> OUT
  VM --> SITE
  CI -->|scp back| OUT
  CI -->|scp back| SITE
  CI -->|commit/push| REPO
  PAGES --> SITE
```

## Runtime Sequence

```mermaid
sequenceDiagram
  participant Dev as Developer
  participant CI as GitHub Actions
  participant VM as Azure Server
  participant Repo as GitHub Repo

  Dev->>CI: push to main / workflow_dispatch
  CI->>CI: detect changed configs
  CI->>CI: generate setup.yaml files
  CI->>CI: run sanity configs
  CI->>CI: build server queue
  CI->>VM: copy queue + trigger runner
  VM->>VM: git restore . && git pull --ff-only
  VM->>VM: setup env + execute notebooks
  VM->>VM: generate manifest + gallery
  CI->>VM: fetch out/ and docs-site/
  CI->>Repo: commit generated artifacts
```

## Responsibility Split

- **CI job**
  - Orchestration, validation, dispatch, publishing
- **Server scripts**
  - Environment provisioning and notebook execution
- **Gallery script**
  - Rendered HTML notebook previews and index generation
- **Pages workflows**
  - Deploy static content from `docs-site/`
