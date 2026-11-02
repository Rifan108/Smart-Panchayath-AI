"""
Multi-State Panchayat Data Generator (Calibrated to Real Government Statistics)
States: Kerala, Karnataka, Tamil Nadu, Andhra Pradesh, Maharashtra
Grounded in NITI Aayog MPI 2023, Census 2011/Projections, NFHS-5, and MoPR LGD
"""

import os
import sys
import numpy as np
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SECTORS, SECTOR_INDICATORS, RAW_DATA_DIR
from data.panchayat_geography import (
    STATES_PANCHAYAT_DATA, STATE_REAL_BENCHMARKS,
    KERALA_DISTRICT_BENCHMARKS, ALL_DISTRICT_BENCHMARKS,
    get_district_benchmark, get_location_lgd_identifiers,
    normalize_ward_populations
)
from data.generate_dataset import INDICATOR_PARAMS

np.random.seed(42)

MULTI_STATE_CSV = os.path.join(RAW_DATA_DIR, "panchayats_multi_state_data.csv")


def generate_ward_record(state_name, district_name, panchayat_name, ward_num, ward_name, profile, ward_pop, global_id, taluk="N/A", constituency="N/A", mla_name="N/A", mla_party="N/A"):
    """Generate a single ward record calibrated to real state & district benchmarks."""
    benchmarks = STATE_REAL_BENCHMARKS.get(state_name, STATE_REAL_BENCHMARKS["Kerala"]).copy()
    
    # Override with fine-grained District Benchmarks across all 5 states
    d_bench = get_district_benchmark(state_name, district_name)
    if d_bench:
        for k, v in d_bench.items():
            benchmarks[k] = v

    lgds = get_location_lgd_identifiers(state_name, district_name, panchayat_name)

    record = {
        "ward_id": global_id,
        "state": state_name,
        "state_lgd": lgds.get("state_lgd", None),
        "district": district_name,
        "district_lgd": lgds.get("district_lgd", None),
        "panchayat_name": panchayat_name,
        "panchayat_lgd": lgds.get("panchayat_lgd", None),
        "geographical_level": "GRAM_PANCHAYAT",
        "taluk": taluk,
        "assembly_constituency": constituency,
        "mla_name": mla_name,
        "mla_party": mla_party,
        "ward_number": ward_num,
        "ward_name": ward_name,
        "ward_profile": profile,
        "population": ward_pop,
        "is_synthetic": True,
        "data_provenance": "MoPR LGD / NITI Aayog MPI 2023 Calibrated Ward Data",
    }

    # Generate each indicator based on base distribution + state/district benchmark offsets
    for indicator, (base_m, base_s, min_v, max_v, polarity) in INDICATOR_PARAMS.items():
        if indicator == "literacy_rate":
            mean_val = benchmarks.get("literacy_rate", base_m)
            std_val = 2.2
        elif indicator == "poverty_rate_bpl_pct":
            # Real BPL headcount ratio calibrated to NITI Aayog MPI
            mpi = benchmarks.get("mpi_poverty_pct", 5.0)
            mean_val = max(0.8, mpi * 2.2) if mpi > 0 else 0.5
            std_val = max(0.5, mean_val * 0.22)
        elif indicator == "infant_mortality_rate":
            mean_val = benchmarks.get("infant_mortality_rate", base_m)
            std_val = max(1.0, mean_val * 0.18)
        elif indicator == "safe_drinking_water_pct":
            mean_val = benchmarks.get("safe_drinking_water_pct", base_m)
            std_val = 5.0
        elif indicator == "electrification_pct":
            mean_val = benchmarks.get("electrification_pct", base_m)
            std_val = 1.0
        elif indicator == "internet_penetration_pct":
            mean_val = benchmarks.get("internet_penetration_pct", base_m)
            std_val = 6.5
        elif indicator == "digital_literacy_pct":
            mean_val = benchmarks.get("digital_literacy_pct", base_m)
            std_val = 6.0
        elif indicator == "doctor_patient_ratio":
            mean_val = benchmarks.get("doctor_patient_ratio", base_m)
            std_val = 0.12
        elif indicator == "hospital_beds_per_1000":
            mean_val = benchmarks.get("hospital_beds_per_1000", base_m)
            std_val = 0.35
        elif indicator == "women_empowerment_index":
            mean_val = benchmarks.get("women_empowerment_index", base_m)
            std_val = 0.06
        elif indicator == "per_capita_income":
            mean_val = benchmarks.get("per_capita_income", base_m)
            std_val = 28000
        elif indicator == "flood_risk_score":
            mean_val = benchmarks.get("flood_risk_base", 0.40)
            std_val = 0.10
        elif indicator == "sc_st_population_pct" and "sc_st_pct" in benchmarks:
            mean_val = benchmarks["sc_st_pct"]
            std_val = max(1.5, mean_val * 0.25)
        else:
            mean_val = base_m
            std_val = base_s

        # Sample with normal distribution
        raw_val = np.random.normal(mean_val, std_val)

        # Profile/terrain effects
        if "coastal" in profile:
            if indicator in ["flood_risk_score", "water_body_health_index"]:
                raw_val *= 1.25
            elif indicator in ["tourism_potential_index"]:
                raw_val *= 1.30
        elif "highland" in profile or "hilly" in profile:
            if indicator in ["green_cover_pct"]:
                raw_val *= 1.40
            elif indicator in ["road_connectivity_index", "internet_penetration_pct"]:
                raw_val *= 0.85
        elif "tribal" in profile or "forest" in profile:
            if indicator in ["sc_st_population_pct"]:
                raw_val = np.random.uniform(22.0, 55.0)
            elif indicator in ["poverty_rate_bpl_pct"]:
                raw_val *= 1.30
            elif indicator in ["green_cover_pct"]:
                raw_val *= 1.45
        elif "urban" in profile or "tech" in profile or "industrial" in profile:
            if indicator in ["internet_penetration_pct", "digital_literacy_pct", "e_service_adoption_rate"]:
                raw_val *= 1.30
            elif indicator in ["msme_density", "employment_rate", "per_capita_income"]:
                raw_val *= 1.25
            elif indicator in ["green_cover_pct"]:
                raw_val *= 0.70
        elif "agricultural" in profile or "paddy" in profile or "delta" in profile or "sugar" in profile:
            if indicator in ["cultivable_land_pct", "irrigation_coverage_pct", "crop_yield_index"]:
                raw_val *= 1.30

        clipped_val = float(np.clip(raw_val, min_v, max_v))
        if max_v <= 1.0:
            record[indicator] = round(clipped_val, 3)
        elif max_v <= 100:
            record[indicator] = round(clipped_val, 1)
        else:
            record[indicator] = int(clipped_val)

    return record


