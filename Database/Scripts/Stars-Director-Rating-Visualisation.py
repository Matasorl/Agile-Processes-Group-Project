# director_star_analysis.py
# This script analyzes how directors and individual stars affect normalized movie ratings and popularity

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------
# Step 1. Load data from database
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
# Step 3. Select top 50 starts
# -------------------------------
# Split on commas and explode into separate rows
df_stars = df.copy()
df_stars['stars'] = df_stars['stars'].str.split(',')
df_stars = df_stars.explode('stars')
df_stars['stars'] = df_stars['stars'].str.strip()

# Select top 50 most frequent individual stars
top_stars = df_stars['stars'].value_counts().head(50).index
df_stars = df_stars[df_stars['stars'].isin(top_stars)]

# -------------------------------
# Step 4. Aggregate average normalized rating
# -------------------------------
avg_rating_director = df_directors.groupby('director')['rating'].mean().sort_values(ascending=False)
avg_rating_star = df_stars.groupby('stars')['rating'].mean().sort_values(ascending=False)


# Count number of movies per director and star

# Number of movies each top director has
movies_per_director = df_directors.groupby('director').size().sort_values(ascending=False)

# Number of movies each top star has
movies_per_star = df_stars.groupby('stars').size().sort_values(ascending=False)

# -------------------------------
# Step 5. Visualize graphs
# -------------------------------

# Combined: Directors visualizations
# One figure with 3 graphs

fig, axes = plt.subplots(3, 1, figsize=(12, 18))

# 1. Average rating per director
avg_rating_director.plot(kind='bar', color='steelblue', ax=axes[0])
axes[0].set_title("Average Normalized Rating per Director (Top 50)")
axes[0].set_ylabel("Average Normalized Rating")
axes[0].set_xlabel("Director")
axes[0].tick_params(axis='x', rotation=90)

# 2. Number of movies per director
movies_per_director.plot(kind='bar', color='skyblue', ax=axes[1])
axes[1].set_title("Number of Movies per Director (Top 50)")
axes[1].set_ylabel("Number of Movies")
axes[1].set_xlabel("Director")
axes[1].tick_params(axis='x', rotation=90)

# 3. Scatter: average rating vs number of movies
axes[2].scatter(movies_per_director, avg_rating_director, color='steelblue', alpha=0.6)
axes[2].set_title("Director: Average Rating vs Number of Movies")
axes[2].set_xlabel("Number of Movies")
axes[2].set_ylabel("Average Normalized Rating")
axes[2].grid(True, linestyle='--', linewidth=0.5)

plt.tight_layout()
plt.savefig("director_combined_visualizations.png", dpi=300)
plt.close()


# Combined: Star visualizations
# One figure with 3 graphs

fig, axes = plt.subplots(3, 1, figsize=(12, 18))

# 1. Average rating per star
avg_rating_star.plot(kind='bar', color='darkorange', ax=axes[0])
axes[0].set_title("Average Normalized Rating per Star (Top 50)")
axes[0].set_ylabel("Average Normalized Rating")
axes[0].set_xlabel("Star")
axes[0].tick_params(axis='x', rotation=90)

# 2. Number of movies per star
movies_per_star.plot(kind='bar', color='orange', ax=axes[1])
axes[1].set_title("Number of Movies per Star (Top 50)")
axes[1].set_ylabel("Number of Movies")
axes[1].set_xlabel("Star")
axes[1].tick_params(axis='x', rotation=90)

# 3. Scatter: average rating vs number of movies
axes[2].scatter(movies_per_star, avg_rating_star, color='darkorange', alpha=0.6)
axes[2].set_title("Star: Average Rating vs Number of Movies")
axes[2].set_xlabel("Number of Movies")
axes[2].set_ylabel("Average Normalized Rating")
axes[2].grid(True, linestyle='--', linewidth=0.5)

plt.tight_layout()
plt.savefig("star_combined_visualizations.png", dpi=300)
plt.close()


# -------------------------------
# Step 6. Generate key insights
# -------------------------------
top_director = avg_rating_director.head(1)
top_star = avg_rating_star.head(1)

print("=== Insights ===")
print(f"Highest-rated director: {top_director.index[0]} with average normalized rating {top_director.values[0]:.3f}")
print(f"Highest-rated individual star: {top_star.index[0]} with average normalized rating {top_star.values[0]:.3f}")


print("\nVisualizations saved as:")
print("- director_combined_visualizations.png")
print("- star_combined_visualizations.png")

# -------------------------------
# Step 7. Save combined director and star ratings to CSV (with movie counts)
# -------------------------------

# Reset indexes to turn Series into DataFrames
df_directors_avg = avg_rating_director.reset_index()
df_directors_avg.columns = ['director', 'avg_rating_director']

df_stars_avg = avg_rating_star.reset_index()
df_stars_avg.columns = ['star', 'avg_rating_star']

# Add number of movies of each star and director
df_directors_avg['movies_director'] = movies_per_director.values
df_stars_avg['movies_star'] = movies_per_star.values

# Concatenate side by side
combined_df = pd.concat([df_directors_avg, df_stars_avg], axis=1)

# Save to CSV
combined_df.to_csv("avg_ratings_directors_stars.csv", index=False)

print("\nCombined CSV saved as:")
print("- avg_ratings_directors_stars.csv")


