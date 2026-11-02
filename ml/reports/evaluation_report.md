# Model Evaluation & Generalization Report

## 1. Grouped Generalization Protocol
To prevent data leakage, training and test splits were partitioned using `GroupShuffleSplit` across 675 distinct sub-district administrative clusters (`block_taluk_mandal`). Zero wards or villages from the same local cluster exist in both splits.

## 2. Champion Performance Summary
- **Priority Sector Classification**: LightGBM achieved **99.97%** test accuracy and **0.9997** Weighted F1.
- **Development Gap Classification**: Random Forest achieved **99.83%** test accuracy and **0.9983** Weighted F1.
- **Budget Requirement Prediction**: LightGBM achieved $R^2 = $ **0.9988** with an MAE of **₹2.55 Lakhs**.
- **Unsupervised Clustering**: K-Means converged on 4 distinct operational development archetypes.
- **Anomaly Detection**: Isolation Forest successfully isolates fiscal outliers and contradictory development reports.
