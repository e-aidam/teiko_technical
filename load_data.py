import sqlite3

import pandas as pd

# Load data from CSV
df = pd.read_csv("cell-count.csv")

# Create database connection
conn = sqlite3.connect("cell-data.db")


# Part 1: Data Management
# Create table for subjects
subjects = df[["subject", "project", "condition", "age", "sex", "treatment", "response"]]
subjects.drop_duplicates().to_sql("subjects", conn, if_exists="replace", index=False)

# Create table for samples
samples = df[["sample", "subject", "sample_type", "time_from_treatment_start"]]
samples.to_sql("samples", conn, if_exists="replace", index=False)

# Create table for cell counts
counts = df.melt(
    id_vars="sample",
    value_vars=["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"],
    var_name="population",
    value_name="count",
)
counts.to_sql("cell_counts", conn, if_exists="replace", index=False)

conn.close()
