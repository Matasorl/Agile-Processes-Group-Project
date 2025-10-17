import sqlite3
import pandas as pd

# Load CSV
df = pd.read_csv("movies.csv")

# Create local database
conn = sqlite3.connect("movies.db")
c = conn.cursor()

# Create table
c.execute('''
CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    movie TEXT,
    genre TEXT,
    runtime TEXT,
    certificate TEXT,
    rating REAL,
    stars TEXT,
    description TEXT,
    votes TEXT,
    director TEXT
)
''')

# Insert data
df.to_sql("movies", conn, if_exists="append", index=False)

conn.commit()
conn.close()
