"""
Smart AI Panchayat – Official Indian Government Digital Platform (LSGI)
Recreates the National Governance Portal Experience:
Top Utility Bar, Sticky Main Navigation Header, Cascading Multi-State Jurisdictional Bar,
Accessibility Controls, Responsive Navigation, and Institutional Public-Sector Design.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
from services.i18n import LANGUAGES, t
from data.panchayat_geography import STATES_PANCHAYAT_DATA
from services.provenance_service import ProvenanceService


def create_top_government_bar(lang="en"):
    """Create the top official government utility bar with accessibility options."""
    lang = lang or "en"
    lang_options = [
        {"label": f"{info['native']} ({info['name']})", "value": code}
        for code, info in LANGUAGES.items()
    ]

    return html.Div(
        [
            html.Div(
                [
                    html.Span(t("gov_india", lang), id="topbar-gov-india", className="govt-topbar-tag-bold"),
                    html.Span("|", className="govt-topbar-divider"),
                    html.Span(t("min_panchayati_raj", lang), id="topbar-min-panchayat", className="govt-topbar-tag"),
                    html.Span("|", className="govt-topbar-divider d-none d-lg-inline"),
                    html.Span("Digital India Platform", className="govt-topbar-tag d-none d-lg-inline"),
                ],
                className="govt-topbar-left d-flex align-items-center flex-wrap",
            ),
            html.Div(
                [
                    html.Span(
                        [html.Span("⚑ ", style={"fontSize": "0.75rem", "marginRight": "2px"}), html.Span(t("screen_reader_access", lang), id="topbar-screen-reader")],
                        className="govt-topbar-link d-none d-md-inline",
                    ),
                    html.Span("|", className="govt-topbar-divider d-none d-md-inline"),
                    html.Div(
                        [
                            html.Button("A+", id="btn-font-inc", className="accessibility-pill", title="Increase text size"),
                            html.Button("A", id="btn-font-norm", className="accessibility-pill", title="Reset text size"),
                            html.Button("A-", id="btn-font-dec", className="accessibility-pill", title="Decrease text size"),
                        ],
                        className="accessibility-group d-flex align-items-center",
                    ),
                    html.Span("|", className="govt-topbar-divider"),
                    # Language Selector Dropdown
                    html.Div(
                        [
                            html.Span("🌐", style={"fontSize": "0.85rem", "marginRight": "4px"}),
                            dcc.Dropdown(
                                id="header-lang-selector",
                                options=lang_options,
                                value="en",
                                clearable=False,
                                searchable=False,
                                className="topbar-lang-dropdown",
                                style={"minWidth": "115px"},
                            ),
                        ],
                        className="d-flex align-items-center",
                    ),
                    html.Span("|", className="govt-topbar-divider"),
                    html.Button("🌓", id="btn-contrast-toggle", className="accessibility-pill", title="Toggle High Contrast"),
                    html.Span("|", className="govt-topbar-divider d-none d-sm-inline"),
                    html.Button(
                        "📊 Data Provenance",
                        id="btn-provenance-open",
                        className="govt-topbar-link",
                        style={"background": "none", "border": "none", "cursor": "pointer", "color": "inherit", "fontSize": "0.78rem", "fontWeight": "600", "padding": "0"},
                        title="Audit Government Data Lineage & Verification Tiers",
                    ),
                    html.Span("|", className="govt-topbar-divider d-none d-sm-inline"),
                    dcc.Link(
                        "ⓘ Help",
                        href="/dashboard/explanations",
                        className="govt-topbar-link d-none d-sm-inline",
                    ),
                    html.Span("|", className="govt-topbar-divider d-none d-sm-inline"),
                    dcc.Link(
                        "✆ Contact",
                        href="/dashboard/auth",
                        className="govt-topbar-link d-none d-sm-inline",
                    ),
                ],
                className="govt-topbar-right d-flex align-items-center gap-2",
            ),
        ],
        className="govt-topbar",
    )


def create_top_header(lang="en"):
    """Create the sticky main government navigation bar with institutional branding."""
    lang = lang or "en"

    return html.Div(
        [
            # Left: Official Project Branding & Emblem
            dcc.Link(
                [
                    html.Img(
                        src="/dashboard/assets/images/emblem.svg",
                        className="govt-emblem-svg",
                        alt="Smart AI Panchayat Emblem",
                    ),
                    html.Div(
                        [
                            html.H1(
                                "Smart AI Panchayat",
                                id="header-brand-title",
                                className="govt-brand-title",
                            ),
                            html.P(
                                t("header_brand_sub", lang),
                                id="header-brand-sub",
                                className="govt-brand-subtitle",
                            ),
                        ],
                        className="brand-text-container",
                    ),
                ],
                href="/dashboard/",
                className="govt-brand-box text-decoration-none",
            ),

            # Center: Pill Navigation Menu
            html.Nav(
                [
                    dcc.Link(html.Span(t("nav_home", lang), id="nav-lbl-home"), href="/dashboard/", className="nav-pill-link", id="pill-nav-home"),
                    dcc.Link(html.Span(t("nav_about", lang), id="nav-lbl-about"), href="/dashboard/about", className="nav-pill-link", id="pill-nav-about"),
                    dcc.Link(
                        [html.Span(t("nav_dashboard", lang), id="nav-lbl-dashboard"), html.Span(" ▾", className="nav-caret")],
                        href="/dashboard/vulnerability",
                        className="nav-pill-link",
                        id="pill-nav-dashboard",
                    ),
                    dcc.Link(
                        [html.Span(t("nav_planning", lang), id="nav-lbl-planning"), html.Span(" ▾", className="nav-caret")],
                        href="/dashboard/budget",
                        className="nav-pill-link",
                        id="pill-nav-planning",
                    ),
                    dcc.Link(
                        [html.Span(t("nav_insights", lang), id="nav-lbl-insights"), html.Span(" ▾", className="nav-caret")],
                        href="/dashboard/explanations",
                        className="nav-pill-link",
                        id="pill-nav-insights",
                    ),
                    dcc.Link(html.Span(t("nav_reports", lang), id="nav-lbl-reports"), href="/dashboard/compare", className="nav-pill-link", id="pill-nav-reports"),
                    dcc.Link(html.Span(t("nav_contact", lang), id="nav-lbl-contact"), href="/dashboard/auth", className="nav-pill-link", id="pill-nav-contact"),
                ],
                className="header-pill-nav d-none d-xl-flex align-items-center",
            ),

            # Right: Officer Portal Button / User Widget
            html.Div(
                [
                    html.Div(
                        id="header-user-widget",
                        children=[
                            dcc.Link(
                                [
                                    html.Span("🪪", className="me-1"),
                                    html.Span(t("officer_portal", lang), id="officer-portal-label"),
                                    html.Span(" →", className="ms-1"),
                                ],
                                href="/dashboard/auth",
                                className="btn-officer-portal",
                            )
                        ],
                        className="top-user-widget d-flex align-items-center",
                    ),
                ],
                className="header-right-controls d-flex align-items-center gap-2",
            ),
        ],
        className="govt-main-header d-flex align-items-center justify-content-between flex-wrap",
    )


def create_shared_location_breadcrumb(state="ALL", district="ALL", panchayat="ALL", year="2026-27", lang="en"):
    """Render a persistent, standardized institutional location breadcrumb across all pages."""
    lang = lang or "en"
    state_str = state if state and state != "ALL" else f"{t('all_states', lang)} (5 States)"
    dist_str = district if district and district != "ALL" else t("all_districts", lang)
    panch_str = f"{panchayat} GP" if panchayat and panchayat != "ALL" else t("all_panchayats", lang)
    fy_str = f"{t('lbl_fy', lang)} {year}" if year else f"{t('lbl_fy', lang)} 2026-27"

    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(f"🏛️ {t('active_jurisdiction', lang)}", className="breadcrumb-gov-label me-2"),
                            html.Span(f"🇮🇳 {t('country_india', lang)}", className="crumb-segment"),
                            html.Span(" / ", className="crumb-sep"),
                            html.Span(state_str, className="crumb-segment font-semibold" if state != "ALL" else "crumb-segment text-muted"),
                            html.Span(" / ", className="crumb-sep"),
                            html.Span(dist_str, className="crumb-segment font-semibold" if district != "ALL" else "crumb-segment text-muted"),
                            html.Span(" / ", className="crumb-sep"),
                            html.Span(panch_str, className="crumb-segment crumb-active"),
                            html.Span(" • ", className="crumb-sep"),
                            html.Span(fy_str, className="crumb-fy-badge"),
                        ],
                        className="d-flex align-items-center flex-wrap gap-1",
                    ),
                ],
                className="breadcrumb-left-content",
            ),
            html.Div(
                [
                    html.Span(f"⚡ {t('synced_master_location', lang)}", className="sync-status-badge d-none d-md-inline-block me-2"),
                    dcc.Link(f"← {t('change_on_home', lang)}", href="/dashboard/#state-selection-section", className="crumb-change-link"),
                ],
                className="breadcrumb-right-actions d-flex align-items-center",
            ),
        ],
        className="universal-location-breadcrumb-bar mb-3",
    )


def create_cascading_subbar(lang="en"):
    """Create the dedicated administrative cascading filter bar for State, District, Panchayat & Financial Year."""
    lang = lang or "en"
    state_options = [{"label": f"🌟 {t('all_states', lang)} (5 States)", "value": "ALL"}] + [
        {"label": f"📍 {s}", "value": s} for s in sorted(STATES_PANCHAYAT_DATA.keys())
    ]

    return html.Div(
        [
            html.Div(
                [
                    # Left Label
                    html.Div(
                        [
                            html.Span("🏛️", className="me-2", style={"fontSize": "1.05rem"}),
                            html.Strong(t("admin_jurisdiction", lang), id="subbar-jurisdiction-label", style={"color": "#142D4E", "fontSize": "0.85rem", "fontWeight": "700"}),
                        ],
                        className="d-flex align-items-center me-3 subbar-label-box",
                    ),

                    # 1. State Selector
                    html.Div(
                        [
                            html.Label(t("lbl_state", lang), id="header-lbl-state", className="subbar-input-label"),
                            dcc.Dropdown(
                                id="header-state-selector",
                                options=state_options,
                                value="ALL",
                                clearable=False,
                                searchable=True,
                                placeholder="Select State",
                                className="subbar-dropdown state-dropdown",
                                style={"minWidth": "165px"},
                                persistence=True,
                                persistence_type="local",
                            ),
                        ],
                        className="subbar-filter-group",
                    ),

                    # 2. District Selector (Cascading from State)
                    html.Div(
                        [
                            html.Label(t("lbl_district", lang), id="header-lbl-district", className="subbar-input-label"),
                            dcc.Dropdown(
                                id="header-district-selector",
                                options=[{"label": f"🌟 {t('all_districts', lang)}", "value": "ALL"}],
                                value="ALL",
                                clearable=False,
                                searchable=True,
                                placeholder="All Districts",
                                className="subbar-dropdown district-dropdown",
                                style={"minWidth": "175px"},
                                persistence=True,
                                persistence_type="local",
                            ),
                        ],
                        className="subbar-filter-group",
                    ),

                    # 3. Panchayat Selector (Cascading from District)
                    html.Div(
                        [
                            html.Label(t("lbl_panchayat", lang), id="header-lbl-panchayat", className="subbar-input-label"),
                            dcc.Dropdown(
                                id="header-panchayat-selector",
                                options=[{"label": f"🌟 {t('all_panchayats', lang)}", "value": "ALL"}],
                                value="ALL",
                                clearable=False,
                                searchable=True,
                                placeholder="All Panchayats",
                                className="subbar-dropdown panchayat-dropdown",
                                style={"minWidth": "190px"},
                                persistence=True,
                                persistence_type="local",
                            ),
                        ],
                        className="subbar-filter-group",
                    ),

                    # 4. Financial Year Selector
                    html.Div(
                        [
                            html.Label(t("lbl_fy", lang), id="header-lbl-year", className="subbar-input-label"),
                            dcc.Dropdown(
                                id="header-year-selector",
                                options=[
                                    {"label": "FY 2026-27 (Current)", "value": "2026-27"},
                                    {"label": "FY 2025-26", "value": "2025-26"},
                                    {"label": "FY 2024-25", "value": "2024-25"},
                                ],
                                value="2026-27",
                                clearable=False,
                                searchable=False,
                                className="subbar-dropdown year-dropdown",
                                style={"minWidth": "160px"},
                                persistence=True,
                                persistence_type="local",
                            ),
                        ],
                        className="subbar-filter-group",
                    ),

                    html.Label(t("lbl_language", lang), id="header-lbl-language", className="d-none"),

                    # Right Active Scope Pill
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("Active Scope: ", style={"color": "#64748B", "fontSize": "0.76rem", "fontWeight": "600"}),
                                    html.Span("National Coverage • 5 States • 32 Districts • 128 Panchayats", id="subbar-scope-text", style={"color": "#142D4E", "fontSize": "0.82rem", "fontWeight": "700"}),
                                    html.Span(" | FY 2026-27", id="subbar-fy-text", style={"color": "#25845A", "fontSize": "0.78rem", "fontWeight": "700"}),
                                ],
                                className="subbar-scope-pill",
                            )
                        ],
                        className="ms-auto d-none d-lg-flex align-items-center",
                    ),
                ],
                className="subbar-inner-container d-flex align-items-center flex-wrap gap-2",
            ),
        ],
        className="govt-admin-subbar",
    )


def create_sidebar(lang="en", state="ALL", district="ALL", panchayat="ALL"):
    """Create the institutional sidebar navigation shell (accessible on demand)."""
    lang = lang or "en"
    if panchayat and panchayat != "ALL":
        p_label = f"{panchayat} GP"
        sub_label = f"{district or state or ''}"
    elif district and district != "ALL":
        p_label = f"{district} {t('th_district', lang)}"
        sub_label = f"{state if state != 'ALL' else t('all_states', lang)}"
    elif state and state != "ALL":
        p_label = f"{state} {t('th_state', lang)}"
        sub_label = t("all_districts", lang)
    else:
        p_label = t("all_panchayats", lang)
        sub_label = f"5 {t('th_state', lang)} • 32 {t('th_district', lang)}"

    return html.Div(
        [
            html.Div(
                [
                    html.H4("Public Governance", id="sidebar-brand-title", className="sidebar-title"),
                    html.P("Decision Support Navigation", id="sidebar-brand-sub", className="sidebar-subtitle"),
                ],
                className="sidebar-header",
            ),
            dbc.Nav(
                [
                    dbc.NavLink(
                        [html.Span("🏛️", className="me-2"), html.Span(t("nav_overview", lang), id="nav-lbl-overview")],
                        href="/dashboard/",
                        active="exact",
                        id="nav-overview",
                    ),
                    dbc.NavLink(
                        [html.Span("📊", className="me-2"), html.Span(t("nav_vulnerability", lang), id="nav-lbl-vulnerability")],
                        href="/dashboard/vulnerability",
                        active="exact",
                        id="nav-vulnerability",
                    ),
                    dbc.NavLink(
                        [html.Span("⚖️", className="me-2"), html.Span(t("nav_budget", lang), id="nav-lbl-budget")],
                        href="/dashboard/budget",
                        active="exact",
                        id="nav-budget",
                    ),
                    dbc.NavLink(
                        [html.Span("🧠", className="me-2"), html.Span(t("nav_explanations", lang), id="nav-lbl-explanations")],
                        href="/dashboard/explanations",
                        active="exact",
                        id="nav-explanations",
                    ),
                    dbc.NavLink(
                        [html.Span("📈", className="me-2"), html.Span(t("nav_compare", lang), id="nav-lbl-compare")],
                        href="/dashboard/compare",
                        active="exact",
                        id="nav-compare",
                    ),
                    dbc.NavLink(
                        [html.Span("🪪", className="me-2"), html.Span("Officer Portal", id="nav-lbl-auth")],
                        href="/dashboard/auth",
                        active="exact",
                        id="nav-auth",
                    ),
                ],
                vertical=True,
                pills=True,
                className="sidebar-nav",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span("📍 ", style={"color": "#245B91"}),
                            html.Span(p_label, id="sidebar-context-label", className="sidebar-footer-text"),
                        ]
                    ),
                    html.P(sub_label, id="sidebar-context-sub", className="sidebar-footer-sub"),
                ],
                className="sidebar-footer",
            ),
        ],
        id="sidebar",
        className="sidebar d-none",  # Accessible when needed
    )


def create_government_footer(lang="en"):
    """Create the official government footer with tricolour divider and institutional links."""
    lang = lang or "en"
    return html.Footer(
        [
            # Tricolour ribbon divider
            html.Div(className="govt-tricolour-bar"),
            html.Div(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            html.Img(src="/dashboard/assets/images/emblem.svg", className="footer-emblem-svg me-2", alt="Emblem"),
                                            html.H5("Smart AI Panchayat", className="footer-brand-title m-0"),
                                        ],
                                        className="d-flex align-items-center mb-3 footer-col-header",
                                    ),
                                    html.P(
                                        t("footer_brand_sub", lang),
                                        className="footer-brand-sub",
                                    ),
                                    html.Small(
                                        t("footer_participating_states", lang),
                                        className="footer-states-text",
                                    ),
                                ],
                                md=5,
                                lg=5,
                                className="mb-4 pe-lg-4",
                            ),
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            html.H6(t("footer_core_systems", lang), className="footer-heading m-0"),
                                        ],
                                        className="d-flex align-items-center mb-3 footer-col-header",
                                    ),
                                    html.Ul(
                                        [
                                            html.Li(dcc.Link(t("footer_about", lang), href="/dashboard/about")),
                                            html.Li(dcc.Link(t("footer_vuln_index", lang), href="/dashboard/vulnerability")),
                                            html.Li(dcc.Link(t("footer_budget", lang), href="/dashboard/budget")),
                                            html.Li(dcc.Link(t("footer_ai_explain", lang), href="/dashboard/explanations")),
                                            html.Li(dcc.Link(t("footer_compare", lang), href="/dashboard/compare")),
                                        ],
                                        className="footer-links-list",
                                    ),
                                ],
                                md=3,
                                lg=3,
                                sm=6,
                                className="mb-4 ps-lg-3",
                            ),
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            html.H6(t("footer_data_sources", lang), className="footer-heading m-0"),
                                        ],
                                        className="d-flex align-items-center mb-3 footer-col-header",
                                    ),
                                    html.Ul(
                                        [
                                            html.Li(html.A(t("footer_niti_aayog", lang), href="https://www.niti.gov.in", target="_blank")),
                                            html.Li(html.A(t("footer_nfhs", lang), href="http://rchiips.org/nfhs", target="_blank")),
                                            html.Li(html.A(t("footer_census", lang), href="https://censusindia.gov.in", target="_blank")),
                                            html.Li(dcc.Link(t("footer_officer_portal", lang), href="/dashboard/auth")),
                                        ],
                                        className="footer-links-list",
                                    ),
                                ],
                                md=4,
                                lg=4,
                                sm=6,
                                className="mb-4 ps-lg-4",
                            ),
                        ],
                        className="g-4 g-lg-5 justify-content-between",
                    ),
                    html.Div(
                        [
                            html.P(
                                t("footer_copyright", lang),
                                className="footer-copyright-text",
                            ),
                            html.Small(
                                t("footer_compliance", lang),
                                className="footer-compliance-text",
                            ),
                        ],
                        className="footer-bottom-bar",
                    ),
                ],
                className="govt-footer-content",
            ),
        ],
        id="govt-footer-section",
        className="govt-footer",
    )


def create_layout():
    """Create the full application layout shell."""
    return html.Div(
        [
            dcc.Location(id="url", refresh=False),
            # Session and Local Storage stores
            dcc.Store(id="current-user-store", storage_type="session", data=None),
            dcc.Store(id="current-lang-store", storage_type="local", data="en"),
            dcc.Store(
                id="global-location-store",
                storage_type="local",
                data={
                    "state_id": "ALL",
                    "state_name": "ALL",
                    "district_id": "ALL",
                    "district_name": "ALL",
                    "panchayat_id": "ALL",
                    "panchayat_name": "ALL",
                    "financial_year": "2026-27",
                    "state": "ALL",
                    "district": "ALL",
                    "panchayat": "ALL",
                    "year": "2026-27",
                },
            ),
            dcc.Store(id="selected-state-store", storage_type="local", data="ALL"),
            dcc.Store(id="selected-district-store", storage_type="local", data="ALL"),
            dcc.Store(id="selected-panchayat-store", storage_type="local", data="ALL"),
            dcc.Store(id="selected-year-store", storage_type="local", data="2026-27"),
            
            # Data Provenance & Traceability Ledger Modal
            ProvenanceService.create_provenance_modal(),

            # Top National Tricolour Band
            html.Div(className="govt-tricolour-bar"),
            # Top Government Information Bar
            create_top_government_bar(),
            # Sticky Main Navigation Header
            create_top_header(),
            # Cascading Administrative Jurisdiction Bar
            create_cascading_subbar(),
            
            # Main Layout Container
            html.Div(
                [
                    create_sidebar(),
                    html.Div(
                        [
                            dcc.Loading(
                                id="loading-page-content",
                                type="dot",
                                color="#245B91",
                                children=html.Div(id="page-content", className="page-inner-content"),
                            ),
                        ],
                        className="main-content-full",
                    ),
                ],
                className="app-container-full",
            ),
            
            # Official Government Footer Container (Dynamically localized)
            html.Div(id="dynamic-footer-container", children=create_government_footer("en")),
        ],
        className="app-root",
    )
