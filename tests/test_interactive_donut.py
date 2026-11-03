import os
import sys
import subprocess
import pytest

from services.analysis_service import AnalysisEngine
from dashboard.pages.overview import create_mini_donut_svg, create_overview_layout


def test_donut_svg_attributes():
    """Verify that every slice in mini donut SVG has accurate index, value, amt and color attributes."""
    sample_data = [
        ("Economic Development", 30, 15.0, "#142D4E"),
        ("Health & Sanitation", 25, 12.5, "#245B91"),
        ("Agriculture & Food Security", 20, 10.0, "#E99A36"),
        ("Education", 15, 7.5, "#25845A"),
        ("Others", 10, 5.0, "#64748B"),
    ]
    donut_md = create_mini_donut_svg(sectors_data=sample_data, total_budget_cr=50.0, lang="en")
    html_content = donut_md.children

    # Verify container and center overlay
    assert 'id="interactive-hero-donut"' in html_content
    assert 'id="donut-center-val"' in html_content
    assert 'id="donut-center-lbl"' in html_content
    assert 'id="donut-center-sub"' in html_content
    assert 'id="donut-hover-tooltip"' in html_content

    # Verify each slice has index and amount attributes
    for idx, (name, pct, amt, color) in enumerate(sample_data):
        assert f'data-index="{idx}"' in html_content
        assert f'data-val="{pct}%"' in html_content
        assert color in html_content
        assert f'data-amt="₹{amt:.1f} Cr"' in html_content


def test_donut_legend_elements_and_sync():
    """Verify that overview layout generates synchronized legend elements matching the donut slices."""
    engine = AnalysisEngine()
    engine.initialize()
    layout = create_overview_layout(engine, state="Kerala", district="Kasargod", panchayat="Manjeshwar")
    
    # Traverse layout to find donut-legend-item components
    def find_components_by_class(component, class_name):
        matches = []
        if hasattr(component, "className") and component.className and class_name in component.className:
            matches.append(component)
        if hasattr(component, "children"):
            children = component.children
            if isinstance(children, list):
                for child in children:
                    matches.extend(find_components_by_class(child, class_name))
            elif children is not None:
                matches.extend(find_components_by_class(children, class_name))
        return matches

    legend_items = find_components_by_class(layout, "donut-legend-item")
    assert len(legend_items) >= 4, f"Expected at least 4 top sectors in legend, found {len(legend_items)}"

    # Check each legend element has the proper data attributes for tap interaction
    for idx, item in enumerate(legend_items):
        props = item.__dict__
        # In Dash, custom data-* kwargs are preserved in props
        assert props.get("data-index") == str(idx), f"Item {idx} missing data-index"
        assert "data-val" in props, f"Item {idx} missing data-val"
        assert "data-amt" in props, f"Item {idx} missing data-amt"
        assert "data-color" in props, f"Item {idx} missing data-color"
        assert "data-sector" in props, f"Item {idx} missing data-sector"


def test_gov_interactions_syntax_and_event_binding():
    """Ensure gov_interactions.js passes Node.js syntax check and includes complete tap/touch handlers."""
    js_path = os.path.join(os.path.dirname(__file__), "..", "assets", "gov_interactions.js")
    assert os.path.exists(js_path), "gov_interactions.js must exist"

    # 1. Syntax check with Node.js
    res = subprocess.run(["node", "-c", js_path], capture_output=True, text=True)
    assert res.returncode == 0, f"gov_interactions.js syntax error: {res.stderr}"

    # 2. Check for required interaction handlers
    with open(js_path, "r", encoding="utf-8") as f:
        code = f.read()

    assert "function handleDonutInteraction" in code
    assert "function attachDonutListeners" in code
    assert "active-slice" in code
    assert "active-legend" in code
    assert "pointerdown" in code
    assert "touchstart" in code
    assert "click" in code
    assert "data-index" in code
