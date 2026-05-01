"""
Synthetic Dataset Generator for Manjeshwar Grama Panchayat
Generates realistic ward-level socio-economic data for 24 wards across 8 sectors.

Data is based on real Kasaragod district statistics with ward-level variations
reflecting geographic patterns (coastal vs interior, town-center vs rural).
"""

import os
import sys
import numpy as np
import pandas as pd

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import WARD_NAMES, SECTORS, SECTOR_INDICATORS, RAW_DATA_DIR

np.random.seed(42)


# ─── Ward Characteristics ──────────────────────────────────────────────
# Each ward has a "profile" that influences its indicator values.
# Categories: urban, semi_urban, rural, coastal
WARD_PROFILES = {
    "Hosabettu": "rural",
    "Mangalpady": "semi_urban",
    "Uppala East": "semi_urban",
    "Uppala West": "semi_urban",
    "Kudupu": "rural",
    "Manjeshwar Town North": "urban",
    "Manjeshwar Town South": "urban",       # KJM Road area
    "Pajeer": "rural",
    "Kalnad": "rural",
    "Kukkehalli": "rural",
    "Bevinje": "coastal",
    "Manjanady": "semi_urban",
    "Paika": "rural",
    "Enmakaje": "rural",
    "Miyapadav": "coastal",
    "Koliyadka": "rural",
    "Meenja": "rural",
    "Vorkady": "rural",
    "Badiadka East": "semi_urban",
    "Badiadka West": "semi_urban",
    "Kumbla North": "semi_urban",
    "Kumbla South": "semi_urban",
    "Perla": "rural",
    "Badiyadka Central": "semi_urban",
}

# Profile-based modifiers (higher = better for positive indicators)
PROFILE_MODIFIERS = {
    "urban": {"development": 1.20, "vulnerability": 0.80, "digital": 1.30},
    "semi_urban": {"development": 1.05, "vulnerability": 0.95, "digital": 1.10},
    "rural": {"development": 0.85, "vulnerability": 1.15, "digital": 0.75},
    "coastal": {"development": 0.90, "vulnerability": 1.10, "digital": 0.85},
}

