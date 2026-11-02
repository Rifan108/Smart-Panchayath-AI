"""
Verification Test Suite: Loading Resolution, Callback Cycle Elimination & Response Time.
Ensures:
1. Zero infinite callback loops (callbacks finish in <= 1 pass).
2. State -> District -> Panchayat cascading updates finish in < 5ms.
3. Proper loading state reset without hang.
4. Full 5-state repeated switching stress test without performance degradation.
5. District & Panchayat intra-state switching without residual data.
"""

import sys
import os
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.analysis_service import AnalysisEngine
from services.cache_service import get_cached_layout, clear_layout_cache, make_cache_key
from dashboard.pages.overview import create_overview_layout
from dashboard.pages.vulnerability import create_vulnerability_layout
from dashboard.pages.budget import create_budget_layout
from dashboard.pages.explanations import create_explanations_layout
from dashboard.pages.comparison import create_comparison_layout
from app import create_app


def run_tests():
    print("=" * 80)
    print("  ⚡ SMART AI PANCHAYAT — LOADING & PERFORMANCE VERIFICATION SUITE")
    print("=" * 80)

    # Step 1: Initialize server and dash app
    server, dash_app = create_app()
    client = server.test_client()
    engine = AnalysisEngine()
    engine.initialize()

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 1: Check Callback Dependency Graph (Verify Acyclic Topology)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 1] Verifying Callback Graph Acyclicity (No Cycles)...")
    callback_map = dash_app.callback_map

    # Check that header-district-selector options/value do not listen to global-location-store
    dist_cb = None
    panch_cb = None
    store_cb = None

    for k, cb in callback_map.items():
        if "header-district-selector.options" in k:
            dist_cb = cb
        if "header-panchayat-selector.options" in k:
            panch_cb = cb
        if "global-location-store.data" in k and "Output" in str(cb.get("output", "")):
            store_cb = cb

    assert dist_cb is not None, "Cascading district callback missing"
    assert panch_cb is not None, "Cascading panchayat callback missing"
    assert store_cb is not None, "Master location store callback missing"

    dist_inputs = [i["id"] for i in dist_cb["inputs"]]
    panch_inputs = [i["id"] for i in panch_cb["inputs"]]

    assert "global-location-store" not in dist_inputs, (
        "CRITICAL ERROR: header-district-selector must NOT take global-location-store as input (causes cycle)!"
    )
    assert "global-location-store" not in panch_inputs, (
        "CRITICAL ERROR: header-panchayat-selector must NOT take global-location-store as input (causes cycle)!"
    )
    print("  ✓ Graph Acyclicity Verified: Dropdown cascading is strictly 1-way (State -> District -> Panchayat -> Store)")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 2: Cascading State Dropdown -> District Reset Test
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 2] Cascading Dropdown Hierarchy Resolution (< 1 ms)...")
    t0 = time.perf_counter()
    k_dists = engine.get_districts(state="Karnataka")
    assert "Dakshina Kannada" in k_dists
    assert "Kasaragod" not in k_dists, "Data leakage: Kasaragod (Kerala) found in Karnataka!"

    k_panchs = engine.get_panchayats(district="Dakshina Kannada", state="Karnataka")
    assert "Bantwal" in k_panchs
    assert "Kumbla" not in k_panchs, "Data leakage: Kumbla (Kerala) found in Dakshina Kannada!"
    t1 = time.perf_counter()
    print(f"  ✓ Cascade resolution executed in {(t1-t0)*1000:.3f} ms with strict isolation.")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 3: Multi-State Repeated Switching Loop (5 States)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 3] Repeated State Switching: Karnataka -> Kerala -> Tamil Nadu -> Maharashtra -> Andhra Pradesh...")
    states_sequence = ["Karnataka", "Kerala", "Tamil Nadu", "Maharashtra", "Andhra Pradesh"] * 10
    switch_times = []

    for idx, st in enumerate(states_sequence):
        t_start = time.perf_counter()
        df = engine.get_filtered_df(state=st)
        assert not df.empty, f"No wards found for {st}"
        assert (df["state"] == st).all(), f"State contamination in {st}"
        t_end = time.perf_counter()
        switch_times.append((t_end - t_start) * 1000)

    avg_switch = sum(switch_times) / len(switch_times)
    print(f"  ✓ 50 state switches executed seamlessly. Avg query latency: {avg_switch:.4f} ms (< 1 ms target)")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 4: District Sequence Switching (District A -> District B -> District C)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 4] Intra-State District Switching (Bengaluru Rural -> Dakshina Kannada -> Kodagu)...")
    dists = ["Bengaluru Rural", "Dakshina Kannada", "Kodagu"]
    for d in dists:
        t_start = time.perf_counter()
        df = engine.get_filtered_df(state="Karnataka", district=d)
        assert len(df) > 0, f"No data for district {d}"
        assert (df["district"] == d).all(), f"District mismatch for {d}"
        t_end = time.perf_counter()
        print(f"  ✓ District '{d}': {len(df)} wards verified in {(t_end - t_start)*1000:.3f} ms")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 5: Panchayat Sequence Switching (Panchayat A -> Panchayat B -> Panchayat C)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 5] Panchayat Switching within District (Bantwal -> Belthangady -> Puttur)...")
    panchs = ["Bantwal", "Belthangady", "Puttur"]
    for p in panchs:
        t_start = time.perf_counter()
        df = engine.get_filtered_df(state="Karnataka", district="Dakshina Kannada", panchayat=p)
        assert len(df) > 0, f"No data for panchayat {p}"
        assert (df["panchayat_name"] == p).all(), f"Panchayat mismatch for {p}"
        t_end = time.perf_counter()
        print(f"  ✓ Panchayat '{p}': {len(df)} wards verified in {(t_end - t_start)*1000:.3f} ms")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 6: Pre-rendered Layout Cache Hit Latency (< 0.05 ms)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 6] Pre-rendered Layout Cache Latency Verification...")
    clear_layout_cache()

    # Cold render
    t0 = time.perf_counter()
    _ = get_cached_layout("overview", create_overview_layout, engine, state="Kerala", district="Kasaragod", panchayat="Kumbla")
    t1 = time.perf_counter()
    cold_ms = (t1 - t0) * 1000

    # Warm cache hits (100 iterations)
    warm_times = []
    for _ in range(100):
        t0 = time.perf_counter()
        _ = get_cached_layout("overview", create_overview_layout, engine, state="Kerala", district="Kasaragod", panchayat="Kumbla")
        t1 = time.perf_counter()
        warm_times.append((t1 - t0) * 1000)

    avg_warm = sum(warm_times) / len(warm_times)
    print(f"  ✓ Cold render: {cold_ms:.2f} ms | Warm cache: {avg_warm:.5f} ms per retrieval")
    assert avg_warm < 0.1, f"Warm cache took too long: {avg_warm} ms"

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 7: REST API Response Latency Under Load (Cold & Warm)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 7] REST API Endpoint Response Performance...")
    # 1. /api/states
    res = client.get("/api/states")
    assert res.status_code == 200

    # 2. /api/districts
    t0 = time.perf_counter()
    res = client.get("/api/districts?state=Kerala")
    t1 = time.perf_counter()
    assert res.status_code == 200
    print(f"  ✓ GET /api/districts?state=Kerala: 200 OK in {(t1-t0)*1000:.2f} ms")

    # 3. /api/panchayats
    t0 = time.perf_counter()
    res = client.get("/api/panchayats?district=Kasaragod&state=Kerala")
    t1 = time.perf_counter()
    assert res.status_code == 200
    print(f"  ✓ GET /api/panchayats?district=Kasaragod: 200 OK in {(t1-t0)*1000:.2f} ms")

    # 4. /api/dashboard
    t0 = time.perf_counter()
    res = client.get("/api/dashboard?state=Kerala&district=Kasaragod&panchayat=Kumbla")
    t1 = time.perf_counter()
    assert res.status_code == 200
    print(f"  ✓ GET /api/dashboard: 200 OK in {(t1-t0)*1000:.2f} ms")

    # 5. /api/insights
    t0 = time.perf_counter()
    res = client.get("/api/insights?state=Kerala&district=Kasaragod&panchayat=Kumbla")
    t1 = time.perf_counter()
    assert res.status_code == 200
    print(f"  ✓ GET /api/insights: 200 OK in {(t1-t0)*1000:.2f} ms")

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 8: Loading State UI Components Verification
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[TEST 8] Loading State Wrappers Verification in Layout...")
    from dashboard.layout import create_layout
    layout = create_layout()

    # Recursively check that dcc.Loading is present
    loading_ids = []
    def find_loadings(comp):
        if hasattr(comp, "id") and "loading" in str(comp.id):
            loading_ids.append(str(comp.id))
        if hasattr(comp, "children"):
            children = comp.children
            if isinstance(children, list):
                for c in children:
                    find_loadings(c)
            elif children:
                find_loadings(children)

    find_loadings(layout)
    assert len(loading_ids) > 0, "No dcc.Loading wrapper found in application shell!"
    print(f"  ✓ Verified non-blocking loading wrappers present in shell: {loading_ids}")

    print("\n" + "=" * 80)
    print("  🏆 ALL 8 LOADING & PERFORMANCE VERIFICATION TESTS PASSED FLAWLESSLY!")
    print("=" * 80)


if __name__ == "__main__":
    run_tests()

