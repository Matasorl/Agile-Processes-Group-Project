# This script performs ML analyses and integrates LLM OpenAI API

import sqlite3
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
from openai import OpenAI
import traceback
import os
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import ShuffleSplit, cross_validate
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import f1_score, precision_score, recall_score, confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline
from dotenv import load_dotenv

load_dotenv()


#############################################
#  Load data from sqlite
#############################################

def load_movies_from_db(db_path='movies.db'):
    """
    Load movies data from SQLite database.
    If database doesn't exist or table is missing, loads from CSV as fallback.
    """
    # Try to find the database file
    if not os.path.exists(db_path):
        # Try alternative paths
        alternative_paths = [
            'Database/Scripts/movies.db',
            '../movies.db',
            'Database/movies.db'
        ]

        for alt_path in alternative_paths:
            if os.path.exists(alt_path):
                db_path = alt_path
                break
        else:
            print(f"Warning: Database file not found at {db_path}")
            print("Attempting to load from CSV instead...")
            return load_movies_from_csv()

    try:
        conn = sqlite3.connect(db_path)

        # Check if 'movies' table exists
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='movies'")
        if cursor.fetchone() is None:
            print("Warning: 'movies' table not found in database")
            print("Attempting to load from CSV instead...")
            conn.close()
            return load_movies_from_csv()

        df = pd.read_sql_query('SELECT * FROM movies', conn)
        conn.close()
        print(f"Successfully loaded {len(df)} movies from database")
        return df

    except Exception as e:
        print(f"Error loading from database: {e}")
        print("Attempting to load from CSV instead...")
        return load_movies_from_csv()


def load_movies_from_csv(csv_path='movies_category_cleaned.csv'):
    """
    Fallback function to load movies from CSV file.
    """
    # Try to find the CSV file
    if not os.path.exists(csv_path):
        alternative_paths = [
            'Database/movies_category_cleaned.csv',
            'Database/Data/movies_category_cleaned.csv',
            'movies-cleaned.csv',
            'Database/movies-cleaned.csv'
        ]

        for alt_path in alternative_paths:
            if os.path.exists(alt_path):
                csv_path = alt_path
                break
        else:
            raise FileNotFoundError(
                f"Could not find movie data file. Tried:\n"
                f"- {csv_path}\n" +
                "\n".join(f"- {p}" for p in alternative_paths)
            )

    try:
        df = pd.read_csv(csv_path)
        print(f"Successfully loaded {len(df)} movies from CSV: {csv_path}")
        return df
    except Exception as e:
        raise Exception(f"Error loading CSV file {csv_path}: {e}")


#############################################
# Machine Learning analysis tasks
#############################################

def analyze_runtime_rating(df):
    try:
        df_copy = df.copy()
        print("inside analyze_runtime_rating")

        runtime_avg = (
            df_copy.groupby("runtime")["rating"].mean().sort_values(ascending=False)
        )

        label_encoder = LabelEncoder()
        df_copy["runtime_encoded"] = label_encoder.fit_transform(df_copy["runtime"])

        X = df_copy[["runtime_encoded"]]
        y = df_copy["rating"]

        model = LinearRegression()
        model.fit(X, y)

        coefficient = float(model.coef_[0])
        intercept = float(model.intercept_)

        print("Finishing analyze_runtime_rating and returning insight.")

        return {
            "coefficient": coefficient,
            "intercept": intercept,
            "top_runtimes": runtime_avg.head(10).to_dict(),
            "bottom_runtimes": runtime_avg.tail(10).to_dict(),
            "num_runtimes": len(runtime_avg),
            "avg_rating_overall": float(df_copy["rating"].mean())
        }
    except Exception as e:
        return {
            "error": str(e),
            "trace": traceback.format_exc()
        }


