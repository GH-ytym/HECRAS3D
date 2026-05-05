#!/usr/bin/env python3
"""
Generate a 2D diagram for stride-controlled point thinning.

The figure shows:
- a regular 2D point lattice
- keeping one sample every i points along both x and y
- highlighted sampled points connected as coarse rectangular cells
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


BASE_POINT_COLOR = "#B8B8B8"
SAMPLED_POINT_COLOR = "#D94141"
LINE_COLOR = "#2F5DCC"


def generate_points(
    rows: int,
    cols: int,
    spacing_x: float,
    spacing_y: float,
) -> list[tuple[int, int, float, float]]:
    """Generate a regular 2D point lattice."""
    points: list[tuple[int, int, float, float]] = []
    for row in range(rows):
        for col in range(cols):
            points.append((row, col, col * spacing_x, row * spacing_y))
    return points


def sample_grid_points(
    points: list[tuple[int, int, float, float]],
    stride: int,
    offset_row: int = 0,
    offset_col: int = 0,
) -> list[tuple[int, int, float, float]]:
    """Keep one point every stride points along both row and column."""
    if stride <= 0:
        raise ValueError("stride must be a positive integer")
    if offset_row < 0 or offset_col < 0:
        raise ValueError("offset_row and offset_col must be non-negative")

    sampled_points: list[tuple[int, int, float, float]] = []
    for row, col, x, y in points:
        if row >= offset_row and col >= offset_col:
            if (row - offset_row) % stride == 0 and (col - offset_col) % stride == 0:
                sampled_points.append((row, col, x, y))
    return sampled_points


def draw_figure(
    rows: int,
    cols: int,
    stride: int,
    output_path: Path,
    dpi: int,
    spacing_x: float,
    spacing_y: float,
    offset_row: int,
    offset_col: int,
) -> Path:
    """Draw the thinning diagram and save it."""
    points = generate_points(
        rows=rows,
        cols=cols,
        spacing_x=spacing_x,
        spacing_y=spacing_y,
    )
    sampled_points = sample_grid_points(
        points=points,
        stride=stride,
        offset_row=offset_row,
        offset_col=offset_col,
    )

    fig_width = max(6.2, cols * spacing_x * 0.95)
    fig_height = max(4.6, rows * spacing_y * 0.95)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.set_facecolor("white")

    x_all = [point[2] for point in points]
    y_all = [point[3] for point in points]
    ax.scatter(
        x_all,
        y_all,
        s=18,
        c=BASE_POINT_COLOR,
        marker="o",
        edgecolors="none",
        zorder=1,
    )

    if sampled_points:
        sampled_lookup = {
            (row, col): (x, y) for row, col, x, y in sampled_points
        }
        for row, col, x, y in sampled_points:
            right_key = (row, col + stride)
            down_key = (row + stride, col)
            if right_key in sampled_lookup:
                right_x, right_y = sampled_lookup[right_key]
                ax.plot(
                    [x, right_x],
                    [y, right_y],
                    color=LINE_COLOR,
                    linewidth=1.5,
                    zorder=2,
                )
            if down_key in sampled_lookup:
                down_x, down_y = sampled_lookup[down_key]
                ax.plot(
                    [x, down_x],
                    [y, down_y],
                    color=LINE_COLOR,
                    linewidth=1.5,
                    zorder=2,
                )

        x_sampled = [point[2] for point in sampled_points]
        y_sampled = [point[3] for point in sampled_points]
        ax.scatter(
            x_sampled,
            y_sampled,
            s=42,
            c=SAMPLED_POINT_COLOR,
            marker="o",
            edgecolors="black",
            linewidths=0.5,
            zorder=3,
        )

    ax.set_aspect("equal")
    max_x = (cols - 1) * spacing_x
    max_y = (rows - 1) * spacing_y
    margin_x = max(spacing_x * 0.8, 0.2)
    margin_y = max(spacing_y * 0.8, 0.2)
    ax.set_xlim(-margin_x, max_x + margin_x)
    ax.set_ylim(-margin_y, max_y + margin_y)
    ax.invert_yaxis()
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_title("Stride-Controlled Point Thinning", fontsize=13)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return output_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Draw a 2D figure for stride-controlled point thinning.",
    )
    parser.add_argument("--rows", type=int, default=6, help="Number of point rows.")
    parser.add_argument("--cols", type=int, default=16, help="Number of point columns.")
    parser.add_argument(
        "--stride",
        type=int,
        default=4,
        help="Keep one point every stride points in both x and y directions.",
    )
    parser.add_argument(
        "--spacing-x",
        type=float,
        default=0.58,
        help="Horizontal distance between adjacent original points.",
    )
    parser.add_argument(
        "--spacing-y",
        type=float,
        default=0.58,
        help="Vertical distance between adjacent original points.",
    )
    parser.add_argument(
        "--offset-row",
        type=int,
        default=0,
        help="Sampling row offset for the first retained point.",
    )
    parser.add_argument(
        "--offset-col",
        type=int,
        default=0,
        help="Sampling column offset for the first retained point.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("stride_sampling_figure.png"),
        help="Output image path.",
    )
    parser.add_argument("--dpi", type=int, default=300, help="Output image DPI.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    saved_path = draw_figure(
        rows=args.rows,
        cols=args.cols,
        stride=args.stride,
        output_path=args.output,
        dpi=args.dpi,
        spacing_x=args.spacing_x,
        spacing_y=args.spacing_y,
        offset_row=args.offset_row,
        offset_col=args.offset_col,
    )
    print(f"Saved figure to: {saved_path.resolve()}")


if __name__ == "__main__":
    main()
