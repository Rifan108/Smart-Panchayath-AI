"""
Multi-State ML Model Training & Benchmarking Pipeline
Evaluates candidate ML models (HistGradientBoosting, Gradient Boosting, Random Forest, Extra Trees)
to identify and train the BEST performing model for Panchayat priority & vulnerability predictions.
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    HistGradientBoostingClassifier,
    ExtraTreesClassifier,
    RandomForestRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor,
)
from sklearn.metrics import accuracy_score, f1_score, r2_score, mean_squared_error

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MODEL_DIR, SECTOR_INDICATORS
from services.data_service import (
    clean_data, normalize_indicators, compute_sector_scores,
    compute_overall_vulnerability, identify_priority_sector
)

MULTI_STATE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "raw", "panchayats_multi_state_data.csv"
)
LEGACY_ALL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "raw", "kerala_all_panchayats_ward_data.csv"
)


def get_feature_indicators():
    """Extract all 40 indicator column names in deterministic order."""
    cols = []
    for indicators in SECTOR_INDICATORS.values():
        cols.extend(indicators)
    return sorted(list(set(cols)))


def prepare_training_dataset(data_path=None):
    """Load, preprocess, score, and label the dataset for training."""
    path = data_path or (MULTI_STATE_PATH if os.path.exists(MULTI_STATE_PATH) else LEGACY_ALL_PATH)
    if not os.path.exists(path):
        from data.generate_multi_state_dataset import main as gen_multi
        gen_multi()
        path = MULTI_STATE_PATH

    df = pd.read_csv(path)
    print(f"Loaded {len(df)} rows across {df['state'].nunique() if 'state' in df.columns else 1} states for training.")

    # Clean & normalize
    df = clean_data(df)
    df_norm, _ = normalize_indicators(df)
    df_scored = compute_sector_scores(df_norm)
    df_full = compute_overall_vulnerability(df_scored)
    df_full = identify_priority_sector(df_full)

    feature_cols = [c for c in get_feature_indicators() if c in df_full.columns]
    X = df_full[feature_cols].copy()
    y_class = df_full["priority_sector"].copy()
    y_reg = df_full["vulnerability_index"].copy()

    return df_full, X, y_class, y_reg, feature_cols


def benchmark_and_train_best_models(data_path=None):
    """
    Train and benchmark multiple candidate ML models.
    Selects the champion classifier and regressor based on cross-validation and test accuracy.
    """
    os.makedirs(MODEL_DIR, exist_ok=True)
    df_full, X, y_class, y_reg, feature_cols = prepare_training_dataset(data_path)

    # Encode sector labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y_class)
    sector_to_id = {cls: int(idx) for idx, cls in enumerate(le.classes_)}
    id_to_sector = {int(idx): cls for idx, cls in enumerate(le.classes_)}

    # Train/test split (80/20 stratified)
    X_train, X_test, y_train, y_test, y_reg_train, y_reg_test = train_test_split(
        X, y_encoded, y_reg, test_size=0.20, random_state=42, stratify=y_encoded
    )

    # Standardize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    X_all_scaled = scaler.transform(X)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    print("\n[1/3] Benchmarking Candidate Priority Classifiers...", flush=True)
    candidate_classifiers = {
        "Hist Gradient Boosting": HistGradientBoostingClassifier(
            max_iter=150, learning_rate=0.08, max_depth=7, min_samples_leaf=15, l2_regularization=0.1, random_state=42
        ),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=120, max_depth=12, random_state=42, n_jobs=-1),
        "Extra Trees": ExtraTreesClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1),
    }

    clf_results = {}
    best_clf_name = None
    best_clf_score = -1.0
    best_clf_model = None

    for name, model in candidate_classifiers.items():
        # Fit model
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        acc = float(accuracy_score(y_test, y_pred)) * 100
        f1 = float(f1_score(y_test, y_pred, average="weighted", zero_division=0)) * 100
        cv_scores = cross_val_score(model, X, y_encoded, cv=cv, scoring="accuracy", n_jobs=-1)
        cv_mean = float(cv_scores.mean()) * 100

        clf_results[name] = {
            "test_accuracy": round(acc, 2),
            "weighted_f1": round(f1, 2),
            "cv_accuracy_5fold": round(cv_mean, 2),
        }
        print(f"   -> {name:24s} | Test Acc: {acc:5.2f}% | F1: {f1:5.2f}% | 5-Fold CV: {cv_mean:5.2f}%", flush=True)

        if acc > best_clf_score:
            best_clf_score = acc
            best_clf_name = name
            best_clf_model = model

    print(f"\n🏆 Champion Classifier Selected: {best_clf_name} ({best_clf_score:.2f}% Accuracy)", flush=True)

    print("\n[2/3] Benchmarking Candidate Vulnerability Regressors...", flush=True)
    candidate_regressors = {
        "Hist Gradient Boosting Regressor": HistGradientBoostingRegressor(
            max_iter=150, learning_rate=0.08, max_depth=7, min_samples_leaf=15, l2_regularization=0.1, random_state=42
        ),
        "Gradient Boosting Regressor": GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42),
        "Random Forest Regressor": RandomForestRegressor(n_estimators=120, max_depth=12, random_state=42, n_jobs=-1),
    }

    reg_results = {}
    best_reg_name = None
    best_reg_r2 = -999.0
    best_reg_model = None

    for name, model in candidate_regressors.items():
        model.fit(X_train, y_reg_train)
        y_reg_pred = model.predict(X_test)

        r2 = float(r2_score(y_reg_test, y_reg_pred))
        mse = float(mean_squared_error(y_reg_test, y_reg_pred))

        reg_results[name] = {
            "r2_score": round(r2, 4),
            "mse": round(mse, 6),
        }
        print(f"   -> {name:32s} | R²: {r2:6.4f} | MSE: {mse:8.6f}", flush=True)

        if r2 > best_reg_r2:
            best_reg_r2 = r2
            best_reg_name = name
            best_reg_model = model

    print(f"\n🏆 Champion Regressor Selected: {best_reg_name} (R²: {best_reg_r2:.4f})", flush=True)

    # Feature importances from champion model
    top_features = []
    if hasattr(best_clf_model, "feature_importances_"):
        importances = best_clf_model.feature_importances_
        sorted_indices = np.argsort(importances)[::-1]
        for idx in sorted_indices[:15]:
            top_features.append({
                "feature": feature_cols[idx],
                "importance": round(float(importances[idx]), 4),
            })

    # Save artifacts
    print("\n[3/3] Saving Champion ML Models and Metadata...")
    joblib.dump(best_clf_model, os.path.join(MODEL_DIR, "champion_priority_model.joblib"))
    joblib.dump(best_clf_model, os.path.join(MODEL_DIR, "xgboost_model.joblib"))  # backward compat
    joblib.dump(best_clf_model, os.path.join(MODEL_DIR, "rf_model.joblib"))       # backward compat
    joblib.dump(best_reg_model, os.path.join(MODEL_DIR, "champion_vulnerability_regressor.joblib"))
    joblib.dump(best_reg_model, os.path.join(MODEL_DIR, "rf_regressor.joblib"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.joblib"))
    joblib.dump(feature_cols, os.path.join(MODEL_DIR, "feature_cols.joblib"))
    joblib.dump(sector_to_id, os.path.join(MODEL_DIR, "sector_to_id.joblib"))
    joblib.dump(id_to_sector, os.path.join(MODEL_DIR, "id_to_sector.joblib"))

    # Save benchmark metrics JSON
    metrics = {
        "status": "success",
        "champion_classifier": best_clf_name,
        "champion_classifier_accuracy": best_clf_score,
        "champion_regressor": best_reg_name,
        "champion_regressor_r2": best_reg_r2,
        "dataset": {
            "total_records": int(len(df_full)),
            "total_states": int(df_full["state"].nunique() if "state" in df_full.columns else 1),
            "states": sorted(df_full["state"].unique().tolist()) if "state" in df_full.columns else ["Kerala"],
            "total_districts": int(df_full["district"].nunique()),
            "total_panchayats": int(df_full["panchayat_name"].nunique()),
            "total_wards": int(len(df_full)),
            "features_count": int(len(feature_cols)),
            "classes_count": int(len(le.classes_)),
            "classes": sorted(list(le.classes_)),
        },
        "classifier_benchmark": clf_results,
        "regressor_benchmark": reg_results,
        "models": {
            "champion_classifier": {
                "name": best_clf_name,
                "accuracy": best_clf_score,
                "f1_score": clf_results[best_clf_name]["weighted_f1"],
                "cv_score_5fold": clf_results[best_clf_name]["cv_accuracy_5fold"],
            },
            "champion_regressor": {
                "name": best_reg_name,
                "r2_score": best_reg_r2,
                "mse": reg_results[best_reg_name]["mse"],
            },
        },
        "top_features": top_features,
        "trained_timestamp": pd.Timestamp.now().isoformat(),
    }

    metrics_path = os.path.join(MODEL_DIR, "metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"✅ Training complete! All artifacts saved to {MODEL_DIR}")
    return metrics


def train_all_models(data_path=None):
    return benchmark_and_train_best_models(data_path)


if __name__ == "__main__":
    benchmark_and_train_best_models()