# ─── Indicator Definitions ─────────────────────────────────────────────
# For each indicator: (base_mean, base_std, min_val, max_val, polarity)
# polarity: "positive" = higher is better, "negative" = higher is worse
INDICATOR_PARAMS = {
    # Health & Sanitation
    "disease_incidence_rate": (8.5, 3.0, 2.0, 20.0, "negative"),
    "hospital_beds_per_1000": (1.8, 0.8, 0.3, 4.5, "positive"),
    "doctor_patient_ratio": (0.5, 0.2, 0.1, 1.2, "positive"),
    "infant_mortality_rate": (10.0, 4.0, 3.0, 22.0, "negative"),
    "vaccination_coverage_pct": (85.0, 8.0, 60.0, 99.0, "positive"),

    # Education
    "literacy_rate": (92.0, 4.0, 78.0, 99.0, "positive"),
    "school_enrollment_ratio": (88.0, 6.0, 70.0, 99.0, "positive"),
    "dropout_rate": (5.0, 3.0, 0.5, 15.0, "negative"),
    "student_teacher_ratio": (28.0, 6.0, 15.0, 45.0, "negative"),
    "digital_classroom_pct": (35.0, 15.0, 5.0, 80.0, "positive"),

    # Infrastructure
    "road_connectivity_index": (0.65, 0.15, 0.2, 0.95, "positive"),
    "safe_drinking_water_pct": (78.0, 12.0, 40.0, 98.0, "positive"),
    "electrification_pct": (95.0, 4.0, 80.0, 100.0, "positive"),
    "housing_adequacy_pct": (72.0, 10.0, 45.0, 95.0, "positive"),
    "public_transport_access": (0.55, 0.20, 0.1, 0.95, "positive"),

    # Agriculture & Food Security
    "cultivable_land_pct": (45.0, 15.0, 10.0, 80.0, "positive"),
    "irrigation_coverage_pct": (38.0, 14.0, 8.0, 75.0, "positive"),
    "crop_yield_index": (0.60, 0.15, 0.2, 0.95, "positive"),
    "farmer_income_level": (45000, 15000, 15000, 90000, "positive"),
    "food_security_score": (0.70, 0.12, 0.3, 0.95, "positive"),

    # Social Welfare
    "poverty_rate_bpl_pct": (18.0, 8.0, 3.0, 40.0, "negative"),
    "sc_st_population_pct": (12.0, 6.0, 2.0, 30.0, "neutral"),
    "women_empowerment_index": (0.62, 0.12, 0.3, 0.90, "positive"),
    "disability_support_coverage": (0.45, 0.15, 0.1, 0.85, "positive"),
    "pension_coverage_pct": (55.0, 12.0, 25.0, 85.0, "positive"),

    # Economic Development
    "employment_rate": (58.0, 10.0, 30.0, 85.0, "positive"),
    "msme_density": (12.0, 6.0, 2.0, 35.0, "positive"),
    "per_capita_income": (85000, 25000, 35000, 160000, "positive"),
    "skill_training_coverage_pct": (22.0, 10.0, 5.0, 55.0, "positive"),
    "tourism_potential_index": (0.35, 0.18, 0.05, 0.85, "positive"),

    # Environment & Disaster Management
    "flood_risk_score": (0.40, 0.20, 0.05, 0.90, "negative"),
    "waste_management_coverage_pct": (45.0, 15.0, 10.0, 85.0, "positive"),
    "green_cover_pct": (55.0, 12.0, 20.0, 85.0, "positive"),
    "water_body_health_index": (0.60, 0.15, 0.2, 0.90, "positive"),
    "disaster_preparedness_score": (0.50, 0.15, 0.1, 0.85, "positive"),

    # Digital & E-Governance
    "internet_penetration_pct": (52.0, 18.0, 15.0, 90.0, "positive"),
    "digital_literacy_pct": (48.0, 16.0, 12.0, 85.0, "positive"),
    "e_service_adoption_rate": (0.30, 0.15, 0.05, 0.75, "positive"),
    "aadhaar_enrollment_pct": (88.0, 6.0, 70.0, 99.0, "positive"),
    "mobile_connectivity_index": (0.72, 0.12, 0.35, 0.95, "positive"),
}


def apply_profile_modifier(value, indicator, profile, params):
    """Apply ward profile modifier to an indicator value."""
    _, _, min_val, max_val, polarity = params
    mod = PROFILE_MODIFIERS[profile]

    if indicator in [
        "internet_penetration_pct", "digital_literacy_pct",
        "e_service_adoption_rate", "digital_classroom_pct",
        "mobile_connectivity_index",
    ]:
        modifier = mod["digital"]
    elif polarity == "negative":
        modifier = mod["vulnerability"]
    else:
        modifier = mod["development"]

    adjusted = value * modifier
    return np.clip(adjusted, min_val, max_val)


