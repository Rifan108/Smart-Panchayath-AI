"""
Analysis Service — Orchestrates data loading, ML model inference, and decision support.
Uses the Champion Machine Learning Model (HistGradientBoosting / Random Forest)
to predict priority sectors, confidence probabilities, and continuous vulnerability indices.
"""

import os
import sys
import json
import joblib
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.data_service import (
    load_raw_data, clean_data, normalize_indicators,
    compute_sector_scores, compute_overall_vulnerability
)
from models.vulnerability_index import get_sector_rankings
from models.budget_allocator import compute_allocation, format_allocation_table
from models.explainer import generate_openai_explanation, get_feature_importance_for_ward
from config import PROCESSED_DATA_FILE, MODEL_DIR, SECTOR_INDICATORS
from data.panchayat_geography import STATES_PANCHAYAT_DATA


def is_all_geographic_val(val):
    """Check if value represents a wildcard 'ALL' selection across geographic levels."""
    if val is None:
        return True
    s = str(val).strip().upper()
    return (
        s in ("", "ALL", "NONE", "NULL", "UNDEFINED")
        or s.startswith("ALL ")
        or s.endswith(" ALL")
        or "ALL DISTRICTS" in s
        or "ALL PANCHAYATS" in s
        or "ALL STATES" in s
    )


