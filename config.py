"""
Configuration settings for Kerala Smart Panchayat AI Planner
Focused on Manjeshwar Grama Panchayat, Kasaragod District, Kerala
"""

import os

# Load .env file if present (for local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ─── OpenAI Configuration ─────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-3.5-turbo"  # Cheapest OpenAI model
# Set to True only if you want remote GPT queries; False enables instant (<1ms) local ML diagnostics
ENABLE_OPENAI_EXPLANATIONS = os.getenv("ENABLE_OPENAI_EXPLANATIONS", "false").lower() in ("true", "1", "yes")

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database
DATABASE_PATH = os.path.join(BASE_DIR, "data", "panchayat.db")

# Data paths
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
RAW_DATA_FILE = os.path.join(RAW_DATA_DIR, "manjeshwar_ward_data.csv")
PROCESSED_DATA_FILE = os.path.join(PROCESSED_DATA_DIR, "processed_data.csv")

# Model paths
MODEL_DIR = os.path.join(BASE_DIR, "trained_models")
XGBOOST_MODEL_PATH = os.path.join(MODEL_DIR, "xgboost_model.joblib")
RF_MODEL_PATH = os.path.join(MODEL_DIR, "rf_model.joblib")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.joblib")

# Report output
REPORT_DIR = os.path.join(BASE_DIR, "reports")

# ─── Panchayat Configuration ───────────────────────────────────────────
PANCHAYAT_NAME = "Manjeshwar Grama Panchayat"
DISTRICT = "Kasaragod"
STATE = "Kerala"
TOTAL_WARDS = 24
POPULATION = 41515  # 2011 Census
AREA_SQ_KM = 24.4

# ─── Ward Names (Manjeshwar Grama Panchayat - 24 Wards) ────────────────
WARD_NAMES = [
    "Hosabettu",
    "Mangalpady",
    "Uppala East",
    "Uppala West",
    "Kudupu",
    "Manjeshwar Town North",
    "Manjeshwar Town South",  # KJM Road area
    "Pajeer",
    "Kalnad",
    "Kukkehalli",
    "Bevinje",
    "Manjanady",
    "Paika",
    "Enmakaje",
    "Miyapadav",
    "Koliyadka",
    "Meenja",
    "Vorkady",
    "Badiadka East",
    "Badiadka West",
    "Kumbla North",
    "Kumbla South",
    "Perla",
    "Badiyadka Central",
]

# ─── Development Sectors ───────────────────────────────────────────────
SECTORS = [
    "Health & Sanitation",
    "Education",
    "Infrastructure",
    "Agriculture & Food Security",
    "Social Welfare",
    "Economic Development",
    "Environment & Disaster Mgmt",
    "Digital & E-Governance",
]

# ─── Sector Indicators ─────────────────────────────────────────────────
SECTOR_INDICATORS = {
    "Health & Sanitation": [
        "disease_incidence_rate",
        "hospital_beds_per_1000",
        "doctor_patient_ratio",
        "infant_mortality_rate",
        "vaccination_coverage_pct",
    ],
    "Education": [
        "literacy_rate",
        "school_enrollment_ratio",
        "dropout_rate",
        "student_teacher_ratio",
        "digital_classroom_pct",
    ],
    "Infrastructure": [
        "road_connectivity_index",
        "safe_drinking_water_pct",
        "electrification_pct",
        "housing_adequacy_pct",
        "public_transport_access",
    ],
    "Agriculture & Food Security": [
        "cultivable_land_pct",
        "irrigation_coverage_pct",
        "crop_yield_index",
        "farmer_income_level",
        "food_security_score",
    ],
    "Social Welfare": [
        "poverty_rate_bpl_pct",
        "sc_st_population_pct",
        "women_empowerment_index",
        "disability_support_coverage",
        "pension_coverage_pct",
    ],
    "Economic Development": [
        "employment_rate",
        "msme_density",
        "per_capita_income",
        "skill_training_coverage_pct",
        "tourism_potential_index",
    ],
    "Environment & Disaster Mgmt": [
        "flood_risk_score",
        "waste_management_coverage_pct",
        "green_cover_pct",
        "water_body_health_index",
        "disaster_preparedness_score",
    ],
    "Digital & E-Governance": [
        "internet_penetration_pct",
        "digital_literacy_pct",
        "e_service_adoption_rate",
        "aadhaar_enrollment_pct",
        "mobile_connectivity_index",
    ],
}

# ─── Vulnerability Weights (domain-expert-informed) ────────────────────
# Higher weight = more important for overall vulnerability
SECTOR_WEIGHTS = {
    "Health & Sanitation": 0.20,
    "Education": 0.15,
    "Infrastructure": 0.15,
    "Agriculture & Food Security": 0.10,
    "Social Welfare": 0.15,
    "Economic Development": 0.10,
    "Environment & Disaster Mgmt": 0.08,
    "Digital & E-Governance": 0.07,
}

# ─── Budget Allocation Constraints ─────────────────────────────────────
DEFAULT_TOTAL_BUDGET = 50_00_000  # ₹50 Lakhs (typical Panchayat dev fund)
MIN_SECTOR_ALLOCATION_PCT = 5.0    # Minimum 5% per sector
MAX_SECTOR_ALLOCATION_PCT = 30.0   # Maximum 30% per sector
PRIORITY_BOOST_FACTOR = 1.25       # 25% boost for Top 3 sectors

# ─── ML Model Configuration ───────────────────────────────────────────
XGBOOST_PARAMS = {
    "n_estimators": 100,
    "max_depth": 5,
    "learning_rate": 0.1,
    "random_state": 42,
    "use_label_encoder": False,
    "eval_metric": "mlogloss",
}

RANDOM_FOREST_PARAMS = {
    "n_estimators": 100,
    "max_depth": 8,
    "random_state": 42,
    "n_jobs": -1,
}

CROSS_VALIDATION_FOLDS = 5

# ─── Dashboard Configuration ──────────────────────────────────────────────
DASH_DEBUG = os.getenv("DASH_DEBUG", "False").lower() == "true"
DASH_HOST = "0.0.0.0"  # Required for cloud deployment
DASH_PORT = int(os.getenv("PORT", "8050"))

# Color Palette
COLORS = {
    "primary": "#00695C",       # Kerala Green
    "primary_light": "#26A69A", # Teal accent
    "primary_dark": "#004D40",
    "background": "#0F1419",    # Dark background
    "card_bg": "rgba(255, 255, 255, 0.05)",
    "card_border": "rgba(255, 255, 255, 0.1)",
    "text_primary": "#E7E9EA",
    "text_secondary": "#8B98A5",
    "danger": "#F44336",
    "warning": "#FF9800",
    "success": "#4CAF50",
    "info": "#2196F3",
    "chart_colors": [
        "#26A69A", "#EF5350", "#AB47BC", "#42A5F5",
        "#66BB6A", "#FFA726", "#EC407A", "#78909C",
    ],
}
