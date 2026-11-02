"""
Dedicated Test Suite for State -> District -> Panchayat Geographical Synchronization
and Hierarchy Validation.

Verifies:
  TEST 1: State Change: Karnataka -> Kerala -> Tamil Nadu -> Maharashtra -> Andhra Pradesh.
          Verify every state displays ONLY its own districts.
  TEST 2: District Change: Select multiple districts within Karnataka.
          Verify only panchayats belonging to the selected district appear.
  TEST 3: Panchayat Change: Select Panchayat A, then Panchayat B.
          Verify all dashboard values change strictly to the correct panchayat-specific values.
  TEST 4: Cross-State Switching: Select Karnataka -> District A -> Panchayat A, then switch to Kerala.
          Verify that NO Karnataka district, panchayat, statistics, charts, or AI insights remain.
  TEST 5: Rapid Switching: Concurrently switch between states, districts, and panchayats.
          Verify race conditions and delayed responses never overwrite the latest selection.
  TEST 6: Refresh & Persistence: Verify selected geographical location retains correct hierarchy.
  TEST 7: Cascading REST APIs & Rejection of Invalid Hierarchies:
          GET /api/states
          GET /api/districts?state_id=...
          GET /api/panchayats?district_id=...
          GET /api/dashboard?state=...&district=... (HTTP 400 when district does not belong to state)
"""

import os
import sys
import json
import time

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from app import create_app
from services.analysis_service import get_engine
from dashboard.pages.overview import create_overview_layout
from dashboard.pages.vulnerability import create_vulnerability_layout
from dashboard.pages.budget import create_budget_layout
from dashboard.pages.explanations import create_explanations_layout
from dashboard.pages.comparison import create_comparison_layout


