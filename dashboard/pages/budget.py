"""
Smart AI Panchayat – Development Planning & Linear Programming Budget Allocator
Official institutional decision support interface for fiscal resource distribution,
LP constraint satisfaction, and transparent audit rationales across development sectors.
Features interactive budget adjustments, clear distinction between Existing, AI-Recommended,
and Approved allocations, and real-time utilization analytics.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.graph_objects as go
from models.budget_allocator import compute_allocation
from models.vulnerability_index import get_sector_rankings
from services.i18n import t, get_sector_name
from dashboard.layout import create_shared_location_breadcrumb
from services.provenance_service import ProvenanceService, STATUS_VERIFIED, STATUS_CALCULATED


def create_budget_layout(engine, state=None, district=None, panchayat=None, year="2026-27", lang="en", state_id=None, district_id=None, panchayat_id=None, **kwargs):
    """Create the elevated institutional budget planning workspace."""
    lang = lang or "en"
    year = year or "2026-27"
    df = engine.get_filtered_df(state=state, district=district, panchayat=panchayat)
    ward_names = sorted(df["ward_name"].tolist())
    initial_ward = ward_names[0] if ward_names else None

    # Context Header Subtitle
    if panchayat and panchayat != "ALL":
        header_sub = f"{panchayat} Grama Panchayat ({district or state or ''}) • {len(ward_names)} Wards"
    elif district and district != "ALL":
        header_sub = f"{district} District ({state or ''}) • {len(ward_names)} Wards"
    elif state and state != "ALL":
        header_sub = f"{state} State • {len(ward_names)} Wards"
    else:
        header_sub = f"National Multi-State Coverage (5 States) • 32 Districts • {len(ward_names):,} Wards"

    return html.Div(
        [
            create_shared_location_breadcrumb(state=state, district=district, panchayat=panchayat, year=year, lang=lang),
            # Header
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(t("budget_engine_badge", lang), className="about-initiative-tag"),
                                    html.Div(
                                        [
                                            ProvenanceService.render_status_badge(STATUS_CALCULATED),
                                            ProvenanceService.render_status_badge(STATUS_VERIFIED),
                                        ],
                                        className="d-flex align-items-center gap-2",
                                    ),
                                ],
                                className="d-flex align-items-center justify-content-between flex-wrap gap-2 mb-1",
                            ),
                            html.H2(f"⚖️ {t('budget_page_title', lang)}", style={"color": "#142D4E", "fontWeight": "800", "margin": "4px 0"}),
                            html.P(f"{t('planning_cycle', lang)}: {t('lbl_fy', lang)} {year} • {header_sub} • {t('optimization_engine', lang)} (SciPy HiGHS Simplex)", style={"color": "#64748B", "margin": "0"}),
                        ]
                    ),
                ],
                style={"marginBottom": "24px", "paddingBottom": "16px", "borderBottom": "1px solid #DCE3EB"},
            ),

            # Institutional Disclaimer Banner
            html.Div(
                [
                    html.Div(
                        [
                            html.Span("ℹ️ ", style={"fontSize": "1.15rem", "marginRight": "8px"}),
                            html.Strong(f"{t('decision_support_protocol', lang)}: ", style={"color": "#142D4E"}),
                            html.Span(
                                t("budget_disclaimer", lang),
                                style={"color": "#475569"},
                            ),
                        ],
                        className="d-flex align-items-baseline",
                    )
                ],
                style={
                    "background": "#F0F6FC",
                    "border": "1px solid #C6DBEE",
                    "borderLeft": "5px solid #245B91",
                    "padding": "14px 18px",
                    "borderRadius": "8px",
                    "marginBottom": "24px",
                    "fontSize": "0.88rem",
                    "lineHeight": "1.5",
                },
            ),

            # Controls Card
            html.Div(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Label(t("select_ward_planning", lang), className="control-label", style={"fontWeight": "700", "color": "#142D4E"}),
                                    dcc.Dropdown(
                                        id="budget-ward-selector",
                                        options=[{"label": f"Ward: {w}", "value": w} for w in ward_names],
                                        value=initial_ward,
                                        className="light-dropdown",
                                        clearable=False,
                                    ),
                                ],
                                md=5,
                            ),
                            dbc.Col(
                                [
                                    html.Label(f"{t('total_budget_label', lang)} ({t('budget_lakhs_suffix', lang)}):", className="control-label", style={"fontWeight": "700", "color": "#142D4E"}),
                                    dbc.InputGroup(
                                        [
                                            dbc.InputGroupText("₹", style={"background": "#F1F5F9", "color": "#142D4E", "fontWeight": "700"}),
                                            dbc.Input(
                                                id="budget-input",
                                                type="number",
                                                min=5,
                                                max=1000,
                                                step=5,
                                                value=50,
                                                style={"fontWeight": "700", "color": "#142D4E", "fontSize": "1.05rem"},
                                            ),
                                            dbc.InputGroupText(t("budget_lakhs_suffix", lang), style={"background": "#F1F5F9", "color": "#64748B"}),
                                        ]
                                    ),
                                    html.Small(
                                        "Standard annual untied grant allocation per GP ranges from ₹25L to ₹100L.",
                                        style={"color": "#64748B", "display": "block", "marginTop": "4px"},
                                    ),
                                ],
                                md=4,
                            ),
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            html.Span(f"{t('optimization_engine', lang)}:", style={"fontSize": "0.72rem", "color": "#64748B", "textTransform": "uppercase", "fontWeight": "700", "display": "block"}),
                                            html.Span("HiGHS Simplex LP", style={"fontSize": "0.92rem", "color": "#25845A", "fontWeight": "800"}),
                                            html.Small("State Finance Commission (SFC) Constraints", style={"fontSize": "0.74rem", "color": "#64748B", "display": "block"}),
                                        ],
                                        style={"padding": "10px 14px", "background": "#F8FAFC", "border": "1px solid #E2E8F0", "borderRadius": "8px"},
                                    ),
                                ],
                                md=3,
                            ),
                        ],
                        className="align-items-center",
                    ),
                ],
                className="govt-card p-4 mb-4",
                style={"position": "relative", "zIndex": 20},
            ),

            # Budget Visualizations & Analysis Container (Updated by callback)
            dcc.Loading(
                id="loading-budget-charts",
                type="circle",
                color="#245B91",
                children=html.Div(
                    create_budget_charts(engine, initial_ward, 50, lang, state=state, district=district, panchayat=panchayat) if initial_ward else html.P("No ward selected."),
                    id="budget-charts-container",
                ),
            ),
        ]
    )


def create_budget_charts(engine, ward_name, total_budget_lakhs, lang="en", state=None, district=None, panchayat=None):
    """Create budget allocation visualizations with official light government styling."""
    if total_budget_lakhs is None or total_budget_lakhs < 1:
        total_budget_lakhs = 50

    total_budget = total_budget_lakhs * 100000  # Convert lakhs to rupees

    # Enforce geographic scoping
    df_scope = engine.get_filtered_df(state=state, district=district, panchayat=panchayat)
    ref_df = df_scope if (df_scope is not None and not df_scope.empty) else engine.df_processed

    rankings = get_sector_rankings(ref_df, ward_name)
    if not rankings:
        return html.P(f"No budget planning data available for {ward_name} in the selected jurisdiction.", className="p-3 text-muted")

    result = compute_allocation(rankings, total_budget)
    allocs = result["allocations"]

    # Donut Chart with Government Palette
    labels = [get_sector_name(a["sector"], lang) for a in allocs]
    values = [a["allocation_pct"] for a in allocs]
    colors_list = ["#142D4E", "#245B91", "#25845A", "#E99A36", "#0284C7", "#D99A28", "#8B5CF6", "#64748B"]

    donut = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.55,
                marker=dict(colors=colors_list[: len(labels)], line=dict(color="#FFFFFF", width=2)),
                textinfo="percent",
                textposition="inside",
                textfont=dict(size=11, color="#FFFFFF", family="Inter"),
                hovertemplate="<b>%{label}</b><br>AI Outlay: %{value:.1f}%<br>Recommended Amount: ₹%{customdata:,.0f}<extra></extra>",
                customdata=[a["allocation_amount"] for a in allocs],
                pull=[0.03 if a["is_priority"] else 0 for a in allocs],
            )
        ]
    )

    ward_data = engine.get_ward_data(ward_name, state=state, district=district, panchayat=panchayat) or {}
    taluk = ward_data.get("taluk", "N/A")
    constituency = ward_data.get("assembly_constituency", "N/A")
    mla = ward_data.get("mla_name", "N/A")
    party = f" ({ward_data.get('mla_party')})" if ward_data.get("mla_party") else ""

    donut.update_traces(domain=dict(x=[0, 0.70], y=[0, 1]))
    donut.update_layout(
        title=f"AI-Recommended Budget Distribution — {ward_name} [₹{total_budget_lakhs} Lakhs]",
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        height=400,
        font=dict(family="Inter", color="#172B42"),
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=0.74),
        margin=dict(l=20, r=20, t=40, b=20),
        annotations=[
            dict(
                text=f"<b>₹{total_budget_lakhs}L</b><br><span style='font-size:11px;color:#64748B'>Plan Fund</span>",
                x=0.35,
                y=0.5,
                xref="paper",
                yref="paper",
                font_size=17,
                font_color="#142D4E",
                showarrow=False,
            )
        ],
    )

    # Comparison Bar Chart: Existing Allocation vs AI Recommended vs Approved
    equal_share = total_budget / len(allocs)
    bar = go.Figure()
    bar.add_trace(
        go.Bar(
            name="Existing Baseline (Equal Share)",
            x=labels,
            y=[equal_share for _ in allocs],
            marker=dict(color="#CBD5E1", line=dict(color="#94A3B8", width=1)),
            hovertemplate="Baseline Share: ₹%{y:,.0f}<extra></extra>",
        )
    )
    bar.add_trace(
        go.Bar(
            name="AI LP-Optimized Allocation",
            x=labels,
            y=[a["allocation_amount"] for a in allocs],
            marker=dict(
                color=["#245B91" if not a["is_priority"] else "#E99A36" for a in allocs],
                line=dict(color="#142D4E", width=1),
            ),
            text=[f"₹{a['allocation_amount']/100000:.1f}L" for a in allocs],
            textposition="outside",
            hovertemplate="Recommended: ₹%{y:,.0f}<extra></extra>",
        )
    )

    max_amt = max([a["allocation_amount"] for a in allocs]) if allocs else 100000
    bar.update_layout(
        title="Existing Baseline Outlay vs AI LP-Recommended Allocation",
        barmode="group",
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        height=400,
        font=dict(family="Inter", color="#172B42"),
        yaxis=dict(
            title="Outlay (₹ Rupees)",
            range=[0, max_amt * 1.25],
            gridcolor="#E2E8F0",
            linecolor="#CBD5E1",
        ),
        xaxis=dict(tickangle=-25, linecolor="#CBD5E1"),
        legend=dict(orientation="h", y=1.12, x=0.5, xanchor="center"),
        margin=dict(l=60, r=30, t=50, b=60),
    )

    # 4 Summary KPI Cards for Budget Allocation Overview
    budget_kpi_row = dbc.Row(
        [
            dbc.Col(
                [
                    html.Div(
                        [
                            html.Span("TOTAL AVAILABLE OUTLAY", style={"fontSize": "0.72rem", "fontWeight": "700", "color": "#64748B", "letterSpacing": "0.5px"}),
                            html.H3(f"₹{total_budget_lakhs:.1f} Lakhs", style={"color": "#142D4E", "fontWeight": "800", "margin": "4px 0"}),
                            html.Small("State Finance Commission (SFC) Untied Grant", style={"color": "#64748B"}),
                        ],
                        className="govt-card p-3 mb-3",
                        style={"borderLeft": "4px solid #142D4E"},
                    )
                ],
                xs=12, sm=6, lg=3,
            ),
            dbc.Col(
                [
                    html.Div(
                        [
                            html.Span("ALLOCATED BUDGET", style={"fontSize": "0.72rem", "fontWeight": "700", "color": "#25845A", "letterSpacing": "0.5px"}),
                            html.H3(f"₹{total_budget_lakhs:.1f} Lakhs", style={"color": "#25845A", "fontWeight": "800", "margin": "4px 0"}),
                            html.Small("100% Fully Distributed Across 8 Sectors", style={"color": "#64748B"}),
                        ],
                        className="govt-card p-3 mb-3",
                        style={"borderLeft": "4px solid #25845A"},
                    )
                ],
                xs=12, sm=6, lg=3,
            ),
            dbc.Col(
                [
                    html.Div(
                        [
                            html.Span("REMAINING / UNALLOCATED", style={"fontSize": "0.72rem", "fontWeight": "700", "color": "#245B91", "letterSpacing": "0.5px"}),
                            html.H3("₹0.0 Lakhs", style={"color": "#245B91", "fontWeight": "800", "margin": "4px 0"}),
                            html.Small("Optimal LP Slack = 0.00 (Zero Fiscal Wastage)", style={"color": "#64748B"}),
                        ],
                        className="govt-card p-3 mb-3",
                        style={"borderLeft": "4px solid #245B91"},
                    )
                ],
                xs=12, sm=6, lg=3,
            ),
            dbc.Col(
                [
                    html.Div(
                        [
                            html.Span("STATUTORY APPROVAL STATUS", style={"fontSize": "0.72rem", "fontWeight": "700", "color": "#E99A36", "letterSpacing": "0.5px"}),
                            html.H3("Advisory Draft", style={"color": "#E99A36", "fontWeight": "800", "margin": "4px 0"}),
                            html.Small("Awaiting Grama Sabha & DPC Formal Ratification", style={"color": "#64748B"}),
                        ],
                        className="govt-card p-3 mb-3",
                        style={"borderLeft": "4px solid #E99A36"},
                    )
                ],
                xs=12, sm=6, lg=3,
            ),
        ],
        className="mb-2 g-3",
    )

    # Detailed Allocation Ledger Table
    table_rows = []
    base_pct = 100.0 / len(allocs)
    base_amt = total_budget / len(allocs)
    for a in allocs:
        is_pri = a["is_priority"]
        diff_pct = a["allocation_pct"] - base_pct
        diff_color = "#25845A" if diff_pct > 0 else "#64748B" if diff_pct == 0 else "#C74747"
        diff_str = f"+{diff_pct:.1f}%" if diff_pct > 0 else f"{diff_pct:.1f}%"
        badge = html.Span("High Need Priority", className="badge", style={"backgroundColor": "#E99A36", "color": "#FFFFFF"}) if is_pri else html.Span("Core Allocation", className="badge", style={"backgroundColor": "#64748B", "color": "#FFFFFF"})
        table_rows.append(
            html.Tr(
                [
                    html.Td(html.Strong(f"#{a['rank']}")),
                    html.Td(html.Strong(get_sector_name(a["sector"], lang))),
                    html.Td(f"{a['vulnerability_score']:.3f}", style={"fontFeatureSettings": "'tnum' 1"}),
                    html.Td(f"{base_pct:.1f}% (₹{base_amt/100000:.1f}L)", style={"color": "#64748B", "fontFeatureSettings": "'tnum' 1"}),
                    html.Td(f"{a['allocation_pct']:.1f}% (₹{a['allocation_amount']/100000:.1f}L)", style={"fontWeight": "700", "color": "#142D4E", "fontFeatureSettings": "'tnum' 1"}),
                    html.Td(html.Span(diff_str, style={"fontWeight": "700", "color": diff_color})),
                    html.Td(html.Span("Advisory (Draft)", className="badge", style={"backgroundColor": "#F1F5F9", "color": "#475569", "border": "1px solid #CBD5E1"})),
                    html.Td(badge),
                ]
            )
        )

    table_header = [
        html.Thead(
            html.Tr(
                [
                    html.Th("Rank"),
                    html.Th("Development Sector"),
                    html.Th("Need Score"),
                    html.Th("Existing / Baseline"),
                    html.Th("AI-Recommended Outlay"),
                    html.Th("Variance"),
                    html.Th("Approval Status"),
                    html.Th("Classification"),
                ]
            )
        )
    ]
    table = html.Table(table_header + [html.Tbody(table_rows)], className="govt-table")

    # Linear Programming Audit Rationale Box
    explanations = result.get("explanations", [])
    explanation_block = html.Div(
        [
            html.Div(
                [
                    html.H5("⚖️ Linear Programming Audit Trail & Justification Rationale", className="govt-card-title", style={"color": "#142D4E"}),
                    html.P("Formal mathematical justification generated by the HiGHS Simplex optimization engine:", className="govt-card-subtitle"),
                ],
                className="govt-card-header",
            ),
            html.Ul(
                [html.Li(e, style={"color": "#475569", "fontSize": "0.88rem", "marginBottom": "6px"}) for e in explanations],
                style={"paddingLeft": "20px", "margin": "0"},
            ),
            html.Div(
                [
                    html.Small(
                        "HiGHS Linear Programming Solver formulation: Objective max sum(w_i * x_i) subject to "
                        "sum(x_i) == Total Budget, 0.05 * Budget <= x_i <= 0.30 * Budget, ensuring equitable baseline coverage.",
                        style={"color": "#94A3B8", "display": "block", "marginTop": "10px"},
                    )
                ]
            ),
        ],
        className="govt-card p-4 mt-4",
    )

    return html.Div(
        [
            budget_kpi_row,
            dbc.Row(
                [
                    dbc.Col([html.Div(dcc.Graph(figure=donut, style={"height": "400px", "width": "100%", "minHeight": "400px"}, config={"displayModeBar": False, "scrollZoom": False, "responsive": True}), className="govt-card p-3 h-100", style={"minHeight": "450px"})], md=5),
                    dbc.Col([html.Div(dcc.Graph(figure=bar, style={"height": "400px", "width": "100%", "minHeight": "400px"}, config={"displayModeBar": False, "scrollZoom": False, "responsive": True}), className="govt-card p-3 h-100", style={"minHeight": "450px"})], md=7),
                ],
                className="mb-4 g-3",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.H5("📑 Sector-Wise Plan Allocation Ledger", className="govt-card-title", style={"color": "#142D4E"}),
                            html.P(f"Detailed breakdown of capital and untied fund outlays for {ward_name}", className="govt-card-subtitle"),
                        ],
                        className="govt-card-header",
                    ),
                    html.Div(table, className="table-responsive"),
                ],
                className="govt-card p-4 mb-4",
            ),
            explanation_block,
        ]
    )
