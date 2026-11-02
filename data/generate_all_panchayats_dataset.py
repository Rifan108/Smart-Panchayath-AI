"""
Synthetic Dataset Generator for ALL 14 Districts of Kerala.
Generates comprehensive ward-level socio-economic data across 56 representative
Grama Panchayats (1,200+ wards total) spanning all 8 sectors.
"""

import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SECTORS, SECTOR_INDICATORS, RAW_DATA_DIR
from data.kerala_geography import KERALA_DISTRICTS_DATA, PROFILE_TERRAIN_MODIFIERS
from data.generate_dataset import INDICATOR_PARAMS

np.random.seed(42)

ALL_PANCHAYATS_CSV = os.path.join(RAW_DATA_DIR, "kerala_all_panchayats_ward_data.csv")


def apply_terrain_modifiers(record, profile):
    """Apply geographic terrain and profile multipliers to indicators."""
    mods = PROFILE_TERRAIN_MODIFIERS.get(profile, {})
    
    mapping = {
        "flood_risk": ["flood_risk_score"],
        "water_body": ["water_body_health_index"],
        "cultivable": ["cultivable_land_pct"],
        "tourism": ["tourism_potential_index"],
        "digital": ["internet_penetration_pct", "digital_literacy_pct", "e_service_adoption_rate", "mobile_connectivity_index"],
        "msme": ["msme_density"],
        "employment": ["employment_rate"],
        "doctor": ["doctor_patient_ratio", "hospital_beds_per_1000"],
        "poverty": ["poverty_rate_bpl_pct"],
        "green_cover": ["green_cover_pct"],
        "sc_st": ["sc_st_population_pct"],
        "literacy": ["literacy_rate", "school_enrollment_ratio"],
        "farmer_income": ["farmer_income_level"],
        "irrigation": ["irrigation_coverage_pct"],
        "crop_yield": ["crop_yield_index"],
        "food_security": ["food_security_score"],
        "road_access": ["road_connectivity_index", "public_transport_access"],
        "waste": ["waste_management_coverage_pct"],
        "per_capita": ["per_capita_income"],
        "pension": ["pension_coverage_pct"],
        "safe_water": ["safe_drinking_water_pct"],
        "women_empowerment": ["women_empowerment_index"],
        "disaster": ["disaster_preparedness_score"],
    }
    
    for mod_key, factor in mods.items():
        if mod_key in mapping:
            for ind in mapping[mod_key]:
                if ind in record and ind in INDICATOR_PARAMS:
                    _, _, min_v, max_v, _ = INDICATOR_PARAMS[ind]
                    new_val = record[ind] * factor
                    record[ind] = float(np.clip(new_val, min_v, max_v))
                    if max_v <= 1.0:
                        record[ind] = round(record[ind], 3)
                    elif max_v <= 100:
                        record[ind] = round(record[ind], 1)
                    else:
                        record[ind] = int(record[ind])
    return record


def generate_all_kerala_dataset():
    """Generate ward-level data for all 14 districts and 56 panchayats in Kerala."""
    all_records = []
    global_ward_id = 1

    for district, dist_data in KERALA_DISTRICTS_DATA.items():
        panchayats = dist_data["panchayats"]
        for p_name, p_info in panchayats.items():
            num_wards = p_info["wards"]
            total_p_pop = p_info["pop"]
            profile = p_info["profile"]
            
            # Generate exact normalized ward populations that strictly sum to total_p_pop
            from data.panchayat_geography import normalize_ward_populations
            raw_weights = [np.random.uniform(0.75, 1.35) for _ in range(num_wards)]
            ward_populations = normalize_ward_populations(raw_weights, total_p_pop)
            assert sum(ward_populations) == total_p_pop

            for w_num in range(1, num_wards + 1):
                ward_name = f"{p_name} Ward {w_num}"
                
                # Special ward names for Manjeshwar for exact backward-compatibility
                if p_name == "Manjeshwar" and w_num <= 24:
                    from config import WARD_NAMES
                    if w_num - 1 < len(WARD_NAMES):
                        ward_name = WARD_NAMES[w_num - 1]

                ward_pop = ward_populations[w_num - 1]

                record = {
                    "ward_id": global_ward_id,
                    "district": district,
                    "panchayat_name": p_name,
                    "ward_number": w_num,
                    "ward_name": ward_name,
                    "ward_profile": profile,
                    "population": ward_pop,
                }

                # Generate base indicators
                for sector, indicators in SECTOR_INDICATORS.items():
                    for indicator in indicators:
                        mean, std, min_val, max_val, polarity = INDICATOR_PARAMS[indicator]
                        val = np.random.normal(mean, std)
                        val = np.clip(val, min_val, max_val)
                        if max_val <= 1.0:
                            record[indicator] = round(float(val), 3)
                        elif max_val <= 100:
                            record[indicator] = round(float(val), 1)
                        else:
                            record[indicator] = int(val)

                # Apply terrain modifiers
                record = apply_terrain_modifiers(record, profile)

                all_records.append(record)
                global_ward_id += 1

    df = pd.DataFrame(all_records)

    # Realistic inter-indicator relationships
    df["digital_literacy_pct"] = (
        df["digital_literacy_pct"] * 0.55 + df["literacy_rate"] * 0.45 * 0.55
    ).clip(12, 85).round(1)

    df["disease_incidence_rate"] = (
        df["disease_incidence_rate"] * 0.70 + df["poverty_rate_bpl_pct"] * 0.30 * 0.5
    ).clip(2, 20).round(1)

    df["e_service_adoption_rate"] = (
        df["e_service_adoption_rate"] * 0.60 + (df["internet_penetration_pct"] / 100) * 0.40
    ).clip(0.05, 0.85).round(3)

    df["per_capita_income"] = (
        df["per_capita_income"] * 0.65 + df["employment_rate"] * 1600 * 0.35
    ).clip(35000, 185000).astype(int)

    return df


def main():
    print("=" * 60)
    print("  Statewide Kerala Panchayat Dataset Generator")
    print("  Generating data for all 14 Districts and 56 Grama Panchayats")
    print("=" * 60)

    df = generate_all_kerala_dataset()
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    df.to_csv(ALL_PANCHAYATS_CSV, index=False)

    print(f"\n[OK] Statewide dataset created successfully!")
    print(f"   File: {ALL_PANCHAYATS_CSV}")
    print(f"   Total Districts: {df['district'].nunique()}")
    print(f"   Total Panchayats: {df['panchayat_name'].nunique()}")
    print(f"   Total Wards: {len(df)}")
    print(f"   Total Population Covered: {df['population'].sum():,}")
    print(f"\nPanchayats per District:")
    for dist, group in df.groupby("district"):
        panchayats_list = ", ".join(group["panchayat_name"].unique())
        print(f"   * {dist:18s} ({group['ward_id'].count()} wards): {panchayats_list}")

    return df


if __name__ == "__main__":
    main()
