"""
REST API Blueprint for Smart AI Panchayat.
Exposes high-performance, strictly-scoped geographic endpoints:
- GET /api/locations
- GET /api/dashboard
- GET /api/insights
- GET /api/planning
- GET /api/budget
- GET /api/reports
- GET /api/sectors
- GET /api/health
"""

from datetime import datetime
import numpy as np
import pandas as pd
from flask import Blueprint, jsonify, request
from services.analysis_service import get_engine
from services.cache_service import get_cached_data, set_cached_data

api_bp = Blueprint("api_bp", __name__, url_prefix="/api")


def _sanitize_for_json(val):
    """Recursively convert NumPy and Pandas types to standard Python types for JSON serialization."""
    if isinstance(val, (np.integer, np.int64, np.int32)):
        return int(val)
    elif isinstance(val, (np.floating, np.float64, np.float32)):
        return None if np.isnan(val) else round(float(val), 4)
    elif isinstance(val, (np.bool_, bool)):
        return bool(val)
    elif isinstance(val, (np.ndarray, list)):
        return [_sanitize_for_json(x) for x in val]
    elif isinstance(val, dict):
        return {str(k): _sanitize_for_json(v) for k, v in val.items()}
    elif pd.isna(val):
        return None
    return val


def _extract_location_params(req):
    """Extract and resolve standardized 7-key location metadata from request arguments."""
    engine = get_engine()
    state_id = req.args.get("state_id") or req.args.get("stateId")
    district_id = req.args.get("district_id") or req.args.get("districtId")
    panchayat_id = req.args.get("panchayat_id") or req.args.get("panchayatId")

    state_name = req.args.get("state") or req.args.get("state_name")
    district_name = req.args.get("district") or req.args.get("district_name")
    panchayat_name = req.args.get("panchayat") or req.args.get("panchayat_name")

    year = req.args.get("financial_year") or req.args.get("year") or "2026-27"

    meta = engine.get_location_metadata(
        state=state_name,
        district=district_name,
        panchayat=panchayat_name,
        state_id=state_id,
        district_id=district_id,
        panchayat_id=panchayat_id,
        year=year,
    )
    return meta


@api_bp.route("/health", methods=["GET"])
def health_check():
    """System health check and ML model status."""
    engine = get_engine()
    return jsonify({
        "status": "healthy",
        "engine_initialized": engine._is_initialized,
        "champion_classifier": type(engine.champion_clf).__name__ if engine.champion_clf else "fallback",
        "champion_regressor": type(engine.champion_regressor if hasattr(engine, "champion_regressor") else engine.champion_reg).__name__ if engine.champion_reg else "fallback",
        "total_wards_loaded": len(engine.df_processed) if engine.df_processed is not None else 0,
        "available_states": engine.get_states(),
    })


@api_bp.route("/states", methods=["GET"])
def get_states():
    """
    Get all supported States with official LGD IDs and summary statistics.
    Follows State -> District -> Panchayat cascading architecture.
    """
    cached = get_cached_data("api_states")
    if cached is not None:
        return jsonify(cached)

    engine = get_engine()
    states_list = []
    for s in engine.get_states():
        df_s = engine.get_filtered_df(state=s)
        states_list.append({
            "state_id": engine.get_state_id(s),
            "state_name": s,
            "total_districts": len(engine.get_districts(state=s)),
            "total_panchayats": len(engine.get_panchayats(state=s)),
            "total_wards": len(df_s),
            "total_population": int(df_s["population"].sum()) if "population" in df_s.columns else 0,
        })
    res = {"total_states": len(states_list), "states": states_list}
    set_cached_data(res, "api_states")
    return jsonify(res)