def analyze_stars_rating(df):
    try:
        df_copy = df.copy()
        print("inside analyze_stars_rating")
        # Split actor groups into individual actors
        df_copy["stars_list"] = df_copy["stars"].str.split(",")
        df_exploded = df_copy.explode("stars_list")
        df_exploded["stars_list"] = df_exploded["stars_list"].str.strip()

        grouped = df_exploded.groupby("stars_list")

        # Calculate the average rating for each star
        avg_rating_per_star = grouped['rating'].mean().sort_values(ascending=False)

        # Count number of movies per star
        movies_per_star = df_exploded["stars_list"].value_counts()

        # Convert ratings into categories (classification: High vs Low)
        # Example threshold: above/below global average
        avg_rating_overall = df_copy["rating"].mean()  # Overall average movie rating
        rating_class = (grouped["rating"].mean() >= avg_rating_overall).astype(int)

        # Create DataFrame to merge data per actor
        actor_summary = pd.DataFrame({
            "avg_rating": avg_rating_per_star,
            "num_movies": movies_per_star,
            "rating_class": rating_class
        })

        # Add relative frequency (proportion movies_per_star/total_movies)
        # This prevents “Actor X with 2 movies rated 9.5” from unfairly outranking “Actor Y with 200 movies averaging 8.2.”
        total_movies = len(df_exploded)
        actor_summary["relative_freq"] = (actor_summary["num_movies"] / total_movies) * 100

        # Add weighted score
        # This balances rating with reliability
        # For example: Contribution to dataset rating: 0.002%
        actor_summary["weighted_score"] = (actor_summary["avg_rating"] * actor_summary["relative_freq"])

        # fair_actors_sorted = fair_actors.sort_values(by=["avg_rating", "num_movies"], ascending=[False, False])
        # Sort by num_movies (descending)
        actor_summary_sorted = actor_summary.sort_values(by=["num_movies", "avg_rating"], ascending=False)
        # Filter out actors with too few movies (e.g., < 3)
        actor_summary_sorted = actor_summary_sorted[actor_summary_sorted["num_movies"] >= 3]

        # actor_dict = actor_summary_sorted[["avg_rating", "num_movies", "relative_freq", "weighted_score"]].to_dict(orient="index")
        top_n = 50
        bottom_n = 50
        top_actors = actor_summary_sorted.head(top_n).to_dict(orient="index")  # highest-rated actors
        bottom_actors = actor_summary.tail(bottom_n).to_dict(orient="index")

        # Train a model
        models = {
            "DecisionTree": Pipeline(
                [("scaler", MinMaxScaler()), ("clf", DecisionTreeClassifier(max_depth=10, random_state=42))]),
            "LogisticRegression": Pipeline(
                [("scaler", MinMaxScaler()), ("clf", LogisticRegression(max_iter=1000, random_state=42))]),
            "RandomForest": Pipeline(
                [("scaler", MinMaxScaler()), ("clf", RandomForestClassifier(n_estimators=100, random_state=42))]),
            "SVM": Pipeline([("scaler", MinMaxScaler()), ("clf", SVC(kernel="rbf"))])
        }

        # Input X (features)
        X = actor_summary_sorted[["num_movies", "relative_freq", "weighted_score"]]
        # Target class y
        y = actor_summary_sorted["rating_class"]

        shuffle_split = ShuffleSplit(n_splits=10, test_size=0.3, random_state=42)

        results = {}
        for name, pipeline in models.items():
            cv_results = cross_validate(
                pipeline, X, y, cv=shuffle_split,
                scoring=["accuracy", "f1"],
                return_train_score=True
            )
            results[name] = {
                "train_accuracy": np.mean(cv_results["train_accuracy"]),
                "test_accuracy": np.mean(cv_results["test_accuracy"]),
                "f1_score": np.mean(cv_results["test_f1"]),
                "iterations": shuffle_split.get_n_splits(),
                "hyperparameters": pipeline.named_steps["clf"].get_params()
            }

        # Choose best model by test accuracy
        best_model_by_accuracy = max(results.items(), key=lambda x: x[1]["test_accuracy"])

        # Choose best model by F1 score
        best_model_by_f1 = max(results.items(), key=lambda x: x[1]["f1_score"])

        # Convert results dict into tidy DataFrame
        data = []
        for model, metrics in results.items():
            data.append({"Model": model, "Metric": "Test Accuracy", "Score": metrics["test_accuracy"]})
            data.append({"Model": model, "Metric": "F1 Score", "Score": metrics["f1_score"]})

        df_results = pd.DataFrame(data)

        # Model Performance Comparison barchart
        plt.figure(figsize=(10, 8))

        base_palette = sns.color_palette("colorblind")
        custom_palette = [base_palette[0], base_palette[4]]  # 2, 4

        sns.barplot(x="Model", y="Score", hue="Metric", data=df_results, palette=custom_palette)

        plt.title("Model Performance Comparison (Test Accuracy vs F1 Score)", fontsize=14, fontweight='bold')
        plt.ylabel("Score")
        plt.ylim(0.6, 1.05)  # zoom in for clarity
        plt.legend(title='Metric')
        plt.tight_layout()

        # Save diagram into Images folder
        plt.savefig("../Images/model_performance_comparison.png", dpi=300)

        # Top 50 Actors by Average Rating (Above vs Below Global Average)
        # Show the highest-rated actors (filtered for enough movies to be reliable)
        # Visualisation shows how ratings vary across different actors and whether their
        # average rating is above or below the global average.
        # Select top 50 actors by average rating
        top_actors_df = actor_summary_sorted.head(50).reset_index()
        top_actors_df = top_actors_df.sort_values(by="avg_rating", ascending=False)

        # Add a flag for above/below average
        top_actors_df["above_avg"] = top_actors_df["avg_rating"] > avg_rating_overall

        plt.figure(figsize=(15, 10))
        # Use one color for above, another for below
        sns.barplot(x="avg_rating", y="stars_list", data=top_actors_df, hue="above_avg", dodge=False,
                    palette={True: "#1f77b4", False: "#4fa8dc"})
        # Add vertical line for global average rating
        plt.axvline(avg_rating_overall, color="black", linestyle="--", linewidth=2,
                    label=f"Global Avg: {avg_rating_overall:.2f}")
        plt.title("Top 50 Actors by Average Rating (Above vs Below Global Average)", fontsize=14, fontweight='bold')
        plt.xlabel("Average Rating")
        plt.ylabel("Actor")
        plt.legend(title="Above Global Avg", loc="center right")
        plt.tight_layout()

        # Save diagram into Images folder
        plt.savefig("../Images/Top 50 Actors by Average Rating (Above vs Below Global Average).png", dpi=300)

        # Scatterplot: Number of Movies vs Average Rating
        plt.figure(figsize=(10, 6))
        sns.scatterplot(x="num_movies", y="avg_rating", data=actor_summary_sorted, hue="num_movies", size="num_movies",
                        palette="Blues",
                        sizes=(20, 200))  # hue-color intensity by number of movies, # larger points for more movies
        plt.title("Actor Ratings vs Number of Movies", fontsize=14, fontweight="bold")
        # Add horizontal line for global average rating
        plt.axhline(avg_rating_overall, color="black", linestyle="--", linewidth=2,
                    label=f"Global Avg: {avg_rating_overall:.2f}")
        plt.xlabel("Number of Movies")
        plt.ylabel("Average Rating")
        plt.legend(title="Global Average", loc="lower right")
        plt.tight_layout()
        # Save scatterplot into Images folder
        plt.savefig("../Images/Actor Ratings vs Number of Movies(Scatterplot).png", dpi=300)

        # plt.show()
        print("Finishing analyze_stars_rating and returning insight.")
        # return a dictionary containing key insights
        return {
            "top_actors": top_actors,  # Top 50 actors by num_movies
            "bottom_actors": bottom_actors,  # Bottom 50 actors by num_movies
            "total_movies": int(total_movies),  # Total number of movies
            "num_actors": len(actor_summary_sorted),  # Total actors considered
            "avg_rating_overall": float(avg_rating_overall),  # Global average rating baseline
            "best_model": {
                "by_accuracy": best_model_by_accuracy[0],
                "accuracy_score": best_model_by_accuracy[1]["test_accuracy"],
                "by_f1": best_model_by_f1[0],
                "f1_score": best_model_by_f1[1]["f1_score"]
            }
        }


    except Exception as e:
        return {
            "error": str(e),
            "trace": traceback.format_exc()
        }


