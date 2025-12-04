import sqlite3
import os

# get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# construct the path to the database file (2 levels up from script location)
db_path = os.path.join(script_dir, "..", "..", "movies.db")
db_path = os.path.abspath(db_path)  # Normalize the path

# Connect to the local database
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Select movies with rating > 8
c.execute("SELECT movie, rating FROM movies WHERE rating > 8")
# sample query for testing new code after cleaning
c.execute("SELECT movie, rating FROM movies LIMIT 10")

for row in c.fetchall():
    print(row)

# Count total movies
c.execute("SELECT COUNT(*) FROM movies")
print("Total movies:", c.fetchone()[0])

# Close the connection
conn.close()
