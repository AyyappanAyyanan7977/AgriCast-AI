# Machine-learning evaluation protocol

## Current implementation

The baseline training function drops rows with missing target values, converts the target to numeric, checks minimum row count and feature presence, builds a scikit-learn preprocessing/regression pipeline, and reports MAE, RMSE, and R² on a random holdout split. The report stores estimator, target, row counts, split settings, and a model version.

## Limitations

- The bundled CSV is synthetic and the bundled evaluation report is illustrative only.
- A random split can leak information when records share farms, locations, seasons, or time periods.
- The current pipeline does not automatically infer causal leakage from feature names or data semantics.
- Metrics are not meaningful unless the dataset's target units, source, sampling, and intended prediction time are documented.

## Before making a real-world claim

1. Record source URL/owner, license, collection period, geography, target definition, and units.
2. Check duplicates, missingness, outliers, unit consistency, target distribution, and label quality.
3. Define the prediction moment and remove fields that would only be known after that moment.
4. Choose a split matching intended use: time-based for future seasons, group-based for unseen farms/regions, or a justified random split for independent samples.
5. Compare at least one simple baseline (e.g. mean predictor or Ridge) with tree-based candidates.
6. Report MAE, RMSE, R², test sample count, split protocol, and segment-level errors where sample size permits.
7. Repeat with fixed seeds or cross-validation when appropriate; inspect residuals and uncertainty.
8. Keep a versioned, untouched evaluation set and rerun the tests after changes.

Do not present the synthetic demonstration model's metrics as evidence of agronomic accuracy.
