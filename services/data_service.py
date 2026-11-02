"""
Data Service — Data loading, cleaning, preprocessing, and feature engineering
for the Kerala Smart Panchayat AI Planner.
ML dependencies (sklearn scaler) replaced with pure numpy normalization.
"""

import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    RAW_DATA_FILE, PROCESSED_DATA_FILE, PROCESSED_DATA_DIR,
    SECTOR_INDICATORS,
)


def load_raw_data(filepath=None):
    """Load raw ward-level CSV data across states and districts."""
    if filepath is None:
        multi_state_path = os.path.join(
            os.path.dirname(RAW_DATA_FILE), "panchayats_multi_state_data.csv"
        )
        all_panchayats_path = os.path.join(
            os.path.dirname(RAW_DATA_FILE), "kerala_all_panchayats_ward_data.csv"
        )
        if os.path.exists(multi_state_path):
            filepath = multi_state_path
        elif os.path.exists(all_panchayats_path):
            filepath = all_panchayats_path
        else:
            filepath = RAW_DATA_FILE

    if not os.path.exists(filepath):
        # Auto-generate if missing
        try:
            from data.generate_multi_state_dataset import main as gen_multi
            df = gen_multi()
            return df
        except Exception:
            raise FileNotFoundError(
                f"Dataset not found at {filepath}. "
                f"Run 'python data/generate_multi_state_dataset.py' first."
            )

    df = pd.read_csv(filepath)
    if "state" not in df.columns:
        df["state"] = "Kerala"
    if "district" not in df.columns:
        df["district"] = "Kasaragod"
    if "panchayat_name" not in df.columns:
        df["panchayat_name"] = "Manjeshwar"

    print(f"Loaded {len(df)} wards from {filepath}")
    return df


def clean_data(df):
    """Clean and validate the dataset."""
    # Drop any fully null rows
    df = df.dropna(how="all")

    # Get all indicator columns
    all_indicators = []
    for indicators in SECTOR_INDICATORS.values():
        all_indicators.extend(indicators)

    # Fill missing numeric values with column median
    for col in all_indicators:
        if col in df.columns and df[col].isnull().any():
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)

    # Clip extreme outliers (1st–99th percentile)
    for col in all_indicators:
        if col in df.columns:
            q1 = df[col].quantile(0.01)
            q99 = df[col].quantile(0.99)
            df[col] = df[col].clip(q1, q99)

    print(f"Data cleaning complete. Shape: {df.shape}")
    return df


def normalize_indicators(df):
    """
    Normalize all indicator columns to 0-1 scale using Min-Max scaling.
    Pure numpy implementation — no sklearn required.
    Returns normalized df and a simple dict of {col: (min, max)}.
    """
    all_indicators = []
    for indicators in SECTOR_INDICATORS.values():
        all_indicators.extend(indicators)

    available = [col for col in all_indicators if col in df.columns]
    df_normalized = df.copy()
    scale_params = {}

    for col in available:
        col_min = df[col].min()
        col_max = df[col].max()
        if col_max > col_min:
            df_normalized[col] = (df[col] - col_min) / (col_max - col_min)
        else:
            df_normalized[col] = 0.0
        scale_params[col] = (col_min, col_max)

    print(f"Normalized {len(available)} indicators to [0, 1] range")
    return df_normalized, scale_params


def compute_sector_scores(df):
    """
    Compute a composite vulnerability score per sector for each ward.
    For 'negative' polarity indicators, we keep as-is (higher = more vulnerable).
    For 'positive' polarity, we invert (lower development = higher vulnerability).
    """
    # Indicators where higher value means MORE vulnerable
    NEGATIVE_INDICATORS = {
        "disease_incidence_rate", "infant_mortality_rate", "dropout_rate",
        "student_teacher_ratio", "poverty_rate_bpl_pct", "flood_risk_score",
    }

    for sector, indicators in SECTOR_INDICATORS.items():
        available = [col for col in indicators if col in df.columns]
        if not available:
            continue

        sector_col = f"score_{sector.lower().replace(' ', '_').replace('&', 'and').replace('.', '')}"

        adjusted_cols = []
        for col in available:
            adj_col = f"_adj_{col}"
            if col in NEGATIVE_INDICATORS:
                df[adj_col] = df[col]
            else:
                df[adj_col] = 1 - df[col]
            adjusted_cols.append(adj_col)

        df[sector_col] = df[adjusted_cols].mean(axis=1)
        df = df.drop(columns=adjusted_cols)

    print(f"Computed vulnerability scores for {len(SECTOR_INDICATORS)} sectors")
    return df


def compute_overall_vulnerability(df):
    """Compute weighted overall vulnerability index for each ward."""
    from config import SECTOR_WEIGHTS

    score_cols = [col for col in df.columns if col.startswith("score_")]

    sector_col_map = {}
    for sector in SECTOR_WEIGHTS:
        col_name = f"score_{sector.lower().replace(' ', '_').replace('&', 'and').replace('.', '')}"
        if col_name in score_cols:
            sector_col_map[sector] = col_name

    df["vulnerability_index"] = 0.0
    for sector, col in sector_col_map.items():
        weight = SECTOR_WEIGHTS.get(sector, 0.1)
        df["vulnerability_index"] += df[col] * weight

    vi_min = df["vulnerability_index"].min()
    vi_max = df["vulnerability_index"].max()
    if vi_max > vi_min:
        df["vulnerability_index"] = (df["vulnerability_index"] - vi_min) / (vi_max - vi_min)

    df["vulnerability_category"] = pd.cut(
        df["vulnerability_index"],
        bins=[0, 0.3, 0.6, 1.0],
        labels=["Low", "Medium", "High"],
        include_lowest=True,
    )

    print(f"Overall vulnerability index computed")
    return df


def identify_priority_sector(df):
    """Identify the most vulnerable (priority) sector for each ward."""
    score_cols = [col for col in df.columns if col.startswith("score_")]
    df["priority_sector"] = df[score_cols].idxmax(axis=1)
    df["priority_sector"] = (
        df["priority_sector"]
        .str.replace("score_", "")
        .str.replace("_and_", " & ")
        .str.replace("_", " ")
        .str.title()
    )
    print(f"Priority sectors identified for each ward")
    return df


def preprocess_pipeline(filepath=None):
    """Run the full preprocessing pipeline."""
    print("\n" + "=" * 60)
    print("  Data Preprocessing Pipeline")
    print("=" * 60 + "\n")

    df = load_raw_data(filepath)
    df = clean_data(df)
    df_normalized, scale_params = normalize_indicators(df)
    df_normalized = compute_sector_scores(df_normalized)
    df_normalized = compute_overall_vulnerability(df_normalized)
    df_normalized = identify_priority_sector(df_normalized)

    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    df_normalized.to_csv(PROCESSED_DATA_FILE, index=False)
    print(f"Processed data saved to {PROCESSED_DATA_FILE}")

    return df_normalized, scale_params


if __name__ == "__main__":
    df, _ = preprocess_pipeline()
    print("\nProcessed Data Preview:")
    cols_to_show = ["ward_name", "vulnerability_index", "vulnerability_category", "priority_sector"]
    available_cols = [c for c in cols_to_show if c in df.columns]
    print(df[available_cols].to_string(index=False))
