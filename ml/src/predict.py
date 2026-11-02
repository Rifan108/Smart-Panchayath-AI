"""
Inference Service for Smart Panchayat AI
Provides low-latency multi-task predictions:
- Priority Sector Multi-class Classification
- Development Gap 5-Class Ordinal Classification
- Budget Requirement Regression (₹ Lakhs)
- Unsupervised Cluster Archetype Assignment
- Isolation Forest Anomaly Detection
- Linear Programming Budget Optimization
- SHAP / Feature Attribution Explanations
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Union

# Add current directory to path if needed
curr_dir = os.path.dirname(os.path.abspath(__file__))
if curr_dir not in sys.path:
    sys.path.insert(0, curr_dir)

from feature_engineering import PanchayatFeatureEngineer
from preprocessing import PanchayatPreprocessor
from budget_optimizer import LinearBudgetOptimizer
from explainability import PanchayatModelExplainer

# Cluster Archetype Labels
CLUSTER_ARCHETYPES = {
    0: "Aspirational Rural Cluster (High Infrastructure & Water Need)",
    1: "Progressive Mixed Economy (Balanced Basic Amenities)",
    2: "Agrarian Vulnerable Belt (High Groundwater & Drought Stress)",
    3: "Peri-Urban High-Density Growth Corridor"
}

class SmartPanchayatInferenceService:
    """Production ML Inference Service with multi-task prediction capabilities."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SmartPanchayatInferenceService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, models_dir: str = "ml/models"):
        if getattr(self, "_initialized", False):
            return

        self.models_dir = models_dir
        self.preprocessor: Optional[PanchayatPreprocessor] = None
        self.priority_model = None
        self.gap_model = None
        self.budget_model = None
        self.kmeans_model = None
        self.anomaly_model = None
        
        self.fe = PanchayatFeatureEngineer()
        self.optimizer = LinearBudgetOptimizer()
        self.explainer: Optional[PanchayatModelExplainer] = None

        self.load_models()
        self._initialized = True

    def load_models(self):
        """Load all champion models and preprocessor into memory once."""
        prep_path = os.path.join(self.models_dir, "preprocessor.joblib")
        if os.path.exists(prep_path):
            self.preprocessor = joblib.load(prep_path)

        p_path = os.path.join(self.models_dir, "classification", "champion_priority_sector_model.joblib")
        if os.path.exists(p_path):
            self.priority_model = joblib.load(p_path)

        g_path = os.path.join(self.models_dir, "classification", "champion_development_gap_model.joblib")
        if os.path.exists(g_path):
            self.gap_model = joblib.load(g_path)

        b_path = os.path.join(self.models_dir, "regression", "champion_budget_requirement_model.joblib")
        if os.path.exists(b_path):
            self.budget_model = joblib.load(b_path)

        k_path = os.path.join(self.models_dir, "clustering", "kmeans_panchayat_clusters.joblib")
        if os.path.exists(k_path):
            self.kmeans_model = joblib.load(k_path)

        a_path = os.path.join(self.models_dir, "anomaly_detection", "isolation_forest_anomaly_detector.joblib")
        if os.path.exists(a_path):
            self.anomaly_model = joblib.load(a_path)

        self.explainer = PanchayatModelExplainer(p_path, prep_path)
        print("[Inference Service] Successfully loaded all models and pipelines into memory.")

    def predict_panchayat(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run complete multi-task ML inference for a single Panchayat record.
        """
        if self.preprocessor is None or self.priority_model is None:
            raise RuntimeError("Inference service models are not loaded.")

        df = pd.DataFrame([record])
        df_fe = self.fe.transform(df)
        X = self.preprocessor.transform_features(df_fe)

        # 1. Priority Sector Prediction
        priority_idx = self.priority_model.predict(X)[0]
        if hasattr(priority_idx, "item"):
            priority_idx = int(priority_idx)
        
        target_encoder = self.preprocessor.target_encoders.get("priority_sector")
        priority_sector = target_encoder.inverse_transform([priority_idx])[0] if target_encoder else str(priority_idx)

        # Probabilities
        priority_probs = {}
        if hasattr(self.priority_model, "predict_proba"):
            probs = self.priority_model.predict_proba(X)[0]
            if target_encoder:
                for idx, c in enumerate(target_encoder.classes_):
                    priority_probs[c] = round(float(probs[idx]), 4)

        # 2. Development Gap Category
        gap_idx = self.gap_model.predict(X)[0]
        if hasattr(gap_idx, "item"):
            gap_idx = int(gap_idx)
        gap_encoder = self.preprocessor.target_encoders.get("development_gap_category")
        gap_category = gap_encoder.inverse_transform([gap_idx])[0] if gap_encoder else str(gap_idx)

        # 3. Budget Requirement Regression
        est_req_lakhs = float(self.budget_model.predict(X)[0])
        est_req_lakhs = round(max(10.0, est_req_lakhs), 2)

        # 4. Cluster Archetype
        cluster_id = int(self.kmeans_model.predict(X)[0])
        cluster_desc = CLUSTER_ARCHETYPES.get(cluster_id, f"Cluster {cluster_id}")

        # 5. Anomaly Detection
        iso_pred = int(self.anomaly_model.predict(X)[0])
        is_anomaly = bool(iso_pred == -1)
        anomaly_score = round(float(self.anomaly_model.score_samples(X)[0]), 4)

        # 6. Extracted Domain Scores
        domain_scores = {
            "healthcare_accessibility": float(df_fe["healthcare_accessibility_score"].iloc[0]),
            "education_development": float(df_fe["education_development_score"].iloc[0]),
            "water_security": float(df_fe["water_security_score"].iloc[0]),
            "infrastructure_gap": float(df_fe["infrastructure_gap_score"].iloc[0]),
            "livelihood_opportunity": float(df_fe["livelihood_opportunity_score"].iloc[0]),
            "financial_utilization": float(df_fe["financial_utilization_score"].iloc[0]),
            "overall_development_score": float(df_fe["overall_development_score"].iloc[0]),
        }

        # 7. Sector Deficits for Budget Optimization
        sector_deficits = {
            "Water & Sanitation": round(1.0 - domain_scores["water_security"], 3),
            "Healthcare": round(1.0 - domain_scores["healthcare_accessibility"], 3),
            "Education": round(1.0 - domain_scores["education_development"], 3),
            "Infrastructure": round(domain_scores["infrastructure_gap"], 3),
            "Agriculture & Livelihood": round(1.0 - domain_scores["livelihood_opportunity"], 3),
            "Social Welfare": round(float(df_fe.get("poverty_rate", pd.Series([0.1])).iloc[0]) * 2.0, 3),
        }

        # Available budget
        avail_budget = float(record.get("available_dev_funds_lakhs", record.get("annual_panchayat_budget_lakhs", 150.0)))
        pop = int(record.get("population", 5000))

        # 8. LP Budget Optimization
        optimized_budget = self.optimizer.optimize_budget(
            total_budget_lakhs=avail_budget,
            sector_deficits=sector_deficits,
            population=pop,
            priority_sector=priority_sector
        )

        # 9. SHAP Explainability
        explanation = self.explainer.explain_instance(record)

        return {
            "status": "success",
            "panchayat_name": record.get("gram_panchayat", "Unknown"),
            "state": record.get("state", "Kerala"),
            "population": pop,
            "predictions": {
                "priority_sector": priority_sector,
                "priority_sector_confidence": priority_probs.get(priority_sector, 1.0),
                "sector_probabilities": priority_probs,
                "development_gap_category": gap_category,
                "estimated_development_requirement_lakhs": est_req_lakhs,
                "cluster_archetype_id": cluster_id,
                "cluster_archetype": cluster_desc,
                "is_statistical_anomaly": is_anomaly,
                "anomaly_score": anomaly_score,
            },
            "domain_scores": domain_scores,
            "budget_allocation": optimized_budget,
            "explainability": explanation
        }

    def predict_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """Vectorized inference over a batch dataframe."""
        df_fe = self.fe.transform(df)
        X = self.preprocessor.transform_features(df_fe)

        target_encoder = self.preprocessor.target_encoders.get("priority_sector")
        gap_encoder = self.preprocessor.target_encoders.get("development_gap_category")

        p_idx = self.priority_model.predict(X)
        g_idx = self.gap_model.predict(X)
        b_preds = self.budget_model.predict(X)
        clusters = self.kmeans_model.predict(X)
        anomalies = (self.anomaly_model.predict(X) == -1)

        res = df_fe.copy()
        res["predicted_priority_sector"] = target_encoder.inverse_transform(p_idx) if target_encoder else p_idx
        res["predicted_gap_category"] = gap_encoder.inverse_transform(g_idx) if gap_encoder else g_idx
        res["predicted_budget_requirement_lakhs"] = np.round(b_preds, 2)
        res["cluster_archetype_id"] = clusters
        res["is_anomaly"] = anomalies

        return res

# Global service instance
def get_inference_service() -> SmartPanchayatInferenceService:
    return SmartPanchayatInferenceService()
