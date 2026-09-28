import sqlite3

import pandas as pd

conn = sqlite3.connect("cell-data.db")


# Part 4: Data Subset Analysis
# Melanoma PBMC samples at baseline from patients treated with miraclib
baseline = pd.read_sql("""
    SELECT s.sample, sub.subject, sub.project, sub.response, sub.sex
    FROM samples s
    JOIN subjects sub ON s.subject = sub.subject
    WHERE sub.condition = 'melanoma'
      AND sub.treatment = 'miraclib'
      AND s.sample_type = 'PBMC'
      AND s.time_from_treatment_start = 0
""", conn)
print(baseline)

# Number of samples from each project
project_counts = baseline.groupby("project")["sample"].count().reset_index(name="samples")
print(project_counts)

# Number of responder and non-responder subjects
response_counts = baseline.groupby("response")["subject"].nunique().reset_index(name="subjects")
print(response_counts)

# Number of male and female subjects
sex_counts = baseline.groupby("sex")["subject"].nunique().reset_index(name="subjects")
print(sex_counts)

# Average B cells for melanoma male responders at time 0 (all sample and treatment types)
avg_b_cell = pd.read_sql("""
    SELECT AVG(c.count) AS avg_b_cell
    FROM cell_counts c
    JOIN samples s ON c.sample = s.sample
    JOIN subjects sub ON s.subject = sub.subject
    WHERE c.population = 'b_cell'
      AND sub.condition = 'melanoma'
      AND sub.sex = 'M'
      AND sub.response = 'yes'
      AND s.time_from_treatment_start = 0
""", conn)
avg_b_cell["avg_b_cell"] = avg_b_cell["avg_b_cell"].round(2)
print(f"Average B cells: {avg_b_cell['avg_b_cell'][0]:.2f}")

# Save results to the database
baseline.to_sql("baseline_samples", conn, if_exists="replace", index=False)
project_counts.to_sql("baseline_project_counts", conn, if_exists="replace", index=False)
response_counts.to_sql("baseline_response_counts", conn, if_exists="replace", index=False)
sex_counts.to_sql("baseline_sex_counts", conn, if_exists="replace", index=False)
avg_b_cell.to_sql("avg_b_cell", conn, if_exists="replace", index=False)
conn.close()
