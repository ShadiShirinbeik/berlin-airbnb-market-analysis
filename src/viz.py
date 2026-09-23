"""Plot theme and the two reusable charts.

One theme applied everywhere is what makes a repo look like one piece of
work rather than a pile of notebooks.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from . import config as cfg


def set_theme() -> None:
    """Call once at the top of every notebook."""
    sns.set_theme(style="whitegrid", palette=cfg.PALETTE, context="notebook")
    plt.rcParams.update(
        {
            "figure.figsize": cfg.FIG_SIZE,
            "figure.dpi": 110,
            "savefig.dpi": cfg.FIG_DPI,
            "savefig.bbox": "tight",
            "axes.titlesize": 13,
            "axes.titleweight": "bold",
            "axes.labelsize": 11,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "font.size": 10,
        }
    )


def save_fig(fig, name: str) -> None:
    """Write a figure to reports/figures/ so the README can embed it."""
    path = cfg.FIGURES_DIR / f"{name}.png"
    fig.savefig(path)
    print(f"saved -> {path.relative_to(cfg.PROJECT_ROOT)}")


def plot_distribution(s: pd.Series, title: str = "", log: bool = False, bins: int = 60):
    """Histogram + ECDF side by side.

    The ECDF answers "what share of listings cost under X?" — the question
    people actually ask, far more often than "what is the mean?".
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    data = np.log10(s[s > 0]) if log else s

    sns.histplot(data, bins=bins, ax=axes[0], edgecolor="white", linewidth=0.4)
    axes[0].set_title(f"{title} — distribution")
    axes[0].set_xlabel("log10(value)" if log else "value")

    sns.ecdfplot(data, ax=axes[1])
    axes[1].set_title(f"{title} — cumulative (ECDF)")
    axes[1].set_xlabel("log10(value)" if log else "value")

    fig.tight_layout()
    return fig, axes


def plot_ci_comparison(
    results: pd.DataFrame,
    label_col: str,
    est_col: str = "estimate",
    low_col: str = "lower",
    high_col: str = "upper",
    title: str = "",
    xlabel: str = "",
):
    """Dot-and-whisker chart of estimates with intervals.

    Replaces a bar chart of means throughout the project: a bar chart
    invites the eye to see a difference between two bars of slightly
    different height; this shows how much of that difference is real.
    """
    d = results.sort_values(est_col)
    fig, ax = plt.subplots(figsize=(8, 0.5 * len(d) + 2))
    y = np.arange(len(d))
    ax.errorbar(
        d[est_col], y,
        xerr=[d[est_col] - d[low_col], d[high_col] - d[est_col]],
        fmt="o", capsize=4, markersize=7,
    )
    ax.set_yticks(y)
    ax.set_yticklabels(d[label_col])
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    return fig, ax
