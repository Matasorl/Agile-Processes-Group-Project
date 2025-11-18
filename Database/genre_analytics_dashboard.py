"""
Genre analytics:
- Average rating per genre (clean DataFrame + CSV)
- Bar chart of rating vs genre
- Popular genre dashboard (frequency + avg rating)
- Scatterplot of rating vs another numeric field (e.g., votes)

Relies on existing helpers and plotting style from Genre_Avg_Rating_DB.py.
"""

import argparse
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from Genre_Avg_Rating_DB import compute_genre_averages_from_df, plot_barh


def load_movie_columns(db_path: str, table: str, columns) -> pd.DataFrame:
    with sqlite3.connect(db_path) as conn:
        col_clause = ", ".join([f'"{col}"' for col in columns])
        query = f'SELECT {col_clause} FROM "{table}"'
        return pd.read_sql_query(query, conn)


def plot_genre_correlation_bar(agg: pd.DataFrame, genre_col: str, rating_col_name: str,
                               out_png: Path, title: str, top_n: int = None):
    data = agg
    if top_n:
        data = data.head(top_n)
    plt.figure(figsize=(12, 6))
    plt.bar(data[genre_col], data[rating_col_name], color="steelblue")
    plt.title(title)
    plt.xlabel("Genre")
    plt.ylabel("Average Rating")
    plt.xticks(rotation=65, ha="right")
    plt.tight_layout()
    out_path = Path(out_png)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_genre_dashboard(agg: pd.DataFrame, genre_col: str, rating_col_name: str,
                         out_png: Path, title: str, top_n: int = 15):
    top_by_count = agg.sort_values("count", ascending=False).head(top_n)
    top_by_rating = agg.sort_values(rating_col_name, ascending=False).head(top_n)

    fig, axes = plt.subplots(2, 1, figsize=(14, 12))
    fig.suptitle(title, fontsize=16)

    axes[0].bar(top_by_count[genre_col], top_by_count["count"], color="skyblue")
    axes[0].set_title(f"Genre Frequency (Top {top_n})")
    axes[0].set_xlabel("Genre")
    axes[0].set_ylabel("Count")
    axes[0].tick_params(axis="x", rotation=65)

    axes[1].bar(top_by_rating[genre_col], top_by_rating[rating_col_name], color="steelblue")
    axes[1].set_title(f"Average Rating per Genre (Top {top_n})")
    axes[1].set_xlabel("Genre")
    axes[1].set_ylabel("Average Rating")
    axes[1].tick_params(axis="x", rotation=65)

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    out_path = Path(out_png)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_rating_scatter(df: pd.DataFrame, x_col: str, y_col: str,
                        out_png: Path, title: str):
    df = df.copy()
    df[x_col] = pd.to_numeric(df[x_col], errors="coerce")
    df[y_col] = pd.to_numeric(df[y_col], errors="coerce")
    df = df.dropna(subset=[x_col, y_col])

    plot_df = df
    if len(plot_df) > 5000:
        plot_df = plot_df.sample(2000, random_state=42)

    plt.figure(figsize=(8, 6))
    plt.scatter(plot_df[x_col], plot_df[y_col], s=12, alpha=0.35, color="darkorange")

    if len(plot_df) > 1:
        m, b = np.polyfit(plot_df[x_col], plot_df[y_col], 1)
        xx = np.linspace(plot_df[x_col].min(), plot_df[x_col].max(), 100)
        yy = m * xx + b
        plt.plot(xx, yy, linewidth=2, color="red", label=f"y = {m:.3f}x + {b:.3f}")
        plt.legend()

    plt.title(title)
    plt.xlabel(x_col.replace("_", " ").title())
    plt.ylabel(y_col.replace("_", " ").title())
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.7)
    plt.tight_layout()
    out_path = Path(out_png)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="./movies.db")
    ap.add_argument("--table", default="movies")
    ap.add_argument("--genre-col", default="genre")
    ap.add_argument("--rating-col", default="rating")
    ap.add_argument("--delimiter", default=",")
    ap.add_argument("--min-count", type=int, default=1)
    ap.add_argument("--out-csv", default="./genre_avg_ratings_dashboard.csv")
    ap.add_argument("--avg-rating-bar-png", default="./genre_rating_bar.png")
    ap.add_argument("--avg-rating-title", default="Average Rating per Genre")
    ap.add_argument("--genre-corr-png", default="./genre_rating_correlation_bar.png")
    ap.add_argument("--genre-corr-title", default="Rating vs Genre (Average Rating)")
    ap.add_argument("--dashboard-png", default="./genre_dashboard.png")
    ap.add_argument("--dashboard-title", default="Popular Genres Dashboard")
    ap.add_argument("--dashboard-top-n", type=int, default=15)
    ap.add_argument("--scatter-x", default="votes")
    ap.add_argument("--scatter-png", default="./rating_vs_votes_scatter.png")
    ap.add_argument("--scatter-title", default="Rating vs Votes (scatter)")
    args = ap.parse_args()

    cols_to_load = {args.genre_col, args.rating_col, args.scatter_x}
    df = load_movie_columns(args.db, args.table, list(cols_to_load))

    genre_avg = compute_genre_averages_from_df(
        df[[args.genre_col, args.rating_col]],
        args.genre_col,
        args.rating_col,
        args.delimiter,
        args.min_count
    )

    out_csv = Path(args.out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    genre_avg.to_csv(out_csv, index=False)

    plot_barh(genre_avg, args.genre_col, "avg_rating", args.avg_rating_bar_png, args.avg_rating_title)
    plot_genre_correlation_bar(genre_avg, args.genre_col, "avg_rating",
                               args.genre_corr_png, args.genre_corr_title)
    plot_genre_dashboard(genre_avg, args.genre_col, "avg_rating",
                         args.dashboard_png, args.dashboard_title, args.dashboard_top_n)
    plot_rating_scatter(df, args.scatter_x, args.rating_col,
                        args.scatter_png, args.scatter_title)

    print(f"Saved: {out_csv}")
    print(f"Saved: {args.avg_rating_bar_png}")
    print(f"Saved: {args.genre_corr_png}")
    print(f"Saved: {args.dashboard_png}")
    print(f"Saved: {args.scatter_png}")


if __name__ == "__main__":
    main()
