import sqlite3

# Connect to the local database
conn = sqlite3.connect("movies.db")
c = conn.cursor()

# Select movies with rating > 8
c.execute("SELECT movie, rating FROM movies WHERE rating > 8")
for row in c.fetchall():
    print(row)

# Count total movies
c.execute("SELECT COUNT(*) FROM movies")
print("Total movies:", c.fetchone()[0])

# Close the connection
conn.close()