@api_bp.route("/districts", methods=["GET"])
def get_districts():
    """
    Get districts strictly belonging to the specified state.
    Query params: state_id or state (required).
    Rejects requests with HTTP 400 if state is invalid.
    """
    engine = get_engine()
    state_id = request.args.get("state_id") or request.args.get("stateId")
    state_name = request.args.get("state") or request.args.get("state_name")

    if not state_id and not state_name:
        return jsonify({"error": "Missing required parameter 'state_id' or 'state'"}), 400

    if state_id and str(state_id).strip().upper() != "ALL":
        resolved_state = engine._state_id_to_name.get(str(state_id).strip(), state_name or "ALL")
    else:
        resolved_state = state_name or "ALL"

    valid_states = engine.get_states()
    if resolved_state != "ALL" and resolved_state not in valid_states:
        return jsonify({
            "error": f"Invalid State: '{resolved_state}'. Supported states: {', '.join(valid_states)}"
        }), 400

    cache_key = ("api_districts", resolved_state)
    cached = get_cached_data(*cache_key)
    if cached is not None:
        return jsonify(cached)

    districts = engine.get_districts(state=resolved_state)
    districts_list = []
    for d in districts:
        df_d = engine.get_filtered_df(state=resolved_state, district=d)
        districts_list.append({
            "district_id": engine.get_district_id(d, state=resolved_state),
            "district_name": d,
            "state_id": engine.get_state_id(resolved_state),
            "state_name": resolved_state,
            "total_panchayats": len(engine.get_panchayats(district=d, state=resolved_state)),
            "total_wards": len(df_d),
            "total_population": int(df_d["population"].sum()) if "population" in df_d.columns else 0,
        })

    res = {
        "state_id": engine.get_state_id(resolved_state),
        "state_name": resolved_state,
        "total_districts": len(districts_list),
        "districts": districts_list,
    }
    set_cached_data(res, *cache_key)
    return jsonify(res)


@api_bp.route("/panchayats", methods=["GET"])
def get_panchayats():
    """
    Get panchayats strictly belonging to the specified district.
    Query params: district_id or district (required), state_id or state (optional).
    Rejects requests with HTTP 400 if district does not belong to the state.
    """
    engine = get_engine()
    district_id = request.args.get("district_id") or request.args.get("districtId")
    district_name = request.args.get("district") or request.args.get("district_name")
    state_id = request.args.get("state_id") or request.args.get("stateId")
    state_name = request.args.get("state") or request.args.get("state_name")

    if not district_id and not district_name:
        return jsonify({"error": "Missing required parameter 'district_id' or 'district'"}), 400

    # Resolve state and district
    if state_id and str(state_id).strip().upper() != "ALL":
        resolved_state = engine._state_id_to_name.get(str(state_id).strip(), state_name or "ALL")
    else:
        resolved_state = state_name or "ALL"

    if district_id and str(district_id).strip().upper() != "ALL":
        resolved_dist = engine._district_id_to_name.get(str(district_id).strip(), district_name or "ALL")
    else:
        resolved_dist = district_name or "ALL"

    # Validate hierarchy: If state was provided, district must belong to it
    if resolved_state != "ALL" and resolved_dist != "ALL":
        valid_districts = engine.get_districts(state=resolved_state)
        if resolved_dist not in valid_districts:
            return jsonify({
                "error": f"Geographical hierarchy violation: District '{resolved_dist}' does not belong to State '{resolved_state}'"
            }), 400

    cache_key = ("api_panchayats", resolved_state, resolved_dist)
    cached = get_cached_data(*cache_key)
    if cached is not None:
        return jsonify(cached)

    panchayats = engine.get_panchayats(district=resolved_dist, state=resolved_state if resolved_state != "ALL" else None)
    panchayats_list = []
    for p in panchayats:
        df_p = engine.get_filtered_df(state=resolved_state, district=resolved_dist, panchayat=p)
        panchayats_list.append({
            "panchayat_id": engine.get_panchayat_id(p, district=resolved_dist, state=resolved_state),
            "panchayat_name": p,
            "district_id": engine.get_district_id(resolved_dist, state=resolved_state),
            "district_name": resolved_dist,
            "state_id": engine.get_state_id(resolved_state),
            "state_name": resolved_state,
            "total_wards": len(df_p),
            "total_population": int(df_p["population"].sum()) if "population" in df_p.columns else 0,
        })

    res = {
        "district_id": engine.get_district_id(resolved_dist, state=resolved_state),
        "district_name": resolved_dist,
        "state_name": resolved_state,
        "total_panchayats": len(panchayats_list),
        "panchayats": panchayats_list,
    }
    set_cached_data(res, *cache_key)
    return jsonify(res)


