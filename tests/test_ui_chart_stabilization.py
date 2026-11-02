"""
Automated Test Suite for UI Chart Stabilization, Container Sizing,
and Complete Geographic Hierarchy Quality Assurance.
"""

import os
import sys
import pytest

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from services.analysis_service import AnalysisEngine, is_all_geographic_val
from dashboard.pages.overview import create_overview_layout
from dashboard.pages.budget import create_budget_layout, create_budget_charts
from dashboard.pages.comparison import create_comparison_layout
from dashboard.pages.explanations import create_explanations_layout
from dashboard.pages.vulnerability import create_vulnerability_layout


def test_is_all_geographic_val():
    assert is_all_geographic_val("ALL") is True
    assert is_all_geographic_val("All 5 Districts") is True
    assert is_all_geographic_val("All Districts") is True
    assert is_all_geographic_val("All 32 Districts") is True
    assert is_all_geographic_val("All 5 States") is True
    assert is_all_geographic_val("All 128 Panchayats") is True
    assert is_all_geographic_val(None) is True
    assert is_all_geographic_val("") is True
    assert is_all_geographic_val("Kerala") is False
    assert is_all_geographic_val("Dakshina Kannada") is False
    assert is_all_geographic_val("Bantwal") is False


from dash import dcc


def _find_graphs_in_node(node):
    graphs = []
    if isinstance(node, dcc.Graph):
        graphs.append(node)
    if hasattr(node, "children"):
        ch = node.children
        if isinstance(ch, list):
            for c in ch:
                graphs.extend(_find_graphs_in_node(c))
        elif ch is not None:
            graphs.extend(_find_graphs_in_node(ch))
    return graphs


def test_overview_charts_have_explicit_dimensions():
    engine = AnalysisEngine()
    engine.initialize()

    # Test under Karnataka -> Bantwal
    layout = create_overview_layout(engine, state="Karnataka", district="Dakshina Kannada", panchayat="Bantwal")
    assert layout is not None

    graphs = _find_graphs_in_node(layout)
    assert len(graphs) >= 6, f"Expected at least 6 governance charts in overview layout, found {len(graphs)}"

    for g in graphs:
        style = getattr(g, "style", {}) or {}
        assert "height" in style, f"Graph missing explicit style height"
        assert style["height"] in ("320px", "340px", "350px", "380px", "400px"), f"Unexpected graph height: {style['height']}"
        assert style.get("width") == "100%", "Graph must have 100% width for full card responsiveness"
        assert "minHeight" in style, "Graph must have minHeight to prevent zero-height collapse"


def test_budget_charts_have_explicit_dimensions():
    engine = AnalysisEngine()
    engine.initialize()

    charts = create_budget_charts(engine, ward_name="Hosabettu", total_budget_lakhs=50.0, state="Kerala", district="Kasaragod", panchayat="Manjeshwar")
    assert charts is not None

    graphs = _find_graphs_in_node(charts)
    assert len(graphs) >= 2, f"Expected 2 budget charts, found {len(graphs)}"
    for g in graphs:
        style = getattr(g, "style", {}) or {}
        assert style.get("height") == "400px", f"Budget chart must have 400px height, got {style.get('height')}"
        assert style.get("width") == "100%"
        assert style.get("minHeight") == "400px"


def test_all_five_states_render_without_error():
    engine = AnalysisEngine()
    engine.initialize()

    states = ["Kerala", "Karnataka", "Tamil Nadu", "Andhra Pradesh", "Maharashtra"]
    for s in states:
        dists = engine.get_districts(state=s)
        assert len(dists) > 0, f"State {s} has no districts"
        d = dists[0]
        panchs = engine.get_panchayats(district=d, state=s)
        assert len(panchs) > 0, f"District {d} in {s} has no panchayats"
        p = panchs[0]

        df = engine.get_filtered_df(state=s, district=d, panchayat=p)
        assert len(df) > 0, f"Zero records returned for {s} -> {d} -> {p}"
        assert df["state"].iloc[0] == s
        assert df["district"].iloc[0] == d
        assert df["panchayat_name"].iloc[0] == p

        layout = create_overview_layout(engine, state=s, district=d, panchayat=p)
        assert layout is not None


def test_validate_hierarchy_accepts_year():
    engine = AnalysisEngine()
    engine.initialize()

    is_valid, err, meta = engine.validate_hierarchy(
        state="Karnataka", district="Dakshina Kannada", panchayat="Bantwal", year="2026-27"
    )
    assert is_valid is True
    assert err is None
    assert meta["state_name"] == "Karnataka"
    assert meta["district_name"] == "Dakshina Kannada"
    assert meta["panchayat_name"] == "Bantwal"
    assert meta["financial_year"] == "2026-27"


if __name__ == "__main__":
    test_is_all_geographic_val()
    test_overview_charts_have_explicit_dimensions()
    test_budget_charts_have_explicit_dimensions()
    test_all_five_states_render_without_error()
    test_validate_hierarchy_accepts_year()
    print("All UI chart stabilization tests passed successfully!")
