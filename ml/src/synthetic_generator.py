"""
High-Fidelity Synthetic Dataset Generator for Smart Panchayat AI
Calibrated on Official National & State Benchmarks:
- PAI (Panchayat Advancement Index 2023)
- eGramSwaraj Fiscal Devolution Metrics
- Mission Antyodaya Eleventh Schedule Survey
- NITI Aayog Multidimensional Poverty Index (2023 Review)
- NFHS-5 State Fact Sheets
- Census of India 2011 PCA Demographics

Generates 60,000 synthetic Panchayat records across Kerala, Karnataka, Tamil Nadu, Andhra Pradesh, and Maharashtra.
Includes realistic multi-tier distribution (Aspirational/Critical, High Priority, Moderate, Good, Well Developed)
and balanced priority sectors (Water & Sanitation, Healthcare, Education, Infrastructure, Agriculture & Livelihood, Social Welfare).
"""

import os
import sys
import numpy as np
import pandas as pd
from typing import Dict, List, Any

# Ensure stdout handles unicode
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ADMIN_ROSTERS = {
    "Kerala": {
        "districts": ["Kasaragod", "Kannur", "Wayanad", "Kozhikode", "Malappuram", "Palakkad", 
                      "Thrissur", "Ernakulam", "Idukki", "Kottayam", "Alappuzha", "Pathanamthitta", 
                      "Kollam", "Thiruvananthapuram"],
        "taluk_prefix": ["Taluk", "Block"],
        "gp_suffixes": ["Gramam", "Panchayat", "Pura", "Kulam", "Cheri", "Kode", "Puzha", "Vayal", "Nadu", "Kavu"],
        "pop_mu": 32000,
        "pop_sigma": 7500,
        "pop_min": 14000,
        "pop_max": 65000,
    },
    "Karnataka": {
        "districts": ["Belagavi", "Vijayapura", "Kalaburagi", "Yadgir", "Raichur", "Ballari", 
                      "Shivamogga", "Udupi", "Dakshina Kannada", "Mysuru", "Mandya", "Hassan", 
                      "Tumakuru", "Kolar", "Chikkaballapura", "Bengaluru Rural"],
        "taluk_prefix": ["Taluk", "Hobli"],
        "gp_suffixes": ["Halli", "Pura", "Kote", "Nagara", "Gere", "Bavi", "Gowdanahalli", "Mane", "Wad"],
        "pop_mu": 5200,
        "pop_sigma": 1800,
        "pop_min": 1800,
        "pop_max": 14000,
    },
    "Tamil Nadu": {
        "districts": ["Kanchipuram", "Vellore", "Tiruvannamalai", "Salem", "Dharmapuri", "Coimbatore", 
                      "Erode", "Tiruchirappalli", "Thanjavur", "Madurai", "Dindigul", "Ramanathapuram", 
                      "Tirunelveli", "Kanniyakumari"],
        "taluk_prefix": ["Taluk", "Union"],
        "gp_suffixes": ["Patti", "Palayam", "Kottai", "Mangalam", "Kulam", "Ur", "Puram", "Cheri", "Veli"],
        "pop_mu": 4200,
        "pop_sigma": 1500,
        "pop_min": 1500,
        "pop_max": 12000,
    },
    "Andhra Pradesh": {
        "districts": ["Srikakulam", "Vizianagaram", "Visakhapatnam", "East Godavari", "West Godavari", 
                      "Krishna", "Guntur", "Prakasam", "Nellore", "Kurnool", "Anantapur", "YSR Kadapa", "Chittoor"],
        "taluk_prefix": ["Mandal"],
        "gp_suffixes": ["Palle", "Padu", "Valasa", "Gudem", "Cheruvu", "Puram", "Kunta", "Palem", "Veedhi"],
        "pop_mu": 3800,
        "pop_sigma": 1300,
        "pop_min": 1400,
        "pop_max": 10000,
    },
    "Maharashtra": {
        "districts": ["Nandurbar", "Dhule", "Jalgaon", "Nashik", "Ahmednagar", "Pune", "Satara", 
                      "Solapur", "Kolhapur", "Aurangabad", "Jalna", "Beed", "Nanded", "Amravati", 
                      "Yavatmal", "Nagpur", "Gadchiroli"],
        "taluk_prefix": ["Taluka", "Tehsil"],
        "gp_suffixes": ["Gaon", "Wadi", "Khed", "Bazar", "Pur", "Peth", "Ghar", "Pada", "Shir"],
        "pop_mu": 3400,
        "pop_sigma": 1600,
        "pop_min": 1200,
        "pop_max": 15000,
    },
}

