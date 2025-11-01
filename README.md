# Agile Movie Analytics Project

This project focuses on exploring, cleaning, normalizing and analysing a movie dataset using Python, SQLite and basic chart visualizations. The goal is to demonstrate Agile Data Pipeline work: from raw dataset → preprocessing → database → analysis visualizations.

---

## Project Structure

Agile-Processes-Group-Project-main/
│
├── Database/
│ ├── movies.csv # original raw dataset
│ ├── movies-cleaned.csv # cleaned dataset
│ ├── movies-column-dropped.csv # after dropping unneeded columns
│ ├── movies-normalized.csv # normalized version (2NF/3NF style)
│ ├── movies.db # SQLite database version
│ │
│ ├── data_cleaning.py # initial cleaning operations
│ ├── Column_Drop.py # removes non important columns
│ ├── Normalize.py # normalization logic
│ ├── DB-Script.py # loads CSV into SQLite database
│ ├── Sample_Query.py # sample database queries
│ ├── boxplot_rows_drop.py # outlier / missingness visualization (QA)
│ ├── Genre_Avg_Rating.py # CSV based genre average rating analysis +
│
└──
├── LICENCE
├── README.md

---

## Main Features

- **Data Cleaning**  
  Removing sparse + noisy rows, mean imputation, missingness analysis via boxplots.
- **Data Normalization**  
  Dataset is transformed to a more relational friendly form.

- **SQLite Storage**  
  Movies dataset stored as local SQLite DB.

- **EDA / Insights**  
  Calculate average rating per genre and visualize ranked results.

- **Agile Steps**  
  Each script is small, focused, incremental, testable.

---

## Requirements

- Python 3
- `pip install pandas matplotlib sqlite3` _(sqlite3 included by default with Python)_

---

## How To Run

### 1) Run data cleaning pipeline

```bash
cd Database
python data_cleaning.py
python Column_Drop.py
python Normalize.py
2) Load into SQLite database
bash
Copy code
python DB-Script.py
3) Run sample SQL queries
bash
Copy code
python Sample_Query.py
4) Run Genre Analysis
bash
Copy code
python Genre_Avg_Rating_DB.py --db "./movies.db" \
       --out-csv "./genre_avg_ratings_from_db.csv" \
       --out-png "./genre_avg_ratings_from_db.png"
```
