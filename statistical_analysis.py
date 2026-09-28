import sqlite3

import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import ttest_ind
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Load melanoma PBMC samples from patients treated with miraclib
conn = sqlite3.connect("cell-data.db")
df = pd.read_sql("""
    SELECT c.sample, c.population, c.count, sub.subject, sub.response, sub.age, sub.sex
    FROM cell_counts c
    JOIN samples s ON c.sample = s.sample
    JOIN subjects sub ON s.subject = sub.subject
    WHERE sub.condition = 'melanoma'
      AND sub.treatment = 'miraclib'
      AND s.sample_type = 'PBMC'
""", conn)


# Part 3: Statistical Analysis
# Compute relative frequencies
df["total_count"] = df.groupby("sample")["count"].transform("sum")
df["percentage"] = df["count"] / df["total_count"] * 100

populations = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]

# Boxplot of responders vs non-responders for each population
fig, axes = plt.subplots(1, 5, figsize=(20, 5))
for ax, population in zip(axes, populations):
    pop_df = df[df["population"] == population]
    responders = pop_df[pop_df["response"] == "yes"]["percentage"]
    non_responders = pop_df[pop_df["response"] == "no"]["percentage"]
    ax.boxplot([responders, non_responders], tick_labels=["Responders", "Non-responders"])
    ax.set_title(population)
    ax.set_ylabel("Relative frequency (%)")
fig.suptitle("Cell Population Relative Frequencies: Responders vs Non-responders (Melanoma, Miraclib, PBMC)")
plt.tight_layout()
plt.savefig("boxplot.pdf")

# t-test for each population
results = []
for population in populations:
    pop_df = df[df["population"] == population]
    responders = pop_df[pop_df["response"] == "yes"]["percentage"]
    non_responders = pop_df[pop_df["response"] == "no"]["percentage"]
    stat, p = ttest_ind(responders, non_responders, equal_var=False)
    results.append([population, responders.mean(), non_responders.mean(), p])

results = pd.DataFrame(results, columns=["population", "mean_responders", "mean_non_responders", "p_value"])

# Bonferroni correction for testing five populations
results["p_adjusted"] = (results["p_value"] * len(populations)).clip(upper=1)
results["significant"] = results["p_adjusted"] < 0.05

print(results.to_string(index=False))
print("Significant populations:", list(results[results["significant"]]["population"]))
results.to_sql("statistical_results", conn, if_exists="replace", index=False)


# Predict response from the five population frequencies, adjusted for age and sex
wide = df.pivot_table(index=["sample", "subject", "response", "age", "sex"], columns="population", values="percentage").reset_index()
wide["responded"] = (wide["response"] == "yes").astype(int)
wide["male"] = (wide["sex"] == "M").astype(int)
features = populations + ["age", "male"]

# Split by subject so samples from one patient are not in both train and test sets
subjects = list(wide["subject"].unique())
train_subjects, test_subjects = train_test_split(subjects, test_size=0.25, random_state=0)
train = wide[wide["subject"].isin(train_subjects)]
test = wide[wide["subject"].isin(test_subjects)]

X_train, y_train = train[features], train["responded"]
X_test, y_test = test[features], test["responded"]

# Logistic regression (features are standardized so coefficients can be compared)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

log_reg = LogisticRegression(max_iter=1000)
log_reg.fit(X_train_scaled, y_train)
log_reg_auc = roc_auc_score(y_test, log_reg.predict_proba(X_test_scaled)[:, 1])
print(f"\nLogistic regression test AUC: {log_reg_auc:.3f}")

# Random forest
forest = RandomForestClassifier(n_estimators=500, random_state=0)
forest.fit(X_train, y_train)
forest_auc = roc_auc_score(y_test, forest.predict_proba(X_test)[:, 1])
print(f"Random forest test AUC: {forest_auc:.3f}")

# Feature importance from both models
importance = pd.DataFrame({
    "feature": features,
    "logistic_coefficient": log_reg.coef_[0],
    "random_forest_importance": forest.feature_importances_,
})
importance = importance.sort_values("random_forest_importance", ascending=False)
print("\nFeature importance:")
print(importance.to_string(index=False))

# Save model results to the database
models = pd.DataFrame({"model": ["Logistic regression", "Random forest"], "test_auc": [log_reg_auc, forest_auc]})
models.to_sql("model_results", conn, if_exists="replace", index=False)
importance.to_sql("feature_importance", conn, if_exists="replace", index=False)
conn.close()
