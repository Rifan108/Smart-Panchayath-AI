"""
Analysis Service — Orchestrates the full AI analysis pipeline.
Connects data → vulnerability → prioritization → budget → explanations.
"""

import sys, os
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.data_service import load_raw_data, clean_data, normalize_indicators
from models.vulnerability_index import compute_all_sector_scores, compute_overall_index, get_sector_rankings
from models.sector_prioritizer import (
    train_and_save_models, load_models, prepare_training_data,
    ensemble_predict, get_top_n_sectors, get_feature_importance,
)
from models.budget_allocator import compute_allocation, format_allocation_table
from models.explainer import load_explainer_and_compute, get_feature_shap_for_ward, generate_natural_language_explanation
from config import PROCESSED_DATA_FILE, SECTOR_INDICATORS


class AnalysisEngine:
    """Central engine that runs and caches all analyses."""

    def __init__(self):
        self.df_raw = None
        self.df_processed = None
        self.xgb_model = None
        self.rf_model = None
        self.feature_cols = None
        self.sector_to_id = None
        self.id_to_sector = None
        self.shap_values = None
        self.shap_explainer = None
        self._is_initialized = False

    def initialize(self, data_path=None):
        """Run full pipeline: load → preprocess → train → analyze."""
        print("\n" + "🚀" * 20)
        print("  Kerala Smart Panchayat AI Planner — Initializing")
        print("🚀" * 20)

        # Step 1: Load and preprocess
        self.df_raw = load_raw_data(data_path)
        self.df_processed = clean_data(self.df_raw.copy())
        self.df_processed, _ = normalize_indicators(self.df_processed)

        # Step 2: Compute vulnerability scores
        self.df_processed, _ = compute_all_sector_scores(self.df_processed)
        self.df_processed = compute_overall_index(self.df_processed)

        # Step 3: Train ML models
        (self.xgb_model, self.rf_model, self.feature_cols,
         self.sector_to_id, self.id_to_sector) = train_and_save_models(self.df_processed)

        # Step 4: Generate predictions for all wards
        X = self.df_processed[[c for c in self.feature_cols if c in self.df_processed.columns]].values
        predictions, probs = ensemble_predict(self.xgb_model, self.rf_model, X)
        top_sectors = get_top_n_sectors(probs, self.id_to_sector, n=3)

        self.df_processed["priority_sector_1"] = [t[0]["sector"] for t in top_sectors]
        self.df_processed["priority_confidence_1"] = [t[0]["confidence"] for t in top_sectors]
        self.df_processed["priority_sector_2"] = [t[1]["sector"] if len(t) > 1 else "" for t in top_sectors]
        self.df_processed["priority_sector_3"] = [t[2]["sector"] if len(t) > 2 else "" for t in top_sectors]

        # Step 5: Compute SHAP
        try:
            self.shap_values, _, self.shap_explainer = load_explainer_and_compute(self.df_processed)
            print("✅ SHAP values computed")
        except Exception as e:
            print(f"⚠️  SHAP computation skipped: {e}")
            self.shap_values = None

        # Save processed data
        os.makedirs(os.path.dirname(PROCESSED_DATA_FILE), exist_ok=True)
        self.df_processed.to_csv(PROCESSED_DATA_FILE, index=False)

        self._is_initialized = True
        print("\n✅ Analysis engine fully initialized!")
        return self

    def get_ward_data(self, ward_name):
        """Get all data for a specific ward."""
        row = self.df_processed[self.df_processed["ward_name"] == ward_name]
        if row.empty:
            return None
        return row.iloc[0].to_dict()

    def get_ward_budget(self, ward_name, total_budget=None):
        """Get budget allocation for a specific ward."""
        rankings = get_sector_rankings(self.df_processed, ward_name)
        if not rankings:
            return None
        return compute_allocation(rankings, total_budget)

    def get_ward_explanation(self, ward_name, sector_name=None):
        """Get SHAP-based explanation for a ward's priority sector."""
        ward_data = self.get_ward_data(ward_name)
        if not ward_data or self.shap_values is None:
            return "Explanation not available."

        ward_idx = self.df_processed[self.df_processed["ward_name"] == ward_name].index[0]

        if sector_name is None:
            sector_name = ward_data.get("priority_sector_1", "Unknown")

        contributions = get_feature_shap_for_ward(
            self.shap_values, ward_idx, self.feature_cols
        )

        score_col = "score_" + sector_name.lower().replace(" ", "_").replace("&", "and").replace(".", "")
        vuln_score = ward_data.get(score_col, 0.5)

        return generate_natural_language_explanation(
            ward_name, sector_name, contributions, vuln_score
        )

    def get_all_wards_summary(self):
        """Get summary DataFrame for all wards."""
        cols = ["ward_id", "ward_name", "ward_profile", "population",
                "vulnerability_index", "vulnerability_category",
                "priority_sector_1", "priority_confidence_1"]
        available = [c for c in cols if c in self.df_processed.columns]
        return self.df_processed[available].sort_values("vulnerability_index", ascending=False)

    def get_sector_scores_matrix(self):
        """Get matrix of sector scores for all wards (for heatmap)."""
        score_cols = [c for c in self.df_processed.columns if c.startswith("score_")]
        return self.df_processed[["ward_name"] + score_cols]

    def get_feature_importance(self):
        """Get combined feature importance from both models."""
        return get_feature_importance(self.xgb_model, self.rf_model, self.feature_cols)


# Singleton instance
_engine = None

def get_engine():
    global _engine
    if _engine is None or not _engine._is_initialized:
        _engine = AnalysisEngine()
        _engine.initialize()
    return _engine
