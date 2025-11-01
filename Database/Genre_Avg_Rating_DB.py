"""
Reads movie, genre, rating from SQLite (movies.db),
splits multi-genre rows, computes average rating per genre,
ranks genres, and saves both CSV + chart (PNG).
"""

import argparse
import sqlite3
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def compute_genre_averages_from_df(df: pd.DataFrame, genre_col: str, rating_col: str,
                                   delimiter: str = ",", min_count: int = 1) -> pd.DataFrame:
    # Make rating numeric and drop missing
    df = df.copy()
    df[rating_col] = pd.to_numeric(df[rating_col], errors="coerce")
    df = df.dropna(subset=[rating_col, genre_col])

    # Split & explode genres
    df[genre_col] = df[genre_col].astype(str).str.split(delimiter)
    df = df.explode(genre_col)
    df[genre_col] = df[genre_col].astype(str).str.strip()
    df = df[df[genre_col] != ""]

    # Group and aggregate
    agg = (
        df.groupby(genre_col, as_index=False)[rating_col]
          .agg(avg_rating="mean", count="size")
    )

    # Optional min count filter
    if min_count > 1:
        agg = agg[agg["count"] >= min_count]

    # Sort + rank
    agg = agg.sort_values(["avg_rating", "count"], ascending=[False, False]).reset_index(drop=True)
    agg["rank"] = range(1, len(agg) + 1)
    return agg[["rank", genre_col, "avg_rating", "count"]]


def plot_barh(agg: pd.DataFrame, genre_col: str, rating_col_name: str, out_png: Path = None,
              title: str = "Average Rating per Genre"):
    plt.figure(figsize=(10, max(4, 0.35 * len(agg))))
    plt.barh(agg[genre_col], agg[rating_col_name])
    plt.xlabel("Average Rating")
    plt.ylabel("Genre")
    plt.title(title)
    plt.gca().invert_yaxis()
    plt.tight_layout()
    if out_png:
        out_png = Path(out_png)
        out_png.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(out_png, dpi=200, bbox_inches="tight")
    else:
        plt.show()
    plt.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="./movies.db")
    ap.add_argument("--table", default="movies")
    ap.add_argument("--genre-col", default="genre")
    ap.add_argument("--rating-col", default="rating")
    ap.add_argument("--delimiter", default=",")
    ap.add_argument("--min-count", type=int, default=1)
    ap.add_argument("--out-csv", default="./genre_avg_ratings_from_db.csv")
    ap.add_argument("--out-png", default="./genre_avg_ratings_from_db.png")
    ap.add_argument("--title", default="Average Rating per Genre (from SQLite)")
    args = ap.parse_args()

    # Read the needed columns from SQLite
    with sqlite3.connect(args.db) as conn:
        df = pd.read_sql_query(
            f'SELECT "{args.genre_col}" AS genre, "{args.rating_col}" AS rating FROM "{args.table}"',
            conn
        )

    agg = compute_genre_averages_from_df(df, "genre", "rating", args.delimiter, args.min_count)

    # Save CSV
    out_csv = Path(args.out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    agg.to_csv(out_csv, index=False)

    # Plot PNG
    plot_barh(agg, "genre", "avg_rating", args.out_png, args.title)

    print(f"Saved: {out_csv}")
    print(f"Saved: {args.out_png}")


if __name__ == "__main__":
    main()
