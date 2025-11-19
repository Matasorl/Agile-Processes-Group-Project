# this script creates a database schema and stores the processed data

import sqlite3
import pandas as pd

# load the cleaned csv
df = pd.read_csv("movies_category_cleaned.csv")

# create sqlite database
conn = sqlite3.connect("movies.db")
cur = conn.cursor()

# create schema
cur.execute("""
CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    movie TEXT NOT NULL,
    genre TEXT,
    runtime REAL,
    rating REAL,
    stars TEXT,
    description TEXT,
    votes REAL,
    director TEXT
)
""")

# clears the table before inserting new data to avoid duplicates
cur.execute("DELETE FROM movies")

# insert data
# pandas maps to existing columns by name
df.to_sql("movies", conn, if_exists="append", index=False)

conn.commit()
conn.close()

print("Loaded", len(df), "rows into movies.db")