@api_bp.route("/locations", methods=["GET"])
def get_locations():
    """
    Get cascading location hierarchy with official LGD IDs.
    Query params: state_id (optional), district_id (optional).
    """
    engine = get_engine()
    state_id = request.args.get("state_id")
    state_name = request.args.get("state")
    district_id = request.args.get("district_id")
    district_name = request.args.get("district")

    # Resolve state
    if state_id and str(state_id).strip().upper() != "ALL":
        resolved_state = engine._state_id_to_name.get(str(state_id).strip(), state_name or "ALL")
    else:
        resolved_state = state_name or "ALL"

    # Resolve district
    if district_id and str(district_id).strip().upper() != "ALL":
        resolved_dist = engine._district_id_to_name.get(str(district_id).strip(), district_name or "ALL")
    else:
        resolved_dist = district_name or "ALL"

    states_list = [
        {"state_id": engine.get_state_id(s), "state_name": s}
        for s in engine.get_states()
    ]

    districts = engine.get_districts(state=resolved_state)
    districts_list = [
        {"district_id": engine.get_district_id(d, state=resolved_state), "district_name": d}
        for d in districts
    ]

    panchayats = engine.get_panchayats(district=resolved_dist)
    panchayats_list = [
        {"panchayat_id": engine.get_panchayat_id(p, district=resolved_dist, state=resolved_state), "panchayat_name": p}
        for p in panchayats
    ]

    return jsonify({
        "selected_scope": {
            "state_id": engine.get_state_id(resolved_state),
            "state_name": resolved_state,
            "district_id": engine.get_district_id(resolved_dist, state=resolved_state),
            "district_name": resolved_dist,
        },
        "states": states_list,
        "districts": districts_list,
        "panchayats": panchayats_list,
    })


