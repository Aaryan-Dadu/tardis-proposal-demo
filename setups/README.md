# TARDIS Configuration Setups

This directory contains example TARDIS configurations for the approach-4 pipeline.

## Structure

Each configuration is organized as:

```
setups/
└── 2026/
    └── GSOC_2026_Paper/
        ├── setup.yaml           # Environment and TARDIS version specification
        └── tardis_example.yml   # TARDIS simulation configuration
```

## setup.yaml Format

Each configuration directory must contain a `setup.yaml` that specifies:

- **environment.lockfile_url**: URL to tardisbase conda-lock file (for reproducible base dependencies)
- **environment.channels**: Conda channels to use (typically `conda-forge`)
- **environment.extra_packages**: Additional packages besides tardis-sn (e.g., visualization tools)
- **tardis.requested_ref**: TARDIS version tag or `release-latest`
- **tardis.conda_spec**: Conda install spec (e.g., `tardis-sn` or `tardis-sn=2024.06.09`)
- **config.path**: Path to the TARDIS YAML config file
- **config.atom_data**: Atom data identifier (e.g., `kurucz_cd23_chianti_H_He_latest`)

### Example

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
  requested_ref: release-latest
  conda_spec: tardis-sn
config:
  path: setups/2026/GSOC_2026_Paper/tardis_example.yml
  atom_data: kurucz_cd23_chianti_H_He_latest
```

## How Configurations Flow Through the Pipeline

1. **Config committed to repo** → changes detected by CI
2. **CI generates setup.yaml** → infers TARDIS version from config metadata
3. **CI creates sanity config** → lightweight test version with reduced iterations
4. **CI runs sanity check** → verifies config is valid
5. **Server creates environment** → conda-lock → install TARDIS → install extras
6. **Server executes notebook** → Papermill injects config path and atom data
7. **Server generates gallery** → card links to notebooks and configs

## Adding New Configurations

1. Create a new directory under `setups/2026/` (year as needed)
2. Add your `tardis_example.yml` configuration file
3. Optionally add `metadata.tardis_version: <tag>` to the config if you want a specific TARDIS version
4. Commit to main branch
5. GitHub Actions will automatically:
   - Generate `setup.yaml`
   - Run sanity checks
   - Queue for server execution (if secrets configured)
   - Generate notebook and add to gallery

## Troubleshooting

### Config not detected
- Ensure file ends in `.yml`, `.yaml`, or `.csvy`
- Commit to `main` branch (PR merges also work)

### Setup.yaml generation fails
- Check YAML syntax in your config
- Verify `atom_data` is a valid identifier (not a file path)

### Sanity check fails
- Check error message in CI logs
- May indicate invalid TARDIS config syntax
- Verify config values are reasonable (packets, iterations, etc.)

### Server notebook generation fails
- Check server logs (if Azure integration is set up)
- Verify atom data is available for download
- Ensure TARDIS can import configuration
