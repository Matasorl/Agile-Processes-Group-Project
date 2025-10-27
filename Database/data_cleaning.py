"""
In this script we pre-process our dataset for further use.

Tasks:

> Normalize columns with numerical values
> Drop rows based on missing percentage
> Drop column(s) based on missing percentage
> Dealing with Missing values


Notes:
We want to visualize:
1.  Genre vs Rating Distribution
2.  Rating vs Runtime Distribution
3.  Director & Stars Rating Correlation

"""

import numpy as np
import pandas as pd
def clean_data(file):
    # Load the original file
    df = pd.read_csv(file)

    # Number of columns
    num_columns = df.shape[1]

    ##########################################################################################
    # Normalize columns with existing NON-NUMERICAL values in a numerical column
    ##########################################################################################
    # get list of columns
    print(df.columns)

    # votes column
    df['votes'] = df['votes'].astype(str).str.replace(',', '')
    df['votes'] = pd.to_numeric(df['votes'], errors='coerce')  # invalid parsing will be set as NaN.
    print(df['votes'])

    # rating column
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')


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


    #############################################
    # Drop columns with >50% missing values
    #############################################
    # Count missing values per column
    missing_values_cols = df.isnull().sum()
    print("\nCount missing values per column")
    print(missing_values_cols)

    # Calculate percentage of missing values per column
    missing_values_cols_perc = (missing_values_cols / len(df)) * 100
    print("\nCalculate percentage of missing values per column")
    print(missing_values_cols_perc.round(2))

    # Drop columns with >50% missing values
    df = df.loc[:, missing_values_cols_perc < 50]
    print("\nDataFrame after dropping columns with >50% missing values:")
    print(df)





    # Save cleaned data to csv file
    df.to_csv('movies-cleaned.csv', index=False)
    print("Cleaned data successfully saved to 'movies-cleaned.csv'.")


















def main():
    dataset = "imdb-original.csv"
    clean_data(dataset)






if __name__ == "__main__":
        main()
