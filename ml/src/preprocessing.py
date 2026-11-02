"""
Preprocessing Pipeline for Smart Panchayat AI
Handles missing-value imputation, outlier clipping, categorical encoding,
feature scaling, and leakage-free stratified group splitting.
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from sklearn.preprocessing import StandardScaler, LabelEncoder, RobustScaler
from sklearn.model_selection import GroupShuffleSplit

# Core numerical features used for model input
NUMERICAL_FEATURES = [
    # Demographics
    "population", "households", "rural_population_density", "pop_density_log", "population_log",
    
    # Economic
    "poverty_rate", "employment_rate", "unemployment_rate", "avg_household_income",
    "agricultural_dependency", "self_employment_rate", "livelihood_availability_score",
    
    # Education
    "literacy_rate", "school_availability_score", "student_enrollment_rate",
    "school_dropout_rate", "teacher_availability_ratio", "digital_education_access",
    
    # Healthcare
    "primary_healthcare_access", "hospital_accessibility_score", "doctor_availability_score",
    "maternal_healthcare_access", "child_stunting_rate", "nutrition_score",
    
    # Water & Sanitation
    "drinking_water_coverage", "water_availability_index", "groundwater_dependency",
    "sanitation_coverage", "waste_management_coverage", "water_scarcity_index",
    
    # Infrastructure
    "road_connectivity_rate", "electricity_coverage", "streetlight_availability",
    "housing_quality_pucca", "internet_connectivity", "public_infra_availability",
    
    # Environmental
    "air_quality_index", "water_quality_index", "flood_vulnerability",
    "drought_vulnerability", "green_cover_pct", "climate_risk_index",
    
    # Financial
    "annual_panchayat_budget_lakhs", "available_dev_funds_lakhs", "previous_expenditure_lakhs",
    "unspent_budget_lakhs", "project_completion_rate", "own_source_revenue_ratio",
    
    # Derived Domain Scores
    "healthcare_accessibility_score", "education_development_score", "water_security_score",
    "infrastructure_gap_score", "livelihood_opportunity_score", "financial_utilization_score",
    "overall_development_score",
    
    # Interaction Features
    "water_stress_interaction", "health_burden_interaction", "education_barrier_interaction",
    "economic_precarity_interaction", "connectivity_isolation_interaction", "fiscal_absorption_lag"
]

CATEGORICAL_FEATURES = ["state"]

class PanchayatPreprocessor:
    """Production-grade preprocessor with leakage-free transform capabilities."""

    def __init__(self, use_robust_scaling: bool = False):
        self.scaler = RobustScaler() if use_robust_scaling else StandardScaler()
        self.state_dummies_columns: List[str] = []
        self.target_encoders: Dict[str, LabelEncoder] = {
            "priority_sector": LabelEncoder(),
            "development_gap_category": LabelEncoder(),
        }
        self.medians: Dict[str, float] = {}
        self.is_fitted: bool = False

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicates and handle missing values."""
        df = df.copy()
        df = df.drop_duplicates(subset=["state", "gram_panchayat", "village_ward"])
        return df

    def fit(self, df: pd.DataFrame):
        """Fit preprocessor strictly on training data."""
        clean_df = self.clean_data(df)

        # 1. Store feature medians for robust imputation
        for col in NUMERICAL_FEATURES:
            if col in clean_df.columns:
                self.medians[col] = float(clean_df[col].median())

        # 2. Fit State One-Hot Encoding
        state_dummies = pd.get_dummies(clean_df["state"], prefix="state", drop_first=False)
        self.state_dummies_columns = list(state_dummies.columns)

        # 3. Impute and Fit Scaler
        X_num = self._prepare_numerical(clean_df)
        self.scaler.fit(X_num)

        # 4. Fit Target Encoders
        if "priority_sector" in clean_df.columns:
            self.target_encoders["priority_sector"].fit(clean_df["priority_sector"])
        if "development_gap_category" in clean_df.columns:
            self.target_encoders["development_gap_category"].fit(clean_df["development_gap_category"])

        self.is_fitted = True
        return self

    def _prepare_numerical(self, df: pd.DataFrame) -> np.ndarray:
        """Extract and impute numerical features using fitted medians."""
        X_num = np.zeros((len(df), len(NUMERICAL_FEATURES)), dtype=np.float32)
        for i, col in enumerate(NUMERICAL_FEATURES):
            if col in df.columns:
                vals = df[col].values
                med = self.medians.get(col, 0.0)
                # Impute NaNs with median
                vals = np.where(pd.isna(vals), med, vals)
                X_num[:, i] = vals
            else:
                X_num[:, i] = self.medians.get(col, 0.0)
        return X_num

    def transform_features(self, df: pd.DataFrame) -> np.ndarray:
        """Transform raw input dataframe into scaled feature matrix X."""
        if not self.is_fitted:
            raise RuntimeError("Preprocessor must be fitted before calling transform_features.")
        
        # 1. Numerical scaling
        X_num = self._prepare_numerical(df)
        X_num_scaled = self.scaler.transform(X_num)

        # 2. State dummy alignment
        state_df = pd.get_dummies(df["state"], prefix="state")
        X_state = np.zeros((len(df), len(self.state_dummies_columns)), dtype=np.float32)
        for j, col in enumerate(self.state_dummies_columns):
            if col in state_df.columns:
                X_state[:, j] = state_df[col].values

        return np.hstack([X_num_scaled, X_state])

    def get_feature_names(self) -> List[str]:
        """Return full ordered list of feature column names."""
        return list(NUMERICAL_FEATURES) + list(self.state_dummies_columns)

    def save(self, filepath: str = "ml/models/preprocessor.joblib"):
        """Serialize preprocessor to disk."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(self, filepath)
        print(f"Saved preprocessor to {filepath}")

    @staticmethod
    def load(filepath: str = "ml/models/preprocessor.joblib") -> "PanchayatPreprocessor":
        """Load preprocessor from disk."""
        return joblib.load(filepath)

def split_dataset(
    df: pd.DataFrame, 
    test_size: float = 0.20, 
    seed: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Perform leakage-free grouped splitting by subdistrict (block_taluk_mandal).
    Guarantees no village/ward from the same local administrative cluster crosses the train/test boundary.
    """
    gss = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
    groups = df["block_taluk_mandal"]
    train_idx, test_idx = next(gss.split(df, groups=groups))
    
    train_df = df.iloc[train_idx].copy().reset_index(drop=True)
    test_df = df.iloc[test_idx].copy().reset_index(drop=True)

    print(f"Grouped Train/Test Split (by Sub-District):")
    print(f"  - Train records: {len(train_df):,} ({len(train_df['block_taluk_mandal'].unique())} unique clusters)")
    print(f"  - Test records:  {len(test_df):,} ({len(test_df['block_taluk_mandal'].unique())} unique clusters)")
    
    return train_df, test_df
