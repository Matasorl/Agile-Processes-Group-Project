import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# pip install scikit-learn

# Load CSV
df = pd.read_csv('movies.csv')

# Remove commas and convert numeric votes; 
df['votes'] = pd.to_numeric(df['votes'].str.replace(',', '', regex=False), errors='coerce')

# Extract numeric value from runtime (e.g., "60 min" -> 60)
df['runtime'] = df['runtime'].str.extract('(\d+)').astype(float)



# Columns to normalize
cols_to_normalize = ['rating', 'votes', 'runtime']

# Initialize scaler
scaler = MinMaxScaler()

# Normalize
df[cols_to_normalize] = scaler.fit_transform(df[cols_to_normalize])

df[cols_to_normalize] = df[cols_to_normalize].round(2)

# Save
df.to_csv('movies-normalized.csv', index=False)

print("Normalized 'rating', 'votes', and 'runtime' columns. Saved to movies-normalized.csv.")