def analyze_director_rating(df):
    try:
        # Make a copy of the dataframe to avoid modifying the original data
        df_copy = df.copy()
        print("Inside analyze_director_rating.")

        # Calculate the average rating for each director
        # This groups the dataframe by the "director" column and computes the mean of the "rating" column
        # Sorting descending so the highest-rated directors are first
        director_avg = (
            df_copy.groupby("director")["rating"]
            .mean()
            .sort_values(ascending=False)
        )

        # Encode director names as numeric values for regression
        # LabelEncoder converts categorical text labels into numbers (0,1,2,…)
        # This allows Linear Regression to use the director as an input feature
        label_encoder = LabelEncoder()
        df_copy["director_encoded"] = label_encoder.fit_transform(df_copy["director"])

        # Define the input (X) and target (y) for regression
        X = df_copy[["director_encoded"]]  # Encoded director names as input
        y = df_copy["rating"]  # Movie ratings as target

        # Create and fit a simple linear regression model
        # This will try to find a linear relationship between director encoding and movie rating
        model = LinearRegression()
        model.fit(X, y)

        # Extract the model's coefficient and intercept
        # Coefficient indicates the "slope" (how much rating changes per unit of encoded director)
        # Intercept indicates the baseline rating when director_encoded=0
        coefficient = float(model.coef_[0])
        intercept = float(model.intercept_)
        print("Finishing analyze_director_rating and returning insights from it.")
        # Return a dictionary containing key insights:
        return {
            "coefficient": coefficient,  # Trend of ratings vs. director encoding
            "intercept": intercept,  # Baseline rating
            "top_directors": director_avg.head(10).to_dict(),  # Top 10 directors by average rating
            "bottom_directors": director_avg.tail(10).to_dict(),  # Bottom 10 directors by average rating
            "num_directors": len(director_avg),  # Total number of unique directors
            "avg_rating_overall": float(df_copy["rating"].mean())  # Overall average movie rating
        }

    except Exception as e:
        # Catch any errors during processing and return the error message and traceback
        return {
            "error": str(e),
            "trace": traceback.format_exc()
        }


