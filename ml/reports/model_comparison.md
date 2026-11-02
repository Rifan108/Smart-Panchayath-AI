# Model Comparison Report: Smart Panchayat AI

Evaluation across CatBoost, XGBoost, LightGBM, and Random Forest on 11,663 Unseen Grouped Test Records.

## Task 1: Priority Sector Multi-class Classification

| Model | Accuracy | F1-Macro | F1-Weighted | Precision-Macro | Recall-Macro | Training Time (s) |
|---|---|---|---|---|---|---|
| **Random Forest** | 99.94% | 0.9992 | 0.9994 | 0.999 | 0.9994 | 1.94s |
| **LightGBM** | 99.97% | 0.9995 | 0.9997 | 0.9996 | 0.9995 | 2.2s |
| **XGBoost** | 99.94% | 0.9992 | 0.9994 | 0.9991 | 0.9993 | 4.14s |
| **CatBoost** | 99.92% | 0.9989 | 0.9992 | 0.9988 | 0.9991 | 5.98s |

*Selected Champion: **LightGBM***

## Task 2: Development Gap 5-Class Ordinal Classification

| Model | Accuracy | F1-Macro | F1-Weighted | Precision-Macro | Recall-Macro | Training Time (s) |
|---|---|---|---|---|---|---|
| **Random Forest** | 99.83% | 0.9968 | 0.9983 | 0.9986 | 0.995 | 1.86s |
| **LightGBM** | 99.72% | 0.9972 | 0.9972 | 0.9977 | 0.9967 | 1.73s |
| **XGBoost** | 99.43% | 0.9912 | 0.9943 | 0.9893 | 0.9931 | 3.36s |
| **CatBoost** | 99.37% | 0.99 | 0.9937 | 0.9891 | 0.991 | 4.2s |

*Selected Champion: **Random Forest***

## Task 3: Budget Requirement Regression

| Model | $R^2$ Score | MAE (₹ Lakhs) | RMSE (₹ Lakhs) | Training Time (s) |
|---|---|---|---|---|
| **Random Forest** | 0.9983 | ₹2.87 L | ₹5.31 L | 18.49s |
| **LightGBM** | 0.9988 | ₹2.55 L | ₹4.43 L | 0.51s |
| **XGBoost** | 0.9988 | ₹2.53 L | ₹4.55 L | 1.21s |
| **CatBoost** | 0.998 | ₹3.85 L | ₹5.85 L | 1.49s |

*Selected Champion: **LightGBM***

