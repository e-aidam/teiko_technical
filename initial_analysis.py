import sqlite3

import pandas as pd

# Load cell count data from database
conn = sqlite3.connect("cell-data.db")
df = pd.read_sql("SELECT * FROM cell_counts", conn)


# Part 2: Initial Analysis - Data Overview
# Sum counts across all five sample populations
df["total_count"] = df.groupby("sample")["count"].transform("sum")

# Compute relative frequencies
df["percentage"] = df["count"] / df["total_count"] * 100

# Create summary table
summary = df[["sample", "total_count", "population", "count", "percentage"]].sort_values(["sample", "population"])
print(summary)

# Save summary table to the database and a csv file
summary.to_sql("summary_table", conn, if_exists="replace", index=False)
summary.to_csv("summary_table.csv", index=False)
conn.close()