def generate_multi_state_dataset():
    """Generate ward-level data for all 5 states, 36 districts, 144 panchayats."""
    print("=" * 65)
    print("  Multi-State Synthetic Data Generator (Calibrated to Real Stats)")
    print("  States: Kerala, Karnataka, Tamil Nadu, Andhra Pradesh, Maharashtra")
    print("  Exact Census Population Normalization Enabled")
    print("=" * 65)

    all_records = []
    global_ward_id = 1

    for state_name, state_info in STATES_PANCHAYAT_DATA.items():
        districts = state_info["districts"]
        for dist_name, dist_info in districts.items():
            panchayats = dist_info["panchayats"]
            for p_name, p_info in panchayats.items():
                num_wards = p_info["wards"]
                pop_total = p_info["pop"]
                profile = p_info["profile"]

                taluk = p_info.get("taluk", p_name)
                constituency = p_info.get("constituency", p_name)
                mla_name = p_info.get("mla", "N/A")
                mla_party = p_info.get("party", "N/A")

                # Generate raw proportional weights across wards
                raw_weights = []
                for w in range(1, num_wards + 1):
                    w_weight = np.random.uniform(0.75, 1.35)
                    if "urban" in profile and 3 <= w <= 8:
                        w_weight *= 1.25
                    raw_weights.append(w_weight)

                # Exactly normalize ward populations to strictly sum to pop_total
                ward_populations = normalize_ward_populations(raw_weights, pop_total)
                assert sum(ward_populations) == pop_total, f"Population sum error in {p_name}"

                for w_num in range(1, num_wards + 1):
                    # Preserve exact historical ward names for Manjeshwar
                    if state_name == "Kerala" and p_name == "Manjeshwar" and w_num <= 24:
                        from config import WARD_NAMES
                        ward_name = WARD_NAMES[w_num - 1] if w_num - 1 < len(WARD_NAMES) else f"Ward {w_num}"
                    else:
                        ward_name = f"{p_name} Ward {w_num}"

                    ward_pop = ward_populations[w_num - 1]

                    rec = generate_ward_record(
                        state_name=state_name,
                        district_name=dist_name,
                        panchayat_name=p_name,
                        ward_num=w_num,
                        ward_name=ward_name,
                        profile=profile,
                        ward_pop=ward_pop,
                        global_id=global_ward_id,
                        taluk=taluk,
                        constituency=constituency,
                        mla_name=mla_name,
                        mla_party=mla_party,
                    )
                    all_records.append(rec)
                    global_ward_id += 1

    df = pd.DataFrame(all_records)

    # Realistic inter-indicator relationships grounded in public data patterns
    if "digital_literacy_pct" in df.columns and "literacy_rate" in df.columns:
        df["digital_literacy_pct"] = (
            df["digital_literacy_pct"] * 0.55 + df["literacy_rate"] * 0.45 * 0.55
        ).clip(12, 85).round(1)

    if "disease_incidence_rate" in df.columns and "poverty_rate_bpl_pct" in df.columns:
        df["disease_incidence_rate"] = (
            df["disease_incidence_rate"] * 0.70 + df["poverty_rate_bpl_pct"] * 0.30 * 0.5
        ).clip(2, 20).round(1)

    if "e_service_adoption_rate" in df.columns and "internet_penetration_pct" in df.columns:
        df["e_service_adoption_rate"] = (
            df["e_service_adoption_rate"] * 0.60 + (df["internet_penetration_pct"] / 100) * 0.40
        ).clip(0.05, 0.85).round(3)

    if "per_capita_income" in df.columns and "employment_rate" in df.columns:
        df["per_capita_income"] = (
            df["per_capita_income"] * 0.65 + df["employment_rate"] * 1600 * 0.35
        ).clip(35000, 310000).astype(int)

    # Save to raw data folder
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    df.to_csv(MULTI_STATE_CSV, index=False)
    
    # Also overwrite kerala_all_panchayats_ward_data.csv with the full dataset for seamless backward-compatibility
    legacy_path = os.path.join(RAW_DATA_DIR, "kerala_all_panchayats_ward_data.csv")
    df.to_csv(legacy_path, index=False)

    print(f"\n[OK] Multi-state dataset generated successfully!")
    print(f"   File: {MULTI_STATE_CSV}")
    print(f"   Dimensions: {df.shape[0]} wards x {df.shape[1]} columns")
    print(f"   States: {df['state'].nunique()} ({', '.join(df['state'].unique())})")
    print(f"   Districts: {df['district'].nunique()}")
    print(f"   Grama Panchayats: {df['panchayat_name'].nunique()}")
    print(f"   Total Population: {df['population'].sum():,}")

    return df


def main():
    return generate_multi_state_dataset()


if __name__ == "__main__":
    main()
