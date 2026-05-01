"""
Data Service — Data loading, cleaning, preprocessing, and feature engineering
for the Kerala Smart Panchayat AI Planner.
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import joblib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    RAW_DATA_FILE, PROCESSED_DATA_FILE, PROCESSED_DATA_DIR,
    SECTOR_INDICATORS, SCALER_PATH, MODEL_DIR,
)


def load_raw_data(filepath=None):
    """Load raw ward-level CSV data."""
    filepath = filepath or RAW_DATA_FILE
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Dataset not found at {filepath}. "
            f"Run 'python data/generate_dataset.py' first."
        )
    df = pd.read_csv(filepath)
    print(f"✅ Loaded {len(df)} wards from {filepath}")
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
            print(f"   ⚠️  Filled {col} nulls with median: {median_val:.2f}")

    # Validate ranges (clip extreme outliers)
    for col in all_indicators:
        if col in df.columns:
            q1 = df[col].quantile(0.01)
            q99 = df[col].quantile(0.99)
            original_count = len(df[(df[col] < q1) | (df[col] > q99)])
            if original_count > 0:
                df[col] = df[col].clip(q1, q99)

    print(f"✅ Data cleaning complete. Shape: {df.shape}")
    return df


def normalize_indicators(df):
    """
    Normalize all indicator columns to 0-1 scale using Min-Max scaling.
    Returns normalized df and the fitted scaler.
    """
    all_indicators = []
    for indicators in SECTOR_INDICATORS.values():
        all_indicators.extend(indicators)

    # Only normalize columns that exist
    available = [col for col in all_indicators if col in df.columns]

    scaler = MinMaxScaler()
    df_normalized = df.copy()
    df_normalized[available] = scaler.fit_transform(df[available])

    # Save scaler for later use
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(scaler, SCALER_PATH)
    print(f"✅ Normalized {len(available)} indicators to [0, 1] range")

    return df_normalized, scaler


def compute_sector_scores(df):
    """
    Compute a composite score per sector for each ward.
    For 'negative' polarity indicators, we invert them so higher = more vulnerable.
    """
    from config import SECTOR_INDICATORS

    # Indicators where higher value means MORE vulnerable (negative polarity)
    NEGATIVE_INDICATORS = {
        "disease_incidence_rate", "infant_mortality_rate", "dropout_rate",
        "student_teacher_ratio", "poverty_rate_bpl_pct", "flood_risk_score",
    }

    for sector, indicators in SECTOR_INDICATORS.items():
        available = [col for col in indicators if col in df.columns]
        if not available:
            continue

        sector_col = f"score_{sector.lower().replace(' ', '_').replace('&', 'and').replace('.', '')}"

        # For each indicator, invert if negative polarity
        adjusted_cols = []
        for col in available:
            if col in NEGATIVE_INDICATORS:
                # Invert: higher disease = higher vulnerability score
                df[f"_adj_{col}"] = df[col]
            else:
                # Invert: lower development = higher vulnerability score
                df[f"_adj_{col}"] = 1 - df[col]
            adjusted_cols.append(f"_adj_{col}")

        # Sector vulnerability score = mean of adjusted indicators
        df[sector_col] = df[adjusted_cols].mean(axis=1)

        # Clean up temporary columns
        df = df.drop(columns=adjusted_cols)

    print(f"✅ Computed vulnerability scores for {len(SECTOR_INDICATORS)} sectors")
    return df


def compute_overall_vulnerability(df):
    """Compute weighted overall vulnerability index for each ward."""
    from config import SECTOR_WEIGHTS

    score_cols = [col for col in df.columns if col.startswith("score_")]

    # Map score columns back to sector names for weighting
    sector_col_map = {}
    for sector in SECTOR_WEIGHTS:
        col_name = f"score_{sector.lower().replace(' ', '_').replace('&', 'and').replace('.', '')}"
        if col_name in score_cols:
            sector_col_map[sector] = col_name

    # Weighted sum
    df["vulnerability_index"] = 0.0
    for sector, col in sector_col_map.items():
        weight = SECTOR_WEIGHTS.get(sector, 0.1)
        df["vulnerability_index"] += df[col] * weight

    # Normalize to 0-1
    vi_min = df["vulnerability_index"].min()
    vi_max = df["vulnerability_index"].max()
    if vi_max > vi_min:
        df["vulnerability_index"] = (df["vulnerability_index"] - vi_min) / (vi_max - vi_min)

    # Categorize vulnerability
    df["vulnerability_category"] = pd.cut(
        df["vulnerability_index"],
        bins=[0, 0.3, 0.6, 1.0],
        labels=["Low", "Medium", "High"],
        include_lowest=True,
    )

    print(f"✅ Overall vulnerability index computed")
    print(f"   Distribution: {df['vulnerability_category'].value_counts().to_dict()}")
    return df


def identify_priority_sector(df):
    """Identify the most vulnerable (priority) sector for each ward."""
    score_cols = [col for col in df.columns if col.startswith("score_")]

    # For each ward, find the sector with the highest vulnerability score
    df["priority_sector"] = df[score_cols].idxmax(axis=1)
    # Clean up the column name to a readable sector name
    df["priority_sector"] = df["priority_sector"].str.replace("score_", "").str.replace("_", " ").str.title()

    print(f"✅ Priority sectors identified for each ward")
    return df


def preprocess_pipeline(filepath=None):
    """Run the full preprocessing pipeline."""
    print("\n" + "=" * 60)
    print("  Data Preprocessing Pipeline")
    print("=" * 60 + "\n")

    # Step 1: Load
    df = load_raw_data(filepath)

    # Step 2: Clean
    df = clean_data(df)

    # Step 3: Normalize
    df_normalized, scaler = normalize_indicators(df)

    # Step 4: Compute sector scores
    df_normalized = compute_sector_scores(df_normalized)

    # Step 5: Compute overall vulnerability
    df_normalized = compute_overall_vulnerability(df_normalized)

    # Step 6: Identify priority sectors
    df_normalized = identify_priority_sector(df_normalized)

    # Save processed data
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    df_normalized.to_csv(PROCESSED_DATA_FILE, index=False)
    print(f"\n💾 Processed data saved to {PROCESSED_DATA_FILE}")

    return df_normalized, scaler


if __name__ == "__main__":
    df, scaler = preprocess_pipeline()
    print("\n📊 Processed Data Preview:")
    cols_to_show = ["ward_name", "vulnerability_index", "vulnerability_category", "priority_sector"]
    available_cols = [c for c in cols_to_show if c in df.columns]
    print(df[available_cols].to_string(index=False))
