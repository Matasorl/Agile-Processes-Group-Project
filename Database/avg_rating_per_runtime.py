import pandas as pd
import matplotlib.pyplot as plt

# load the CSV
df = pd.read_csv("movies_category_cleaned.csv")

# keep only rows that have both runtime and rating
df = df.dropna(subset=["runtime", "rating"])

# task: average rating for each runtime value
# groupby runtime and compute the mean rating
avg_by_runtime = (
    df.groupby("runtime", as_index=False)["rating"]
      .mean()
      .rename(columns={"rating": "avg_rating"})
      .sort_values("runtime")
)

# for readability - 2 decimal places
avg_by_runtime_2dp = avg_by_runtime.copy()
avg_by_runtime_2dp["runtime"] = avg_by_runtime_2dp["runtime"].round(2)
avg_by_runtime_2dp["avg_rating"] = avg_by_runtime_2dp["avg_rating"].round(2)

# save to a CSV file
# full version
avg_by_runtime.to_csv("avg_rating_by_runtime.csv", index=False)
# 2 decimal points version
avg_by_runtime_2dp.to_csv("avg_rating_by_runtime_2dp.csv", index=False)

# both can be used. full version is better for further analysis. 2 decimal points version is for reports (clean)

# preview in your console
print("Preview (2 d.p.):")
print(avg_by_runtime_2dp.head(10))
