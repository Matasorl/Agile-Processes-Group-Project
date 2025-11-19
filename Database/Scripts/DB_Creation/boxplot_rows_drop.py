# this script creates a boxplot of the numeric columns in movies-column-dropped.csv
# the boxplot indicates which rows to drop based on:
# if row >= 50% outliers, drop row
# if row <= 50% outliers, keep it

# the first boxplot shows the row-level missingness before cleaning
# AKA the reason for dropping rows

# the second boxplot shows the numeric columns after dropping sparse rows and mean imputation
# AKA the state of the data after cleaning

import pandas as pd
import matplotlib.pyplot as plt

# load data
df = pd.read_csv("movies-column-dropped.csv")   # change path if needed

# calculate missingness per row (fraction of columns that are NaN)
row_missing_ratio = df.isna().mean(axis=1)   # example; 0.33 means 33% of that row is missing

# boxplot of row-level missingness
plt.figure(figsize=(5, 5))
plt.boxplot(row_missing_ratio, vert=True)
plt.title("Row-level missingness (before cleaning)")
plt.xlabel("rows")
plt.ylabel("fraction of missing values per row")

# red-line at 0.5 (>= 0.5 -> drop)
# rows above the red line were dropped, the rest were given a mean imputation
plt.axhline(0.5, color="red", linestyle="--", label="drop if > 0.5 missing")
plt.legend()
plt.tight_layout()
plt.show()

# drop rows with >= 50% missing
to_drop = row_missing_ratio >= 0.5
print("Original total rows:", len(df))
print("Rows to drop (>50% missing):", to_drop.sum())
print("Rows kept:", len(df) - to_drop.sum())

df_clean = df.loc[~to_drop].copy()

# fill missing numeric columns with the column mean
numeric_cols = df_clean.select_dtypes(include=["number"]).columns
for col in numeric_cols:
    mean_val = df_clean[col].mean()
    df_clean[col] = df_clean[col].fillna(mean_val)

# round numeric columns to 2 decimals
df_clean[numeric_cols] = df_clean[numeric_cols].round(2)

# boxplot of numeric data AFTER cleaning
plt.figure(figsize=(8, 5))
df_clean[numeric_cols].boxplot()
plt.title("Numeric columns after dropping sparse rows + mean imputation")
plt.tight_layout()
plt.show()

# df_clean.to_csv("movies-cleaned-boxplot.csv", index=False)
# commented out as it's similar to movies-cleaned.csv