@api_bp.route("/dashboard", methods=["GET"])
def get_dashboard_data():
    """
    Core Dashboard Data Endpoint.
    Strictly filters data to the requested geographic coordinates.
    Never returns cross-panchayat or cross-state contaminated data.
    """
    engine = get_engine()
    loc = _extract_location_params(request)

    # Strictly validate 3-tier geographical hierarchy
    is_valid, err_msg, _ = engine.validate_hierarchy(
        state=loc["state_name"], district=loc["district_name"], panchayat=loc["panchayat_name"],
        state_id=loc["state_id"], district_id=loc["district_id"], panchayat_id=loc["panchayat_id"]
    )
    if not is_valid:
        return jsonify({"error": err_msg, "location": loc}), 400

    # Strictly validate 3-tier geographical hierarchy
    is_valid, err_msg, _ = engine.validate_hierarchy(
        state=loc["state_name"], district=loc["district_name"], panchayat=loc["panchayat_name"],
        state_id=loc["state_id"], district_id=loc["district_id"], panchayat_id=loc["panchayat_id"]
    )
    if not is_valid:
        return jsonify({"error": err_msg, "location": loc}), 400

    cache_key = [
        "api_dashboard",
        loc["state_id"],
        loc["district_id"],
        loc["panchayat_id"],
        loc["financial_year"],
    ]
    cached = get_cached_data(*cache_key)
    if cached is not None:
        return jsonify(cached)

    df = engine.get_filtered_df(
        state=loc["state_name"],
        district=loc["district_name"],
        panchayat=loc["panchayat_name"],
        state_id=loc["state_id"],
        district_id=loc["district_id"],
        panchayat_id=loc["panchayat_id"],
    )

    if df.empty:
        resp = {
            "location": loc,
            "error": "No records found matching the requested geographic hierarchy.",
            "total_wards": 0,
            "kpis": {},
            "governance": None,
            "wards": [],
        }
        return jsonify(resp), 404

    # Aggregate Key Demographic and Development Indicators
    total_pop = int(df["population"].sum()) if "population" in df.columns else 0
    avg_vuln = float(df["vulnerability_index"].mean()) if "vulnerability_index" in df.columns else 0.0
    high_vuln_wards = int((df["vulnerability_index"] > 0.65).sum()) if "vulnerability_index" in df.columns else 0

    # Sector averages
    sector_scores = {}
    for col in df.columns:
        if col.startswith("score_"):
            sec_name = col.replace("score_", "").replace("_", " ").title()
            sector_scores[sec_name] = round(float(df[col].mean()), 4)

    # Core indicator stats
    indicators = {
        "piped_water_coverage": float(df["piped_water_coverage"].mean()) if "piped_water_coverage" in df.columns else None,
        "road_connectivity": float(df["road_connectivity_index"].mean()) if "road_connectivity_index" in df.columns else None,
        "electrification_rate": float(df["electrification_rate"].mean()) if "electrification_rate" in df.columns else None,
        "phc_distance_km": float(df["avg_distance_phc"].mean()) if "avg_distance_phc" in df.columns else None,
        "school_dropout_rate": float(df["school_dropout_rate"].mean()) if "school_dropout_rate" in df.columns else None,
        "broadband_coverage": float(df["broadband_penetration"].mean()) if "broadband_penetration" in df.columns else None,
        "solid_waste_coverage": float(df["solid_waste_segregation_rate"].mean()) if "solid_waste_segregation_rate" in df.columns else None,
        "irrigation_coverage": float(df["irrigation_coverage_pct"].mean()) if "irrigation_coverage_pct" in df.columns else None,
        "mgnrega_utilization": float(df["mgnrega_work_demand_met_pct"].mean()) if "mgnrega_work_demand_met_pct" in df.columns else None,
    }

    # Governance
    gov = engine.get_panchayat_governance(
        state=loc["state_name"],
        district=loc["district_name"],
        panchayat=loc["panchayat_name"],
        state_id=loc["state_id"],
        district_id=loc["district_id"],
        panchayat_id=loc["panchayat_id"],
    )

    # Priority distribution
    priority_counts = {}
    if "priority_sector_1" in df.columns:
        priority_counts = df["priority_sector_1"].value_counts().to_dict()

    # Wards list summary
    wards_summary = engine.get_all_wards_summary(
        state=loc["state_name"],
        district=loc["district_name"],
        panchayat=loc["panchayat_name"],
        state_id=loc["state_id"],
        district_id=loc["district_id"],
        panchayat_id=loc["panchayat_id"],
    )

    demographics = engine.get_demographic_profile(
        state=loc["state_name"],
        district=loc["district_name"],
        panchayat=loc["panchayat_name"],
    )
    historical_trajectory = engine.get_historical_records(
        state=loc["state_name"],
        district=loc["district_name"],
        panchayat=loc["panchayat_name"],
    )

    result = {
        "location": loc,
        "total_wards": len(df),
        "kpis": {
            "total_population": total_pop,
            "avg_vulnerability_index": round(avg_vuln, 4),
            "high_vulnerability_ward_count": high_vuln_wards,
            "vulnerability_category": "High" if avg_vuln > 0.65 else ("Medium" if avg_vuln > 0.35 else "Low"),
        },
        "demographics": _sanitize_for_json(demographics),
        "historical_trajectory": _sanitize_for_json(historical_trajectory),
        "governance": gov,
        "sector_vulnerability_scores": sector_scores,
        "indicators": _sanitize_for_json(indicators),
        "top_priorities": priority_counts,
        "wards": _sanitize_for_json(wards_summary.to_dict(orient="records")),
    }

    set_cached_data(result, *cache_key)
    return jsonify(result)