class AnalysisEngine:
    """Central engine that executes ML inference and decision intelligence."""

    def __init__(self):
        self.df_raw = None
        self.df_processed = None
        self.champion_clf = None
        self.champion_reg = None
        self.feature_cols = None
        self.id_to_sector = None
        self._is_initialized = False
        self._filter_cache = {}
        self._ward_dict = {}
        self._known_states = None
        self._known_districts = None

    def load_champion_models(self):
        """Load trained champion ML models from disk."""
        clf_path = os.path.join(MODEL_DIR, "champion_priority_model.joblib")
        if not os.path.exists(clf_path):
            clf_path = os.path.join(MODEL_DIR, "rf_model.joblib")

        reg_path = os.path.join(MODEL_DIR, "champion_vulnerability_regressor.joblib")
        if not os.path.exists(reg_path):
            reg_path = os.path.join(MODEL_DIR, "rf_regressor.joblib")

        feat_path = os.path.join(MODEL_DIR, "feature_cols.joblib")
        id_path = os.path.join(MODEL_DIR, "id_to_sector.joblib")

        if os.path.exists(clf_path):
            self.champion_clf = joblib.load(clf_path)
            print(f"Loaded Champion Classifier: {type(self.champion_clf).__name__}")
        if os.path.exists(reg_path):
            self.champion_reg = joblib.load(reg_path)
            print(f"Loaded Champion Regressor: {type(self.champion_reg).__name__}")
        if os.path.exists(feat_path):
            self.feature_cols = joblib.load(feat_path)
        if os.path.exists(id_path):
            self.id_to_sector = joblib.load(id_path)

    def apply_ml_predictions(self, df):
        """Use trained champion ML model to generate priority predictions and probabilities."""
        if self.champion_clf is None:
            self.load_champion_models()

        if self.feature_cols is None:
            cols = []
            for indicators in SECTOR_INDICATORS.values():
                cols.extend(indicators)
            self.feature_cols = sorted(list(set(cols)))

        avail_cols = [c for c in self.feature_cols if c in df.columns]
        if not avail_cols:
            return df

        X = df[avail_cols].copy()

        # Fill any missing values with median
        for c in avail_cols:
            if X[c].isnull().any():
                X[c] = X[c].fillna(X[c].median())

        # Predict continuous vulnerability with ML Regressor if available
        if self.champion_reg is not None:
            try:
                pred_vuln = self.champion_reg.predict(X)
                df["vulnerability_index"] = np.clip(pred_vuln, 0.0, 1.0)
                df["vulnerability_category"] = pd.cut(
                    df["vulnerability_index"],
                    bins=[0.0, 0.35, 0.65, 1.0],
                    labels=["Low", "Medium", "High"],
                    include_lowest=True,
                )
            except Exception as e:
                print(f"Warning: ML regressor prediction skipped: {e}")

        # Predict sector priorities with Champion Classifier
        if self.champion_clf is not None:
            try:
                probs = self.champion_clf.predict_proba(X)
                classes = self.champion_clf.classes_

                p1_list, p2_list, p3_list = [], [], []
                conf1_list, conf2_list, conf3_list = [], [], []

                for row_prob in probs:
                    ranked_idx = np.argsort(row_prob)[::-1]
                    # Map to class labels
                    top1_raw = classes[ranked_idx[0]]
                    top2_raw = classes[ranked_idx[1]] if len(ranked_idx) > 1 else top1_raw
                    top3_raw = classes[ranked_idx[2]] if len(ranked_idx) > 2 else top2_raw

                    if self.id_to_sector:
                        top1_name = self.id_to_sector.get(top1_raw, str(top1_raw))
                        top2_name = self.id_to_sector.get(top2_raw, str(top2_raw))
                        top3_name = self.id_to_sector.get(top3_raw, str(top3_raw))
                    else:
                        top1_name = str(top1_raw)
                        top2_name = str(top2_raw)
                        top3_name = str(top3_raw)

                    p1_list.append(top1_name)
                    p2_list.append(top2_name)
                    p3_list.append(top3_name)
                    conf1_list.append(float(row_prob[ranked_idx[0]]))
                    conf2_list.append(float(row_prob[ranked_idx[1]]) if len(ranked_idx) > 1 else float(row_prob[ranked_idx[0]]) * 0.85)
                    conf3_list.append(float(row_prob[ranked_idx[2]]) if len(ranked_idx) > 2 else float(row_prob[ranked_idx[0]]) * 0.70)

                df["priority_sector_1"] = p1_list
                df["priority_sector_2"] = p2_list
                df["priority_sector_3"] = p3_list
                df["priority_confidence_1"] = conf1_list
                df["priority_confidence_2"] = conf2_list
                df["priority_confidence_3"] = conf3_list
                print(f"Applied Champion ML predictions for {len(df)} wards!")
                return df

            except Exception as e:
                print(f"Warning: ML classifier prediction failed: {e}")

        # Fallback to pure math if ML model not available
        from models.sector_prioritizer import assign_priority_columns
        df = assign_priority_columns(df)
        return df

    def initialize(self, data_path=None):
        """Run full pipeline: load → preprocess → compute scores → run Champion ML inference."""
        print("Initializing Smart Panchayat AI Planner with Multi-State ML Engine...")

        # Step 1: Load and preprocess raw multi-state data
        self.df_raw = load_raw_data(data_path)
        self.df_processed = clean_data(self.df_raw.copy())
        self.df_processed, _ = normalize_indicators(self.df_processed)

        # Step 2: Compute sector vulnerability scores
        self.df_processed = compute_sector_scores(self.df_processed)
        self.df_processed = compute_overall_vulnerability(self.df_processed)

        # Step 3: Load Champion ML models and predict
        self.load_champion_models()
        self.df_processed = self.apply_ml_predictions(self.df_processed)

        # Step 4: Save processed data
        os.makedirs(os.path.dirname(PROCESSED_DATA_FILE), exist_ok=True)
        self.df_processed.to_csv(PROCESSED_DATA_FILE, index=False)

        # Pre-index for instantaneous O(1) query lookups
        self._ward_dict = {str(r["ward_name"]).strip(): r.to_dict() for _, r in self.df_processed.iterrows()}
        self._known_states = sorted(self.df_processed["state"].dropna().unique().tolist()) if "state" in self.df_processed.columns else sorted(list(STATES_PANCHAYAT_DATA.keys()))
        self._known_districts = set(self.df_processed["district"].dropna().unique().tolist()) if "district" in self.df_processed.columns else set()
        
        # Build bidirectional geographic ID <-> Name maps
        self._state_name_to_id = {}
        self._state_id_to_name = {}
        self._district_name_to_id = {}
        self._district_id_to_name = {}
        self._panchayat_name_to_id = {}
        self._panchayat_id_to_name = {}

        if "state" in self.df_processed.columns and "state_lgd" in self.df_processed.columns:
            for _, r in self.df_processed[["state", "state_lgd"]].drop_duplicates().iterrows():
                s_name = str(r["state"]).strip()
                s_id = str(r["state_lgd"]).strip()
                self._state_name_to_id[s_name.lower()] = s_id
                self._state_id_to_name[s_id] = s_name

        if "district" in self.df_processed.columns and "district_lgd" in self.df_processed.columns:
            for _, r in self.df_processed[["state", "district", "district_lgd"]].drop_duplicates().iterrows():
                s_name = str(r["state"]).strip().lower()
                d_name = str(r["district"]).strip()
                d_id = str(r["district_lgd"]).strip()
                self._district_name_to_id[(s_name, d_name.lower())] = d_id
                self._district_name_to_id[d_name.lower()] = d_id
                self._district_id_to_name[d_id] = d_name

        p_col = "panchayat_name" if "panchayat_name" in self.df_processed.columns else "panchayat"
        if p_col in self.df_processed.columns and "panchayat_lgd" in self.df_processed.columns:
            for _, r in self.df_processed[["district", p_col, "panchayat_lgd"]].drop_duplicates().iterrows():
                d_name = str(r["district"]).strip().lower()
                p_name = str(r[p_col]).strip()
                p_id = str(r["panchayat_lgd"]).strip()
                self._panchayat_name_to_id[(d_name, p_name.lower())] = p_id
                self._panchayat_name_to_id[p_name.lower()] = p_id
                self._panchayat_id_to_name[p_id] = p_name

        # Precompute string numpy arrays for ultra-fast vectorized filtering (< 0.05ms)
        self._s_lgd_arr = self.df_processed["state_lgd"].astype(str).str.strip().values if "state_lgd" in self.df_processed.columns else None
        self._s_name_arr = self.df_processed["state"].astype(str).str.strip().str.lower().values if "state" in self.df_processed.columns else None
        self._d_lgd_arr = self.df_processed["district_lgd"].astype(str).str.strip().values if "district_lgd" in self.df_processed.columns else None
        self._d_name_arr = self.df_processed["district"].astype(str).str.strip().str.lower().values if "district" in self.df_processed.columns else None
        self._p_lgd_arr = self.df_processed["panchayat_lgd"].astype(str).str.strip().values if "panchayat_lgd" in self.df_processed.columns else None
        self._p_name_arr = self.df_processed[p_col].astype(str).str.strip().str.lower().values if p_col in self.df_processed.columns else None

        self._filter_cache = {}

        self._is_initialized = True
        print(f"Analysis engine fully initialized with {len(self.df_processed)} wards!")
        return self

    def get_state_id(self, state_name):
        """Resolve state name or code to official LGD State ID."""
        if is_all_geographic_val(state_name):
            return "ALL"
        clean = str(state_name).strip()
        if clean.isdigit():
            return clean
        if hasattr(self, "_state_name_to_id") and clean.lower() in self._state_name_to_id:
            return self._state_name_to_id[clean.lower()]
        from data.panchayat_geography import LGD_STATE_CODES
        return str(LGD_STATE_CODES.get(clean, "ALL"))

    def get_district_id(self, district_name, state=None):
        """Resolve district name or code to official LGD District ID."""
        if is_all_geographic_val(district_name):
            return "ALL"
        clean = str(district_name).strip()
        if clean.isdigit():
            return clean
        if hasattr(self, "_district_name_to_id"):
            if state and not is_all_geographic_val(state):
                key = (str(state).strip().lower(), clean.lower())
                if key in self._district_name_to_id:
                    return self._district_name_to_id[key]
            if clean.lower() in self._district_name_to_id:
                return self._district_name_to_id[clean.lower()]
        from data.panchayat_geography import LGD_DISTRICT_CODES
        return str(LGD_DISTRICT_CODES.get(clean, "ALL"))

    def get_panchayat_id(self, panchayat_name, district=None, state=None):
        """Resolve panchayat name or code to official LGD Panchayat ID."""
        if is_all_geographic_val(panchayat_name):
            return "ALL"
        clean = str(panchayat_name).strip()
        if clean.isdigit():
            return clean
        if hasattr(self, "_panchayat_name_to_id"):
            if district and not is_all_geographic_val(district):
                key = (str(district).strip().lower(), clean.lower())
                if key in self._panchayat_name_to_id:
                    return self._panchayat_name_to_id[key]
            if clean.lower() in self._panchayat_name_to_id:
                return self._panchayat_name_to_id[clean.lower()]
        return "ALL"

    def get_location_metadata(self, state=None, district=None, panchayat=None, state_id=None, district_id=None, panchayat_id=None, year="2026-27"):
        """Produce the standardized centralized location dictionary with all 7 required attributes."""
        # Normalize state
        state_str = str(state or "ALL").strip()
        if is_all_geographic_val(state_str) and is_all_geographic_val(state_id):
            sid_str = "ALL"
            sname = "ALL"
        elif state_id and not is_all_geographic_val(state_id):
            sid_str = str(state_id).strip()
            sname = self._state_id_to_name.get(sid_str, state_str if not is_all_geographic_val(state_str) else "ALL")
        else:
            sid_str = self.get_state_id(state_str)
            sname = "ALL" if sid_str == "ALL" else state_str

        # Normalize district
        dist_str = str(district or "ALL").strip()
        if is_all_geographic_val(dist_str) and is_all_geographic_val(district_id):
            did_str = "ALL"
            dname = "ALL"
        elif district_id and not is_all_geographic_val(district_id):
            did_str = str(district_id).strip()
            dname = self._district_id_to_name.get(did_str, dist_str if not is_all_geographic_val(dist_str) else "ALL")
        else:
            did_str = self.get_district_id(dist_str, state=sname)
            dname = "ALL" if did_str == "ALL" else dist_str

        # Normalize panchayat
        panch_str = str(panchayat or "ALL").strip()
        if is_all_geographic_val(panch_str) and is_all_geographic_val(panchayat_id):
            pid_str = "ALL"
            pname = "ALL"
        elif panchayat_id and not is_all_geographic_val(panchayat_id):
            pid_str = str(panchayat_id).strip()
            pname = self._panchayat_id_to_name.get(pid_str, panch_str if not is_all_geographic_val(panch_str) else "ALL")
        else:
            pid_str = self.get_panchayat_id(panch_str, district=dname, state=sname)
            pname = "ALL" if pid_str == "ALL" else panch_str

        # If a specific panchayat is selected but district/state was "ALL", resolve from panchayat hierarchy
        if pname != "ALL" and self.df_processed is not None and "panchayat_name" in self.df_processed.columns:
            if dname == "ALL" or sname == "ALL":
                p_match = self.df_processed[self.df_processed["panchayat_name"].astype(str).str.strip().str.lower() == pname.lower()]
                if not p_match.empty:
                    r0 = p_match.iloc[0]
                    if dname == "ALL":
                        dname = str(r0["district"])
                        did_str = str(r0.get("district_lgd", self.get_district_id(dname)))
                    if sname == "ALL":
                        sname = str(r0["state"])
                        sid_str = str(r0.get("state_lgd", self.get_state_id(sname)))
                    if pid_str == "ALL":
                        pid_str = str(r0.get("panchayat_lgd", "ALL"))

        year_str = str(year or "2026-27").strip()

        return {
            "state_id": sid_str,
            "state_name": sname,
            "district_id": did_str,
            "district_name": dname,
            "panchayat_id": pid_str,
            "panchayat_name": pname,
            "financial_year": year_str,
            # Legacy compatibility aliases
            "state": sname,
            "district": dname,
            "panchayat": pname,
            "year": year_str,
        }

    def get_states(self):
        """Get list of all states available in the dataset."""
        if self._known_states:
            return self._known_states
        if self.df_processed is not None and "state" in self.df_processed.columns:
            self._known_states = sorted(self.df_processed["state"].dropna().unique().tolist())
            if self._known_states:
                return self._known_states
        return sorted(list(STATES_PANCHAYAT_DATA.keys()))

    def get_districts(self, state=None, state_id=None):
        """Get list of districts for a given state or all."""
        resolved_state = state
        if state_id and str(state_id).strip().upper() != "ALL":
            resolved_state = self._state_id_to_name.get(str(state_id).strip(), state or "ALL")

        if self.df_processed is not None and "district" in self.df_processed.columns:
            df = self.df_processed
            if resolved_state and resolved_state != "ALL" and "state" in df.columns:
                df = df[df["state"] == resolved_state]
            dists = sorted(df["district"].dropna().unique().tolist())
            if dists:
                return dists
        if resolved_state and resolved_state in STATES_PANCHAYAT_DATA:
            return sorted(list(STATES_PANCHAYAT_DATA[resolved_state].get("districts", {}).keys()))
        all_dists = []
        for s_info in STATES_PANCHAYAT_DATA.values():
            all_dists.extend(s_info.get("districts", {}).keys())
        return sorted(list(set(all_dists)))

    def get_panchayats(self, district=None, state=None, district_id=None, state_id=None):
        """Get list of panchayats for a district or state."""
        resolved_state = state
        if state_id and str(state_id).strip().upper() != "ALL":
            resolved_state = self._state_id_to_name.get(str(state_id).strip(), state or "ALL")

        resolved_dist = district
        if district_id and str(district_id).strip().upper() != "ALL":
            resolved_dist = self._district_id_to_name.get(str(district_id).strip(), district or "ALL")

        col = "panchayat_name" if (self.df_processed is not None and "panchayat_name" in self.df_processed.columns) else "panchayat"
        if self.df_processed is not None and col in self.df_processed.columns:
            df = self.df_processed
            if resolved_state and resolved_state != "ALL" and "state" in df.columns:
                df = df[df["state"] == resolved_state]
            if resolved_dist and resolved_dist != "ALL" and "district" in df.columns:
                df = df[df["district"] == resolved_dist]
            panchs = sorted(df[col].dropna().unique().tolist())
            if panchs:
                return panchs
        # Fallback to geography mapping
        if resolved_state and resolved_state in STATES_PANCHAYAT_DATA:
            dist_map = STATES_PANCHAYAT_DATA[resolved_state].get("districts", {})
            if resolved_dist and resolved_dist in dist_map:
                return sorted(list(dist_map[resolved_dist].get("panchayats", {}).keys()))
            all_p = []
            for d_info in dist_map.values():
                all_p.extend(d_info.get("panchayats", {}).keys())
            return sorted(list(set(all_p)))
        return []

    def validate_hierarchy(self, state=None, district=None, panchayat=None, state_id=None, district_id=None, panchayat_id=None, year="2026-27", **kwargs):
        """
        Validate strict 3-tier geographical hierarchy:
        State -> District -> Panchayat.
        Returns: (is_valid: bool, error_msg: str or None, metadata: dict)
        """
        meta = self.get_location_metadata(
            state=state, district=district, panchayat=panchayat,
            state_id=state_id, district_id=district_id, panchayat_id=panchayat_id,
            year=year
        )
        s_name = meta["state_name"]
        d_name = meta["district_name"]
        p_name = meta["panchayat_name"]

        # 1. State validation
        if s_name != "ALL":
            valid_states = self.get_states()
            if s_name not in valid_states:
                return False, f"Invalid State: '{s_name}'. Supported states are: {', '.join(valid_states)}", meta

        # 2. District validation
        if d_name != "ALL":
            if s_name == "ALL":
                all_dists = self.get_districts()
                if d_name not in all_dists:
                    return False, f"District '{d_name}' not found in any supported state", meta
            else:
                valid_districts = self.get_districts(state=s_name)
                if d_name not in valid_districts:
                    return False, f"Geographical hierarchy violation: District '{d_name}' does not belong to State '{s_name}'", meta

        # 3. Panchayat validation
        if p_name != "ALL":
            if d_name == "ALL":
                all_panchs = self.get_panchayats(state=s_name if s_name != "ALL" else None)
                if p_name not in all_panchs:
                    return False, f"Panchayat '{p_name}' not found in specified geographical scope", meta
            else:
                valid_panchayats = self.get_panchayats(district=d_name, state=s_name if s_name != "ALL" else None)
                if p_name not in valid_panchayats:
                    return False, f"Geographical hierarchy violation: Panchayat '{p_name}' does not belong to District '{d_name}'", meta

        return True, None, meta

    def get_filtered_df(self, state=None, district=None, panchayat=None, state_id=None, district_id=None, panchayat_id=None, year=None):
        """Filter dataset dynamically by state, district, and panchayat using either names or official LGD IDs.
        Applies strict hierarchical filtering to prevent any cross-location data leakage.
        Utilizes an in-memory dictionary cache for sub-millisecond response.
        """
        if self.df_processed is None:
            return pd.DataFrame()

        # Resolve IDs if only names were given, or names if only IDs were given
        meta = self.get_location_metadata(
            state=state, district=district, panchayat=panchayat,
            state_id=state_id, district_id=district_id, panchayat_id=panchayat_id,
            year=year
        )
        s_id = meta["state_id"]
        s_name = meta["state_name"]
        d_id = meta["district_id"]
        d_name = meta["district_name"]
        p_id = meta["panchayat_id"]
        p_name = meta["panchayat_name"]

        cache_key = (
            str(s_id).strip(),
            str(s_name).strip().lower(),
            str(d_id).strip(),
            str(d_name).strip().lower(),
            str(p_id).strip(),
            str(p_name).strip().lower(),
        )
        if hasattr(self, "_filter_cache") and self._filter_cache is not None:
            if cache_key in self._filter_cache:
                return self._filter_cache[cache_key]

        # Use vectorized boolean filtering on precomputed arrays
        n_rows = len(self.df_processed)
        mask = np.ones(n_rows, dtype=bool)

        # 1. State Filter
        if s_id != "ALL" and self._s_lgd_arr is not None:
            mask &= (self._s_lgd_arr == str(s_id).strip())
        elif s_name != "ALL" and not is_all_geographic_val(s_name) and self._s_name_arr is not None:
            mask &= (self._s_name_arr == s_name.lower())

        # 2. District Filter
        if d_id != "ALL" and self._d_lgd_arr is not None:
            mask &= (self._d_lgd_arr == str(d_id).strip())
        elif d_name != "ALL" and not is_all_geographic_val(d_name) and self._d_name_arr is not None:
            mask &= (self._d_name_arr == d_name.lower())

        # 3. Panchayat Filter
        if p_id != "ALL" and self._p_lgd_arr is not None:
            mask &= (self._p_lgd_arr == str(p_id).strip())
        elif p_name != "ALL" and not is_all_geographic_val(p_name) and self._p_name_arr is not None:
            mask &= (self._p_name_arr == p_name.lower())

        df = self.df_processed[mask]

        if hasattr(self, "_filter_cache") and self._filter_cache is not None:
            self._filter_cache[cache_key] = df
        return df

    def get_ward_names(self, state=None, district=None, panchayat=None, state_id=None, district_id=None, panchayat_id=None):
        """Get list of ward names for the specified geographic location."""
        df = self.get_filtered_df(state=state, district=district, panchayat=panchayat,
                                  state_id=state_id, district_id=district_id, panchayat_id=panchayat_id)
        if df is not None and not df.empty and "ward_name" in df.columns:
            return sorted(df["ward_name"].dropna().unique().tolist())
        return []

    def get_ward_data(self, ward_name, state=None, district=None, panchayat=None, state_id=None, district_id=None, panchayat_id=None):
        """Get all data for a specific ward guaranteed to belong to the requested geographic scope."""
        if not ward_name:
            return None
        clean_name = str(ward_name).strip().lower()

        # If location scope is specified, query within that filtered slice
        has_scope = any(
            v and str(v).strip().upper() != "ALL"
            for v in [state, district, panchayat, state_id, district_id, panchayat_id]
        )
        if has_scope:
            df = self.get_filtered_df(state=state, district=district, panchayat=panchayat,
                                      state_id=state_id, district_id=district_id, panchayat_id=panchayat_id)
            if df is not None and not df.empty and "ward_name" in df.columns:
                match = df[df["ward_name"].astype(str).str.strip().str.lower() == clean_name]
                if not match.empty:
                    return match.iloc[0].to_dict()
            return None

        # Fallback to direct lookup only when no geographic filters were provided
        if hasattr(self, "_ward_dict") and self._ward_dict:
            raw_clean = str(ward_name).strip()
            if raw_clean in self._ward_dict:
                return self._ward_dict[raw_clean]

        if self.df_processed is not None and "ward_name" in self.df_processed.columns:
            match = self.df_processed[self.df_processed["ward_name"].astype(str).str.strip().str.lower() == clean_name]
            if not match.empty:
                return match.iloc[0].to_dict()
        return None

    def get_ward_budget(self, ward_name, total_budget=None, state=None, district=None, panchayat=None):
        """Get budget allocation for a specific ward within the specified location scope."""
        ward_data = self.get_ward_data(ward_name, state=state, district=district, panchayat=panchayat)
        if not ward_data:
            return None
        rankings = get_sector_rankings(ward_data, ward_name)
        if not rankings:
            return None
        return compute_allocation(rankings, total_budget)

    def get_ward_explanation(self, ward_name, sector_name=None, lang="en", state=None, district=None, panchayat=None):
        """Generate AI explanation for a ward's priority sector within the specified location scope."""
        ward_data = self.get_ward_data(ward_name, state=state, district=district, panchayat=panchayat)
        if not ward_data:
            return "No data available for this ward in the selected jurisdiction."

        if sector_name is None:
            sector_name = ward_data.get("priority_sector_1", "")

        from config import SECTOR_INDICATORS
        if sector_name not in SECTOR_INDICATORS:
            for key in SECTOR_INDICATORS:
                if key.lower().replace(" ", "") == sector_name.lower().replace(" ", "").replace("&", "and"):
                    sector_name = key
                    break

        score_col = (
            "score_" + sector_name.lower()
            .replace(" ", "_")
            .replace("&", "and")
            .replace(".", "")
        )
        vulnerability_score = float(ward_data.get(score_col, ward_data.get("vulnerability_index", 0.5)))
        return generate_openai_explanation(ward_name, sector_name, ward_data, vulnerability_score, lang=lang)

    def get_all_wards_summary(self, state=None, district=None, panchayat=None, state_id=None, district_id=None, panchayat_id=None):
        """Get summary DataFrame for wards with optional state/district/panchayat filter."""
        df = self.get_filtered_df(state=state, district=district, panchayat=panchayat,
                                  state_id=state_id, district_id=district_id, panchayat_id=panchayat_id)
        cols = ["ward_id", "state", "district", "panchayat_name", "taluk", "assembly_constituency", "mla_name", "mla_party",
                "ward_name", "ward_profile", "population",
                "vulnerability_index", "vulnerability_category",
                "priority_sector_1", "priority_confidence_1"]
        available = [c for c in cols if c in df.columns]
        if "vulnerability_index" in available and not df.empty:
            return df[available].sort_values("vulnerability_index", ascending=False)
        return df[available] if available else pd.DataFrame(columns=cols)

    def get_panchayat_governance(self, state=None, district=None, panchayat=None, state_id=None, district_id=None, panchayat_id=None):
        """Get governance details (Taluk, Constituency, MLA, Party) for current filter."""
        df = self.get_filtered_df(state=state, district=district, panchayat=panchayat,
                                  state_id=state_id, district_id=district_id, panchayat_id=panchayat_id)
        if df.empty:
            return None
        first = df.iloc[0]
        return {
            "taluk": first.get("taluk", "N/A"),
            "assembly_constituency": first.get("assembly_constituency", "N/A"),
            "mla_name": first.get("mla_name", "N/A"),
            "mla_party": first.get("mla_party", "N/A"),
            "state": first.get("state", state or "N/A"),
            "district": first.get("district", district or "N/A"),
            "panchayat_name": first.get("panchayat_name", panchayat or "N/A"),
            "state_id": str(first.get("state_lgd", state_id or "ALL")),
            "district_id": str(first.get("district_lgd", district_id or "ALL")),
            "panchayat_id": str(first.get("panchayat_lgd", panchayat_id or "ALL")),
        }

    def get_sector_scores_matrix(self, state=None, district=None, panchayat=None, state_id=None, district_id=None, panchayat_id=None):
        """Get matrix of sector scores for wards (for heatmap)."""
        df = self.get_filtered_df(state=state, district=district, panchayat=panchayat,
                                  state_id=state_id, district_id=district_id, panchayat_id=panchayat_id)
        score_cols = [c for c in df.columns if c.startswith("score_")]
        return df[["ward_name"] + score_cols]

    def get_feature_importance(self):
        """Get feature importance from champion ML model or fallback (cached)."""
        if hasattr(self, "_feature_importance_cache") and self._feature_importance_cache:
            return self._feature_importance_cache

        if self.champion_clf and hasattr(self.champion_clf, "feature_importances_"):
            importances = self.champion_clf.feature_importances_
            feature_dict = {}
            for idx, col in enumerate(self.feature_cols):
                if idx < len(importances):
                    feature_dict[col] = float(importances[idx])
            self._feature_importance_cache = dict(sorted(feature_dict.items(), key=lambda x: x[1], reverse=True))
            return self._feature_importance_cache

        from models.sector_prioritizer import get_feature_importance_from_scores
        self._feature_importance_cache = get_feature_importance_from_scores(self.df_processed)
        return self._feature_importance_cache

    def get_training_metrics(self):
        """Load trained models metrics from JSON."""
        metrics_file = os.path.join(MODEL_DIR, "metrics.json")
        if os.path.exists(metrics_file):
            try:
                with open(metrics_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return None

    def retrain_models(self):
        """Trigger ML model retraining on all-panchayat dataset."""
        from models.train_pipeline import benchmark_and_train_best_models
        metrics = benchmark_and_train_best_models()
        self.load_champion_models()
        self._feature_importance_cache = None
        self.df_processed = self.apply_ml_predictions(self.df_processed)
        self._ward_dict = {str(r["ward_name"]).strip(): r.to_dict() for _, r in self.df_processed.iterrows()}
        self._filter_cache = {}
        return metrics


# Singleton instance
_engine = None

def get_engine():
    global _engine
    if _engine is None or not _engine._is_initialized:
        _engine = AnalysisEngine()
        _engine.initialize()
    return _engine
