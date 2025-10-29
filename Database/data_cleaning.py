"""
In this script we pre-process our dataset for further use.

Task: TVMOV-4 Validate and Clean Data
Subtasks:
> Drop rows based on missing value percentage
> Dealing with Missing values
"""

import numpy as np
import pandas as pd

def clean_data(file):
    # Load the original file
    df = pd.read_csv(file)

    # Number of columns
    num_columns = df.shape[1]

    ########################################################
    # Drop rows with >50% missing values
    ########################################################
    # If more than 50% missing values per row - drop this row.
    # Calculate missing values(columns) per row
    missing_values_rows = df.isnull().sum(axis=1)
    print('\nCount missing values per row')
    print(missing_values_rows)

    # Calculate percentage of missing values per row
    missing_values_rows_percent = (missing_values_rows / num_columns) * 100
    print("\nPercentage of missing values per row:")
    print(missing_values_rows_percent.round(2))

    # Drop rows with >50% missing values
    df = df[missing_values_rows_percent < 50]
    print("\nDrop rows with >50% missing values")
    print(df)

    ########################################################
    # Dealing with missing values
    ########################################################
    """
    Missing Value Imputation:
    Replaced missing values in numeric columns with column-wise mean to preserve row count
    and enable complete visualizations in the next epic. 
    """
    df['runtime'] = df['runtime'].fillna(df['runtime'].mean().round(2))
    df['rating'] = df['rating'].fillna(df['rating'].mean().round(2))
    df['votes'] = df['votes'].fillna(df['votes'].mean().round(2))
    print("Filled missing values in 'runtime', 'rating' and 'votes' with average values.")



    # Save processed data to csv file
    df.to_csv('movies-cleaned.csv', index=False)
    print("Cleaned dataset saved to 'movies-cleaned.csv'.")


















def main():
    dataset = "movies-column-dropped.csv"
    clean_data(dataset)






if __name__ == "__main__":
        main()