@api_bp.route("/insights", methods=["GET"])
def get_insights():
    """
    AI Insights Endpoint.
    Returns ML predictions, confidence levels, and feature importance scoped to location/ward.
    """
    engine = get_engine()
    loc = _extract_location_params(request)

    # Strictly validate 3-tier geographical hierarchy
    is_valid, err_msg, _ = engine.validate_hierarchy(
        state=loc["state_name"], district=loc["district_name"], panchayat=loc["panchayat_name"],
        state_id=loc["state_id"], district_id=loc["district_id"], panchayat_id=loc["panchayat_id"]
    )
    if not is_valid:
        return jsonify({"error": err_msg, "location": loc}), 400
    ward_name = request.args.get("ward_name") or request.args.get("ward")

    cache_key = ("api_insights", loc["state_id"], loc["district_id"], loc["panchayat_id"], loc["financial_year"], str(ward_name or "ALL"))
    cached = get_cached_data(*cache_key)
    if cached is not None:
        return jsonify(cached)

    df = engine.get_filtered_df(
        state=loc["state_name"],
        district=loc["district_name"],
        panchayat=loc["panchayat_name"],
        state_id=loc["state_id"],
        district_id=loc["district_id"],
        panchayat_id=loc["panchayat_id"],
    )

    if df.empty:
        return jsonify({"location": loc, "error": "No records found"}), 404

    # Global feature importance from champion model
    feat_importance = engine.get_feature_importance()

    ward_insight = None
    if ward_name and ward_name.strip().upper() != "ALL":
        wdata = engine.get_ward_data(
            ward_name,
            state=loc["state_name"],
            district=loc["district_name"],
            panchayat=loc["panchayat_name"],
        )
        if wdata:
            narrative = engine.get_ward_explanation(
                ward_name,
                state=loc["state_name"],
                district=loc["district_name"],
                panchayat=loc["panchayat_name"],
            )
            ward_insight = {
                "ward_name": wdata.get("ward_name"),
                "priority_sector_1": wdata.get("priority_sector_1"),
                "priority_confidence_1": float(wdata.get("priority_confidence_1", 0.0)),
                "priority_sector_2": wdata.get("priority_sector_2"),
                "priority_sector_3": wdata.get("priority_sector_3"),
                "vulnerability_index": float(wdata.get("vulnerability_index", 0.0)),
                "ai_narrative": narrative,
            }

    resp = {
        "location": loc,
        "model_used": type(engine.champion_clf).__name__ if engine.champion_clf else "fallback",
        "feature_importance": _sanitize_for_json(feat_importance),
        "ward_insight": _sanitize_for_json(ward_insight),
        "total_wards_analyzed": len(df),
    }
    set_cached_data(resp, *cache_key)
    return jsonify(resp)


@api_bp.route("/planning", methods=["GET"])
def get_planning():
    """
    Development Planning Endpoint.
    Returns sector vulnerability matrix and prioritized development interventions.
    """
    engine = get_engine()
    loc = _extract_location_params(request)

    # Strictly validate 3-tier geographical hierarchy
    is_valid, err_msg, _ = engine.validate_hierarchy(
        state=loc["state_name"], district=loc["district_name"], panchayat=loc["panchayat_name"],
        state_id=loc["state_id"], district_id=loc["district_id"], panchayat_id=loc["panchayat_id"]
    )
    if not is_valid:
        return jsonify({"error": err_msg, "location": loc}), 400

    cache_key = ("api_planning", loc["state_id"], loc["district_id"], loc["panchayat_id"], loc["financial_year"])
    cached = get_cached_data(*cache_key)
    if cached is not None:
        return jsonify(cached)

    matrix = engine.get_sector_scores_matrix(
        state=loc["state_name"],
        district=loc["district_name"],
        panchayat=loc["panchayat_name"],
        state_id=loc["state_id"],
        district_id=loc["district_id"],
        panchayat_id=loc["panchayat_id"],
    )

    summary = engine.get_all_wards_summary(
        state=loc["state_name"],
        district=loc["district_name"],
        panchayat=loc["panchayat_name"],
        state_id=loc["state_id"],
        district_id=loc["district_id"],
        panchayat_id=loc["panchayat_id"],
    )

    res = {
        "location": loc,
        "ward_count": len(summary),
        "planning_matrix": _sanitize_for_json(matrix.to_dict(orient="records")),
        "priorities": _sanitize_for_json(summary[["ward_name", "vulnerability_index", "priority_sector_1", "priority_confidence_1"]].to_dict(orient="records")),
    }
    set_cached_data(res, *cache_key)
    return jsonify(res)


