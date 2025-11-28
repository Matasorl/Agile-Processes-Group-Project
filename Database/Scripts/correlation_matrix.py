import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# load data
conn = sqlite3.connect("../movies.db")
df = pd.read_sql_query("SELECT * FROM movies", conn)
conn.close()

print("Original dtypes from DB:")
print(df.dtypes)
print()

# clean numeric columns
df["runtime"] = pd.to_numeric(df["runtime"], errors="coerce")
df["votes"] = pd.to_numeric(df["votes"], errors="coerce")
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

# always require a rating
df = df.dropna(subset=["rating"]).copy()

# feature engineering
# num of genres
df["num_genres"] = df["genre"].fillna("").str.count(",") + 1
df.loc[df["genre"].isna(), "num_genres"] = np.nan

# log votes
df["log_votes"] = np.log10(df["votes"] + 1)

# main genre (first in the list)
df["main_genre"] = df["genre"].str.split(",").str[0].str.strip()

# relative runtime bands using normalized runtime (0–1)
# split titles into quartiles: shortest 25% -> longest 25%
df["runtime_band"] = pd.qcut(
    df["runtime"],
    q=4,
    labels=["shortest 25%", "25–50%", "50–75%", "longest 25%"]
)

print("Dtypes after feature engineering:")
print(df.dtypes)
print()

# numeric corelation matrix
numeric_cols = ["runtime", "rating", "votes", "log_votes", "num_genres"]
numeric_cols = [c for c in numeric_cols if c in df.columns]

num_df = df[numeric_cols].copy()
corr_matrix = num_df.corr()

print("Full correlation matrix (numeric features):")
print(corr_matrix.round(3))
print()

if "rating" in corr_matrix.columns:
    corr_with_rating = corr_matrix["rating"].sort_values(ascending=False)
    print("Correlation of each feature with rating (sorted):")
    print(corr_with_rating.round(3))
    print()

    # Simple bar chart of correlation with rating (excluding rating itself)
    corr_features = corr_with_rating.drop("rating", errors="ignore")
    plt.figure(figsize=(7, 4))
    corr_features.plot(kind="bar")
    plt.axhline(0, linewidth=1)
    plt.ylabel("Correlation with rating")
    plt.title("Numeric features vs rating (correlation)")
    plt.tight_layout()
    plt.show()
else:
    print("No 'rating' column in correlation matrix.")
    print()

# group-based insights
# average rating by relative runtime band
runtime_band_means = (
    df.groupby("runtime_band")["rating"]
      .mean()
      .sort_index()
)
print("Average rating by runtime band (relative):")
print(runtime_band_means.round(2))
print()

# average rating by main genre (top 10)
genre_means = (
    df.groupby("main_genre")["rating"]
      .mean()
      .sort_values(ascending=False)
)
print("Average rating by main genre (top 10):")
print(genre_means.round(2).head(10))
print()

# directors with enough titles
min_titles = 5

director_stats = (
    df.groupby("director")["rating"]
      .agg(["mean", "size"])
)
director_stats.columns = ["mean_rating", "num_titles"]
director_stats = director_stats[director_stats["num_titles"] >= min_titles]
director_stats = director_stats.sort_values("mean_rating", ascending=False)

print(f"Director stats (at least {min_titles} titles) – top 10:")
print(director_stats.head(10).round(2))
print()

# stars with enough titles
star_stats = (
    df.groupby("stars")["rating"]
      .agg(["mean", "size"])
)
star_stats.columns = ["mean_rating", "num_titles"]
star_stats = star_stats[star_stats["num_titles"] >= min_titles]
star_stats = star_stats.sort_values("mean_rating", ascending=False)

print(f"Star stats (at least {min_titles} titles) – top 10:")
print(star_stats.head(10).round(2))
print()
