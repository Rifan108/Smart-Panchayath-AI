"""
SHAP Explainer Module — Provides explainable AI insights for sector prioritization.
Generates waterfall, summary, force plots, and natural language explanations.
"""

import sys, os
import numpy as np
import pandas as pd
import shap
import joblib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MODEL_DIR, XGBOOST_MODEL_PATH, SECTOR_INDICATORS


def create_explainer(model, X_background=None):
    """Create a SHAP TreeExplainer for a tree-based model."""
    if X_background is not None:
        return shap.TreeExplainer(model, X_background)
    return shap.TreeExplainer(model)


def get_shap_values(explainer, X):
    """Compute SHAP values for input data."""
    return explainer(X)


def get_feature_shap_for_ward(shap_values, ward_idx, feature_names, top_n=10):
    """Get top N SHAP feature contributions for a specific ward."""
    if hasattr(shap_values, 'values'):
        vals = shap_values.values[ward_idx]
    else:
        vals = shap_values[ward_idx]

    # If multi-class, take the predicted class
    if len(vals.shape) > 1:
        class_idx = np.argmax(np.abs(vals).sum(axis=0))
        vals = vals[:, class_idx] if vals.shape[1] > 1 else vals[:, 0]

    importance = list(zip(feature_names, vals))
    importance.sort(key=lambda x: abs(x[1]), reverse=True)
    return importance[:top_n]