def extract_all_insights(df):
    return {
        "runtime_rating": analyze_runtime_rating(df),
        "stars_rating": analyze_stars_rating(df),
        "director_rating": analyze_director_rating(df)
    }


#############################################
# LLM client (OpenAI)
#############################################

def call_llm(insights: dict, audience_preferences=None):
    print("Inside def call_llm(insights: dict, audience_preferences=None):")
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    # Format insights into a readable string
    runtime_insights = insights.get("runtime_rating", {})
    stars_insights = insights.get("stars_rating", {})
    director_insights = insights.get("director_rating", {})

    # Build audience preference context
    audience_context = ""
    if audience_preferences:
        audience_context = f"\nAudience Preferences: {audience_preferences}"

    prompt = f"""
    You are an AI data analyst for a movie intelligence platform.

    STAKEHOLDERS:
    - General Audience: individuals wants easy explanations and movie/TV recommendations(genre, runtime, stars, directors, popularity).
    - Streaming Platforms: companies that use insights to improve recommendation systems.
    - Industry Stakeholders:  need data-driven behaviour patterns, correlations, and predictions for content success.

    Analysis Results:
    - Runtime vs Rating: {runtime_insights}
    - Stars vs Rating: {stars_insights}
    - Directors vs Rating: {director_insights}
    {audience_context}

    TASK: 
    1. For General Audience: Provide clear, user-friendly recommendations of movies/TV shows that align with preferences.
    2. For Streaming Platforms: Suggest how these insights can improve recommendation systems.
    3. For Industry Stakeholders: Deliver data-driven insights to understand audience behaviour, predict title success, and inform content creation.
    4. Generate a clear, user-friendly summary for both audiences and stakeholders. 
    """
    print("Creating response...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful data analyst."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    df = load_movies_from_db()
    print('Getting insights...')
    insights = extract_all_insights(df)
    print("Creating summary...")
    summary = call_llm(insights)
    print(summary)






