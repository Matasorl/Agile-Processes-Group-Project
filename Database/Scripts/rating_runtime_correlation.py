import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# load data from database and select relevant columns
conn = sqlite3.connect("movies.db")
df = pd.read_sql_query("SELECT runtime, rating FROM movies", conn)

# convert to numeric
df['runtime'] = pd.to_numeric(df['runtime'], errors='coerce')
df['rating'] = pd.to_numeric(df['rating'], errors='coerce')

# drop rows with missing values
df = df.dropna(subset=['runtime', 'rating'])

# average rating for each runtime
avg_by_runtime = (
    df.groupby("runtime", as_index=False)["rating"]
      .mean()
      .rename(columns={"rating": "avg_rating"})
      .sort_values("runtime")
)

avg_by_runtime.to_csv("avg_rating_by_runtime.csv", index=False)

# Correlations (Pearson for linear, Spearman for monotonic)
pearson_r  = df[["runtime", "rating"]].corr(method="pearson").loc["runtime", "rating"]
spearman_r = df[["runtime", "rating"]].corr(method="spearman").loc["runtime", "rating"]

corr_df = pd.DataFrame({
    "method": ["Pearson r", "Spearman r"],
    "correlation": [pearson_r, spearman_r],
})
# r^2 for Pearson r correlation
corr_df["r_squared (pearson)"] = [pearson_r ** 2, None]
corr_df.round(4).to_csv("runtime_rating_correlations.csv", index=False)

# bar chart of correlations
plt.figure(figsize=(6, 5))
plt.bar(corr_df["method"], corr_df["correlation"])
plt.title("Correlation between Rating and Runtime")
plt.xlabel("Correlation method")
plt.ylabel("Correlation coefficient (r)")
plt.tight_layout()
plt.show()


# Bin runtime into 20 equal-width bins in [0, 1]
bins = np.linspace(0, 1, 21)
df["runtime_bin"] = pd.cut(df["runtime"], bins=bins, include_lowest=True)

# Average rating in each bin
avg_by_bin = (
    df.groupby("runtime_bin", observed=False)["rating"]
    .mean()
    . reset_index()
    .rename(columns={"rating": "avg_rating"})
)

# Use bin midpoints for a nicer numeric x-axis
bin_mid = avg_by_bin["runtime_bin"].apply(lambda iv: iv.mid)

plt.figure(figsize=(9, 5))
plt.bar(bin_mid, avg_by_bin["avg_rating"], width=(bins[1] - bins[0]) * 0.9)
plt.title("Average Rating by Runtime (0–1)")
plt.xlabel("Runtime")
plt.ylabel("Average Rating (0–1)")
plt.xlim(0, 1)
plt.ylim(0, 1)
plt.tight_layout()
plt.savefig("avg_rating_by_runtime.png", dpi=150)
plt.show()

# Save the table (with midpoints) for your report
# avg_by_bin.assign(runtime_mid=bin_mid).to_csv("avg_rating_by_runtime_bins.csv", index=False)

# scatterplot with sample
plot_df = df
if len(plot_df) > 5000:  # downsample for readability/perf
    plot_df = plot_df.sample(2000, random_state=42)

x = df["runtime"].to_numpy()
y = df["rating"].to_numpy()
if len(x) > 1:
    m, b = np.polyfit(x, y, 1)
    xx = np.linspace(0, 1, 100)
    yy = m * xx + b
    plt.figure(figsize=(7, 5))
    plt.scatter(plot_df["runtime"], plot_df["rating"], s=6, alpha=0.15)
    plt.plot(xx, yy, linewidth=2, label=f'y = {m:.4f}x + {b:.4f}', color='red')
    plt.title("Runtime vs Rating (sampled 2000 movies and shows)")
    plt.xlabel("Runtime (0–1 Normalized)")
    plt.ylabel("Rating (0–1 Normalized)")
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig("runtime_rating_scatterplot.png", dpi=150)
    plt.show()


conn.close()
print("CSV saved and PNG created.")

# the correlations show a strong negative correlation between runtime and rating
# ratings tends to go DOWN as runtime goes UP

# the average rating by runtime bar chart shows non-linear patterns
# example: ratings are higher for long runtimes and lower for short or mid runtimes
# 20 bins, so it's not too vague nor too messy

# scatterplot shows overall pattern and highlights density and outliers.
# downwards direction so there's a negative correlation, but not a strong one