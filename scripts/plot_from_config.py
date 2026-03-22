"""Generate SDEC and LIV plots from a TARDIS configuration."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from tardis import run_tardis
from tardis.io.atom_data import download_atom_data
from tardis.io.configuration.config_reader import Configuration
from tardis.visualization import LIVPlotter, SDECPlotter

DEFAULT_ATOM_DATA = "kurucz_cd23_chianti_H_He_latest"
PLOTTERS = (SDECPlotter, LIVPlotter)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate SDEC and LIV plots from a TARDIS configuration."
    )
    parser.add_argument("config", help="Path to a configuration YAML file.")
    parser.add_argument("--atom-data", default=None)
    parser.add_argument("--output-prefix", default=None)
    parser.add_argument("--output-dir", default=".")
    parser.add_argument("--format", choices=["png", "pdf"], default="png")
    return parser


def resolve_atom_data(atom_data: str | None) -> str:
    if atom_data:
        return atom_data
    download_atom_data(DEFAULT_ATOM_DATA)
    return DEFAULT_ATOM_DATA


def save_plots(simulation, output_prefix: str, output_dir: Path, fmt: str = "png") -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    created_files: list[str] = []

    for plotter_cls in PLOTTERS:
        plotter = plotter_cls.from_simulation(simulation)
        for packets_mode in ("real", "virtual"):
            artist = plotter.generate_plot_mpl(packets_mode=packets_mode)
            output_path = output_dir / f"{output_prefix}_{plotter_cls.__name__.lower()}_{packets_mode}.{fmt}"
            artist.figure.savefig(output_path, dpi=250, bbox_inches="tight")
            plt.close(artist.figure)
            created_files.append(str(output_path))

    return created_files


def generate_plots_from_config(
    config_path: str | Path,
    *,
    atom_data: str | None = None,
    output_prefix: str | None = None,
    output_dir: str | Path = ".",
    fmt: str = "png",
) -> list[str]:
    config_path = Path(config_path)
    output_dir = Path(output_dir)
    output_prefix = output_prefix or config_path.stem

    config = Configuration.from_yaml(str(config_path))
    simulation = run_tardis(
        config,
        atom_data=resolve_atom_data(atom_data),
        virtual_packet_logging=True,
    )
    return save_plots(simulation, output_prefix, output_dir, fmt)


def main() -> None:
    args = build_arg_parser().parse_args()
    generate_plots_from_config(
        args.config,
        atom_data=args.atom_data,
        output_prefix=args.output_prefix,
        output_dir=args.output_dir,
        fmt=args.format,
    )


if __name__ == "__main__":
    main()