@api_bp.route("/budget", methods=["GET"])
def get_budget():
    """
    Budget Allocation Optimization Endpoint (HiGHS Linear Programming).
    Computes mathematically optimized fund distribution for a specific ward.
    """
    engine = get_engine()
    loc = _extract_location_params(request)

    # Strictly validate 3-tier geographical hierarchy
    is_valid, err_msg, _ = engine.validate_hierarchy(
        state=loc["state_name"], district=loc["district_name"], panchayat=loc["panchayat_name"],
        state_id=loc["state_id"], district_id=loc["district_id"], panchayat_id=loc["panchayat_id"]
    )
    if not is_valid:
        return jsonify({"error": err_msg, "location": loc}), 400
    ward_name = request.args.get("ward_name") or request.args.get("ward")
    total_budget_str = request.args.get("total_budget") or "10000000"

    try:
        total_budget = float(total_budget_str)
    except ValueError:
        total_budget = 10000000.0

    cache_key = ("api_budget", loc["state_id"], loc["district_id"], loc["panchayat_id"], loc["financial_year"], str(ward_name or "DEFAULT"), str(total_budget))
    cached = get_cached_data(*cache_key)
    if cached is not None:
        return jsonify(cached)

    wards_in_scope = engine.get_ward_names(
        state=loc["state_name"],
        district=loc["district_name"],
        panchayat=loc["panchayat_name"],
    )

    if not wards_in_scope:
        return jsonify({"location": loc, "error": "No wards found in this jurisdiction"}), 404

    target_ward = ward_name if (ward_name and ward_name in wards_in_scope) else wards_in_scope[0]

    allocation = engine.get_ward_budget(
        target_ward,
        total_budget=total_budget,
        state=loc["state_name"],
        district=loc["district_name"],
        panchayat=loc["panchayat_name"],
    )

    if not allocation:
        return jsonify({"location": loc, "ward": target_ward, "error": "Optimization failed or ward not found"}), 404

    res = {
        "location": loc,
        "ward_name": target_ward,
        "total_budget": total_budget,
        "allocation": _sanitize_for_json(allocation),
    }
    set_cached_data(res, *cache_key)
    return jsonify(res)


@api_bp.route("/reports", methods=["GET"])
def get_reports():
    """
    Comparative and Disparity Analytics Report Endpoint.
    """
    engine = get_engine()
    loc = _extract_location_params(request)

    # Strictly validate 3-tier geographical hierarchy
    is_valid, err_msg, _ = engine.validate_hierarchy(
        state=loc["state_name"], district=loc["district_name"], panchayat=loc["panchayat_name"],
        state_id=loc["state_id"], district_id=loc["district_id"], panchayat_id=loc["panchayat_id"]
    )
    if not is_valid:
        return jsonify({"error": err_msg, "location": loc}), 400

    cache_key = ("api_reports", loc["state_id"], loc["district_id"], loc["panchayat_id"], loc["financial_year"])
    cached = get_cached_data(*cache_key)
    if cached is not None:
        return jsonify(cached)

    df = engine.get_filtered_df(
        state=loc["state_name"],
        district=loc["district_name"],
        panchayat=loc["panchayat_name"],
        state_id=loc["state_id"],
        district_id=loc["district_id"],
        panchayat_id=loc["panchayat_id"],
    )

    if df.empty:
        return jsonify({"location": loc, "error": "No records found"}), 404

    # Calculate disparity between highest and lowest vulnerability wards
    df_sorted = df.sort_values("vulnerability_index", ascending=False)
    most_vulnerable = df_sorted.iloc[0]["ward_name"] if len(df_sorted) > 0 else "N/A"
    least_vulnerable = df_sorted.iloc[-1]["ward_name"] if len(df_sorted) > 0 else "N/A"

    disparity_gap = float(df_sorted.iloc[0]["vulnerability_index"] - df_sorted.iloc[-1]["vulnerability_index"]) if len(df_sorted) > 1 else 0.0

    res = {
        "location": loc,
        "total_wards": len(df),
        "disparity_analysis": {
            "most_vulnerable_ward": most_vulnerable,
            "highest_vulnerability_index": float(df_sorted.iloc[0]["vulnerability_index"]) if len(df_sorted) > 0 else 0.0,
            "least_vulnerable_ward": least_vulnerable,
            "lowest_vulnerability_index": float(df_sorted.iloc[-1]["vulnerability_index"]) if len(df_sorted) > 0 else 0.0,
            "disparity_gap": round(disparity_gap, 4),
        },
        "wards_ranked": _sanitize_for_json(
            df_sorted[["ward_name", "population", "vulnerability_index", "vulnerability_category", "priority_sector_1"]].to_dict(orient="records")
        ),
    }
    set_cached_data(res, *cache_key)
    return jsonify(res)


