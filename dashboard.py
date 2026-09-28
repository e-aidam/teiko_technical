import sqlite3

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

conn = sqlite3.connect("cell-data.db")

st.title("Miraclib Clinical Trial Dashboard")

# Part 2
st.header("Part 2: Cell Population Frequencies")
summary = pd.read_sql("SELECT * FROM summary_table", conn)
sample = st.selectbox("Choose a sample", summary["sample"].unique())
st.dataframe(summary[summary["sample"] == sample], hide_index=True)

# Part 3
st.header("Part 3: Responders vs Non-responders")
st.write("Melanoma patients treated with miraclib, PBMC samples only.")

# Boxplot of responders vs non-responders for each population
freqs = pd.read_sql("""
    SELECT t.population, t.percentage, sub.response
    FROM summary_table t
    JOIN samples s ON t.sample = s.sample
    JOIN subjects sub ON s.subject = sub.subject
    WHERE sub.condition = 'melanoma'
      AND sub.treatment = 'miraclib'
      AND s.sample_type = 'PBMC'
""", conn)
populations = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]
fig, axes = plt.subplots(1, 5, figsize=(20, 5))
for ax, population in zip(axes, populations):
    pop_df = freqs[freqs["population"] == population]
    responders = pop_df[pop_df["response"] == "yes"]["percentage"]
    non_responders = pop_df[pop_df["response"] == "no"]["percentage"]
    ax.boxplot([responders, non_responders], tick_labels=["Responders", "Non-responders"])
    ax.set_title(population)
    ax.set_ylabel("Relative frequency (%)")
plt.tight_layout()
st.pyplot(fig)

st.subheader("T-test with Bonferroni correction")
st.dataframe(pd.read_sql("SELECT * FROM statistical_results", conn), hide_index=True)
st.subheader("Predicting response, adjusted for age and sex (test ROC AUC)")
st.dataframe(pd.read_sql("SELECT * FROM model_results", conn), hide_index=True)
st.subheader("Feature importance")
st.dataframe(pd.read_sql("SELECT * FROM feature_importance", conn), hide_index=True)

# Part 4
st.header("Part 4: Baseline Melanoma PBMC Samples on Miraclib")
col1, col2, col3 = st.columns(3)
col1.write("Samples per project")
col1.dataframe(pd.read_sql("SELECT * FROM baseline_project_counts", conn), hide_index=True)
col2.write("Subjects by response")
col2.dataframe(pd.read_sql("SELECT * FROM baseline_response_counts", conn), hide_index=True)
col3.write("Subjects by sex")
col3.dataframe(pd.read_sql("SELECT * FROM baseline_sex_counts", conn), hide_index=True)

avg_b_cell = pd.read_sql("SELECT * FROM avg_b_cell", conn)["avg_b_cell"][0]
st.metric("Average B cells (melanoma male responders at time 0)", f"{avg_b_cell:.2f}")

conn.close()
