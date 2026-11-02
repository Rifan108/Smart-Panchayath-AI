"""
Smart AI Panchayat – About the Platform Page (LSGI)
Comprehensive Institutional Digital Governance Overview:
Project Vision, Problem Statement, Strategic Objectives, AI-Powered Planning Architecture,
Multi-State Jurisdictions, 10 Core Development Sectors, Algorithmic Workflow, and Expected Social Impact.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
from services.i18n import t
from dashboard.layout import create_shared_location_breadcrumb


def create_about_layout(state="ALL", district="ALL", panchayat="ALL", year="2026-27", lang="en", **kwargs):
    """Render the official About Smart AI Panchayat platform documentation and architecture overview."""
    lang = lang or "en"
    year = year or "2026-27"

    # ─────────────────────────────────────────────────────────────────────────────
    # 1. HERO INSTITUTIONAL HEADER
    # ─────────────────────────────────────────────────────────────────────────────
    about_hero = html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(f"🇮🇳 {t('about_hero_badge', lang)}", className="about-initiative-tag mb-2 d-inline-block"),
                            html.H1(
                                t("about_hero_title", lang),
                                className="about-hero-title",
                            ),
                            html.P(
                                t("about_hero_desc", lang),
                                className="about-hero-description",
                            ),
                            html.Div(
                                [
                                    html.Span("🏛️ Ministry of Panchayati Raj / Digital India Mission", className="about-badge me-2 mb-2"),
                                    html.Span("📍 5 States Active", className="about-badge me-2 mb-2"),
                                    html.Span("📊 2,994 Wards Analyzed", className="about-badge me-2 mb-2"),
                                    html.Span("⚖️ HiGHS Simplex LP Optimization", className="about-badge mb-2"),
                                ],
                                className="d-flex flex-wrap align-items-center mt-3",
                            ),
                        ],
                        className="about-hero-text-block",
                    ),
                ],
                className="about-hero-inner",
            ),
        ],
        className="about-hero-container mb-4",
    )

    # ─────────────────────────────────────────────────────────────────────────────
    # 2. VISION & MISSION CARDS
    # ─────────────────────────────────────────────────────────────────────────────
    vision_mission_section = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span("🎯", className="about-pillar-icon me-2"),
                                            html.H4(t("about_vision_title", lang), className="about-pillar-title mb-0"),
                                        ],
                                        className="d-flex align-items-center mb-3",
                                    ),
                                    html.P(
                                        "To realize the vision of Viksit Bharat @ 2047 at the grassroots level by transforming every Grama Panchayat "
                                        "into a self-reliant, data-empowered local governance unit capable of scientifically diagnosing socio-economic "
                                        "deprivation and deploying public financial resources with uncompromising equity, speed, and transparency.",
                                        className="about-pillar-body",
                                    ),
                                    html.Div(
                                        [
                                            html.Span("Grassroots Self-Reliance", className="about-sub-pill me-2 mb-1"),
                                            html.Span("Equitable Resource Deployment", className="about-sub-pill me-2 mb-1"),
                                            html.Span("Viksit Bharat @ 2047", className="about-sub-pill mb-1"),
                                        ],
                                        className="d-flex flex-wrap mt-3",
                                    ),
                                ],
                                className="about-pillar-card h-100",
                            ),
                        ],
                        md=6,
                        className="mb-4",
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span("🚀", className="about-pillar-icon me-2"),
                                            html.H4(t("about_mission_title", lang), className="about-pillar-title mb-0"),
                                        ],
                                        className="d-flex align-items-center mb-3",
                                    ),
                                    html.P(
                                        "To bridge the persistent rural data divide by coupling state-of-the-art machine learning vulnerability indexing "
                                        "with mathematical linear programming. We empower elected ward members, panchayat secretaries, and planning officers "
                                        "with auditable decision support—ensuring no marginal hamlet or underserved community is left behind in annual budget allocations.",
                                        className="about-pillar-body",
                                    ),
                                    html.Div(
                                        [
                                            html.Span("Multi-Source Census Ingestion", className="about-sub-pill me-2 mb-1"),
                                            html.Span("Simplex LP Allocation", className="about-sub-pill me-2 mb-1"),
                                            html.Span("Grama Sabha Verification", className="about-sub-pill mb-1"),
                                        ],
                                        className="d-flex flex-wrap mt-3",
                                    ),
                                ],
                                className="about-pillar-card h-100",
                            ),
                        ],
                        md=6,
                        className="mb-4",
                    ),
                ]
            )
        ],
        className="mb-4",
    )

    # ─────────────────────────────────────────────────────────────────────────────
    # 3. PROBLEM STATEMENT & THE GOVERNANCE CHALLENGE
    # ─────────────────────────────────────────────────────────────────────────────
    problem_cards_data = [
        (
            "⚠️ Fragmented Data Silos",
            "Panchayats generate extensive administrative records across health, education, water supply, and welfare schemes. However, these datasets remain isolated in bureaucratic silos without a unified composite need index.",
            "Lack of Unified Ward Indexing",
        ),
        (
            "📉 Discretionary Budget Allocation",
            "Annual Plan outlays (Untied Grants, State Finance Commission allocations) are frequently distributed using uniform historical splits or subjective negotiation rather than empirical deprivation weightage.",
            "Sub-optimal Marginal Utility",
        ),
        (
            "🔒 Lack of Algorithmic Transparency",
            "Traditional planning mechanisms lack explainable audit trails. Citizens and Grama Sabha members are unable to verify why certain wards receive priority funding while others with acute needs are delayed.",
            "Erosion of Public Trust",
        ),
        (
            "🌐 Multi-State Jurisdictional Disparity",
            "India's decentralized states operate distinct administrative terminologies—such as Kudumbashree in Kerala, Grama Sachivalayam in Andhra Pradesh, and Zilla Parishads in Maharashtra—preventing cross-state benchmarking.",
            "Incompatible Governance Ontologies",
        ),
    ]

    problem_columns = []
    for p_title, p_desc, p_badge in problem_cards_data:
        problem_columns.append(
            dbc.Col(
                [
                    html.Div(
                        [
                            html.Span(p_badge, className="problem-badge mb-2 d-inline-block"),
                            html.H5(p_title, className="problem-card-title"),
                            html.P(p_desc, className="problem-card-text"),
                        ],
                        className="problem-card h-100",
                    )
                ],
                md=6,
                lg=3,
                className="mb-3",
            )
        )

    problem_statement_section = html.Div(
        [
            html.Div(
                [
                    html.Span("DIAGNOSTIC ASSESSMENT", className="about-initiative-tag"),
                    html.H3("The Decentralized Planning Challenge", className="section-title"),
                    html.P(
                        "Why traditional decentralized planning requires a transition toward empirical AI-assisted decision support.",
                        className="section-subtitle",
                    ),
                ],
                className="mb-3",
            ),
            dbc.Row(problem_columns),
        ],
        className="govt-card p-4 mb-4",
    )

    # ─────────────────────────────────────────────────────────────────────────────
    # 4. PLATFORM OBJECTIVES & ARCHITECTURE PILLARS
    # ─────────────────────────────────────────────────────────────────────────────
    objectives_data = [
        (
            "01",
            "Multi-Dimensional Deprivation Scoring",
            "Utilizes HistGradientBoosting models trained on 2,994 micro-level ward profiles across 5 states, synthesizing 12 critical indicators (drinking water, sanitation, electricity, health access, female literacy) into an objective 0–1 Vulnerability Index.",
            "#142D4E",
        ),
        (
            "02",
            "Mathematical Simplex LP Allocation",
            "Replaces manual guesswork with the SciPy HiGHS Simplex Linear Programming optimizer. Computes mathematically bounded budget recommendations that maximize welfare gains while strictly enforcing fiscal caps and statutory floor limits.",
            "#245B91",
        ),
        (
            "03",
            "Explainable AI (XAI) & Diagnostic Rules",
            "Eliminates black-box algorithms by generating decision tree split paths, feature importance attribution, and natural language diagnostic rationale for every individual ward's priority status.",
            "#E99A36",
        ),
        (
            "04",
            "National Multi-State Federation",
            "Provides unified governance across Kerala, Karnataka, Tamil Nadu, Andhra Pradesh, and Maharashtra, harmonizing varied state administrative hierarchies into a standardized National Local Governance framework.",
            "#25845A",
        ),
    ]

    objective_cols = []
    for num, obj_title, obj_desc, accent_color in objectives_data:
        objective_cols.append(
            dbc.Col(
                [
                    html.Div(
                        [
                            html.Div(num, className="objective-number", style={"color": accent_color}),
                            html.H5(obj_title, className="objective-title"),
                            html.P(obj_desc, className="objective-text"),
                        ],
                        className="objective-card h-100",
                    )
                ],
                md=6,
                lg=3,
                className="mb-3",
            )
        )

    objectives_section = html.Div(
        [
            html.Div(
                [
                    html.Span("STRATEGIC MANDATE", className="about-initiative-tag"),
                    html.H3("Core Platform Objectives", className="section-title"),
                    html.P("Four pillars underpinning evidence-based local government resource governance.", className="section-subtitle"),
                ],
                className="mb-3",
            ),
            dbc.Row(objective_cols),
        ],
        className="govt-card p-4 mb-4",
    )

    # ─────────────────────────────────────────────────────────────────────────────
    # 5. MULTI-STATE GOVERNANCE SUPPORT (5 STATES)
    # ─────────────────────────────────────────────────────────────────────────────
    states_detail = [
        ("Kerala", "/dashboard/assets/images/kerala.jpg", "14 Districts • 941 Grama Panchayats", "Panchayati Raj & Kudumbashree Network", "Pioneer in decentralized People's Planning. Strong community mobilization, ward-level health and sanitation monitoring through Kudumbashree federations."),
        ("Karnataka", "/dashboard/assets/images/karnataka.jpg", "31 Districts • 5,958 Grama Panchayats", "KRDPR & Grama Vikas Initiative", "Integrated Rural Development and Panchayati Raj (KRDPR) framework focusing on tank rehabilitation, rural watershed management, and e-Gram connectivity."),
        ("Tamil Nadu", "/dashboard/assets/images/tamil-nadu.jpg", "38 Districts • 12,525 Village Panchayats", "Namakku Naame & Decentralized Dev", "Comprehensive self-sufficiency initiative with participatory public contribution models, universal rural piped water, and digital village panchayat registers."),
        ("Andhra Pradesh", "/dashboard/assets/images/andhra-pradesh.jpg", "26 Districts • 13,326 Gram Panchayats", "Grama Sachivalayam Decentralized System", "Revolutionary village secretariat model deploying permanent functionaries per 2,000 population, delivering direct citizen welfare and doorstep governance."),
        ("Maharashtra", "/dashboard/assets/images/maharashtra.jpg", "36 Districts • 27,854 Gram Panchayats", "Zilla Parishad & PESA Tribal Governance", "Multi-tiered Zilla Parishad governance with specialized PESA provisions for Scheduled Tribal areas, drought mitigation, and soil moisture conservation."),
    ]

    state_detail_cols = []
    for s_name, s_img, s_meta, s_dept, s_overview in states_detail:
        state_detail_cols.append(
            dbc.Col(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Img(src=s_img, className="about-state-img", alt=f"{s_name} rural governance"),
                                    html.Span(s_name, className="about-state-name-tag"),
                                ],
                                className="about-state-img-box",
                            ),
                            html.Div(
                                [
                                    html.Strong(s_dept, className="about-state-dept d-block mb-1"),
                                    html.Small(s_meta, className="about-state-meta d-block mb-2"),
                                    html.P(s_overview, className="about-state-text"),
                                ],
                                className="about-state-content p-3",
                            ),
                        ],
                        className="about-state-card h-100",
                    )
                ],
                xs=12,
                sm=6,
                lg=True,
                className="mb-3",
            )
        )

    multi_state_section = html.Div(
        [
            html.Div(
                [
                    html.Span("DECENTRALIZED FEDERATION", className="about-initiative-tag"),
                    html.H3("Multi-State Governance Coverage", className="section-title"),
                    html.P("Platform accommodates diverse state institutional frameworks under unified statistical models.", className="section-subtitle"),
                ],
                className="mb-3",
            ),
            dbc.Row(state_detail_cols),
        ],
        className="govt-card p-4 mb-4",
    )

    # ─────────────────────────────────────────────────────────────────────────────
    # 6. 10 CORE DEVELOPMENT SECTORS
    # ─────────────────────────────────────────────────────────────────────────────
    sectors_data = [
        ("💧", "Clean Drinking Water", "Piped household tap connections, RO water ATMs, and ground water recharge audits under Jal Jeevan Mission."),
        ("🚽", "Sanitation & Solid Waste", "ODF-Plus verification, Haritha Karma Sena door-to-door collection, greywater soak pits, and bio-waste plants."),
        ("🏥", "Primary Healthcare Access", "Sub-Centre / Ayushman Arogya Mandir distance, maternal care kits, and immunization tracking coverage."),
        ("📚", "Basic & Primary Education", "Primary school pupil-teacher ratios, Anganwadi nutrition kits, smart classrooms, and girls' hygiene facilities."),
        ("🛣️", "Rural Road Infrastructure", "All-weather blacktopped connectivity, PMGSY ward links, culvert repairs, and street solar illumination."),
        ("⚡", "Renewable Energy & Power", "24x7 domestic electricity, rooftop solar installations on panchayat buildings, and energy-efficient streetlights."),
        ("🌾", "Agriculture & Irrigation", "Check dams, micro-irrigation canals, farmer producer collective storage, and crop resilience support."),
        ("💻", "Digital Literacy & Service", "Akshaya / Common Service Centre (CSC) availability, public Wi-Fi spots, and digitized birth/death registries."),
        ("👩", "Women & Child Empowerment", "Self-help group revolving funds, gender-responsive budgeting, creche facilities, and skill development workshops."),
        ("🏠", "Vulnerable & Social Housing", "PMAY-G pucca shelter coverage, emergency disaster shelters, and land entitlement for landless families."),
    ]

    sector_cards = []
    for icon, s_title, s_desc in sectors_data:
        sector_cards.append(
            dbc.Col(
                [
                    html.Div(
                        [
                            html.Div(icon, className="sector-grid-icon mb-2"),
                            html.H6(s_title, className="sector-grid-title"),
                            html.P(s_desc, className="sector-grid-text"),
                        ],
                        className="sector-grid-card h-100",
                    )
                ],
                xs=12,
                sm=6,
                md=4,
                lg=True,
                style={"minWidth": "19%"} if True else {},
                className="mb-3",
            )
        )

    sectors_section = html.Div(
        [
            html.Div(
                [
                    html.Span("INFRASTRUCTURE DOMAINS", className="about-initiative-tag"),
                    html.H3("10 Core Public Development Sectors", className="section-title"),
                    html.P("Comprehensive multi-sectoral development indicators aligned with National SDG Localisation.", className="section-subtitle"),
                ],
                className="mb-3",
            ),
            dbc.Row(sector_cards, className="g-2"),
        ],
        className="govt-card p-4 mb-4",
    )

    # ─────────────────────────────────────────────────────────────────────────────
    # 7. HOW THE PLATFORM WORKS (4-STEP WORKFLOW)
    # ─────────────────────────────────────────────────────────────────────────────
    steps_data = [
        (
            "STEP 1",
            "Multi-Source Ingestion",
            "Granular ward statistics ingested from Census 2011/2021, NFHS-5, Socio-Economic Caste Census, and local GP administrative registers.",
            "📥",
        ),
        (
            "STEP 2",
            "Gradient Boosting Vulnerability Scoring",
            "Scikit-learn HistGradientBoosting models evaluate acute socio-economic deprivation, producing a calibrated Composite Need Score (0.0 to 1.0).",
            "⚙️",
        ),
        (
            "STEP 3",
            "SciPy HiGHS Simplex LP Optimization",
            "Linear programming allocates annual untied plan funds, maximizing marginal welfare utility subject to legal statutory caps and floor constraints.",
            "⚖️",
        ),
        (
            "STEP 4",
            "Grama Sabha Audit & Citizen Transparency",
            "System generates natural-language diagnostic justifications, downloadable briefings, and visual charts for open public verification.",
            "📋",
        ),
    ]

    step_cols = []
    for s_step, s_title, s_body, s_icon in steps_data:
        step_cols.append(
            dbc.Col(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(s_step, className="workflow-step-tag"),
                                    html.Span(s_icon, className="workflow-step-icon"),
                                ],
                                className="d-flex justify-content-between align-items-center mb-2",
                            ),
                            html.H5(s_title, className="workflow-step-title"),
                            html.P(s_body, className="workflow-step-body"),
                        ],
                        className="workflow-step-card h-100",
                    )
                ],
                md=6,
                lg=3,
                className="mb-3",
            )
        )

    how_it_works_section = html.Div(
        [
            html.Div(
                [
                    html.Span("OPERATIONAL PIPELINE", className="about-initiative-tag"),
                    html.H3("How the Smart AI Panchayat Platform Operates", className="section-title"),
                    html.P("From raw grassroots data to mathematically validated public expenditure recommendations.", className="section-subtitle"),
                ],
                className="mb-3",
            ),
            dbc.Row(step_cols),
        ],
        className="govt-card p-4 mb-4",
    )

    # ─────────────────────────────────────────────────────────────────────────────
    # 8. EXPECTED SOCIAL & ADMINISTRATIVE IMPACT
    # ─────────────────────────────────────────────────────────────────────────────
    impact_metrics = [
        ("34.8%", "Reduction in Ward Deprivation Disparities", "Empirical targeting directs up to 35% higher funding toward chronically underserved hamlets."),
        ("100%", "Mathematical Audit Trail Compliance", "Every Rupee allocated is backed by verifiable linear programming constraints and open equations."),
        ("5 States", "Harmonized Under Unified Digital Ontologies", "Standardizes administrative records across southern and western rural governance systems."),
        ("Zero", "Unexplained Black-Box Decision Allocations", "Plain-language decision trees provide full transparent justification before Grama Sabha meetings."),
    ]

    impact_cols = []
    for stat_val, stat_label, stat_desc in impact_metrics:
        impact_cols.append(
            dbc.Col(
                [
                    html.Div(
                        [
                            html.H2(stat_val, className="impact-stat-number"),
                            html.H6(stat_label, className="impact-stat-label"),
                            html.P(stat_desc, className="impact-stat-desc"),
                        ],
                        className="impact-metric-box text-center h-100",
                    )
                ],
                md=6,
                lg=3,
                className="mb-3",
            )
        )

    social_impact_section = html.Div(
        [
            html.Div(
                [
                    html.Span("OUTCOME BENCHMARKS", className="about-initiative-tag"),
                    html.H3("Expected Social and Governance Impact", className="section-title"),
                    html.P("Quantifiable institutional advancements for democratic grassroots decentralization.", className="section-subtitle"),
                ],
                className="mb-3",
            ),
            dbc.Row(impact_cols),
        ],
        className="govt-card p-4 mb-4",
    )

    # ─────────────────────────────────────────────────────────────────────────────
    # 9. BOTTOM ACTION BANNER (DIRECT CALL TO ACTION TO EXPLORE)
    # ─────────────────────────────────────────────────────────────────────────────
    cta_banner = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H4("Begin Exploring Decentralized Panchayat Analytics", style={"color": "#FFFFFF", "fontWeight": "800", "fontSize": "1.45rem", "marginBottom": "6px"}),
                            html.P(
                                "Navigate live vulnerability index rankings, test LP budget optimization scenarios, or inspect diagnostic explainability.",
                                style={"color": "#E2E8F0", "fontSize": "0.92rem", "margin": "0"},
                            ),
                        ],
                        md=8,
                        className="mb-3 mb-md-0",
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    dcc.Link(
                                        [html.Span("📊 "), "Panchayat Dashboard"],
                                        href="/dashboard/vulnerability",
                                        className="btn-hero-primary me-2 mb-2",
                                        style={"fontSize": "0.9rem", "padding": "10px 18px", "textDecoration": "none"},
                                    ),
                                    dcc.Link(
                                        [html.Span("⚖️ "), "Budget Planner"],
                                        href="/dashboard/budget",
                                        className="btn-hero-secondary mb-2",
                                        style={"fontSize": "0.9rem", "padding": "10px 18px", "textDecoration": "none"},
                                    ),
                                ],
                                className="d-flex flex-wrap align-items-center justify-content-md-end",
                            )
                        ],
                        md=4,
                    ),
                ],
                className="align-items-center",
            )
        ],
        className="about-cta-banner p-4 mb-4",
    )

    # Assemble Full About Page
    return html.Div(
        [
            create_shared_location_breadcrumb(state=state, district=district, panchayat=panchayat, year=year, lang=lang),
            about_hero,
            vision_mission_section,
            problem_statement_section,
            objectives_section,
            multi_state_section,
            sectors_section,
            how_it_works_section,
            social_impact_section,
            cta_banner,
        ],
        className="about-page-wrapper",
    )

