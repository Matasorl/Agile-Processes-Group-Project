# This script performs ML analyses and integrates LLM OpenAI API


import sqlite3
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
from openai import OpenAI
import traceback


#############################################
#  Load data from sqlite
#############################################

def load_movies_from_db(db_path='movies.db'):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query('SELECT * FROM movies', conn)
    conn.close()
    return df

#############################################
# Machine Learning analysis tasks
#############################################

def analyze_runtime_rating(df):
    pass

def analyze_stars_rating(df):
    pass

def analyze_director_rating(df):
    try:
        # Make a copy of the dataframe to avoid modifying the original data
        df_copy = df.copy()

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
        y = df_copy["rating"]              # Movie ratings as target

        # Create and fit a simple linear regression model
        # This will try to find a linear relationship between director encoding and movie rating
        model = LinearRegression()
        model.fit(X, y)

        # Extract the model's coefficient and intercept
        # Coefficient indicates the "slope" (how much rating changes per unit of encoded director)
        # Intercept indicates the baseline rating when director_encoded=0
        coefficient = float(model.coef_[0])
        intercept = float(model.intercept_)

        # Return a dictionary containing key insights:
        return {
            "coefficient": coefficient,                       # Trend of ratings vs. director encoding
            "intercept": intercept,                           # Baseline rating
            "top_directors": director_avg.head(10).to_dict(),  # Top 10 directors by average rating
            "bottom_directors": director_avg.tail(10).to_dict(), # Bottom 10 directors by average rating
            "num_directors": len(director_avg),              # Total number of unique directors
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
    client = OpenAI()

    # Format insights into a readable string
    runtime_insights = insights.get("runtime_rating", {})
    stars_insights = insights.get("stars_rating", {})
    director_insights = insights.get("director_rating", {})

    prompt = f"""
You are an AI data analyst for a movie intelligence platform.

STAKEHOLDERS:
- General Audience -> wants easy explanations and movie/TV recommendations.
- Industry Stakeholders -> want data-driven behaviour patterns and correlations.

Analysis Results:
- Runtime vs Rating: {runtime_insights}
- Stars vs Rating: {stars_insights}
- Directors vs Rating: {director_insights}

Please generate a clear, user-friendly summary for both audiences and stakeholders. 
"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful data analyst."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    df = load_movies_from_db()
    insights = extract_all_insights(df)
    summary = call_llm(insights)
    print(summary)





