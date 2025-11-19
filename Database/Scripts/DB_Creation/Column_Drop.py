import pandas as pd

# Read the CSV file
df = pd.read_csv('movies-normalized.csv')

# Calculate the threshold for non-missing values
threshold = len(df) * 0.5

# Identify columns to drop
cols_to_drop = df.columns[df.isna().sum() > len(df) - threshold]

# Drop them
df = df.drop(columns=cols_to_drop)

# Print dropped columns
print("Dropped columns:", list(cols_to_drop))

# Save the cleaned DataFrame
df.to_csv('movies-column-dropped.csv', index=False)
