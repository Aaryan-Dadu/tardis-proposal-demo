from __future__ import annotations

import argparse
from pathlib import Path

import papermill as pm


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute report notebook for one config.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--atom-data", required=True)
    parser.add_argument("--output-notebook", required=True)
    parser.add_argument("--template", default="templates/config_report_template.ipynb")
    args = parser.parse_args()

    output_notebook = Path(args.output_notebook)
    output_notebook.parent.mkdir(parents=True, exist_ok=True)

    pm.execute_notebook(
        input_path=args.template,
        output_path=str(output_notebook),
        parameters={
            "config_path": args.config,
            "atom_data": args.atom_data,
        },
        kernel_name="python3",
    )
    print(f"Notebook generated: {output_notebook}")


if __name__ == "__main__":
    main()
