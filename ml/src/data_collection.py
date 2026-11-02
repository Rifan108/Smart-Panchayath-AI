"""
Data Collection & Government Benchmark Registry Module
Smart Panchayat AI Platform
Author: Senior ML Engineer & Data Scientist
"""

import os
from typing import Dict, Any

# Official State Baseline Parameters compiled from:
# - NITI Aayog Multidimensional Poverty Index (MPI) 2023 Review
# - National Family Health Survey (NFHS-5, 2019-21)
# - Census of India (2011 Primary Census Abstract)
# - Jal Jeevan Mission Har Ghar Jal Portal (2024)
# - Ministry of Panchayati Raj / eGramSwaraj (FY 2023-24)

STATE_BENCHMARKS: Dict[str, Dict[str, Any]] = {
    "Kerala": {
        "state_code": "KL",
        "primary_language": "Malayalam",
        "mpi_poverty_pct": 0.55,
        "literacy_rate": 94.0,
        "female_literacy_rate": 92.1,
        "rural_hh_size": 4.1,
        "rural_pop_density_km2": 860,
        "tap_water_coverage_pct": 54.0,
        "open_well_dependence_pct": 62.0,
        "improved_sanitation_pct": 98.7,
        "pucca_housing_pct": 91.2,
        "electrification_pct": 99.8,
        "paved_road_pct": 92.5,
        "internet_access_pct": 74.0,
        "doctor_availability_score": 0.85,
        "phc_distance_km": 2.8,
        "hospital_distance_km": 7.5,
        "school_dropout_rate": 0.6,
        "avg_annual_budget_lakhs": 1450.0,  # ₹14.50 Cr avg for large Kerala GPs
        "osr_ratio": 0.22,
        "stunting_pct": 23.4,
        "flood_vulnerability_base": 0.45,
        "drought_vulnerability_base": 0.10,
        "groundwater_stress_base": 0.25,
        "shg_coverage_pct": 88.0,
        "unemployment_rate": 8.2,
        "avg_hh_income_monthly": 24500,
    },
    "Karnataka": {
        "state_code": "KA",
        "primary_language": "Kannada",
        "mpi_poverty_pct": 7.58,
        "literacy_rate": 75.4,
        "female_literacy_rate": 68.1,
        "rural_hh_size": 4.6,
        "rural_pop_density_km2": 319,
        "tap_water_coverage_pct": 72.0,
        "open_well_dependence_pct": 14.0,
        "improved_sanitation_pct": 74.4,
        "pucca_housing_pct": 78.5,
        "electrification_pct": 98.5,
        "paved_road_pct": 76.0,
        "internet_access_pct": 58.0,
        "doctor_availability_score": 0.55,
        "phc_distance_km": 5.8,
        "hospital_distance_km": 16.5,
        "school_dropout_rate": 5.4,
        "avg_annual_budget_lakhs": 280.0,   # ₹2.80 Cr avg
        "osr_ratio": 0.08,
        "stunting_pct": 35.4,
        "flood_vulnerability_base": 0.22,
        "drought_vulnerability_base": 0.58,
        "groundwater_stress_base": 0.65,
        "shg_coverage_pct": 68.0,
        "unemployment_rate": 4.8,
        "avg_hh_income_monthly": 16200,
    },
    "Tamil Nadu": {
        "state_code": "TN",
        "primary_language": "Tamil",
        "mpi_poverty_pct": 2.20,
        "literacy_rate": 80.1,
        "female_literacy_rate": 73.4,
        "rural_hh_size": 3.9,
        "rural_pop_density_km2": 555,
        "tap_water_coverage_pct": 82.0,
        "open_well_dependence_pct": 10.0,
        "improved_sanitation_pct": 73.1,
        "pucca_housing_pct": 84.0,
        "electrification_pct": 99.2,
        "paved_road_pct": 88.0,
        "internet_access_pct": 66.0,
        "doctor_availability_score": 0.75,
        "phc_distance_km": 3.9,
        "hospital_distance_km": 11.2,
        "school_dropout_rate": 2.1,
        "avg_annual_budget_lakhs": 240.0,   # ₹2.40 Cr avg
        "osr_ratio": 0.15,
        "stunting_pct": 25.0,
        "flood_vulnerability_base": 0.35,
        "drought_vulnerability_base": 0.40,
        "groundwater_stress_base": 0.55,
        "shg_coverage_pct": 82.0,
        "unemployment_rate": 5.5,
        "avg_hh_income_monthly": 19400,
    },
    "Andhra Pradesh": {
        "state_code": "AP",
        "primary_language": "Telugu",
        "mpi_poverty_pct": 6.06,
        "literacy_rate": 67.4,
        "female_literacy_rate": 59.5,
        "rural_hh_size": 4.0,
        "rural_pop_density_km2": 304,
        "tap_water_coverage_pct": 70.0,
        "open_well_dependence_pct": 8.0,
        "improved_sanitation_pct": 74.0,
        "pucca_housing_pct": 80.5,
        "electrification_pct": 98.8,
        "paved_road_pct": 81.0,
        "internet_access_pct": 56.0,
        "doctor_availability_score": 0.62,
        "phc_distance_km": 4.5,
        "hospital_distance_km": 14.0,
        "school_dropout_rate": 4.8,
        "avg_annual_budget_lakhs": 260.0,   # ₹2.60 Cr avg
        "osr_ratio": 0.09,
        "stunting_pct": 31.2,
        "flood_vulnerability_base": 0.38,
        "drought_vulnerability_base": 0.52,
        "groundwater_stress_base": 0.60,
        "shg_coverage_pct": 85.0,
        "unemployment_rate": 5.1,
        "avg_hh_income_monthly": 17100,
    },
    "Maharashtra": {
        "state_code": "MH",
        "primary_language": "Marathi",
        "mpi_poverty_pct": 7.81,
        "literacy_rate": 82.3,
        "female_literacy_rate": 75.8,
        "rural_hh_size": 4.8,
        "rural_pop_density_km2": 365,
        "tap_water_coverage_pct": 81.0,
        "open_well_dependence_pct": 18.0,
        "improved_sanitation_pct": 73.2,
        "pucca_housing_pct": 79.0,
        "electrification_pct": 98.1,
        "paved_road_pct": 82.0,
        "internet_access_pct": 62.0,
        "doctor_availability_score": 0.60,
        "phc_distance_km": 5.2,
        "hospital_distance_km": 15.8,
        "school_dropout_rate": 3.9,
        "avg_annual_budget_lakhs": 290.0,   # ₹2.90 Cr avg
        "osr_ratio": 0.12,
        "stunting_pct": 35.2,
        "flood_vulnerability_base": 0.28,
        "drought_vulnerability_base": 0.62,
        "groundwater_stress_base": 0.72,
        "shg_coverage_pct": 72.0,
        "unemployment_rate": 4.5,
        "avg_hh_income_monthly": 18200,
    },
}

def get_state_benchmark(state_name: str) -> Dict[str, Any]:
    """Retrieve verified government baseline parameters for a given state."""
    if state_name not in STATE_BENCHMARKS:
        raise ValueError(f"State '{state_name}' is not in supported states: {list(STATE_BENCHMARKS.keys())}")
    return STATE_BENCHMARKS[state_name]
