"""
Sector Prioritizer — Pure math-based sector ranking.
Identifies Top 3 priority development sectors for each ward
based on computed vulnerability scores (no ML required).
"""

import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SECTOR_INDICATORS


def get_sector_scores_for_ward(df, ward_name):
    """
    Get a dict of {sector_name: vulnerability_score} for a ward.
    Sorted descending by score (most vulnerable first).
    """
    ward_row = df[df["ward_name"] == ward_name]
    if ward_row.empty:
        return {}

    scores = {}
    score_cols = [c for c in df.columns if c.startswith("score_")]
    for col in score_cols:
        # Convert column name back to readable sector name
        sector_name = (
            col.replace("score_", "")
               .replace("_and_", " & ")
               .replace("_", " ")
               .title()
        )
        scores[sector_name] = float(ward_row[col].values[0])

    return dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))


def get_top_n_sectors_for_ward(df, ward_name, n=3):
    """
    Return a list of top N priority sectors with confidence scores.
    Each item: {"sector": name, "confidence": float, "rank": int}
    """
    scores = get_sector_scores_for_ward(df, ward_name)
    if not scores:
        return []

    # Normalize scores to 0-1 confidence (relative to max)
    max_score = max(scores.values()) if scores else 1.0
    result = []
    for rank, (sector, score) in enumerate(list(scores.items())[:n], start=1):
        confidence = score / max_score if max_score > 0 else 0.0
        result.append({
            "sector": sector,
            "score": score,
            "confidence": min(confidence, 1.0),
            "rank": rank,
        })
    return result


def get_all_wards_top_sectors(df, n=3):
    """
    Return a dict of {ward_name: [top sector dicts]} for all wards.
    """
    result = {}
    for ward_name in df["ward_name"].tolist():
        result[ward_name] = get_top_n_sectors_for_ward(df, ward_name, n)
    return result


def assign_priority_columns(df):
    """
    Add priority_sector_1/2/3 and priority_confidence_1 columns to df.
    Pure math — no ML needed.
    """
    priority_1, priority_2, priority_3 = [], [], []
    conf_1, conf_2, conf_3 = [], [], []

    for _, row in df.iterrows():
        ward_name = row["ward_name"]
        top = get_top_n_sectors_for_ward(df[df["ward_name"] == ward_name], ward_name, n=3)

        priority_1.append(top[0]["sector"] if len(top) > 0 else "")
        priority_2.append(top[1]["sector"] if len(top) > 1 else "")
        priority_3.append(top[2]["sector"] if len(top) > 2 else "")
        conf_1.append(top[0]["confidence"] if len(top) > 0 else 0.0)
        conf_2.append(top[1]["confidence"] if len(top) > 1 else 0.0)
        conf_3.append(top[2]["confidence"] if len(top) > 2 else 0.0)

    df["priority_sector_1"] = priority_1
    df["priority_sector_2"] = priority_2
    df["priority_sector_3"] = priority_3
    df["priority_confidence_1"] = conf_1
    df["priority_confidence_2"] = conf_2
    df["priority_confidence_3"] = conf_3

    return df


def get_feature_importance_from_scores(df):
    """
    Compute which sector indicators contribute most to overall vulnerability
    across all wards (simple mean absolute contribution).
    Returns a sorted dict of {indicator: importance}.
    """
    all_indicators = []
    for indicators in SECTOR_INDICATORS.values():
        all_indicators.extend(indicators)

    available = [col for col in all_indicators if col in df.columns]
    importance = {}
    for col in available:
        importance[col] = float(df[col].std())  # variance across wards = importance

    return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
