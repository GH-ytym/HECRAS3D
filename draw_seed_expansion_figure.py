#!/usr/bin/env python3
"""
Generate a 2D diagram for seed tiles and one-ring neighborhood expansion.

The figure follows these rules:
- uniform tile grid with black outlines
- each tile center marked with an "x"
- tiles whose centers fall inside the frustum footprint are seed tiles (blue)
- one-ring neighbors around all seeds are expanded tiles (yellow)
- duplicates are removed by set semantics
- out-of-bound neighbors are clipped by grid limits
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle


SEED_COLOR = "#4A90E2"
EXPANDED_COLOR = "#F5C242"
EDGE_COLOR = "black"
CENTER_MARK_COLOR = "black"


def point_in_ellipse(
    x: float,
    y: float,
    center_x: float,
    center_y: float,
    radius_x: float,
    radius_y: float,
) -> bool:
    """Return True when a point is inside or on the ellipse boundary."""
    dx = (x - center_x) / radius_x
    dy = (y - center_y) / radius_y
    return dx * dx + dy * dy <= 1.0


def collect_seed_tiles(
    rows: int,
    cols: int,
    ellipse_center_x: float,
    ellipse_center_y: float,
    ellipse_radius_x: float,
    ellipse_radius_y: float,
) -> set[tuple[int, int]]:
    """Collect tiles whose center points fall inside the ellipse."""
    seeds: set[tuple[int, int]] = set()
    for row in range(rows):
        for col in range(cols):
            center_x = col + 0.5
            center_y = row + 0.5
            if point_in_ellipse(
                center_x,
                center_y,
                ellipse_center_x,
                ellipse_center_y,
                ellipse_radius_x,
                ellipse_radius_y,
            ):
                seeds.add((row, col))
    return seeds


def expand_one_ring(
    seeds: set[tuple[int, int]],
    rows: int,
    cols: int,
) -> set[tuple[int, int]]:
    """Expand each seed tile to its surrounding 8-neighborhood."""
    expanded: set[tuple[int, int]] = set()
    for row, col in seeds:
        for d_row in (-1, 0, 1):
            for d_col in (-1, 0, 1):
                n_row = row + d_row
                n_col = col + d_col
                if 0 <= n_row < rows and 0 <= n_col < cols:
                    expanded.add((n_row, n_col))
    return expanded - seeds


def draw_figure(
    rows: int,
    cols: int,
    output_path: Path,
    ellipse_center_x: float,
    ellipse_center_y: float,
    ellipse_radius_x: float,
    ellipse_radius_y: float,
    dpi: int,
) -> Path:
    """Draw the full seed and expansion diagram and save it to disk."""
    seeds = collect_seed_tiles(
        rows=rows,
        cols=cols,
        ellipse_center_x=ellipse_center_x,
        ellipse_center_y=ellipse_center_y,
        ellipse_radius_x=ellipse_radius_x,
        ellipse_radius_y=ellipse_radius_y,
    )
    expanded = expand_one_ring(seeds=seeds, rows=rows, cols=cols)

    fig_width = max(6.0, cols * 0.9)
    fig_height = max(5.0, rows * 0.9)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.set_facecolor("white")

    for row in range(rows):
        for col in range(cols):
            tile = (row, col)
            facecolor = "white"
            if tile in expanded:
                facecolor = EXPANDED_COLOR
            if tile in seeds:
                facecolor = SEED_COLOR

            rect = Rectangle(
                (col, row),
                1.0,
                1.0,
                facecolor=facecolor,
                edgecolor=EDGE_COLOR,
                linewidth=1.1,
            )
            ax.add_patch(rect)
            ax.plot(
                col + 0.5,
                row + 0.5,
                marker="x",
                markersize=5.5,
                markeredgewidth=1.0,
                color=CENTER_MARK_COLOR,
            )

    ellipse = Ellipse(
        xy=(ellipse_center_x, ellipse_center_y),
        width=ellipse_radius_x * 2.0,
        height=ellipse_radius_y * 2.0,
        angle=0.0,
        fill=False,
        edgecolor="black",
        linewidth=2.0,
        linestyle="-",
    )
    ax.add_patch(ellipse)

    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.set_aspect("equal")
    ax.invert_yaxis()
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_title("Seed Tiles And One-Ring Neighborhood Expansion", fontsize=13)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return output_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Draw a 2D tile diagram for seed selection and neighborhood expansion.",
    )
    parser.add_argument("--rows", type=int, default=8, help="Number of tile rows.")
    parser.add_argument("--cols", type=int, default=12, help="Number of tile columns.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("seed_expansion_figure.png"),
        help="Output image path.",
    )
    parser.add_argument(
        "--ellipse-center-x",
        type=float,
        default=6.1,
        help="Ellipse center x coordinate in tile-space.",
    )
    parser.add_argument(
        "--ellipse-center-y",
        type=float,
        default=4.0,
        help="Ellipse center y coordinate in tile-space.",
    )
    parser.add_argument(
        "--ellipse-radius-x",
        type=float,
        default=2.7,
        help="Ellipse radius along x.",
    )
    parser.add_argument(
        "--ellipse-radius-y",
        type=float,
        default=1.8,
        help="Ellipse radius along y.",
    )
    parser.add_argument("--dpi", type=int, default=300, help="Output image DPI.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    saved_path = draw_figure(
        rows=args.rows,
        cols=args.cols,
        output_path=args.output,
        ellipse_center_x=args.ellipse_center_x,
        ellipse_center_y=args.ellipse_center_y,
        ellipse_radius_x=args.ellipse_radius_x,
        ellipse_radius_y=args.ellipse_radius_y,
        dpi=args.dpi,
    )
    print(f"Saved figure to: {saved_path.resolve()}")


if __name__ == "__main__":
    main()
