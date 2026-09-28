# teiko_technical

Teiko Bioinformatics Engineer take-home assignment.

## Run Instructions

Run these three commands from the repository root:

```bash
make setup
make analysis
make dashboard
```

After running make dashboard, the dashboard with the results of the analyses will be available at: http://localhost:8501.

## Database

The database has three main tables:

- subjects: one row per patient (project, condition, age, sex, treatment, response)
- samples: one row per sample (patient, sample type, days since treatment started)
- cell_counts: one row per sample and cell type, with the cell count

Patient details are stored once in subjects and not repeated for every sample.

## Results

### Part 3. Statistical Analysis

#### Analysis

- For each cell type, I compared the mean relative frequency between responders and non-responders with a t-test. A simple t-test  doesn't assume the two groups have equal variance. With ~1,000 samples per group, the sample means are close to normal even though the frequencies are slightly skewed.
- Testing five cell types at p < 0.05 raises the chance of at least one false positive to about 23%. Bonferroni correction (multiply each p-value by 5) was applied to keep the chance of a false positive at  5%.
- To test whether cell frequencies can predict response, I trained a logistic regression and a random forest on the five cell frequencies, adjusted for age and sex. Patients were split 75/25 into train and test sets.

#### Results

- Only CD4 T cells differ significantly (p = 0.005, adjusted p = 0.025). Responders average 30.5% CD4 T cells vs 29.9% for non-responders. The difference is real but small, and the two groups overlap heavily in the boxplot.
- Both models scored close to chance (test AUC 0.50 for logistic regression and 0.56 for the random forest, where 0.5 is random guessing).
- Feature importance:
  - Logistic regression: features were standardized so the coefficients can be compared. Sex (0.17) and age (0.14) have the largest coefficients. Among cell types, CD4 T cells have the largest (0.08), which matches the t-test.
  - Random forest: the five cell types score about the same (0.16-0.17), so no single one stands out. Age is slightly lower (0.14). Sex is lowest (0.02), because a yes/no feature gives the forest few ways to split.

#### Conclusion

- CD4 T cells differ slightly between responders and non-responders. But these cell frequencies, even with age and sex added, can't significantly predict response to miraclib.

### Part 4: Data Subset Analysis

- Samples per project: prj1 = 384, prj2 = 0, prj3 = 272. Project 2 has no PBMC samples.
- Subjects by response: 331 responders, 325 non-responders
- Subjects by sex: 344 male, 312 female
- Average B cells for melanoma male responders at time 0: 10206.15