def add_correlations(df):
    """Add realistic inter-indicator correlations."""
    # Higher literacy → higher digital literacy
    df["digital_literacy_pct"] = df["digital_literacy_pct"] * 0.6 + df["literacy_rate"] * 0.4 * 0.55
    df["digital_literacy_pct"] = df["digital_literacy_pct"].clip(12, 85)

    # Higher poverty → higher disease incidence
    df["disease_incidence_rate"] = df["disease_incidence_rate"] * 0.7 + df["poverty_rate_bpl_pct"] * 0.3 * 0.5
    df["disease_incidence_rate"] = df["disease_incidence_rate"].clip(2, 20)

    # Better infrastructure → better e-governance adoption
    df["e_service_adoption_rate"] = df["e_service_adoption_rate"] * 0.6 + df["internet_penetration_pct"] / 100 * 0.4
    df["e_service_adoption_rate"] = df["e_service_adoption_rate"].clip(0.05, 0.75)

    # Higher employment → higher per capita income
    df["per_capita_income"] = (
        df["per_capita_income"] * 0.7
        + df["employment_rate"] * 1500 * 0.3
    )
    df["per_capita_income"] = df["per_capita_income"].clip(35000, 160000)

    # Coastal wards: higher flood risk, lower cultivable land, higher tourism
    for idx, row in df.iterrows():
        ward = row["ward_name"]
        if WARD_PROFILES.get(ward) == "coastal":
            df.at[idx, "flood_risk_score"] = min(0.90, row["flood_risk_score"] * 1.4)
            df.at[idx, "cultivable_land_pct"] = max(10, row["cultivable_land_pct"] * 0.7)
            df.at[idx, "tourism_potential_index"] = min(0.85, row["tourism_potential_index"] * 1.5)

    return df


def generate_dataset():
    """Generate the complete synthetic dataset for Manjeshwar Grama Panchayat."""
    records = []

    for ward_name in WARD_NAMES:
        profile = WARD_PROFILES[ward_name]
        record = {
            "ward_id": WARD_NAMES.index(ward_name) + 1,
            "ward_name": ward_name,
            "ward_profile": profile,
        }

        # Generate population for each ward (total ~41,515)
        base_pop = 41515 / 24
        pop_variation = np.random.uniform(0.6, 1.5)
        if profile == "urban":
            pop_variation *= 1.3
        record["population"] = int(base_pop * pop_variation)

        # Generate all indicator values
        for sector, indicators in SECTOR_INDICATORS.items():
            for indicator in indicators:
                params = INDICATOR_PARAMS[indicator]
                mean, std, min_val, max_val, polarity = params

                # Generate base value
                value = np.random.normal(mean, std)

                # Apply profile modifier
                value = apply_profile_modifier(value, indicator, profile, params)

                # Clip to valid range
                value = np.clip(value, min_val, max_val)

                # Round appropriately
                if max_val <= 1.0:
                    record[indicator] = round(float(value), 3)
                elif max_val <= 100:
                    record[indicator] = round(float(value), 1)
                else:
                    record[indicator] = int(value)

        records.append(record)

    df = pd.DataFrame(records)

    # Apply correlations
    df = add_correlations(df)

    # Normalize population to sum to ~41,515
    pop_sum = df["population"].sum()
    df["population"] = (df["population"] * 41515 / pop_sum).astype(int)

    return df


def main():
    """Generate and save the dataset."""
    print("=" * 60)
    print("  Manjeshwar Grama Panchayat — Synthetic Data Generator")
    print("=" * 60)

    df = generate_dataset()

    # Create output directory
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    # Save to CSV
    output_path = os.path.join(RAW_DATA_DIR, "manjeshwar_ward_data.csv")
    df.to_csv(output_path, index=False)

    print(f"\n✅ Dataset generated successfully!")
    print(f"   📄 File: {output_path}")
    print(f"   📊 Shape: {df.shape[0]} wards × {df.shape[1]} columns")
    print(f"   🏘️  Total Population: {df['population'].sum():,}")
    print(f"\n📋 Ward Summary:")
    print(df[["ward_id", "ward_name", "ward_profile", "population"]].to_string(index=False))

    print(f"\n📊 Indicator Statistics:")
    # Show stats for a few key indicators
    key_indicators = [
        "literacy_rate", "poverty_rate_bpl_pct", "disease_incidence_rate",
        "road_connectivity_index", "internet_penetration_pct"
    ]
    for ind in key_indicators:
        if ind in df.columns:
            print(f"   {ind}: mean={df[ind].mean():.2f}, "
                  f"min={df[ind].min():.2f}, max={df[ind].max():.2f}")

    return df


if __name__ == "__main__":
    main()