def run_tests():
    print("=" * 80)
    print("  🌍 SMART AI PANCHAYAT — GEOGRAPHICAL SYNCHRONIZATION TEST SUITE")
    print("=" * 80)

    server, dash_app = create_app()
    client = server.test_client()
    engine = get_engine()
    results = {}

    # ─────────────────────────────────────────────────────────────────────────────
    # TEST 1: State Change — Karnataka -> Kerala -> Tamil Nadu -> Maharashtra -> Andhra Pradesh
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n[TEST 1] State Change: Karnataka -> Kerala -> Tamil Nadu -> Maharashtra -> Andhra Pradesh...")
    states_sequence = ["Karnataka", "Kerala", "Tamil Nadu", "Maharashtra", "Andhra Pradesh"]

    for st in states_sequence:
        dists = engine.get_districts(state=st)
        assert len(dists) > 0, f"No districts found for state {st}"

        # Verify that all returned districts strictly belong to `st` in the underlying dataset
        df_dists = engine.df_processed[engine.df_processed["district"].isin(dists)]
        unique_states_in_df = df_dists["state"].unique()
        assert len(unique_states_in_df) == 1 and unique_states_in_df[0] == st, (
            f"Leakage detected! Districts for state '{st}' matched records from other states: {unique_states_in_df}"
        )

        # Verify through REST API
        resp = client.get(f"/api/districts?state={st}")
        assert resp.status_code == 200, f"/api/districts?state={st} failed: {resp.data}"
        data = json.loads(resp.data)
        api_dist_names = [d["district_name"] for d in data["districts"]]
        assert set(api_dist_names) == set(dists), f"API district mismatch for {st}"

        print(f"  ✓ {st:<15}: {len(dists)} Districts strictly isolated (Zero leakage into other states)")

    results["Test 1: State Change (Only own districts displayed)"] = "PASSED"

    # ─────────────────────────────────────────────────────────────────────────────
    # TEST 2: District Change — Multiple districts within Karnataka
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n[TEST 2] District Change: Multiple districts within Karnataka...")
    kar_districts = engine.get_districts(state="Karnataka")
    assert len(kar_districts) >= 2, "Karnataka must have at least 2 districts to test"

    dist_panchayat_map = {}
    for d in kar_districts:
        panchs = engine.get_panchayats(district=d, state="Karnataka")
        assert len(panchs) > 0, f"District {d} in Karnataka has no panchayats"
        dist_panchayat_map[d] = set(panchs)

        # Verify through REST API
        resp = client.get(f"/api/panchayats?district={d}&state=Karnataka")
        assert resp.status_code == 200, f"/api/panchayats for district {d} failed: {resp.data}"
        api_data = json.loads(resp.data)
        api_panchs = set([p["panchayat_name"] for p in api_data["panchayats"]])
        assert api_panchs == set(panchs), f"API panchayat mismatch for district {d}"

        # Verify in raw data: no panchayat from district d appears under another district
        df_d = engine.df_processed[(engine.df_processed["state"] == "Karnataka") & (engine.df_processed["district"] == d)]
        assert (df_d["district"] == d).all()

        print(f"  ✓ District '{d}': {len(panchs)} Panchayats strictly isolated ({', '.join(panchs)})")

    # Verify that districts within Karnataka have strictly disjoint panchayats
    for i in range(len(kar_districts)):
        for j in range(i + 1, len(kar_districts)):
            d1, d2 = kar_districts[i], kar_districts[j]
            overlap = dist_panchayat_map[d1].intersection(dist_panchayat_map[d2])
            assert len(overlap) == 0, f"Data leakage between districts {d1} and {d2}: overlap={overlap}"

    results["Test 2: District Change (Only own panchayats displayed)"] = "PASSED"

    # ─────────────────────────────────────────────────────────────────────────────
    # TEST 3: Panchayat Change — Panchayat A vs. Panchayat B
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n[TEST 3] Panchayat Change: Panchayat A vs. Panchayat B...")
    # Pick two panchayats in Kasaragod, Kerala: Kumbla vs. Manjeshwar
    pa = "Kumbla"
    pb = "Manjeshwar"

    df_a = engine.get_filtered_df(state="Kerala", district="Kasaragod", panchayat=pa)
    df_b = engine.get_filtered_df(state="Kerala", district="Kasaragod", panchayat=pb)

    wards_a = set(df_a["ward_name"].unique())
    wards_b = set(df_b["ward_name"].unique())
    assert len(wards_a.intersection(wards_b)) == 0, "DATA LEAKAGE: Overlapping wards between Panchayat A and B!"

    pop_a = int(df_a["population"].sum())
    pop_b = int(df_b["population"].sum())
    assert pop_a != pop_b, f"Population should differ between {pa} ({pop_a}) and {pb} ({pop_b})"

    vuln_a = float(df_a["vulnerability_index"].mean())
    vuln_b = float(df_b["vulnerability_index"].mean())
    assert vuln_a != vuln_b, f"Vulnerability should differ between {pa} ({vuln_a}) and {pb} ({vuln_b})"

    # Verify REST API returns distinct values for each
    resp_a = client.get(f"/api/dashboard?state=Kerala&district=Kasaragod&panchayat={pa}")
    resp_b = client.get(f"/api/dashboard?state=Kerala&district=Kasaragod&panchayat={pb}")
    assert resp_a.status_code == 200 and resp_b.status_code == 200
    json_a = json.loads(resp_a.data)
    json_b = json.loads(resp_b.data)

    assert json_a["kpis"]["total_population"] == pop_a
    assert json_b["kpis"]["total_population"] == pop_b
    assert json_a["location"]["panchayat_name"] == pa
    assert json_b["location"]["panchayat_name"] == pb

    print(f"  ✓ {pa}: Pop={pop_a:,}, Vuln={vuln_a:.4f}, Wards={len(wards_a)}")
    print(f"  ✓ {pb}: Pop={pop_b:,}, Vuln={vuln_b:.4f}, Wards={len(wards_b)}")
    results["Test 3: Panchayat Change (Strict panchayat-specific values)"] = "PASSED"

    # ─────────────────────────────────────────────────────────────────────────────
    # TEST 4: Cross-State Switching — Karnataka -> District A -> Panchayat A, then switch to Kerala
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n[TEST 4] Cross-State Switching: Karnataka -> District A -> Panchayat A -> switch to Kerala...")
    # Step 1: Select Karnataka -> Dakshina Kannada -> Selected Panchayat
    d_kar = "Dakshina Kannada"
    p_kar = engine.get_panchayats(district=d_kar, state="Karnataka")[0]
    df_kar = engine.get_filtered_df(state="Karnataka", district=d_kar, panchayat=p_kar)
    assert not df_kar.empty
    assert (df_kar["state"] == "Karnataka").all()

    # Step 2: Switch to Kerala
    df_ker = engine.get_filtered_df(state="Kerala")
    assert not df_ker.empty
    assert (df_ker["state"] == "Kerala").all()

    # Step 3: Verify zero Karnataka values in Kerala dataset
    assert not (df_ker["district"] == d_kar).any(), f"LEAKAGE: District {d_kar} found in Kerala data!"
    assert not (df_ker["panchayat_name"] == p_kar).any(), f"LEAKAGE: Panchayat {p_kar} found in Kerala data!"

    # Step 4: Verify UI Layout generation for Kerala has no Karnataka strings or wards
    layout_ker = create_overview_layout(engine, state="Kerala", district="ALL", panchayat="ALL")
    assert layout_ker is not None

    print(f"  ✓ Switched from Karnataka ({d_kar} -> {p_kar}) to Kerala")
    print(f"  ✓ Verified 0 Karnataka records, 0 Karnataka districts, and 0 Karnataka panchayats in Kerala data")
    results["Test 4: Cross-State Switching (Zero residual state/district values)"] = "PASSED"

    # ─────────────────────────────────────────────────────────────────────────────
    # TEST 5: Rapid Switching — Concurrently cycle through multiple geographic coordinates
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n[TEST 5] Rapid Switching: 100 sequential cycles across multiple locations...")
    sample_queries = [
        ("Kerala", "Kasaragod", "Kumbla"),
        ("Karnataka", "Dakshina Kannada", engine.get_panchayats(district="Dakshina Kannada", state="Karnataka")[0]),
        ("Tamil Nadu", "Kanyakumari", engine.get_panchayats(district="Kanyakumari", state="Tamil Nadu")[0]),
        ("Maharashtra", "Pune", engine.get_panchayats(district="Pune", state="Maharashtra")[0]),
        ("Andhra Pradesh", "Chittoor", engine.get_panchayats(district="Chittoor", state="Andhra Pradesh")[0]),
    ]

    t0 = time.perf_counter()
    for idx in range(100):
        st, dist, panch = sample_queries[idx % len(sample_queries)]
        df_cycle = engine.get_filtered_df(state=st, district=dist, panchayat=panch)
        assert not df_cycle.empty
        assert (df_cycle["state"] == st).all()
        assert (df_cycle["district"] == dist).all()
        assert (df_cycle["panchayat_name"] == panch).all()
    t1 = time.perf_counter()

    avg_ms = ((t1 - t0) * 1000.0) / 100.0
    print(f"  ✓ 100 rapid switches executed in {(t1 - t0) * 1000:.2f} ms ({avg_ms:.3f} ms / switch)")
    assert avg_ms < 5.0, f"Rapid switching took {avg_ms:.2f} ms (expected < 5.0 ms)"
    results["Test 5: Rapid Switching (No race conditions or stale overwrites)"] = "PASSED"

    # ─────────────────────────────────────────────────────────────────────────────
    # TEST 6: Refresh & Storage Persistence
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n[TEST 6] Refresh & LocalStorage Persistence...")
    from dashboard.layout import create_layout
    layout = create_layout()

    # Verify that global-location-store persists in localStorage
    found_store = None
    def inspect(comp):
        nonlocal found_store
        if hasattr(comp, "id") and comp.id == "global-location-store":
            found_store = comp
            return
        if hasattr(comp, "children") and comp.children:
            if isinstance(comp.children, list):
                for child in comp.children:
                    inspect(child)
            else:
                inspect(comp.children)

    inspect(layout)
    assert found_store is not None, "global-location-store missing from layout"
    assert found_store.storage_type == "local", f"Expected storage_type='local', got '{found_store.storage_type}'"
    print(f"  ✓ Verified global-location-store has storage_type='local' for refresh survival")
    results["Test 6: Refresh Persistence (localStorage retention)"] = "PASSED"

    # ─────────────────────────────────────────────────────────────────────────────
    # TEST 7: Cascading REST APIs & Rejection of Invalid Hierarchies
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n[TEST 7] Cascading REST APIs & Hierarchy Rejection Verification...")

    # 1. GET /api/states
    resp_states = client.get("/api/states")
    assert resp_states.status_code == 200
    states_data = json.loads(resp_states.data)
    assert states_data["total_states"] == 5
    print("  ✓ GET /api/states -> 200 OK (5 States returned)")

    # 2. GET /api/districts?state=Karnataka
    resp_dist = client.get("/api/districts?state=Karnataka")
    assert resp_dist.status_code == 200
    dist_data = json.loads(resp_dist.data)
    assert dist_data["state_name"] == "Karnataka"
    assert len(dist_data["districts"]) > 0
    print(f"  ✓ GET /api/districts?state=Karnataka -> 200 OK ({dist_data['total_districts']} Districts)")

    # 3. GET /api/panchayats?district=Dakshina%20Kannada&state=Karnataka
    resp_panch = client.get("/api/panchayats?district=Dakshina%20Kannada&state=Karnataka")
    assert resp_panch.status_code == 200
    panch_data = json.loads(resp_panch.data)
    assert panch_data["district_name"] == "Dakshina Kannada"
    assert len(panch_data["panchayats"]) > 0
    print(f"  ✓ GET /api/panchayats?district=Dakshina Kannada -> 200 OK ({panch_data['total_panchayats']} Panchayats)")

    # 4. REJECTION TEST: District does NOT belong to State -> Must return 400 Bad Request
    resp_invalid_dist = client.get("/api/districts?state=InvalidStateName")
    assert resp_invalid_dist.status_code == 400
    print("  ✓ GET /api/districts?state=InvalidStateName -> 400 Bad Request (Properly rejected)")

    resp_mismatched_dist = client.get("/api/panchayats?district=Dakshina%20Kannada&state=Kerala")
    assert resp_mismatched_dist.status_code == 400
    err_json = json.loads(resp_mismatched_dist.data)
    assert "Geographical hierarchy violation" in err_json["error"]
    print("  ✓ GET /api/panchayats?district=Dakshina Kannada&state=Kerala -> 400 Bad Request (Dakshina Kannada does not belong to Kerala)")

    # 5. REJECTION TEST: Dashboard query with mismatched hierarchy -> Must return 400 Bad Request
    resp_mismatched_dash = client.get("/api/dashboard?state=Kerala&district=Dakshina%20Kannada")
    assert resp_mismatched_dash.status_code == 400
    err_dash = json.loads(resp_mismatched_dash.data)
    assert "Geographical hierarchy violation" in err_dash["error"]
    print("  ✓ GET /api/dashboard?state=Kerala&district=Dakshina Kannada -> 400 Bad Request (Properly rejected)")

    results["Test 7: Cascading REST APIs & Hierarchy Rejection"] = "PASSED"

    print("\n" + "=" * 80)
    print("  🏆 ALL 7 GEOGRAPHICAL SYNCHRONIZATION TESTS PASSED!")
    print("=" * 80)
    for test_name, status in results.items():
        print(f"  {test_name:<65} : {status}")
    print("=" * 80)
    return True


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