def generate_natural_language_explanation(ward_name, sector_name, shap_contributions, vulnerability_score):
    """
    Generate a detailed, location-specific, actionable explanation of why a sector
    was prioritized for a ward in Manjeshwar Grama Panchayat.
    Uses plain language and provides concrete development recommendations.
    """
    top_features = shap_contributions[:5]
    total_abs = sum(abs(v) for _, v in top_features)

    positive_drivers = [(f, v) for f, v in top_features if v > 0]
    negative_drivers = [(f, v) for f, v in top_features if v < 0]

    # ─── Readable feature name mapping ───
    FEATURE_LABELS = {
        "disease_incidence_rate": "rate of diseases reported",
        "hospital_beds_per_1000": "number of hospital beds available per 1,000 residents",
        "doctor_patient_ratio": "number of doctors available per patient",
        "infant_mortality_rate": "infant mortality rate (deaths per 1,000 live births)",
        "vaccination_coverage_pct": "percentage of children who received vaccination",
        "literacy_rate": "literacy rate among adults",
        "school_enrollment_ratio": "school enrollment rate for children",
        "dropout_rate": "school dropout rate among students",
        "student_teacher_ratio": "number of students per teacher",
        "digital_classroom_pct": "percentage of classrooms with digital facilities",
        "road_connectivity_index": "quality and connectivity of roads",
        "safe_drinking_water_pct": "percentage of households with safe drinking water",
        "electrification_pct": "percentage of households with electricity",
        "housing_adequacy_pct": "percentage of families living in adequate housing",
        "public_transport_access": "access to public bus and auto services",
        "cultivable_land_pct": "percentage of land available for farming",
        "irrigation_coverage_pct": "percentage of farmland with proper irrigation",
        "crop_yield_index": "average crop output compared to district average",
        "farmer_income_level": "average income of farming families",
        "food_security_score": "level of food availability and affordability",
        "poverty_rate_bpl_pct": "percentage of families below the poverty line (BPL)",
        "sc_st_population_pct": "percentage of SC/ST population",
        "women_empowerment_index": "women's participation in economic and social life",
        "disability_support_coverage": "coverage of disability support and welfare",
        "pension_coverage_pct": "percentage of eligible people receiving pension",
        "employment_rate": "employment rate among working-age population",
        "msme_density": "number of small businesses and enterprises",
        "per_capita_income": "average annual income per person",
        "skill_training_coverage_pct": "percentage of youth who received skill training",
        "tourism_potential_index": "potential for tourism-based income",
        "flood_risk_score": "risk of flooding during monsoon",
        "waste_management_coverage_pct": "coverage of waste collection and disposal",
        "green_cover_pct": "percentage of area covered by trees and vegetation",
        "water_body_health_index": "health of rivers, ponds, and water bodies",
        "disaster_preparedness_score": "preparedness level for natural disasters",
        "internet_penetration_pct": "percentage of households with internet access",
        "digital_literacy_pct": "percentage of people who can use digital services",
        "e_service_adoption_rate": "adoption rate of online government services",
        "aadhaar_enrollment_pct": "Aadhaar enrollment coverage",
        "mobile_connectivity_index": "strength and coverage of mobile network",
        "population": "total population of the ward",
        "population_density": "how densely populated the ward is",
    }

    def readable(feat_name):
        return FEATURE_LABELS.get(feat_name, feat_name.replace("_", " ").replace("pct", "%").title())

    # ─── Sector-specific action recommendations ───
    SECTOR_RECOMMENDATIONS = {
        "Health & Sanitation": {
            "high": (
                "The Panchayat should immediately consider setting up a **Primary Health Sub-Centre** in {ward} "
                "with at least 2 doctors and basic lab facilities. Weekly mobile medical camps should be organized "
                "targeting elderly residents and pregnant women. A **community health worker (ASHA) network** "
                "should be strengthened to ensure door-to-door vaccination and awareness drives.\n\n"
                "**Suggested projects:** Construction of a public health unit near the ward centre, "
                "installation of sanitary public toilets, and a ward-level sanitation drive in collaboration with "
                "Suchitwa Mission Kerala."
            ),
            "medium": (
                "The ward should focus on **upgrading existing health infrastructure** — ensuring the nearest "
                "sub-centre has adequate medicine supply and extending OPD hours. A community awareness program "
                "on hygiene, waste-related diseases, and monsoon health precautions would be beneficial.\n\n"
                "**Suggested projects:** Monthly health camps, mosquito fogging drives before monsoon, "
                "and installation of handwash stations near anganwadis and schools."
            ),
            "low": (
                "Health infrastructure in {ward} is relatively adequate. The Panchayat should focus on "
                "**maintaining standards** and conducting periodic health surveys to catch any emerging issues early."
            ),
        },
        "Education": {
            "high": (
                "Education in {ward} needs urgent improvement. The Panchayat should work with the District "
                "Education Officer to **reduce student-teacher ratios** by deploying additional guest teachers. "
                "A **dropout prevention program** offering free noon meals, school supplies, and transport "
                "for children from BPL families should be launched.\n\n"
                "**Suggested projects:** Digital smart classrooms in government schools, a ward-level "
                "library and study centre, evening tuition programs run by NSS volunteers, and scholarship "
                "programs for SC/ST students."
            ),
            "medium": (
                "Education indicators show room for improvement. The focus should be on **digital learning "
                "infrastructure** — equipping classrooms with projectors and computers, and improving "
                "connectivity so students can access e-learning platforms (KITE Kerala).\n\n"
                "**Suggested projects:** Computer lab upgrades, teacher training workshops on digital "
                "pedagogy, and an after-school skill development program."
            ),
            "low": (
                "Education outcomes in {ward} are strong. The Panchayat should continue supporting existing "
                "programs and explore **higher education scholarships** and vocational training tie-ups."
            ),
        },
        "Infrastructure": {
            "high": (
                "Infrastructure in {ward} requires significant investment. **Road connectivity** should be "
                "the top priority — damaged ward roads and interior connecting paths need resurfacing using "
                "PMGSY or NABARD funding. **Drinking water supply** gaps must be addressed by extending "
                "Jal Jeevan Mission pipelines to underserved areas.\n\n"
                "**Suggested projects:** Tarring of ward interior roads, construction of concrete drains "
                "to prevent waterlogging, streetlight installation under Panchayat own funds, and a "
                "community hall or waiting shed at bus stops."
            ),
            "medium": (
                "Infrastructure is partially developed but needs targeted upgrades. The Panchayat should "
                "prioritize **fixing drainage systems** to reduce monsoon waterlogging, and ensure all "
                "households have functional water connections.\n\n"
                "**Suggested projects:** Drain cleaning and widening, solar-powered streetlights, "
                "and footpath construction along main ward roads."
            ),
            "low": (
                "Infrastructure in {ward} is reasonably well-developed. Focus on **maintenance and "
                "upkeep** of existing roads, drains, and public facilities."
            ),
        },
        "Agriculture & Food Security": {
            "high": (
                "Agriculture in {ward} is struggling and food security is a concern. The Panchayat should "
                "promote **Subhiksha Keralam** programs to increase food crop cultivation on fallow land. "
                "**Irrigation coverage** needs to be expanded — micro-irrigation kits (drip/sprinkler) "
                "should be distributed to small farmers through the Krishi Bhavan.\n\n"
                "**Suggested projects:** Community vegetable gardens (Pachakkari Thottam), organic farming "
                "training through Kudumbashree units, rain water harvesting for agriculture, and a "
                "ward-level farmers' market to reduce middlemen costs."
            ),
            "medium": (
                "Agricultural output can be improved with targeted support. The focus should be on "
                "**crop diversification** and connecting local farmers to Panchayat-run markets.\n\n"
                "**Suggested projects:** Soil testing camps, subsidy facilitation for farm equipment, "
                "and a Kudumbashree-linked food processing unit."
            ),
            "low": (
                "Agriculture and food security are relatively stable in {ward}. The Panchayat should "
                "support **value-addition and market linkages** to boost farmer income further."
            ),
        },
        "Social Welfare": {
            "high": (
                "Social welfare indicators in {ward} are concerning, with a high BPL population and "
                "gaps in pension and disability support coverage. The Panchayat should conduct a "
                "**door-to-door survey** to identify left-out beneficiaries for LIFE Mission housing, "
                "widow pension, old-age pension, and disability pension schemes.\n\n"
                "**Suggested projects:** A Panchayat-level welfare facilitation centre (help desk) for "
                "scheme applications, Kudumbashree-linked livelihood programs for women, free legal "
                "aid clinics, and anti-dowry/domestic violence awareness campaigns."
            ),
            "medium": (
                "Social welfare coverage needs expansion. The Panchayat should ensure **all eligible "
                "families are enrolled** in relevant state and central welfare schemes.\n\n"
                "**Suggested projects:** Welfare scheme awareness camps, women's self-help group "
                "strengthening, and child welfare monitoring through anganwadis."
            ),
            "low": (
                "Social welfare coverage in {ward} is adequate. Continue monitoring and ensure "
                "**no eligible beneficiary is left out** of pension and housing schemes."
            ),
        },
        "Economic Development": {
            "high": (
                "Economic opportunities in {ward} are limited, with low employment and few small "
                "businesses. The Panchayat should promote **micro-enterprises** through PMEGP and "
                "Kudumbashree enterprise loans. **Skill development training** in trades like "
                "plumbing, electrician work, tailoring, and mobile repair should be organized through "
                "DDU-GKY or ASAP Kerala.\n\n"
                "**Suggested projects:** A Panchayat skill training centre, Kudumbashree cafe/catering "
                "units, support for home-based businesses (papad, pickle, snacks), and if the ward has "
                "tourism potential (near Manjeshwar beach or backwaters), a homestay promotion program."
            ),
            "medium": (
                "Economic activity exists but needs strengthening. Focus on **youth employment** "
                "through skill training and encouraging entrepreneurship.\n\n"
                "**Suggested projects:** Job fair organization, MSME registration awareness camps, "
                "and market linkages for local products."
            ),
            "low": (
                "The local economy in {ward} is reasonably active. The Panchayat should focus on "
                "**sustaining growth** and exploring new sectors like agri-tourism or IT-enabled services."
            ),
        },
        "Environment & Disaster Mgmt": {
            "high": (
                "Environmental and disaster risks in {ward} are high — particularly **flood risk during "
                "the Kerala monsoon**. The Panchayat must prepare a **ward-level disaster response plan** "
                "identifying safe shelters, escape routes, and emergency contact numbers. **Waste management** "
                "needs immediate attention — source-level segregation and a ward-level material collection "
                "facility should be set up under Haritha Keralam.\n\n"
                "**Suggested projects:** Flood bund construction along vulnerable stretches, community "
                "emergency kits, tree planting drives (Pachathuruthu), and a ward-level bio-waste "
                "composting unit managed by Haritha Karma Sena."
            ),
            "medium": (
                "Environmental management needs attention. The Panchayat should strengthen **waste "
                "collection routes** and promote household composting.\n\n"
                "**Suggested projects:** Awareness drives on waste segregation, rain garden installations, "
                "and monsoon preparedness drills in schools."
            ),
            "low": (
                "Environmental conditions in {ward} are manageable. Focus on **maintaining green cover** "
                "and updating disaster preparedness plans annually."
            ),
        },
        "Digital & E-Governance": {
            "high": (
                "Digital connectivity in {ward} is poor, limiting residents' access to online government "
                "services, banking, and education. The Panchayat should push for **Akshaya e-Centre** "
                "expansion and work with BSNL/KFON to improve broadband and mobile connectivity.\n\n"
                "**Suggested projects:** A ward-level digital literacy training program (especially for "
                "women and senior citizens), installation of public WiFi hotspots at the ward community "
                "centre, and a help desk for online certificate/pension/scholarship applications."
            ),
            "medium": (
                "Digital access exists but adoption is low. The Panchayat should encourage **online service "
                "adoption** through awareness campaigns and assisted digital service counters.\n\n"
                "**Suggested projects:** Digital literacy workshops through Kudumbashree, and promotion "
                "of e-District and DigiLocker services."
            ),
            "low": (
                "Digital connectivity in {ward} is adequate. Focus on **promoting advanced digital "
                "services** and exploring IT-enabled livelihood opportunities."
            ),
        },
    }

    # ─── Import simple problem text + Malayalam ───
    from models.explanation_text import INDICATOR_PROBLEMS, SECTOR_NAMES_ML, SEVERITY_ML

    # ─── Determine severity level ───
    if vulnerability_score > 0.7:
        severity = "high"
        severity_label = "critically high"
        severity_ml = "ഗുരുതരമായ നിലയിൽ"
        severity_emoji = "🔴"
    elif vulnerability_score > 0.4:
        severity = "medium"
        severity_label = "moderately elevated"
        severity_ml = "മിതമായ തോതിൽ"
        severity_emoji = "🟡"
    else:
        severity = "low"
        severity_label = "within acceptable range"
        severity_ml = "സ്വീകാര്യമായ പരിധിയിൽ"
        severity_emoji = "🟢"

    sector_ml = SECTOR_NAMES_ML.get(sector_name, sector_name)
    parts = []

    # ── 1. Overview (EN + ML) ──
    parts.append(
        f"### Analysis for {ward_name} — {sector_name}\n\n"
        f"{severity_emoji} The AI has identified **{sector_name}** as a priority for "
        f"**{ward_name}** ward. Vulnerability score: **{vulnerability_score:.3f}** — **{severity_label}**.\n\n"
        f"*{severity_emoji} AI **{sector_ml}** മേഖലയെ **{ward_name}** വാർഡിന്റെ "
        f"മുൻഗണനയായി തിരിച്ചറിഞ്ഞു. ദുർബലത സ്കോർ: **{vulnerability_score:.3f}** — **{severity_ml}**.*"
    )

    # ── 2. Problems found (simple language + ML) ──
    if positive_drivers:
        parts.append("\n\n#### 📊 Problems Found / കണ്ടെത്തിയ പ്രശ്നങ്ങൾ\n")
        for feat, val in positive_drivers[:3]:
            pct = abs(val) / total_abs * 100 if total_abs > 0 else 0
            prob = INDICATOR_PROBLEMS.get(feat)
            if prob:
                en_problem, ml_problem, action = prob
                parts.append(
                    f"- ⚠️ **{en_problem}** → *What to do:* {action}\n"
                    f"  - *{ml_problem}*\n"
                )
            else:
                label = readable(feat)
                parts.append(f"- ⚠️ **{label}** needs improvement in this ward.\n")

    # ── 3. Strengths (EN + ML) ──
    if negative_drivers:
        parts.append("\n#### ✅ What's Working Well / നന്നായി പ്രവർത്തിക്കുന്നവ\n")
        for feat, val in negative_drivers[:2]:
            prob = INDICATOR_PROBLEMS.get(feat)
            if prob:
                en_good = prob[0].replace("not ", "").replace("do not", "").replace("too few", "enough").replace("too many", "the right number of")
                parts.append(
                    f"- ✅ {ward_name} is doing **better than average** in: {readable(feat)}\n"
                    f"  - *{ward_name} ഈ മേഖലയിൽ ശരാശരിയേക്കാൾ മികച്ചതാണ്. ഇത് നിലനിർത്തുക.*\n"
                )
            else:
                parts.append(f"- ✅ {readable(feat)} is a strength of this ward.\n")

    # ── 4. Recommendations (EN + ML) ──
    sector_recs = SECTOR_RECOMMENDATIONS.get(sector_name, {})
    rec_text = sector_recs.get(severity, "")
    if rec_text:
        parts.append(f"\n#### 🎯 What Should Be Done / എന്താണ് ചെയ്യേണ്ടത്\n\n{rec_text.format(ward=ward_name)}")

    # ── 5. Funding (EN + ML) ──
    funding_map = {
        "Health & Sanitation": "National Health Mission (NHM), Suchitwa Mission, Panchayat Own Fund",
        "Education": "Samagra Shiksha Abhiyan, KITE Kerala, SSA, Panchayat Education Fund",
        "Infrastructure": "PMGSY, NABARD RIDF, MGNREGS, Panchayat Plan Fund, MLA/MP Fund",
        "Agriculture & Food Security": "Subhiksha Keralam, PMKSY, Krishi Bhavan, NABARD",
        "Social Welfare": "LIFE Mission, NSAP Pensions, SJSRY, Kudumbashree Mission",
        "Economic Development": "PMEGP, DDU-GKY, ASAP Kerala, Kudumbashree Enterprise loans",
        "Environment & Disaster Mgmt": "Haritha Keralam, SDRF, MGNREGS, Clean Kerala Company",
        "Digital & E-Governance": "KFON, BharatNet, Akshaya Project, CSC 2.0",
    }
    schemes = funding_map.get(sector_name, "Panchayat Plan Fund")
    parts.append(f"\n#### 💰 Funding Sources / ധനസഹായ സ്രോതസ്സുകൾ\n")
    parts.append(f"Applicable schemes / ബാധകമായ പദ്ധതികൾ: **{schemes}**")

    return "\n".join(parts)


def get_global_feature_importance(shap_values, feature_names):
    """Get global feature importance from SHAP values (mean absolute)."""
    if hasattr(shap_values, 'values'):
        vals = shap_values.values
    else:
        vals = np.array(shap_values)

    if len(vals.shape) == 3:
        vals = np.abs(vals).mean(axis=2)

    mean_abs = np.abs(vals).mean(axis=0)
    importance = dict(zip(feature_names, mean_abs))
    return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))


def load_explainer_and_compute(df):
    """Load model and compute SHAP values for the full dataset."""
    xgb_model = joblib.load(XGBOOST_MODEL_PATH)
    feature_cols = joblib.load(os.path.join(MODEL_DIR, "feature_cols.joblib"))

    X = df[[c for c in feature_cols if c in df.columns]].values
    explainer = create_explainer(xgb_model)
    shap_vals = get_shap_values(explainer, X)

    return shap_vals, feature_cols, explainer