def generate_state_dataset(state_name: str, n_records: int, seed: int = 42) -> pd.DataFrame:
    """Generate realistic synthetic records for a given state with diverse developmental tiers."""
    rng = np.random.default_rng(seed)
    from data_collection import get_state_benchmark
    bench = get_state_benchmark(state_name)
    roster = ADMIN_ROSTERS[state_name]

    # Assign developmental tier across Gram Panchayats:
    # Tier 0 (Aspirational / Severe Bottlenecks ~18%): high poverty, infrastructure deficit
    # Tier 1 (Developing / Moderate ~42%): average state condition
    # Tier 2 (Progressive / High Human Development ~40%): above average amenities
    tiers = rng.choice([0, 1, 2], size=n_records, p=[0.18, 0.42, 0.40])

    # Distinct local sector bottleneck to reflect real-world localized rural crises:
    # 0: Water crisis, 1: Healthcare deficit, 2: School/Education crisis, 3: Road/Infra gap, 4: Agrarian/Livelihood distress, 5: Welfare/Poverty distress
    bottlenecks = rng.choice([0, 1, 2, 3, 4, 5], size=n_records, p=[0.24, 0.20, 0.16, 0.18, 0.12, 0.10])

    # 1. Administrative
    districts = rng.choice(roster["districts"], size=n_records)
    subdistricts = [f"{dist} {rng.choice(roster['taluk_prefix'])} {rng.integers(1, 6)}" for dist in districts]
    gps = [f"{rng.choice(roster['districts'])[:4]}_{rng.choice(roster['gp_suffixes'])}_{i % 450 + 1}" for i in range(n_records)]
    villages = [f"{gp}_W{rng.integers(1, 21)}" for gp in gps]

    # Populations
    if state_name == "Kerala":
        pops = np.clip(rng.normal(roster["pop_mu"], roster["pop_sigma"], n_records), roster["pop_min"], roster["pop_max"]).astype(int)
    else:
        pops = np.clip(rng.lognormal(np.log(roster["pop_mu"]), 0.35, n_records), roster["pop_min"], roster["pop_max"]).astype(int)

    hh_size = np.clip(rng.normal(bench["rural_hh_size"], 0.25, n_records), 3.0, 6.5)
    households = (pops / hh_size).astype(int)
    densities = np.clip(rng.normal(bench["rural_pop_density_km2"], bench["rural_pop_density_km2"] * 0.2, n_records), 80, 2500).astype(int)

    # 2. Economic Indicators
    base_pov = bench["mpi_poverty_pct"] / 100.0
    tier_pov_mult = np.where(tiers == 0, 2.8, np.where(tiers == 1, 1.1, 0.5))
    pov_rates = np.clip(base_pov * tier_pov_mult * rng.uniform(0.7, 1.4, n_records), 0.002, 0.48)
    
    # Agrarian bottleneck shock
    agri_shock = (bottlenecks == 4)
    unemp_rates = np.clip(rng.normal(bench["unemployment_rate"] / 100.0, 0.015, n_records) + (agri_shock * 0.05), 0.02, 0.22)
    emp_rates = np.clip(1.0 - unemp_rates - (pov_rates * 0.35), 0.38, 0.95)
    
    base_inc = bench["avg_hh_income_monthly"]
    tier_inc_mult = np.where(tiers == 0, 0.65, np.where(tiers == 1, 0.95, 1.25))
    income = np.clip(base_inc * tier_inc_mult * (1.0 - 0.6 * pov_rates) + rng.normal(0, base_inc * 0.08, n_records), 6500, 75000).astype(int)
    
    agri_dep = np.clip(0.65 - (bench["mpi_poverty_pct"] * 0.01) + (agri_shock * 0.15) + rng.normal(0, 0.10, n_records) if state_name != "Kerala" else rng.normal(0.28, 0.08, n_records), 0.08, 0.92)
    self_emp = np.clip(bench["shg_coverage_pct"] / 100.0 * 0.35 + rng.normal(0, 0.05, n_records), 0.10, 0.60)
    livelihood_avail = np.clip(emp_rates * 0.55 + (1.0 - pov_rates) * 0.45 - (agri_shock * 0.25) + rng.normal(0, 0.04, n_records), 0.15, 0.98)

    # 3. Education Indicators
    edu_shock = (bottlenecks == 2)
    lit_base = bench["literacy_rate"] / 100.0
    tier_lit_delta = np.where(tiers == 0, -0.12, np.where(tiers == 1, 0.0, 0.05))
    literacy = np.clip(lit_base + tier_lit_delta - (edu_shock * 0.10) + rng.normal(0, 0.03, n_records), 0.40, 0.99)
    school_avail = np.clip((0.80 if state_name == "Kerala" else 0.68) + (tier_lit_delta * 0.5) - (edu_shock * 0.35) + rng.normal(0, 0.08, n_records), 0.20, 0.98)
    enrollment = np.clip(literacy * 0.45 + 0.50 - (edu_shock * 0.15) + rng.normal(0, 0.03, n_records), 0.55, 0.99)
    dropouts = np.clip((bench["school_dropout_rate"] / 100.0) * np.where(tiers == 0, 2.4, 1.0) + (edu_shock * 0.12) + rng.exponential(0.015, n_records), 0.002, 0.32)
    teacher_avail = np.clip((0.85 if state_name in ["Kerala", "Tamil Nadu"] else 0.70) - (edu_shock * 0.30) + rng.normal(0, 0.08, n_records), 0.25, 0.99)
    digital_edu = np.clip(literacy * 0.55 + bench["internet_access_pct"] / 100.0 * 0.45 - (edu_shock * 0.20) + rng.normal(0, 0.06, n_records), 0.10, 0.96)

    # 4. Healthcare Indicators
    health_shock = (bottlenecks == 1)
    tier_dist_mult = np.where(tiers == 0, 1.8, np.where(tiers == 1, 1.0, 0.6))
    phc_dist = np.clip(bench["phc_distance_km"] * tier_dist_mult * (1.0 + health_shock * 0.8) + rng.normal(0, 1.5, n_records), 0.5, 30.0)
    hosp_dist = np.clip(bench["hospital_distance_km"] * tier_dist_mult * (1.0 + health_shock * 0.8) + rng.normal(0, 3.0, n_records), 2.0, 65.0)
    phc_access = np.clip(1.0 - (phc_dist / 25.0) - (health_shock * 0.25), 0.08, 0.99)
    hosp_access = np.clip(1.0 - (hosp_dist / 50.0) - (health_shock * 0.20), 0.08, 0.96)
    doctor_avail = np.clip(bench["doctor_availability_score"] - (health_shock * 0.35) + rng.normal(0, 0.08, n_records), 0.10, 0.98)
    maternal_health = np.clip(1.0 - (pov_rates * 0.5) - (dropouts * 0.6) - (health_shock * 0.25) + rng.normal(0, 0.04, n_records), 0.25, 0.99)
    stunting = np.clip((bench["stunting_pct"] / 100.0) * np.where(tiers == 0, 1.4, 0.85) + (health_shock * 0.10) + rng.normal(0, 0.04, n_records), 0.06, 0.60)
    nutrition_score = np.clip(1.0 - stunting + rng.normal(0, 0.03, n_records), 0.35, 0.96)

    # 5. Water & Sanitation Indicators
    water_shock = (bottlenecks == 0)
    tap_base = bench["tap_water_coverage_pct"] / 100.0
    drinking_water = np.clip(tap_base * np.where(tiers == 0, 0.65, np.where(tiers == 1, 0.95, 1.15)) - (water_shock * 0.35) + rng.normal(0, 0.08, n_records), 0.10, 0.99)
    gw_dep = np.clip(bench["groundwater_stress_base"] + (water_shock * 0.25) + rng.normal(0, 0.08, n_records), 0.10, 0.98)
    water_avail = np.clip(1.0 - (gw_dep * 0.4) - (water_shock * 0.35) + rng.normal(0, 0.06, n_records), 0.10, 0.98)
    sanitation = np.clip((bench["improved_sanitation_pct"] / 100.0) * np.where(tiers == 0, 0.75, 1.0) - (water_shock * 0.15) + rng.normal(0, 0.05, n_records), 0.30, 0.99)
    waste_mgmt = np.clip(sanitation * 0.45 + (0.65 if state_name == "Kerala" else 0.35) + rng.normal(0, 0.08, n_records), 0.10, 0.95)
    water_scarcity = np.clip((1.0 - drinking_water) * 0.55 + gw_dep * 0.45 + (water_shock * 0.30) + rng.normal(0, 0.05, n_records), 0.05, 0.98)

    # 6. Infrastructure Indicators
    infra_shock = (bottlenecks == 3)
    roads = np.clip((bench["paved_road_pct"] / 100.0) * np.where(tiers == 0, 0.65, 1.0) - (infra_shock * 0.35) + rng.normal(0, 0.06, n_records), 0.20, 0.99)
    electricity = np.clip((bench["electrification_pct"] / 100.0) - (tiers == 0) * 0.05 - (infra_shock * 0.15) + rng.normal(0, 0.02, n_records), 0.70, 0.99)
    streetlights = np.clip(roads * 0.65 - (infra_shock * 0.25) + rng.normal(0.18, 0.06, n_records), 0.15, 0.98)
    pucca_house = np.clip((bench["pucca_housing_pct"] / 100.0) * np.where(tiers == 0, 0.75, 1.0) + rng.normal(0, 0.05, n_records), 0.35, 0.99)
    internet = np.clip((bench["internet_access_pct"] / 100.0) - (infra_shock * 0.25) + rng.normal(0, 0.07, n_records), 0.15, 0.96)
    public_infra = np.clip((roads * 0.4 + electricity * 0.3 + internet * 0.3) - (infra_shock * 0.25) + rng.normal(0, 0.04, n_records), 0.18, 0.98)

    # 7. Environmental Indicators
    flood_vuln = np.clip(bench["flood_vulnerability_base"] + rng.normal(0, 0.12, n_records), 0.05, 0.95)
    drought_vuln = np.clip(bench["drought_vulnerability_base"] + (water_shock * 0.20) + rng.normal(0, 0.12, n_records), 0.05, 0.95)
    green_cover = np.clip(0.85 - (densities / 3500.0) + rng.normal(0, 0.07, n_records), 0.15, 0.95)
    aqi = np.clip(rng.normal(55 if state_name in ["Kerala", "Karnataka"] else 85, 20, n_records), 25, 240).astype(int)
    water_quality = np.clip(1.0 - (water_scarcity * 0.35) - (sanitation < 0.70) * 0.20 + rng.normal(0, 0.05, n_records), 0.15, 0.98)
    climate_risk = np.clip(np.maximum(flood_vuln, drought_vuln) * 0.8 + rng.normal(0, 0.04, n_records), 0.10, 0.95)

    # 8. Financial Indicators
    bud_base = bench["avg_annual_budget_lakhs"]
    budgets = np.clip(bud_base * (pops / roster["pop_mu"])**0.6 * np.where(tiers == 0, 0.75, np.where(tiers == 1, 1.0, 1.25)) + rng.normal(0, bud_base * 0.12, n_records), 50.0, 3600.0).round(2)
    dev_funds = (budgets * rng.uniform(0.70, 0.88, n_records)).round(2)
    prev_exp = (dev_funds * np.where(tiers == 0, rng.uniform(0.60, 0.82, n_records), rng.uniform(0.78, 0.96, n_records))).round(2)
    unspent = (dev_funds - prev_exp).round(2)
    proj_completion = np.clip(prev_exp / dev_funds + rng.normal(0, 0.03, n_records), 0.45, 0.99).round(3)
    osr_ratio = np.clip(bench["osr_ratio"] * np.where(tiers == 0, 0.5, 1.1) + rng.normal(0, 0.02, n_records), 0.01, 0.42).round(3)

    # 9. Derived Domain Scores
    s_health = np.clip(0.25 * phc_access + 0.20 * doctor_avail + 0.25 * maternal_health + 0.15 * (1.0 - stunting) + 0.15 * hosp_access, 0.05, 0.99).round(4)
    s_edu = np.clip(0.30 * literacy + 0.25 * enrollment + 0.25 * (1.0 - dropouts) + 0.10 * teacher_avail + 0.10 * digital_edu, 0.05, 0.99).round(4)
    s_water = np.clip(0.35 * drinking_water + 0.25 * water_avail + 0.20 * (1.0 - water_scarcity) + 0.20 * water_quality, 0.05, 0.99).round(4)
    g_infra = np.clip(1.0 - (0.30 * roads + 0.25 * electricity + 0.20 * streetlights + 0.15 * internet + 0.10 * pucca_house), 0.01, 0.95).round(4)
    s_live = np.clip(0.30 * (1.0 - pov_rates) + 0.25 * emp_rates + 0.20 * self_emp + 0.25 * livelihood_avail, 0.05, 0.99).round(4)
    s_fin = np.clip(0.50 * proj_completion + 0.30 * (prev_exp / dev_funds) + 0.20 * (osr_ratio / 0.30), 0.10, 0.99).round(4)
    
    opds = np.clip(0.20 * s_health + 0.20 * s_edu + 0.20 * s_water + 0.15 * (1.0 - g_infra) + 0.15 * s_live + 0.10 * s_fin, 0.05, 0.99).round(4)

    # 10. Research-Driven Machine Learning Targets
    # Sector Deficits calibrated to create clean, balanced, research-driven priorities
    water_deficit = (1.0 - s_water) * 1.30 + (bottlenecks == 0) * 0.45
    health_deficit = (1.0 - s_health) * 1.30 + (bottlenecks == 1) * 0.45
    edu_deficit = (1.0 - s_edu) * 1.30 + (bottlenecks == 2) * 0.45
    infra_deficit = g_infra * 1.30 + (bottlenecks == 3) * 0.45
    agri_deficit = (1.0 - s_live) * 1.30 + (bottlenecks == 4) * 0.45
    welfare_deficit = (pov_rates * 2.0 + (1.0 - s_live) * 0.5) + (bottlenecks == 5) * 0.45

    deficit_matrix = np.column_stack([water_deficit, health_deficit, edu_deficit, infra_deficit, agri_deficit, welfare_deficit])
    sectors = ["Water & Sanitation", "Healthcare", "Education", "Infrastructure", "Agriculture & Livelihood", "Social Welfare"]
    priority_sector = [sectors[idx] for idx in np.argmax(deficit_matrix, axis=1)]

    # Development Gap Category calibrated to empirical distribution quantiles
    def categorize_opds(score):
        if score < 0.60:
            return "Critical"
        elif score < 0.70:
            return "High Priority"
        elif score < 0.77:
            return "Moderate"
        elif score < 0.83:
            return "Good"
        else:
            return "Well Developed"
    
    gap_category = [categorize_opds(s) for s in opds]

    # Specific Urgency Scores
    infra_urgency = np.clip(g_infra * 0.8 + (1.0 - roads) * 0.2, 0.05, 0.98).round(4)
    health_priority = np.clip((1.0 - s_health) * 0.7 + (1.0 - doctor_avail) * 0.3, 0.05, 0.98).round(4)
    edu_priority = np.clip((1.0 - s_edu) * 0.7 + dropouts * 1.5, 0.05, 0.98).round(4)
    water_priority = np.clip((1.0 - s_water) * 0.7 + water_scarcity * 0.3, 0.05, 0.98).round(4)

    # Estimated Development Budget Requirement (in ₹ Lakhs)
    est_budget_req = (budgets * (1.1 - opds)**1.3 * (pops / roster["pop_mu"])**0.35 * 1.15).round(2)

    # Recommended Budget Distribution (Summing to 100%)
    raw_shares = deficit_matrix + 0.15  # ensure statutory minimum
    norm_shares = raw_shares / raw_shares.sum(axis=1, keepdims=True) * 100.0

    df = pd.DataFrame({
        # Administrative
        "state": state_name,
        "district": districts,
        "block_taluk_mandal": subdistricts,
        "gram_panchayat": gps,
        "village_ward": villages,
        "population": pops,
        "households": households,
        "rural_population_density": densities,

        # Economic
        "poverty_rate": pov_rates.round(4),
        "employment_rate": emp_rates.round(4),
        "unemployment_rate": unemp_rates.round(4),
        "avg_household_income": income,
        "agricultural_dependency": agri_dep.round(4),
        "self_employment_rate": self_emp.round(4),
        "livelihood_availability_score": livelihood_avail.round(4),

        # Education
        "literacy_rate": literacy.round(4),
        "school_availability_score": school_avail.round(4),
        "student_enrollment_rate": enrollment.round(4),
        "school_dropout_rate": dropouts.round(4),
        "teacher_availability_ratio": teacher_avail.round(4),
        "digital_education_access": digital_edu.round(4),

        # Healthcare
        "primary_healthcare_access": phc_access.round(4),
        "hospital_accessibility_score": hosp_access.round(4),
        "doctor_availability_score": doctor_avail.round(4),
        "maternal_healthcare_access": maternal_health.round(4),
        "child_stunting_rate": stunting.round(4),
        "nutrition_score": nutrition_score.round(4),

        # Water & Sanitation
        "drinking_water_coverage": drinking_water.round(4),
        "water_availability_index": water_avail.round(4),
        "groundwater_dependency": gw_dep.round(4),
        "sanitation_coverage": sanitation.round(4),
        "waste_management_coverage": waste_mgmt.round(4),
        "water_scarcity_index": water_scarcity.round(4),

        # Infrastructure
        "road_connectivity_rate": roads.round(4),
        "electricity_coverage": electricity.round(4),
        "streetlight_availability": streetlights.round(4),
        "housing_quality_pucca": pucca_house.round(4),
        "internet_connectivity": internet.round(4),
        "public_infra_availability": public_infra.round(4),

        # Environmental
        "air_quality_index": aqi,
        "water_quality_index": water_quality.round(4),
        "flood_vulnerability": flood_vuln.round(4),
        "drought_vulnerability": drought_vuln.round(4),
        "green_cover_pct": green_cover.round(4),
        "climate_risk_index": climate_risk.round(4),

        # Financial
        "annual_panchayat_budget_lakhs": budgets,
        "available_dev_funds_lakhs": dev_funds,
        "previous_expenditure_lakhs": prev_exp,
        "unspent_budget_lakhs": unspent,
        "project_completion_rate": proj_completion,
        "own_source_revenue_ratio": osr_ratio,

        # Derived Domain Scores
        "healthcare_accessibility_score": s_health,
        "education_development_score": s_edu,
        "water_security_score": s_water,
        "infrastructure_gap_score": g_infra,
        "livelihood_opportunity_score": s_live,
        "financial_utilization_score": s_fin,
        "overall_development_score": opds,

        # Machine Learning Targets
        "priority_sector": priority_sector,
        "development_gap_category": gap_category,
        "infrastructure_urgency": infra_urgency,
        "healthcare_priority": health_priority,
        "education_priority": edu_priority,
        "water_sanitation_priority": water_priority,
        "estimated_development_requirement_lakhs": est_budget_req,

        # Recommended Budget Allocation (%)
        "rec_budget_water_pct": norm_shares[:, 0].round(2),
        "rec_budget_health_pct": norm_shares[:, 1].round(2),
        "rec_budget_edu_pct": norm_shares[:, 2].round(2),
        "rec_budget_infra_pct": norm_shares[:, 3].round(2),
        "rec_budget_agri_pct": norm_shares[:, 4].round(2),
        "rec_budget_welfare_pct": norm_shares[:, 5].round(2),

        # Provenance Metadata
        "is_synthetic": True,
    })

    return df

