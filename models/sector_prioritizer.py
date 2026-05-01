"""
Sector Prioritizer — ML-based sector ranking using XGBoost + Random Forest ensemble.
Identifies the Top 3 priority development sectors for each ward.
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import classification_report, accuracy_score
import xgboost as xgb
import joblib
import warnings

warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    SECTOR_INDICATORS, XGBOOST_PARAMS, RANDOM_FOREST_PARAMS,
    CROSS_VALIDATION_FOLDS, MODEL_DIR,
    XGBOOST_MODEL_PATH, RF_MODEL_PATH,
)


def prepare_training_data(df):
    """
    Prepare feature matrix and target labels for sector prioritization.
    
    The target is the most vulnerable sector (highest sector score) for each ward.
    Features are the raw indicator values.
    """
    # Feature columns: all indicator values
    feature_cols = []
    for indicators in SECTOR_INDICATORS.values():
        feature_cols.extend([col for col in indicators if col in df.columns])

    X = df[feature_cols].values

    # Target: the sector with the highest vulnerability score
    score_cols = [col for col in df.columns if col.startswith("score_")]
    y_sector_names = df[score_cols].idxmax(axis=1)

    # Encode sector names to integers
    unique_sectors = sorted(y_sector_names.unique())
    sector_to_id = {s: i for i, s in enumerate(unique_sectors)}
    id_to_sector = {i: s for s, i in sector_to_id.items()}

    y = y_sector_names.map(sector_to_id).values

    return X, y, feature_cols, sector_to_id, id_to_sector


def train_xgboost(X, y, num_classes):
    """Train XGBoost classifier."""
    params = XGBOOST_PARAMS.copy()
    params["objective"] = "multi:softprob"
    params["num_class"] = num_classes

    model = xgb.XGBClassifier(**params)
    model.fit(X, y)

    return model


def train_random_forest(X, y):
    """Train Random Forest classifier."""
    model = RandomForestClassifier(**RANDOM_FOREST_PARAMS)
    model.fit(X, y)

    return model


def evaluate_model(model, X, y, model_name="Model"):
    """Evaluate model with cross-validation."""
    cv = StratifiedKFold(n_splits=CROSS_VALIDATION_FOLDS, shuffle=True, random_state=42)

    scores = cross_val_score(model, X, y, cv=cv, scoring="accuracy")
    print(f"\n📊 {model_name} Cross-Validation Results:")
    print(f"   Accuracy: {scores.mean():.4f} (+/- {scores.std():.4f})")
    print(f"   Per-fold: {[f'{s:.3f}' for s in scores]}")

    # Full training accuracy
    y_pred = model.predict(X)
    print(f"   Training Accuracy: {accuracy_score(y, y_pred):.4f}")

    return scores


def ensemble_predict(xgb_model, rf_model, X):
    """
    Soft voting ensemble: average probability outputs from both models.
    Returns predicted class and probability distributions.
    """
    xgb_probs = xgb_model.predict_proba(X)
    rf_probs = rf_model.predict_proba(X)

    # Average probabilities (soft voting)
    ensemble_probs = (xgb_probs + rf_probs) / 2

    # Predicted class = highest average probability
    predictions = np.argmax(ensemble_probs, axis=1)

    return predictions, ensemble_probs


def get_top_n_sectors(ensemble_probs, id_to_sector, n=3):
    """
    Get top N priority sectors with confidence scores for each ward.
    
    Returns a list of dicts: [{"sector": name, "confidence": score}, ...]
    """
    results = []

    for i in range(ensemble_probs.shape[0]):
        ward_probs = ensemble_probs[i]
        top_indices = np.argsort(ward_probs)[::-1][:n]

        ward_result = []
        for idx in top_indices:
            sector_col = id_to_sector[idx]
            sector_name = sector_col.replace("score_", "").replace("_", " ").title()
            ward_result.append({
                "sector": sector_name,
                "sector_col": sector_col,
                "confidence": float(ward_probs[idx]),
                "rank": len(ward_result) + 1,
            })
        results.append(ward_result)

    return results


def get_feature_importance(xgb_model, rf_model, feature_names):
    """
    Get combined feature importance from both models.
    Returns sorted dict of feature → importance score.
    """
    xgb_importance = xgb_model.feature_importances_
    rf_importance = rf_model.feature_importances_

    # Average importance
    combined = (xgb_importance + rf_importance) / 2

    importance_dict = dict(zip(feature_names, combined))
    return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))


def train_and_save_models(df):
    """
    Full training pipeline: prepare data, train both models, evaluate, save.
    """
    print("\n" + "=" * 60)
    print("  Sector Prioritization — Model Training")
    print("=" * 60)

    # Prepare data
    X, y, feature_cols, sector_to_id, id_to_sector = prepare_training_data(df)
    num_classes = len(sector_to_id)

    print(f"\n📋 Training Data:")
    print(f"   Features: {X.shape[1]}")
    print(f"   Samples: {X.shape[0]}")
    print(f"   Classes: {num_classes}")
    print(f"   Sectors: {list(sector_to_id.keys())}")

    # Train XGBoost
    print("\n🔧 Training XGBoost...")
    xgb_model = train_xgboost(X, y, num_classes)
    evaluate_model(xgb_model, X, y, "XGBoost")

    # Train Random Forest
    print("\n🔧 Training Random Forest...")
    rf_model = train_random_forest(X, y)
    evaluate_model(rf_model, X, y, "Random Forest")

    # Ensemble evaluation
    print("\n🔧 Ensemble Evaluation...")
    predictions, ensemble_probs = ensemble_predict(xgb_model, rf_model, X)
    ensemble_acc = accuracy_score(y, predictions)
    print(f"   Ensemble Training Accuracy: {ensemble_acc:.4f}")

    # Feature importance
    importance = get_feature_importance(xgb_model, rf_model, feature_cols)
    print(f"\n📊 Top 10 Most Important Features:")
    for i, (feat, imp) in enumerate(list(importance.items())[:10]):
        bar = "█" * int(imp * 200)
        print(f"   {i+1}. {feat}: {imp:.4f} {bar}")

    # Save models
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(xgb_model, XGBOOST_MODEL_PATH)
    joblib.dump(rf_model, RF_MODEL_PATH)
    joblib.dump(sector_to_id, os.path.join(MODEL_DIR, "sector_to_id.joblib"))
    joblib.dump(id_to_sector, os.path.join(MODEL_DIR, "id_to_sector.joblib"))
    joblib.dump(feature_cols, os.path.join(MODEL_DIR, "feature_cols.joblib"))

    print(f"\n💾 Models saved to {MODEL_DIR}")

    return xgb_model, rf_model, feature_cols, sector_to_id, id_to_sector


def load_models():
    """Load pre-trained models from disk."""
    xgb_model = joblib.load(XGBOOST_MODEL_PATH)
    rf_model = joblib.load(RF_MODEL_PATH)
    sector_to_id = joblib.load(os.path.join(MODEL_DIR, "sector_to_id.joblib"))
    id_to_sector = joblib.load(os.path.join(MODEL_DIR, "id_to_sector.joblib"))
    feature_cols = joblib.load(os.path.join(MODEL_DIR, "feature_cols.joblib"))

    return xgb_model, rf_model, feature_cols, sector_to_id, id_to_sector
