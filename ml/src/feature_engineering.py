"""
Feature Engineering Module for Smart Panchayat AI
Calculates domain scores, non-linear cross-sector interaction features,
and state-calibrated vulnerability indices.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple

class PanchayatFeatureEngineer:
    """Computes transparent domain scores and non-linear interactions for rural development analysis."""

    def __init__(self):
        pass

    def compute_domain_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate the 6 core domain scores and composite overall development score (OPDS)."""
        df = df.copy()

        # 1. Healthcare Accessibility Score
        phc = df.get("primary_healthcare_access", 0.7)
        doc = df.get("doctor_availability_score", 0.7)
        mat = df.get("maternal_healthcare_access", 0.8)
        stunt = df.get("child_stunting_rate", 0.25)
        hosp = df.get("hospital_accessibility_score", 0.6)
        df["healthcare_accessibility_score"] = np.clip(
            0.25 * phc + 0.20 * doc + 0.25 * mat + 0.15 * (1.0 - stunt) + 0.15 * hosp,
            0.05, 0.99
        ).round(4)

        # 2. Education Development Score
        lit = df.get("literacy_rate", 0.8)
        enrol = df.get("student_enrollment_rate", 0.85)
        drop = df.get("school_dropout_rate", 0.05)
        teach = df.get("teacher_availability_ratio", 0.75)
        dig_edu = df.get("digital_education_access", 0.6)
        df["education_development_score"] = np.clip(
            0.30 * lit + 0.25 * enrol + 0.25 * (1.0 - drop) + 0.10 * teach + 0.10 * dig_edu,
            0.05, 0.99
        ).round(4)

        # 3. Water Security Score
        tap = df.get("drinking_water_coverage", 0.7)
        avail = df.get("water_availability_index", 0.7)
        scarcity = df.get("water_scarcity_index", 0.3)
        quality = df.get("water_quality_index", 0.75)
        df["water_security_score"] = np.clip(
            0.35 * tap + 0.25 * avail + 0.20 * (1.0 - scarcity) + 0.20 * quality,
            0.05, 0.99
        ).round(4)

        # 4. Infrastructure Gap Score (Deficit: 1 = extreme gap, 0 = no gap)
        roads = df.get("road_connectivity_rate", 0.8)
        elec = df.get("electricity_coverage", 0.95)
        lights = df.get("streetlight_availability", 0.7)
        net = df.get("internet_connectivity", 0.6)
        house = df.get("housing_quality_pucca", 0.8)
        df["infrastructure_gap_score"] = np.clip(
            1.0 - (0.30 * roads + 0.25 * elec + 0.20 * lights + 0.15 * net + 0.10 * house),
            0.01, 0.95
        ).round(4)

        # 5. Livelihood Opportunity Score
        pov = df.get("poverty_rate", 0.10)
        emp = df.get("employment_rate", 0.80)
        self_emp = df.get("self_employment_rate", 0.30)
        live_avail = df.get("livelihood_availability_score", 0.70)
        df["livelihood_opportunity_score"] = np.clip(
            0.30 * (1.0 - pov) + 0.25 * emp + 0.20 * self_emp + 0.25 * live_avail,
            0.05, 0.99
        ).round(4)

        # 6. Financial Utilization Score
        comp = df.get("project_completion_rate", 0.85)
        prev_exp = df.get("previous_expenditure_lakhs", 100.0)
        dev_funds = df.get("available_dev_funds_lakhs", 120.0)
        osr = df.get("own_source_revenue_ratio", 0.10)
        exp_ratio = np.clip(prev_exp / (dev_funds + 1e-5), 0.0, 1.5)
        df["financial_utilization_score"] = np.clip(
            0.50 * comp + 0.30 * exp_ratio + 0.20 * (osr / 0.30),
            0.10, 0.99
        ).round(4)

        # Overall Panchayat Development Score (OPDS)
        df["overall_development_score"] = np.clip(
            0.20 * df["healthcare_accessibility_score"] +
            0.20 * df["education_development_score"] +
            0.20 * df["water_security_score"] +
            0.15 * (1.0 - df["infrastructure_gap_score"]) +
            0.15 * df["livelihood_opportunity_score"] +
            0.10 * df["financial_utilization_score"],
            0.05, 0.99
        ).round(4)

        return df

    def compute_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create non-linear domain interaction terms that expose compounded vulnerabilities."""
        df = df.copy()

        # Water Stress Interaction: Unpiped households * groundwater stress
        df["water_stress_interaction"] = (
            (1.0 - df["drinking_water_coverage"]) * df["groundwater_dependency"]
        ).round(4)

        # Health Deprivation Interaction: Child stunting * distance / lack of PHC
        df["health_burden_interaction"] = (
            df["child_stunting_rate"] * (1.0 - df["primary_healthcare_access"])
        ).round(4)

        # Education Deficit Interaction: Dropouts exacerbated by poor teacher availability
        df["education_barrier_interaction"] = (
            df["school_dropout_rate"] * (1.0 - df["teacher_availability_ratio"])
        ).round(4)

        # Economic Precarity: Poverty rate * Unemployment rate
        df["economic_precarity_interaction"] = (
            df["poverty_rate"] * df["unemployment_rate"]
        ).round(4)

        # Connectivity Isolation: Broken roads * lack of internet
        df["connectivity_isolation_interaction"] = (
            (1.0 - df["road_connectivity_rate"]) * (1.0 - df["internet_connectivity"])
        ).round(4)

        # Fiscal Absorption Lag: Ratio of unspent funds to total annual budget
        df["fiscal_absorption_lag"] = (
            df["unspent_budget_lakhs"] / (df["annual_panchayat_budget_lakhs"] + 1e-5)
        ).clip(0.0, 1.0).round(4)

        # Population Pressure Scale
        df["pop_density_log"] = np.log1p(df["rural_population_density"]).round(4)
        df["population_log"] = np.log1p(df["population"]).round(4)

        return df

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Complete feature engineering pipeline."""
        df = self.compute_domain_scores(df)
        df = self.compute_interaction_features(df)
        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.fit_transform(df)
