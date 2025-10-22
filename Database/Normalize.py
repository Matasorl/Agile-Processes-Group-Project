import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# Load CSV
df = pd.read_csv('movies.csv')

# Remove commas and convert numeric votes; 
df['votes'] = pd.to_numeric(df['votes'].str.replace(',', '', regex=False), errors='coerce')

# Columns to normalize
cols_to_normalize = ['rating', 'votes']

# Initialize scaler
scaler = MinMaxScaler()

# Normalize
df[cols_to_normalize] = scaler.fit_transform(df[cols_to_normalize])

df[cols_to_normalize] = df[cols_to_normalize].round(2)

# Save
df.to_csv('movies-normalized.csv', index=False)

print("Normalized 'rating' and 'votes' columns. Saved to movies_normalized.csv.")