@api_bp.route("/sectors", methods=["GET"])
def get_sectors():
    """
    Sector Deep-Dive Analysis Endpoint (Healthcare, Education, Infrastructure, Agriculture, Water & Sanitation, Employment).
    """
    engine = get_engine()
    loc = _extract_location_params(request)

    # Strictly validate 3-tier geographical hierarchy
    is_valid, err_msg, _ = engine.validate_hierarchy(
        state=loc["state_name"], district=loc["district_name"], panchayat=loc["panchayat_name"],
        state_id=loc["state_id"], district_id=loc["district_id"], panchayat_id=loc["panchayat_id"]
    )
    if not is_valid:
        return jsonify({"error": err_msg, "location": loc}), 400
    sector_filter = request.args.get("sector", "all").lower().strip()

    cache_key = ("api_sectors", loc["state_id"], loc["district_id"], loc["panchayat_id"], loc["financial_year"], sector_filter)
    cached = get_cached_data(*cache_key)
    if cached is not None:
        return jsonify(cached)

    df = engine.get_filtered_df(
        state=loc["state_name"],
        district=loc["district_name"],
        panchayat=loc["panchayat_name"],
        state_id=loc["state_id"],
        district_id=loc["district_id"],
        panchayat_id=loc["panchayat_id"],
    )

    if df.empty:
        return jsonify({"location": loc, "error": "No records found"}), 404

    from config import SECTOR_INDICATORS

    sector_results = {}
    for sec_name, indicators in SECTOR_INDICATORS.items():
        if sector_filter != "all" and sec_name.lower().replace(" ", "_") != sector_filter:
            continue

        score_col = "score_" + sec_name.lower().replace(" ", "_").replace("&", "and").replace(".", "")
        avg_score = float(df[score_col].mean()) if score_col in df.columns else 0.0

        indicator_stats = {}
        for ind in indicators:
            if ind in df.columns:
                indicator_stats[ind] = {
                    "mean": round(float(df[ind].mean()), 4),
                    "min": round(float(df[ind].min()), 4),
                    "max": round(float(df[ind].max()), 4),
                }

        sector_results[sec_name] = {
            "average_vulnerability_score": round(avg_score, 4),
            "indicators": indicator_stats,
        }

    res = {
        "location": loc,
        "sectors": _sanitize_for_json(sector_results),
    }
    set_cached_data(res, *cache_key)
    return jsonify(res)


# ─────────────────────────────────────────────────────────────────────────────
# MULTILINGUAL AI VOICE ASSISTANT ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────
from services.voice_assistant_service import get_voice_assistant


@api_bp.route("/assistant/chat", methods=["POST"])
def assistant_chat():
    """
    Multilingual conversational endpoint for Smart AI Panchayat.
    Accepts question, language, location scope, and history.
    Returns strictly grounded answer, data snapshot, source provenance, and synthesized audio.
    """
    va = get_voice_assistant()
    data = request.get_json(silent=True) or {}

    query = data.get("message") or data.get("query") or "Overview of this Panchayat"
    language = data.get("language") or "en"
    state = data.get("state") or data.get("state_name")
    district = data.get("district") or data.get("district_name")
    panchayat = data.get("panchayat") or data.get("panchayat_name")
    year = data.get("financial_year") or data.get("year") or "2026-27"
    history = data.get("history") or []

    res = va.generate_response(
        query=query,
        language=language,
        state=state,
        district=district,
        panchayat=panchayat,
        year=year,
        history=history,
    )

    # Optional speech synthesis
    synthesize_audio = data.get("synthesize_audio", True)
    if synthesize_audio:
        res["audio_base64"] = va.text_to_speech_base64(res["reply"], language=language)
    else:
        res["audio_base64"] = None

    return jsonify(_sanitize_for_json(res))


