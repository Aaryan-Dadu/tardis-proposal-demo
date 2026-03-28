from __future__ import annotations

import argparse
from pathlib import Path

import papermill as pm


def resolve_atom_data_for_notebook(atom_data: str) -> str:
    candidate = Path(atom_data)
    if candidate.exists():
        return str(candidate)

    normalized = atom_data[:-3] if atom_data.endswith(".h5") else atom_data
    normalized_candidate = Path(normalized)
    if normalized_candidate.exists():
        return str(normalized_candidate)

    h5_candidate = Path(f"{normalized}.h5")
    if h5_candidate.exists():
        return str(h5_candidate)

    try:
        from tardis.io.atom_data import download_atom_data

        downloaded = download_atom_data(normalized)
        if downloaded:
            downloaded_path = Path(str(downloaded))
            if downloaded_path.exists():
                return str(downloaded_path)
    except Exception:
        pass

    if h5_candidate.exists():
        return str(h5_candidate)
    if normalized_candidate.exists():
        return str(normalized_candidate)

    return normalized


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute report notebook for one config.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--atom-data", required=True)
    parser.add_argument("--output-notebook", required=True)
    parser.add_argument("--template", default="templates/config_report_template.ipynb")
    args = parser.parse_args()

    output_notebook = Path(args.output_notebook)
    output_notebook.parent.mkdir(parents=True, exist_ok=True)
    resolved_atom_data = resolve_atom_data_for_notebook(args.atom_data)

    pm.execute_notebook(
        input_path=args.template,
        output_path=str(output_notebook),
        parameters={
            "config_path": args.config,
            "atom_data": resolved_atom_data,
        },
        kernel_name="python3",
    )
    print(f"Notebook generated: {output_notebook}")


if __name__ == "__main__":
    main()
