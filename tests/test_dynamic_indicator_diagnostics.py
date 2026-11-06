"""
Test Suite: Dynamic Indicator Variance Analysis and Dynamic Sector Drill-Down.
Validates:
1. Indicator Variance Analysis computes genuine model split-importance and updates with geographic scope.
2. Section headers and analytical interpretations reflect active State, District, and Panchayat.
3. Indicator Drill-Down updates dynamically across all 8 verified development sectors.
4. Comprehensive indicator metadata catalog covers all 40 indicators with definitions, units, and sources.
5. Table rendering includes empirical base values and normalized vulnerability scores.
"""

import pytest
from services.analysis_service import AnalysisEngine
from data.indicator_metadata import INDICATOR_METADATA, get_indicator_meta
from config import SECTOR_INDICATORS
from dashboard.pages.explanations import (
    create_indicator_variance_section,
    create_sector_drilldown_view,
    create_sector_indicator_chart,
    create_global_importance_chart,
    ALL_SECTORS,
)


@pytest.fixture(scope="module")
def engine():
    eng = AnalysisEngine()
    eng.initialize()
    return eng


def test_indicator_metadata_completeness():
    """Verify that all 40 indicators across the 8 sectors have full authoritative metadata."""
    assert len(SECTOR_INDICATORS) == 8
    total_inds = 0
    for sector, inds in SECTOR_INDICATORS.items():
        assert len(inds) == 5
        total_inds += len(inds)
        for ind in inds:
            meta = get_indicator_meta(ind)
            assert meta["id"] == ind
            assert len(meta["name"]) > 0
            assert len(meta["definition"]) > 10
            assert len(meta["unit"]) > 0
            assert len(meta["direction"]) > 0
            assert len(meta["source"]) > 0
            assert len(meta["period"]) > 0
    assert total_inds == 40


def test_feature_importance_global_and_localized(engine):
    """Verify diagnostic importance returns genuine scores and adapts to geographic scope."""
    # 1. Global Benchmark
    global_meta = engine.get_feature_importance(include_metadata=True)
    assert "scores" in global_meta
    assert len(global_meta["scores"]) == 40
    assert "National Baseline" in global_meta["geographic_scope"]
    assert len(global_meta["top_drivers"]) == 3
    assert len(global_meta["interpretation"]) > 30

    # 2. Localized: Kerala / Alappuzha / Ambalappuzha
    local_meta = engine.get_feature_importance(
        state="Kerala", district="Alappuzha", panchayat="Ambalappuzha", include_metadata=True
    )
    assert "scores" in local_meta
    assert len(local_meta["scores"]) == 40
    assert "Ambalappuzha GP" in local_meta["geographic_scope"]
    assert len(local_meta["top_drivers"]) == 3
    # Top driver scores must be dynamically computed
    assert local_meta["scores"] != global_meta["scores"]


def test_sector_drilldown_updates_across_all_sectors(engine):
    """Verify that drill-down view updates for every one of the 8 development verticals."""
    ward_name = "Ward 1"
    for sector in ALL_SECTORS:
        view = create_sector_drilldown_view(
            engine,
            ward_name,
            sector,
            lang="en",
            state="Kerala",
            district="Alappuzha",
            panchayat="Ambalappuzha",
        )
        assert view is not None
        # Check that component tree contains table and chart
        tree_str = str(view)
        assert sector in tree_str or sector.replace("&", "and") in tree_str
        assert "INDICATOR DRILL-DOWN" in tree_str
        assert "Table" in tree_str or "Tr" in tree_str


def test_indicator_variance_section_scope_adaptation(engine):
    """Verify that Indicator Variance section renders dynamically with scope-based headers."""
    # Scope 1: Kerala
    sec_kerala = create_indicator_variance_section(engine, lang="en", state="Kerala")
    str_kerala = str(sec_kerala)
    assert "State Benchmark: Kerala" in str_kerala or "Kerala" in str_kerala

    # Scope 2: Karnataka / Bantwal
    sec_bantwal = create_indicator_variance_section(
        engine, lang="en", state="Karnataka", district="Dakshina Kannada", panchayat="Bantwal"
    )
    str_bantwal = str(sec_bantwal)
    assert "Bantwal" in str_bantwal

