import pandas as pd

# Load CSV
df = pd.read_csv("movies-cleaned.csv")

# Function to clean the stars and director string lists
def clean_list_column(value):
    if not isinstance(value, str):
        return []
    # remove brackets and split by commas
    value = value.strip().strip("[]")
    parts = [p.strip().strip("'").strip('"') for p in value.split(",")]
    # remove empty strings and stray punctuation
    cleaned = [p.strip() for p in parts if p.strip()]
    return cleaned

# Clean both columns
df['stars'] = df['stars'].apply(clean_list_column)
df['director'] = df['director'].apply(clean_list_column)

df['stars'] = df['stars'].apply(lambda x: ", ".join(x))
df['director'] = df['director'].apply(lambda x: ", ".join(x))

# Save cleaned file
df.to_csv("movies_category_cleaned.csv", index=False)

print("Stars and director columns cleaned and saved as movies_category_cleaned.csv.")