def generate_and_save_all(records_per_state: int = 12000, output_dir: str = "ml/datasets/synthetic"):
    """Generate 60,000 synthetic records, saving individual state and combined files."""
    os.makedirs(output_dir, exist_ok=True)
    all_dfs = []
    states = ["Kerala", "Karnataka", "Tamil Nadu", "Andhra Pradesh", "Maharashtra"]

    print(f"Generating balanced synthetic dataset: {records_per_state} records/state across {len(states)} states (Total: {records_per_state * len(states):,} records)...")

    for i, state in enumerate(states):
        print(f"  -> Generating {state}...")
        df_state = generate_state_dataset(state, records_per_state, seed=100 + i * 37)
        slug = state.lower().replace(" ", "_")
        
        # Save individual state datasets
        csv_path = os.path.join(output_dir, f"synthetic_panchayats_{slug}.csv")
        parquet_path = os.path.join(output_dir, f"synthetic_panchayats_{slug}.parquet")
        df_state.to_csv(csv_path, index=False)
        df_state.to_parquet(parquet_path, index=False, engine="pyarrow")
        print(f"     Saved {csv_path} ({len(df_state):,} rows) and .parquet")
        all_dfs.append(df_state)

    combined_df = pd.concat(all_dfs, ignore_index=True)
    comb_csv = os.path.join(output_dir, "synthetic_panchayats_all_5_states.csv")
    comb_parquet = os.path.join(output_dir, "synthetic_panchayats_all_5_states.parquet")
    combined_df.to_csv(comb_csv, index=False)
    combined_df.to_parquet(comb_parquet, index=False, engine="pyarrow")

    print(f"\n[SUCCESS] Successfully generated and saved {len(combined_df):,} records:")
    print(f"  - Combined CSV: {comb_csv} ({os.path.getsize(comb_csv) / 1024 / 1024:.2f} MB)")
    print(f"  - Combined Parquet: {comb_parquet} ({os.path.getsize(comb_parquet) / 1024 / 1024:.2f} MB)")
    print(f"\n[TARGET DISTRIBUTIONS]:")
    print(f"Priority Sector:\n{combined_df['priority_sector'].value_counts()}")
    print(f"\nDevelopment Gap Category:\n{combined_df['development_gap_category'].value_counts()}")

if __name__ == "__main__":
    records = 12000
    if len(sys.argv) > 1:
        records = int(sys.argv[1])
    generate_and_save_all(records_per_state=records)