@api_bp.route("/assistant/explain", methods=["POST"])
def assistant_explain_component():
    """
    'Explain This' contextual chart and card explanation endpoint.
    Explains the exact metric distribution, highest/lowest sectors, and methodology.
    """
    va = get_voice_assistant()
    data = request.get_json(silent=True) or {}

    comp_id = data.get("component_id", "chart_overview")
    comp_title = data.get("component_title", "Dashboard Component")
    language = data.get("language", "en")
    state = data.get("state")
    district = data.get("district")
    panchayat = data.get("panchayat")
    year = data.get("year", "2026-27")

    comp_context = {
        "id": comp_id,
        "title": comp_title,
        "chart_data": data.get("component_data", {}),
    }

    prompt = f"Explain the dashboard chart: {comp_title}. Detail what the numbers indicate, highest/lowest gaps, and action recommendations."

    res = va.generate_response(
        query=prompt,
        language=language,
        state=state,
        district=district,
        panchayat=panchayat,
        year=year,
        component_context=comp_context,
    )
    res["audio_base64"] = va.text_to_speech_base64(res["reply"], language=language)

    return jsonify(_sanitize_for_json(res))


@api_bp.route("/assistant/tts", methods=["POST"])
def assistant_tts():
    """Generate base64 encoded natural Indic voice MP3 from text."""
    va = get_voice_assistant()
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    language = data.get("language", "en")

    if not text:
        return jsonify({"error": "Missing 'text' parameter"}), 400

    audio_b64 = va.text_to_speech_base64(text, language=language)
    return jsonify({
        "audio_base64": audio_b64,
        "language": language,
        "length_chars": len(text),
    })


@api_bp.route("/assistant/insights", methods=["GET"])
def assistant_proactive_insights():
    """Retrieve proactive developmental intelligence and key alerts for the active Panchayat."""
    va = get_voice_assistant()
    state = request.args.get("state")
    district = request.args.get("district")
    panchayat = request.args.get("panchayat")
    year = request.args.get("year", "2026-27")
    lang = request.args.get("language", "en")

    ctx = va.retrieve_grounded_context(state=state, district=district, panchayat=panchayat, year=year)
    p_name = ctx["location"]["panchayat"]
    s_name = ctx["location"]["state"]
    top_sec = ctx["top_sector"]["name"]
    top_score = ctx["top_sector"]["score"]
    tot_pop = ctx["demographics"]["total_population"]

    insights = [
        {
            "category": "Priority 1 Development Deficit",
            "title": f"Critical Need in {top_sec}",
            "description": f"Model identified deficit score of {top_score:.3f} requiring immediate capital works.",
            "type": "alert",
        },
        {
            "category": "Statutory Budget Outlay",
            "title": f"₹{ctx['lp_budget']['total_plan_fund_lakhs']:.1f}L Recommended SFC Allocation",
            "description": f"SciPy HiGHS LP Solver allocated ₹{ctx['lp_budget']['allocations'][0]['amount_lakhs']}L ({ctx['lp_budget']['allocations'][0]['pct']}%) to primary deficit.",
            "type": "budget",
        },
        {
            "category": "Census Demographics",
            "title": f"{tot_pop:,} Verified Citizen Coverage",
            "description": f"Literacy rate stands at {ctx['demographics']['literacy_rate']}%, with {ctx['demographics']['high_need_wards']} high-deficit wards audited.",
            "type": "demographic",
        },
    ]

    return jsonify({
        "panchayat": p_name,
        "state": s_name,
        "insights": insights,
        "timestamp": datetime.now().isoformat(),
    })
