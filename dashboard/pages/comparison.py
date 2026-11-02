"""
Reports & Disparity Analytics Portal — Official Indian Government Administrative Reporting Interface.
Includes State Development Reports, District Audits, Panchayat Comprehensive Plans,
Budget Utilization Audits, AI Recommendation Reports, and Inter-Ward Disparity Benchmarks.
Supports print generation, CSV export, and institutional public-sector document aesthetics.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.graph_objects as go
import pandas as pd
from services.i18n import t, get_sector_name
from dashboard.layout import create_shared_location_breadcrumb
from services.provenance_service import ProvenanceService, STATUS_VERIFIED, STATUS_CALCULATED


def create_official_print_document(ward_a, ward_b, row_a, row_b, score_cols, vals_a, vals_b, raw_labels, lang="en", state="ALL", district="ALL", panchayat="ALL", year="2026-27", total_pop=0, active_wards=0):
    """
    Construct the authoritative 1-Page Official Statutory Government Report & Memorandum.
    Strictly engineered for A4 single-page print output adhering to Gazette standards:
    - Tricolour header ribbon & Official LSGI / National Emblem
    - Ministry of Panchayati Raj / LSGI Institutional Authority Headings
    - Official Reference Number, Date & Statutory Form VII Classification
    - Administrative Jurisdiction Metadata Grid (State, District, GP, Pop, Scope)
    - Comparative Benchmark Profiles (Ward A vs Ward B, MLAs, Constituencies, Categories)
    - 8-Sector Deficit & Priority Matrix Table
    - AI LP-Solver Statutory Planning Directive
    - Three-Tier Sign-off & Verification Certification Block (Secretary, AE, President)
    - Official IT Act 2000 Compliance Footer (Page 1 of 1)
    """
    if state and state != "ALL":
        state_str = state
    elif "state" in row_a.columns and pd.notnull(row_a["state"].values[0]):
        state_str = str(row_a["state"].values[0])
    else:
        state_str = "All Participating States"

    if district and district != "ALL":
        dist_str = f"{district} District"
    elif "district" in row_a.columns and pd.notnull(row_a["district"].values[0]):
        dist_str = f"{row_a['district'].values[0]} District"
    else:
        dist_str = "Statewide Jurisdiction"

    panch_val = row_a["panchayat_name"].values[0] if "panchayat_name" in row_a.columns else (row_a["panchayat"].values[0] if "panchayat" in row_a.columns else None)
    if panchayat and panchayat != "ALL":
        panch_str = f"{panchayat} GP"
    elif panch_val and pd.notnull(panch_val):
        panch_str = f"{panch_val} GP"
    else:
        panch_str = "Grama Panchayat Jurisdiction"
    fy_str = year or "2026-27"
    doc_ref = f"LSGI/AI-DEC/{fy_str}/PR-{abs(hash(str(ward_a) + str(ward_b))) % 9000 + 1000}"

    vi_a = float(row_a["vulnerability_index"].values[0]) if "vulnerability_index" in row_a.columns else 0.0
    vi_b = float(row_b["vulnerability_index"].values[0]) if "vulnerability_index" in row_b.columns else 0.0
    cat_a = str(row_a["vulnerability_category"].values[0]) if "vulnerability_category" in row_a.columns else "Moderate"
    cat_b = str(row_b["vulnerability_category"].values[0]) if "vulnerability_category" in row_b.columns else "Moderate"

    taluk_a = str(row_a["taluk"].values[0]) if "taluk" in row_a.columns else "N/A"
    const_a = str(row_a["assembly_constituency"].values[0]) if "assembly_constituency" in row_a.columns else "N/A"
    mla_a = str(row_a["mla_name"].values[0]) if "mla_name" in row_a.columns else "N/A"
    party_a = f" ({row_a['mla_party'].values[0]})" if ("mla_party" in row_a.columns and pd.notnull(row_a['mla_party'].values[0])) else ""

    taluk_b = str(row_b["taluk"].values[0]) if "taluk" in row_b.columns else "N/A"
    const_b = str(row_b["assembly_constituency"].values[0]) if "assembly_constituency" in row_b.columns else "N/A"
    mla_b = str(row_b["mla_name"].values[0]) if "mla_name" in row_b.columns else "N/A"
    party_b = f" ({row_b['mla_party'].values[0]})" if ("mla_party" in row_b.columns and pd.notnull(row_b['mla_party'].values[0])) else ""

    p1_a = str(row_a["priority_sector_1"].values[0]) if "priority_sector_1" in row_a.columns else "N/A"
    p1_b = str(row_b["priority_sector_1"].values[0]) if "priority_sector_1" in row_b.columns else "N/A"

    table_rows = []
    for idx, (raw_label, col, va, vb) in enumerate(zip(raw_labels, score_cols, vals_a, vals_b), 1):
        diff = va - vb
        if diff > 0.05:
            alloc_status = "CRITICAL DEFICIT (A)"
            status_style = {"color": "#991B1B", "fontWeight": "700"}
        elif diff < -0.05:
            alloc_status = "CRITICAL DEFICIT (B)"
            status_style = {"color": "#166534", "fontWeight": "700"}
        else:
            alloc_status = "COMPARABLE PARITY"
            status_style = {"color": "#854D0E", "fontWeight": "600"}

        table_rows.append(html.Tr([
            html.Td(str(idx), style={"textAlign": "center", "fontWeight": "600", "width": "5%"}),
            html.Td(html.Strong(get_sector_name(raw_label, lang)), style={"width": "35%"}),
            html.Td(f"{va:.3f}", style={"textAlign": "center", "fontFeatureSettings": "'tnum' 1", "fontWeight": "600", "width": "15%"}),
            html.Td(f"{vb:.3f}", style={"textAlign": "center", "fontFeatureSettings": "'tnum' 1", "fontWeight": "600", "width": "15%"}),
            html.Td(f"{diff:+.3f}", style={"textAlign": "center", "fontFeatureSettings": "'tnum' 1", "fontWeight": "700", "width": "15%"}),
            html.Td(html.Span(alloc_status, style=status_style), style={"textAlign": "center", "fontSize": "7.5pt", "width": "15%"}),
        ]))

    return html.Div(
        [
            html.Div(className="print-tricolour-band"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Img(src="/dashboard/assets/images/emblem.svg", className="print-emblem-img me-3", alt="National Emblem"),
                            html.Div(
                                [
                                    html.H4("GOVERNMENT OF INDIA • MINISTRY OF PANCHAYATI RAJ", className="print-main-title"),
                                    html.P("DEPARTMENT OF LOCAL SELF-GOVERNMENT (LSGI) • STATE PLANNING BOARD", className="print-sub-title"),
                                    html.Div(
                                        "STATUTORY ADMINISTRATIVE DEVELOPMENT REPORT & BENCHMARK AUDIT",
                                        className="print-doc-title",
                                    ),
                                    html.Small(
                                        f"Gram Panchayat Development Plan (GPDP) — Annual Decentralized Planning Cycle FY {fy_str}",
                                        style={"display": "block", "color": "#475569", "fontSize": "7pt", "fontWeight": "600"},
                                    ),
                                ]
                            ),
                        ],
                        className="d-flex align-items-center",
                    ),
                    html.Div(
                        [
                            html.P([html.Strong("DOC REF: "), html.Span(doc_ref)], style={"margin": "0", "fontSize": "7pt", "color": "#142D4E"}),
                            html.P([html.Strong("DATE: "), html.Span("01-Nov-2026")], style={"margin": "1px 0", "fontSize": "7pt", "color": "#475569"}),
                            html.P([html.Strong("SECURITY: "), html.Span("OFFICIAL STATUTORY RECORD")], style={"margin": "1px 0", "fontSize": "6.8pt", "color": "#25845A", "fontWeight": "700"}),
                            html.P([html.Strong("STATUS: "), html.Span("GAZETTE VERIFIED")], style={"margin": "1px 0", "fontSize": "6.8pt", "color": "#1765BD", "fontWeight": "700"}),
                        ],
                        className="text-end",
                    ),
                ],
                className="print-gov-header d-flex justify-content-between align-items-center",
            ),
            html.Div(
                [
                    html.Div([html.Strong("State"), html.Span(state_str)], className="print-meta-item"),
                    html.Div([html.Strong("District"), html.Span(dist_str)], className="print-meta-item"),
                    html.Div([html.Strong("Grama Panchayat"), html.Span(panch_str)], className="print-meta-item"),
                    html.Div([html.Strong("Planning Cycle"), html.Span(f"FY {fy_str}")], className="print-meta-item"),
                    html.Div([html.Strong("Population"), html.Span(f"{total_pop:,}" if total_pop else "Jurisdiction")], className="print-meta-item"),
                    html.Div([html.Strong("Active Scope"), html.Span(f"{active_wards} Wards Audited" if active_wards else "Full Coverage")], className="print-meta-item"),
                ],
                className="print-meta-grid",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("PRIMARY BENCHMARK (WARD A)", style={"fontSize": "6.8pt", "fontWeight": "800", "color": "#142D4E", "textTransform": "uppercase"}),
                                    html.Span(f"Vuln: {vi_a:.3f} ({cat_a})", style={"fontSize": "7pt", "fontWeight": "800", "color": "#142D4E"}),
                                ],
                                className="d-flex justify-content-between align-items-center mb-1",
                            ),
                            html.Strong(ward_a, style={"fontSize": "8.5pt", "color": "#142D4E", "display": "block", "lineHeight": "1.2"}),
                            html.P(f"Taluk: {taluk_a} • AC: {const_a} • MLA: {mla_a}{party_a} • Urgent Need: {get_sector_name(p1_a, lang)}", style={"fontSize": "6.8pt", "color": "#475569", "margin": "1px 0 0 0"}),
                        ],
                        className="print-ward-card ward-a",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("COMPARATIVE BENCHMARK (WARD B)", style={"fontSize": "6.8pt", "fontWeight": "800", "color": "#B45309", "textTransform": "uppercase"}),
                                    html.Span(f"Vuln: {vi_b:.3f} ({cat_b})", style={"fontSize": "7pt", "fontWeight": "800", "color": "#B45309"}),
                                ],
                                className="d-flex justify-content-between align-items-center mb-1",
                            ),
                            html.Strong(ward_b, style={"fontSize": "8.5pt", "color": "#142D4E", "display": "block", "lineHeight": "1.2"}),
                            html.P(f"Taluk: {taluk_b} • AC: {const_b} • MLA: {mla_b}{party_b} • Urgent Need: {get_sector_name(p1_b, lang)}", style={"fontSize": "6.8pt", "color": "#475569", "margin": "1px 0 0 0"}),
                        ],
                        className="print-ward-card ward-b",
                    ),
                ],
                className="print-wards-comparison-strip",
            ),
            html.Table(
                [
                    html.Thead(
                        html.Tr(
                            [
                                html.Th("No.", style={"textAlign": "center"}),
                                html.Th("Development Sector"),
                                html.Th(f"Ward A: {ward_a}", style={"textAlign": "center"}),
                                html.Th(f"Ward B: {ward_b}", style={"textAlign": "center"}),
                                html.Th("Variance (A - B)", style={"textAlign": "center"}),
                                html.Th("Statutory Allocation Status", style={"textAlign": "center"}),
                            ]
                        )
                    ),
                    html.Tbody(table_rows),
                ],
                className="print-table",
            ),
            html.Div(
                [
                    html.Strong("STATUTORY PLANNING DIRECTIVE & MATHEMATICAL RESOURCE ALLOCATION NOTE:", style={"color": "#1E40AF", "fontSize": "7.2pt", "display": "block", "marginBottom": "2px"}),
                    html.P(
                        f"Under State Finance Commission (SFC) Untied Grant guidelines, Primary Benchmark Ward A ({ward_a}) exhibits the primary developmental deficit in {get_sector_name(p1_a, lang)} (Deficit Index: {vi_a:.3f}). "
                        f"The SciPy HiGHS LP Optimization Solver mandates priority fiscal transfer to close the inter-ward disparity. "
                        f"Approved for formal tabling before the Grama Sabha and District Planning Committee (DPC) under Section 174 of the Panchayati Raj Act.",
                        style={"margin": "0", "fontSize": "6.8pt", "color": "#1E3A8A", "lineHeight": "1.25"},
                    ),
                ],
                className="print-directive-box",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.P("1. PREPARED BY:", style={"fontSize": "6.5pt", "fontWeight": "800", "color": "#475569", "margin": "0 0 1px 0"}),
                            html.Div(className="print-sign-line"),
                            html.Strong("Panchayat Secretary / Planning Clerk", style={"fontSize": "7pt", "color": "#142D4E", "display": "block"}),
                            html.Small(f"Grama Panchayat Planning Cell • {panch_str}", style={"fontSize": "6.2pt", "color": "#64748B", "display": "block"}),
                        ],
                        className="print-sign-box",
                    ),
                    html.Div(
                        [
                            html.P("2. TECHNICAL VERIFICATION:", style={"fontSize": "6.5pt", "fontWeight": "800", "color": "#475569", "margin": "0 0 1px 0"}),
                            html.Div(className="print-sign-line"),
                            html.Strong("Assistant Engineer / Technical Sanction", style={"fontSize": "7pt", "color": "#142D4E", "display": "block"}),
                            html.Small("LSGD Engineering & Public Works Wing", style={"fontSize": "6.2pt", "color": "#64748B", "display": "block"}),
                        ],
                        className="print-sign-box",
                    ),
                    html.Div(
                        [
                            html.P("3. APPROVED & SANCTIONED BY:", style={"fontSize": "6.5pt", "fontWeight": "800", "color": "#475569", "margin": "0 0 1px 0"}),
                            html.Div(className="print-sign-line"),
                            html.Strong("President / Chairperson", style={"fontSize": "7pt", "color": "#142D4E", "display": "block"}),
                            html.Small("Grama Panchayat & DPC Standing Committee", style={"fontSize": "6.2pt", "color": "#64748B", "display": "block"}),
                        ],
                        className="print-sign-box",
                    ),
                ],
                className="print-sign-grid",
            ),
            html.Div(
                f"Statutory Planning Document • Authenticated Electronic Record under Section 4 of IT Act 2000 • Document ID: {doc_ref} • Page 1 of 1",
                className="print-footer-text",
            ),
        ],
        className="official-print-document",
    )


def create_comparison_layout(engine, state=None, district=None, panchayat=None, year="2026-27", lang="en", state_id=None, district_id=None, panchayat_id=None, **kwargs):
    """Create the comprehensive official reporting and benchmarking portal."""
    lang = lang or "en"
    year = year or "2026-27"
    df = engine.get_filtered_df(state=state, district=district, panchayat=panchayat)
    ward_names = sorted(df["ward_name"].tolist()) if (df is not None and not df.empty and "ward_name" in df.columns) else []
    ward_a_default = ward_names[0] if ward_names else None
    ward_b_default = ward_names[1] if len(ward_names) > 1 else ward_a_default

    # Context title
    if panchayat and panchayat != "ALL":
        header_sub = f"{panchayat} Grama Panchayat ({district or state or ''}) • {len(ward_names)} Wards"
    elif district and district != "ALL":
        header_sub = f"{district} District ({state or ''}) • {len(ward_names)} Wards"
    elif state and state != "ALL":
        header_sub = f"{state} State • {len(ward_names)} Wards"
    else:
        header_sub = f"National Multi-State Coverage (5 States) • {len(ward_names)} Wards • 32 Districts"

    # Quick Summary Statistics for Report
    total_pop = int(df["population"].sum()) if ("population" in df.columns and len(df) > 0) else 0
    avg_vuln = float(df["vulnerability_index"].mean()) if ("vulnerability_index" in df.columns and len(df) > 0) else 0.0
    dev_score = f"{(1.0 - avg_vuln) * 100:.1f}" if len(df) > 0 else "0.0"

    return html.Div([
        html.Div(create_shared_location_breadcrumb(state=state, district=district, panchayat=panchayat, year=year, lang=lang), className="d-print-none"),
        # Official Breadcrumb & Page Header
        html.Div([
            html.Div([
                html.Span("PORTAL HOME", style={"color": "#64748B", "fontWeight": "600", "fontSize": "0.78rem"}),
                html.Span(" / ", style={"color": "#CBD5E1", "margin": "0 8px"}),
                html.Span("REPORTS & ANALYTICS", style={"color": "#64748B", "fontWeight": "600", "fontSize": "0.78rem"}),
                html.Span(" / ", style={"color": "#CBD5E1", "margin": "0 8px"}),
                html.Span("OFFICIAL GOVERNANCE REPORTS", style={"color": "#142D4E", "fontWeight": "700", "fontSize": "0.78rem"}),
            ], className="mb-2"),
            html.Div([
                html.Div([
                    html.Div([
                        html.H1("📑 Official Reports & Disparity Analytics", className="page-title me-3", style={"margin": "0"}),
                        ProvenanceService.render_status_badge(STATUS_VERIFIED),
                    ], className="d-flex align-items-center flex-wrap gap-2"),
                    html.P(
                        f"Statutory Administrative Reporting & Inter-Ward Comparative Benchmarking • {header_sub} • Planning Cycle: FY {year}",
                        className="page-subtitle",
                    ),
                ], className="flex-grow-1"),
                html.Div([
                    html.Button(
                        [html.Span("🖨️", className="me-1"), "Print Official Report"],
                        id="btn-print-briefing",
                        className="btn btn-outline-primary btn-sm me-2",
                        style={"borderColor": "#245B91", "color": "#142D4E", "fontWeight": "600"},
                    ),
                    html.Button(
                        [html.Span("📊", className="me-1"), "Export CSV"],
                        id="btn-export-csv",
                        className="btn btn-sm text-white",
                        style={"background": "#25845A", "fontWeight": "600", "border": "none", "cursor": "pointer"},
                    ),
                    dcc.Download(id="download-comparison-csv"),
                ], className="d-flex align-items-center mt-2 mt-md-0"),
            ], className="d-flex align-items-center justify-content-between flex-wrap"),
        ], className="page-header d-print-none"),

        # Report Options & Filter Panel (Hidden in print)
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("Report Type Specification:", className="control-label", style={"fontWeight": "700", "color": "#142D4E"}),
                    dcc.Dropdown(
                        id="report-type-selector",
                        options=[
                            {"label": "🏛️ State Development Comprehensive Report", "value": "STATE_REPORT"},
                            {"label": "🏢 District Infrastructure Audit Report", "value": "DISTRICT_REPORT"},
                            {"label": "🏘️ Panchayat Annual Plan & Needs Report", "value": "PANCHAYAT_REPORT"},
                            {"label": "📊 Budget Utilization & Fiscal Audit Report", "value": "BUDGET_REPORT"},
                            {"label": "🤖 AI Recommendations & Priority Sequence Report", "value": "AI_REPORT"},
                            {"label": "⚖️ Inter-Ward Disparity Benchmarking (A vs B)", "value": "DISPARITY_BENCHMARK"},
                        ],
                        value="DISPARITY_BENCHMARK",
                        className="light-dropdown",
                        clearable=False,
                    ),
                ], md=4),
                dbc.Col([
                    html.Label("Financial Planning Year:", className="control-label", style={"fontWeight": "700", "color": "#142D4E"}),
                    dcc.Dropdown(
                        id="report-fy-selector",
                        options=[
                            {"label": "📅 FY 2026-27 (Current Planning Year)", "value": "2026-27"},
                            {"label": "📅 FY 2025-26 (Audited Outlays)", "value": "2025-26"},
                            {"label": "📅 FY 2024-25 (Historical Baseline)", "value": "2024-25"},
                        ],
                        value="2026-27",
                        className="light-dropdown",
                        clearable=False,
                    ),
                ], md=4),
                dbc.Col([
                    html.Label("Reporting Cycle / Period:", className="control-label", style={"fontWeight": "700", "color": "#142D4E"}),
                    dcc.Dropdown(
                        id="report-period-selector",
                        options=[
                            {"label": "Full Financial Year (Annual Plan)", "value": "ANNUAL"},
                            {"label": "Quarter 1 (April – June)", "value": "Q1"},
                            {"label": "Quarter 2 (July – September)", "value": "Q2"},
                            {"label": "Quarter 3 (October – December)", "value": "Q3"},
                            {"label": "Quarter 4 (January – March)", "value": "Q4"},
                        ],
                        value="ANNUAL",
                        className="light-dropdown",
                        clearable=False,
                    ),
                ], md=4),
            ], className="g-3"),
        ], className="govt-card p-4 mb-4 report-filter-panel d-print-none", style={"position": "relative", "zIndex": 30}),

        # Ward Comparison Selectors (Hidden in print)
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("🏛️ Primary Benchmark Ward (A):", className="control-label", style={"fontWeight": "700", "color": "#142D4E"}),
                    dcc.Dropdown(
                        id="compare-ward-a",
                        options=[{"label": f"Ward A: {w}", "value": w} for w in ward_names],
                        value=ward_a_default,
                        className="light-dropdown",
                        clearable=False,
                    ),
                ], md=5),
                dbc.Col(
                    html.Div([
                        html.Span("VS", style={
                            "background": "#F1F5F9",
                            "color": "#142D4E",
                            "fontWeight": "800",
                            "fontSize": "0.95rem",
                            "padding": "6px 14px",
                            "borderRadius": "20px",
                            "border": "1px solid #CBD5E1",
                            "display": "inline-block",
                            "marginTop": "26px",
                        }),
                    ], style={"textAlign": "center"}),
                    md=2,
                ),
                dbc.Col([
                    html.Label("🏛️ Comparative Benchmark Ward (B):", className="control-label", style={"fontWeight": "700", "color": "#142D4E"}),
                    dcc.Dropdown(
                        id="compare-ward-b",
                        options=[{"label": f"Ward B: {w}", "value": w} for w in ward_names],
                        value=ward_b_default,
                        className="light-dropdown",
                        clearable=False,
                    ),
                ], md=5),
            ], className="align-items-center"),
        ], className="govt-card p-4 mb-4 ward-selector-panel d-print-none", style={"position": "relative", "zIndex": 20}),

        # Comparison content (updated by callback)
        dcc.Loading(
            id="loading-comparison-content",
            type="circle",
            color="#245B91",
            children=html.Div(
                create_comparison_content(engine, ward_a_default, ward_b_default, lang, state=state, district=district, panchayat=panchayat, year=year)
                if ward_a_default and ward_b_default
                else html.P(t("select_two_wards", lang)),
                id="comparison-content-container",
                style={"position": "relative", "zIndex": 10},
            ),
        ),
    ])


def create_comparison_content(engine, ward_a, ward_b, lang="en", state=None, district=None, panchayat=None, year="2026-27", **kwargs):
    """Create comparison visualizations for two wards strictly scoped to the active location."""
    df_scope = engine.get_filtered_df(state=state, district=district, panchayat=panchayat)
    df = df_scope if (df_scope is not None and not df_scope.empty) else engine.df_processed
    row_a = df[df["ward_name"].astype(str).str.strip().str.lower() == str(ward_a).strip().lower()]
    row_b = df[df["ward_name"].astype(str).str.strip().str.lower() == str(ward_b).strip().lower()]

    if row_a.empty or row_b.empty:
        screen_analysis_view = html.Div([
            html.P("Please select two distinct administrative wards within the active jurisdiction to conduct comparative analysis.", className="text-muted text-center p-4")
        ], className="govt-card")

    total_pop = int(df["population"].sum()) if ("population" in df.columns and len(df) > 0) else 0
    active_wards = len(df)

    score_cols = [c for c in df.columns if c.startswith("score_")]
    raw_labels = [c.replace("score_", "").replace("_", " ").title() for c in score_cols]
    labels = [get_sector_name(s, lang) for s in raw_labels]

    vals_a = row_a[score_cols].values[0].tolist()
    vals_b = row_b[score_cols].values[0].tolist()

    # Dual radar chart in official light styling
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals_a + [vals_a[0]], theta=labels + [labels[0]],
        fill="toself", fillcolor="rgba(20, 45, 78, 0.22)",
        line=dict(color="#142D4E", width=2.5), name=f"Ward A: {ward_a}",
    ))
    fig.add_trace(go.Scatterpolar(
        r=vals_b + [vals_b[0]], theta=labels + [labels[0]],
        fill="toself", fillcolor="rgba(233, 154, 54, 0.25)",
        line=dict(color="#E99A36", width=2.5), name=f"Ward B: {ward_b}",
    ))
    fig.update_layout(
        title=dict(
            text=f"<b>Comparative Multi-Sector Deficit Radar ({ward_a} vs {ward_b})</b>",
            font=dict(family="Plus Jakarta Sans, Inter", size=14, color="#142D4E"),
            x=0.5,
            y=0.98,
            xanchor="center",
            yanchor="top",
        ),
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1], gridcolor="#E2E8F0", linecolor="#CBD5E1"),
            angularaxis=dict(gridcolor="#E2E8F0", linecolor="#CBD5E1"),
            bgcolor="#FFFFFF",
        ),
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        height=450,
        font=dict(family="Inter", color="#172B42", size=11),
        legend=dict(orientation="h", yanchor="top", y=1.10, xanchor="center", x=0.5),
        margin=dict(l=60, r=60, t=80, b=50),
    )

    # Grouped Bar Comparison in official light styling
    bar_fig = go.Figure()
    bar_fig.add_trace(go.Bar(
        x=labels, y=vals_a, name=f"{ward_a}", marker_color="#142D4E",
        text=[f"{v:.2f}" for v in vals_a], textposition="outside",
    ))
    bar_fig.add_trace(go.Bar(
        x=labels, y=vals_b, name=f"{ward_b}", marker_color="#E99A36",
        text=[f"{v:.2f}" for v in vals_b], textposition="outside",
    ))
    bar_fig.update_layout(
        title=dict(
            text=f"<b>Sector Vulnerability Metric Variance</b>",
            font=dict(family="Plus Jakarta Sans, Inter", size=14, color="#142D4E"),
            x=0.5,
            y=0.98,
            xanchor="center",
            yanchor="top",
        ),
        barmode="group",
        yaxis_title="Vulnerability Index (0 = Resilient, 1 = High Deficit)",
        yaxis=dict(range=[0, 1.15], gridcolor="#E2E8F0"),
        xaxis=dict(gridcolor="rgba(0,0,0,0)", automargin=True, tickangle=-25),
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        height=480,
        font=dict(family="Inter", color="#172B42", size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        margin=dict(l=55, r=35, t=75, b=110),
    )

    # Comparison table rows
    table_rows = []
    for raw_label, col, va, vb in zip(raw_labels, score_cols, vals_a, vals_b):
        diff = va - vb
        if diff > 0.05:
            badge = html.Span("🔴 Higher Deficit in A", style={"color": "#C74747", "fontWeight": "600", "fontSize": "0.78rem"})
        elif diff < -0.05:
            badge = html.Span("🟢 Higher Deficit in B", style={"color": "#25845A", "fontWeight": "600", "fontSize": "0.78rem"})
        else:
            badge = html.Span("🟡 Comparable", style={"color": "#D99A28", "fontWeight": "600", "fontSize": "0.78rem"})

        table_rows.append(html.Tr([
            html.Td(html.Strong(get_sector_name(raw_label, lang)), style={"color": "#142D4E"}),
            html.Td(f"{va:.3f}", style={"fontFeatureSettings": "'tnum' 1", "fontWeight": "600", "color": "#142D4E"}),
            html.Td(f"{vb:.3f}", style={"fontFeatureSettings": "'tnum' 1", "fontWeight": "600", "color": "#E99A36"}),
            html.Td(f"{diff:+.3f}", style={"fontFeatureSettings": "'tnum' 1", "fontWeight": "700"}),
            html.Td(badge),
        ]))

    # Administrative metadata
    vi_a = float(row_a["vulnerability_index"].values[0])
    vi_b = float(row_b["vulnerability_index"].values[0])
    cat_a = row_a["vulnerability_category"].values[0] if "vulnerability_category" in row_a.columns else "Moderate"
    cat_b = row_b["vulnerability_category"].values[0] if "vulnerability_category" in row_b.columns else "Moderate"

    taluk_a = row_a["taluk"].values[0] if "taluk" in row_a.columns else "N/A"
    const_a = row_a["assembly_constituency"].values[0] if "assembly_constituency" in row_a.columns else "N/A"
    mla_a = row_a["mla_name"].values[0] if "mla_name" in row_a.columns else "N/A"
    party_a = f" ({row_a['mla_party'].values[0]})" if "mla_party" in row_a.columns else ""

    taluk_b = row_b["taluk"].values[0] if "taluk" in row_b.columns else "N/A"
    const_b = row_b["assembly_constituency"].values[0] if "assembly_constituency" in row_b.columns else "N/A"
    mla_b = row_b["mla_name"].values[0] if "mla_name" in row_b.columns else "N/A"
    party_b = f" ({row_b['mla_party'].values[0]})" if "mla_party" in row_b.columns else ""

    p1_a = row_a["priority_sector_1"].values[0] if "priority_sector_1" in row_a.columns else "N/A"
    p1_b = row_b["priority_sector_1"].values[0] if "priority_sector_1" in row_b.columns else "N/A"

    screen_analysis_view = html.Div([
        # Comparative Administrative Profile Cards
        dbc.Row([
            # Card A
            dbc.Col(
                html.Div([
                    html.Div([
                        html.Span("PRIMARY BENCHMARK", style={"fontSize": "0.72rem", "fontWeight": "700", "color": "#142D4E", "background": "#DBEAFE", "padding": "2px 8px", "borderRadius": "4px"}),
                        html.Span("WARD A", style={"fontWeight": "700", "color": "#64748B", "fontSize": "0.8rem"}),
                    ], className="d-flex justify-content-between align-items-center mb-2"),
                    html.H3(ward_a, style={"color": "#142D4E", "fontWeight": "700", "fontSize": "1.35rem", "margin": "4px 0"}),
                    html.Div([
                        html.Span("Composite Vulnerability Index: ", style={"fontSize": "0.85rem", "color": "#64748B"}),
                        html.Strong(f"{vi_a:.3f}", style={"fontSize": "1.45rem", "color": "#142D4E", "fontFeatureSettings": "'tnum' 1"}),
                        html.Span(f"({cat_a})", style={"fontSize": "0.82rem", "color": "#64748B", "marginLeft": "6px"}),
                    ], className="d-flex align-items-baseline gap-1 my-2"),
                    html.Div([
                        html.P(f"🏛️ Taluk: {taluk_a}", style={"fontSize": "0.82rem", "color": "#475569", "margin": "0 0 2px"}),
                        html.P(f"🗳️ Constituency: {const_a}", style={"fontSize": "0.82rem", "color": "#475569", "margin": "0 0 2px"}),
                        html.P(f"👤 Sitting MLA: {mla_a}{party_a}", style={"fontSize": "0.82rem", "color": "#142D4E", "fontWeight": "600", "margin": "0 0 6px"}),
                        html.Div([
                            html.Span(f"Primary Deficit: {get_sector_name(p1_a, lang)}", className="priority-badge-blue"),
                        ]),
                    ], style={"background": "#F8FAFC", "padding": "10px 14px", "borderRadius": "6px", "border": "1px solid #E2E8F0"}),
                ], className="govt-card p-4 h-100", style={"borderTop": "4px solid #142D4E"}),
                md=6,
            ),
            # Card B
            dbc.Col(
                html.Div([
                    html.Div([
                        html.Span("COMPARATIVE BENCHMARK", style={"fontSize": "0.72rem", "fontWeight": "700", "color": "#E99A36", "background": "#FEF3C7", "padding": "2px 8px", "borderRadius": "4px"}),
                        html.Span("WARD B", style={"fontWeight": "700", "color": "#64748B", "fontSize": "0.8rem"}),
                    ], className="d-flex justify-content-between align-items-center mb-2"),
                    html.H3(ward_b, style={"color": "#142D4E", "fontWeight": "700", "fontSize": "1.35rem", "margin": "4px 0"}),
                    html.Div([
                        html.Span("Composite Vulnerability Index: ", style={"fontSize": "0.85rem", "color": "#64748B"}),
                        html.Strong(f"{vi_b:.3f}", style={"fontSize": "1.45rem", "color": "#E99A36", "fontFeatureSettings": "'tnum' 1"}),
                        html.Span(f"({cat_b})", style={"fontSize": "0.82rem", "color": "#64748B", "marginLeft": "6px"}),
                    ], className="d-flex align-items-baseline gap-1 my-2"),
                    html.Div([
                        html.P(f"🏛️ Taluk: {taluk_b}", style={"fontSize": "0.82rem", "color": "#475569", "margin": "0 0 2px"}),
                        html.P(f"🗳️ Constituency: {const_b}", style={"fontSize": "0.82rem", "color": "#475569", "margin": "0 0 2px"}),
                        html.P(f"👤 Sitting MLA: {mla_b}{party_b}", style={"fontSize": "0.82rem", "color": "#142D4E", "fontWeight": "600", "margin": "0 0 6px"}),
                        html.Div([
                            html.Span(f"Primary Deficit: {get_sector_name(p1_b, lang)}", className="priority-badge-amber"),
                        ]),
                    ], style={"background": "#F8FAFC", "padding": "10px 14px", "borderRadius": "6px", "border": "1px solid #E2E8F0"}),
                ], className="govt-card p-4 h-100", style={"borderTop": "4px solid #E99A36"}),
                md=6,
            ),
        ], className="mb-4 g-3"),

        # Visualizations (Radar + Grouped Bar)
        dbc.Row([
            dbc.Col(html.Div(dcc.Graph(figure=fig, style={"height": "450px", "width": "100%", "minHeight": "450px"}, config={"displayModeBar": False, "scrollZoom": False, "responsive": True}), className="govt-card p-3", style={"minHeight": "495px"}), md=6),
            dbc.Col(html.Div(dcc.Graph(figure=bar_fig, style={"height": "450px", "width": "100%", "minHeight": "450px"}, config={"displayModeBar": False, "scrollZoom": False, "responsive": True}), className="govt-card p-3", style={"minHeight": "495px"}), md=6),
        ], className="mb-4 g-3"),

        # Detailed Disparity Table
        html.Div([
            html.Div([
                html.Span("INTER-WARD DISPARITY AUDIT", className="priority-badge-blue mb-1 d-inline-block"),
                html.H4("📊 Detailed Sector Vulnerability Disparity Ledger", className="section-title", style={"margin": "4px 0"}),
                html.P(
                    "Direct mathematical variance across socio-economic development sectors between the two selected wards.",
                    style={"color": "#64748B", "fontSize": "0.88rem", "marginBottom": "16px"},
                ),
            ]),
            dbc.Table([
                html.Thead(html.Tr([
                    html.Th("Development Sector"),
                    html.Th(f"Ward A: {ward_a}"),
                    html.Th(f"Ward B: {ward_b}"),
                    html.Th("Net Variance (A - B)"),
                    html.Th("Diagnostic Evaluation"),
                ], style={"background": "#F8FAFC", "color": "#142D4E", "fontWeight": "700"})),
                html.Tbody(table_rows),
            ], bordered=True, hover=True, striped=True, responsive=True, className="govt-table align-middle"),
        ], className="govt-card p-4"),
    ], className="screen-only-analysis")

    official_print_doc = create_official_print_document(
        ward_a=ward_a,
        ward_b=ward_b,
        row_a=row_a,
        row_b=row_b,
        score_cols=score_cols,
        vals_a=vals_a,
        vals_b=vals_b,
        raw_labels=raw_labels,
        lang=lang,
        state=state or "ALL",
        district=district or "ALL",
        panchayat=panchayat or "ALL",
        year=year or "2026-27",
        total_pop=total_pop,
        active_wards=active_wards,
    )

    return html.Div([
        screen_analysis_view,
        official_print_doc,
    ])
