
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# -------------------------------
# Step 1. Load data
# -------------------------------
conn = sqlite3.connect("movies.db")
df = pd.read_sql_query("SELECT movie, director, stars, rating FROM movies", conn)
conn.close()

# -------------------------------
# Step 2. Select top 50 directors
# -------------------------------
top_directors = df['director'].value_counts().head(50).index
df_directors = df[df['director'].isin(top_directors)]

# -------------------------------
# Step 3. Select top 50 stars
# -------------------------------
df_stars = df.copy()
df_stars['stars'] = df_stars['stars'].str.split(',')
df_stars = df_stars.explode('stars')
df_stars['stars'] = df_stars['stars'].str.strip()

top_stars = df_stars['stars'].value_counts().head(50).index
df_stars = df_stars[df_stars['stars'].isin(top_stars)]

# -------------------------------
# Step 4. Aggregations
# -------------------------------
avg_rating_director = df_directors.groupby('director')['rating'].mean().sort_values(ascending=False)
avg_rating_star = df_stars.groupby('stars')['rating'].mean().sort_values(ascending=False)

movies_per_director = df_directors.groupby('director').size().sort_values(ascending=False)
movies_per_star = df_stars.groupby('stars').size().sort_values(ascending=False)

# -------------------------------
# Step 5. Visualizations 
# -------------------------------

# -------------------------------
# Combined Director Plots
# -------------------------------
# Boxplot: Shows rating distribution per director (median, spread, consistency)
# Scatter: Shows relationship between number of movies (X) and average rating (Y)

fig, axes = plt.subplots(2, 1, figsize=(16, 12))

# 1. Boxplot of ratings per director
sns.boxplot(
    data=df_directors,
    x="director",
    y="rating",
    showfliers=False,
    ax=axes[0]
)
plt.setp(axes[0].get_xticklabels(), rotation=90)
axes[0].set_title("Director Rating Distributions (Box Plot)")
axes[0].set_ylabel("Normalized Rating")
axes[0].set_xlabel("Director")

# 2. Scatter plot of avg rating vs movie count
axes[1].scatter(
    movies_per_director,
    avg_rating_director,
    alpha=0.7,
    color="royalblue"
)
axes[1].set_title("Directors: Avg Rating vs Movie Count (Scatter Plot)")
axes[1].set_xlabel("Number of Movies")
axes[1].set_ylabel("Average Rating")
axes[1].grid(True, linestyle="--", alpha=0.5)

plt.tight_layout()
plt.savefig("directors_combined.png")
plt.close()


# -------------------------------
# Combined Star Plots
# -------------------------------
# Boxplot: Shows rating distribution per star (median, spread, consistency)
# Scatter: Shows relationship between number of movies (X) and average rating (Y)

fig, axes = plt.subplots(2, 1, figsize=(16, 12))

# 1. Boxplot of ratings per star
sns.boxplot(
    data=df_stars,
    x="stars",
    y="rating",
    showfliers=False,
    ax=axes[0]
)
plt.setp(axes[0].get_xticklabels(), rotation=90) 
axes[0].set_title("Star Rating Distributions (Box Plot)")
axes[0].set_ylabel("Normalized Rating")
axes[0].set_xlabel("Star")

# 2. Scatter plot of avg rating vs movie count
axes[1].scatter(
    movies_per_star,
    avg_rating_star,
    alpha=0.7,
    color="darkorange"
)
axes[1].set_title("Stars: Avg Rating vs Movie Count (Scatter Plot)")
axes[1].set_xlabel("Number of Movies")
axes[1].set_ylabel("Average Rating")
axes[1].grid(True, linestyle="--", alpha=0.5)

plt.tight_layout()
plt.savefig("stars_combined.png")
plt.close()






# -------------------------------
# Step 6. Insights
# -------------------------------
top_director = avg_rating_director.head(1)
top_star = avg_rating_star.head(1)

print("=== Insights ===")
print(f"Highest-rated director: {top_director.index[0]} with average normalized rating {top_director.values[0]:.3f}")
print(f"Highest-rated star: {top_star.index[0]} with average normalized rating {top_star.values[0]:.3f}")

print("\nNew visualizations saved:")
print("- directors_combined.png  # Boxplot + Scatter Plot for directors")
print("- stars_combined.png      # Boxplot + Scatter Plot for stars")



# -------------------------------
# Step 7. Save CSV
# -------------------------------
df_directors_avg = avg_rating_director.reset_index()
df_directors_avg.columns = ['director', 'avg_rating_director']
df_directors_avg['movies_director'] = movies_per_director.values

df_stars_avg = avg_rating_star.reset_index()
df_stars_avg.columns = ['star', 'avg_rating_star']
df_stars_avg['movies_star'] = movies_per_star.values

combined_df = pd.concat([df_directors_avg, df_stars_avg], axis=1)
combined_df.to_csv("avg_ratings_directors_stars.csv", index=False)

print("\nCombined CSV saved as avg_ratings_directors_stars.csv")
