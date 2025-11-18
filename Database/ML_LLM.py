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
    pass

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





