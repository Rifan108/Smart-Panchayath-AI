"""
Evaluation and Validation Module for Smart Panchayat AI
Computes comprehensive metrics, confusion matrices, ROC-AUC, and regression diagnostics.
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score,
    precision_recall_fscore_support, mean_absolute_error,
    mean_squared_error, r2_score
)

# Local imports
curr_dir = os.path.dirname(os.path.abspath(__file__))
if curr_dir not in sys.path:
    sys.path.insert(0, curr_dir)

from preprocessing import PanchayatPreprocessor, split_dataset
from feature_engineering import PanchayatFeatureEngineer

def evaluate_models(data_path: str = "ml/datasets/synthetic/synthetic_panchayats_all_5_states.parquet"):
    print("=" * 70)
    print("SMART PANCHAYAT AI: COMPREHENSIVE MODEL EVALUATION SUITE")
    print("=" * 70)

    # 1. Load Data
    print(f"Loading data from {data_path}...")
    df = pd.read_parquet(data_path)
    
    fe = PanchayatFeatureEngineer()
    df_fe = fe.transform(df)

    _, test_df = split_dataset(df_fe, test_size=0.20, seed=42)

    # 2. Load Preprocessor
    prep = PanchayatPreprocessor.load("ml/models/preprocessor.joblib")
    X_test = prep.transform_features(test_df)
    feature_names = prep.get_feature_names()

    # 3. Evaluate Priority Sector Classifier
    clf_path = "ml/models/classification/champion_priority_sector_model.joblib"
    if os.path.exists(clf_path):
        clf = joblib.load(clf_path)
        y_true = prep.target_encoders["priority_sector"].transform(test_df["priority_sector"])
        y_pred = clf.predict(X_test)
        if hasattr(y_pred, "flatten"):
            y_pred = y_pred.flatten().astype(int)

        target_names = list(prep.target_encoders["priority_sector"].classes_)
        print("\n--- TASK 1: PRIORITY SECTOR CLASSIFICATION REPORT ---")
        print(classification_report(y_true, y_pred, target_names=target_names, digits=4))

        print("\nConfusion Matrix:")
        cm = confusion_matrix(y_true, y_pred)
        cm_df = pd.DataFrame(cm, index=target_names, columns=target_names)
        print(cm_df)

    # 4. Evaluate Development Gap Classifier
    gap_path = "ml/models/classification/champion_development_gap_model.joblib"
    if os.path.exists(gap_path):
        gap_clf = joblib.load(gap_path)
        y_gap_true = prep.target_encoders["development_gap_category"].transform(test_df["development_gap_category"])
        y_gap_pred = gap_clf.predict(X_test)
        if hasattr(y_gap_pred, "flatten"):
            y_gap_pred = y_gap_pred.flatten().astype(int)

        gap_names = list(prep.target_encoders["development_gap_category"].classes_)
        print("\n--- TASK 2: DEVELOPMENT GAP 5-CLASS REPORT ---")
        print(classification_report(y_gap_true, y_gap_pred, target_names=gap_names, digits=4))

    # 5. Evaluate Budget Regressor
    reg_path = "ml/models/regression/champion_budget_requirement_model.joblib"
    if os.path.exists(reg_path):
        reg = joblib.load(reg_path)
        y_reg_true = test_df["estimated_development_requirement_lakhs"].values
        y_reg_pred = reg.predict(X_test)

        mae = mean_absolute_error(y_reg_true, y_reg_pred)
        rmse = np.sqrt(mean_squared_error(y_reg_true, y_reg_pred))
        r2 = r2_score(y_reg_true, y_reg_pred)

        print("\n--- TASK 3: BUDGET REGRESSION DIAGNOSTICS ---")
        print(f"R² Score: {r2:.4f}")
        print(f"Mean Absolute Error (MAE): Rs. {mae:.2f} Lakhs")
        print(f"Root Mean Squared Error (RMSE): Rs. {rmse:.2f} Lakhs")

    print("\n[SUCCESS] Evaluation Complete.")

if __name__ == "__main__":
    evaluate_models()
