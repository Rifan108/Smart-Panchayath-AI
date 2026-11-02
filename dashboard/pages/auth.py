"""
Authentication Page — Official Government Officer Portal & Registration.
Supports 5 Indian States with multi-state district mapping, mandatory Government ID verification (PEN / Aadhaar / KILA ID),
and institutional public-sector digital governance aesthetics.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
from services.i18n import t
from data.panchayat_geography import STATES_PANCHAYAT_DATA


def create_auth_layout(lang="en", active_tab="login"):
    """Render the official Government Officer Portal login and registration interface."""
    # Build district options across all 5 supported states
    district_options = []
    for state_name, s_data in STATES_PANCHAYAT_DATA.items():
        for dist_name in sorted(s_data.get("districts", {}).keys()):
            district_options.append({
                "label": f"{state_name} — {dist_name}",
                "value": dist_name,
            })

    return html.Div(
        [
            html.Div(
                [
                    # Top Government Identification Bar
                    html.Div(
                        [
                            html.Div([
                                html.Span("🇮🇳 LOCAL GOVERNANCE DIGITAL INFRASTRUCTURE", style={"fontSize": "0.74rem", "fontWeight": "800", "letterSpacing": "1px", "color": "#142D4E"}),
                                html.Span(" • ", style={"color": "#CBD5E1", "margin": "0 6px"}),
                                html.Span("OFFICIAL USE ONLY", style={"fontSize": "0.72rem", "fontWeight": "700", "color": "#C74747", "background": "#FEE2E2", "padding": "2px 8px", "borderRadius": "4px"}),
                            ], className="mb-2 text-center"),
                            html.H2("Smart AI Panchayat Planner", className="auth-brand-title", style={"color": "#142D4E", "fontWeight": "800", "fontSize": "1.75rem", "marginBottom": "4px"}),
                            html.P("Decentralized AI-Enabled Decision Support System for Panchayati Raj Institutions (LSGIs)", className="auth-brand-subtitle", style={"color": "#64748B", "fontSize": "0.88rem"}),
                        ],
                        className="auth-header text-center mb-3",
                    ),

                    # Notification Alert Area
                    html.Div(id="auth-alert-container", style={"marginBottom": "16px"}),

                    # Main Government Auth Card
                    html.Div(
                        [
                            # Tricolour Accent Line at Top of Card
                            html.Div(
                                style={
                                    "height": "4px",
                                    "background": "linear-gradient(90deg, #E99A36 0%, #E99A36 33.3%, #FFFFFF 33.3%, #FFFFFF 66.6%, #25845A 66.6%, #25845A 100%)",
                                    "borderTopLeftRadius": "10px",
                                    "borderTopRightRadius": "10px",
                                }
                            ),
                            html.Div([
                                dbc.Tabs(
                                    [
                                        dbc.Tab(
                                            label=f"🔑 Officer Sign In",
                                            tab_id="tab-login",
                                            active_tab_class_name="auth-tab-active",
                                            tab_style={"fontWeight": "600", "color": "#64748B", "cursor": "pointer"},
                                        ),
                                        dbc.Tab(
                                            label=f"📝 Register Official Account",
                                            tab_id="tab-register",
                                            active_tab_class_name="auth-tab-active",
                                            tab_style={"fontWeight": "600", "color": "#64748B", "cursor": "pointer"},
                                        ),
                                    ],
                                    id="auth-tabs",
                                    active_tab="tab-login",
                                    className="auth-nav-tabs justify-content-center mb-4",
                                ),

                                # ─── Login Form Container ───
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Label("Official Username / Officer ID", className="form-label", style={"fontWeight": "600", "color": "#142D4E", "fontSize": "0.85rem"}),
                                                dbc.Input(
                                                    id="login-username",
                                                    type="text",
                                                    placeholder="Enter official username (e.g. officer.krdpr, secretary)",
                                                    className="auth-input",
                                                ),
                                            ],
                                            className="mb-3",
                                        ),
                                        html.Div(
                                            [
                                                html.Label("Password", className="form-label", style={"fontWeight": "600", "color": "#142D4E", "fontSize": "0.85rem"}),
                                                dbc.Input(
                                                    id="login-password",
                                                    type="password",
                                                    placeholder="Enter secure portal password",
                                                    className="auth-input",
                                                ),
                                            ],
                                            className="mb-4",
                                        ),
                                        dbc.Button(
                                            [html.Span("🔐 "), "Sign In to Governance Portal"],
                                            id="btn-login-submit",
                                            color="primary",
                                            className="w-100 auth-btn-submit py-2",
                                            style={"background": "#142D4E", "borderColor": "#142D4E", "fontWeight": "700", "fontSize": "0.95rem"},
                                        ),
                                        html.Div(
                                            [
                                                html.Small(
                                                    "Authorized access only. All authentication attempts are logged under National Informatics Centre (NIC) audit guidelines.",
                                                    style={"color": "#64748B", "fontSize": "0.74rem", "display": "block", "marginTop": "16px"},
                                                ),
                                            ],
                                            className="text-center",
                                        ),
                                    ],
                                    id="login-container",
                                    className="auth-tab-content",
                                ),

                                # ─── Register Form Container ───
                                html.Div(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        html.Label("Official Full Name *", className="form-label", style={"fontWeight": "600", "color": "#142D4E", "fontSize": "0.85rem"}),
                                                        dbc.Input(id="reg-fullname", type="text", placeholder="e.g. Dr. K. Radhakrishnan, IAS", className="auth-input"),
                                                    ],
                                                    md=6,
                                                    className="mb-3",
                                                ),
                                                dbc.Col(
                                                    [
                                                        html.Label("Official Email Address *", className="form-label", style={"fontWeight": "600", "color": "#142D4E", "fontSize": "0.85rem"}),
                                                        dbc.Input(id="reg-email", type="email", placeholder="officer@nic.in / lsgd.gov.in", className="auth-input"),
                                                    ],
                                                    md=6,
                                                    className="mb-3",
                                                ),
                                            ]
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        html.Label(
                                                            [
                                                                "Government / Employee Identification Number ",
                                                                html.Span("*", style={"color": "#C74747", "fontWeight": "bold"}),
                                                                html.Small(" (PEN / Aadhaar / KILA ID / Voter ID / Official Emp ID)", style={"color": "#64748B", "fontWeight": "normal"}),
                                                            ],
                                                            className="form-label",
                                                            style={"fontWeight": "600", "color": "#142D4E", "fontSize": "0.85rem"},
                                                        ),
                                                        dbc.Input(
                                                            id="reg-govtid",
                                                            type="text",
                                                            placeholder="e.g. KL-LSGD-2026-9901 or PEN-894102 or KA-RDPR-4410",
                                                            className="auth-input",
                                                            value="KL-LSGD-2026-9901",
                                                        ),
                                                    ],
                                                    md=12,
                                                    className="mb-3",
                                                ),
                                            ]
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        html.Label("Desired Username *", className="form-label", style={"fontWeight": "600", "color": "#142D4E", "fontSize": "0.85rem"}),
                                                        dbc.Input(id="reg-username", type="text", placeholder="officer_sk", className="auth-input"),
                                                    ],
                                                    md=6,
                                                    className="mb-3",
                                                ),
                                                dbc.Col(
                                                    [
                                                        html.Label("Designation / Official Role *", className="form-label", style={"fontWeight": "600", "color": "#142D4E", "fontSize": "0.85rem"}),
                                                        dbc.Select(
                                                            id="reg-role",
                                                            options=[
                                                                {"label": "District Planning Officer (DPO)", "value": "District Planning Officer"},
                                                                {"label": "Panchayat Secretary (Grade I/II)", "value": "Panchayat Secretary"},
                                                                {"label": "Elected Ward Member / Councillor", "value": "Ward Member / Councillor"},
                                                                {"label": "Technical Assistant / Engineer", "value": "Technical Assistant"},
                                                                {"label": "Citizen / Public Policy Researcher", "value": "Citizen / Researcher"},
                                                            ],
                                                            value="Panchayat Secretary",
                                                            className="auth-input",
                                                        ),
                                                    ],
                                                    md=6,
                                                    className="mb-3",
                                                ),
                                            ]
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        html.Label("State & District Jurisdiction *", className="form-label", style={"fontWeight": "600", "color": "#142D4E", "fontSize": "0.85rem"}),
                                                        dbc.Select(id="reg-district", options=district_options, value="Kasaragod", className="auth-input"),
                                                    ],
                                                    md=6,
                                                    className="mb-3",
                                                ),
                                                dbc.Col(
                                                    [
                                                        html.Label("Grama Panchayat Jurisdiction *", className="form-label", style={"fontWeight": "600", "color": "#142D4E", "fontSize": "0.85rem"}),
                                                        dbc.Input(id="reg-panchayat", type="text", placeholder="e.g. Manjeshwar / Nileshwaram", value="Manjeshwar", className="auth-input"),
                                                    ],
                                                    md=6,
                                                    className="mb-3",
                                                ),
                                            ]
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        html.Label("Password *", className="form-label", style={"fontWeight": "600", "color": "#142D4E", "fontSize": "0.85rem"}),
                                                        dbc.Input(id="reg-password", type="password", placeholder="Minimum 6 characters", className="auth-input"),
                                                    ],
                                                    md=6,
                                                    className="mb-3",
                                                ),
                                                dbc.Col(
                                                    [
                                                        html.Label("Confirm Password *", className="form-label", style={"fontWeight": "600", "color": "#142D4E", "fontSize": "0.85rem"}),
                                                        dbc.Input(id="reg-confirm-password", type="password", placeholder="Re-enter password", className="auth-input"),
                                                    ],
                                                    md=6,
                                                    className="mb-3",
                                                ),
                                            ]
                                        ),
                                        dbc.Button(
                                            [html.Span("📋 "), "Submit Official Registration"],
                                            id="btn-register-submit",
                                            color="success",
                                            className="w-100 auth-btn-submit mt-2 py-2",
                                            style={"background": "#25845A", "borderColor": "#25845A", "fontWeight": "700", "fontSize": "0.95rem"},
                                        ),
                                    ],
                                    id="register-container",
                                    className="auth-tab-content",
                                    style={"display": "none"},
                                ),
                            ], style={"padding": "28px"}),
                        ],
                        className="gov-card p-0 shadow-sm",
                        style={"background": "#FFFFFF", "borderRadius": "10px", "border": "1px solid #DCE3EB"},
                    ),

                    # Official Security & Institutional Notice
                    html.Div(
                        [
                            html.P(
                                "Ministry of Panchayati Raj • Local Self Government Department (LSGD)",
                                style={"fontSize": "0.82rem", "fontWeight": "600", "color": "#142D4E", "margin": "0 0 4px"},
                            ),
                            html.Small(
                                "Multi-State Decentralized AI Decision Planning Platform (Kerala • Karnataka • Tamil Nadu • Andhra Pradesh • Maharashtra)",
                                style={"color": "#64748B", "fontSize": "0.75rem", "display": "block"},
                            ),
                            html.Small(
                                "Authorized official access only. All login activities and plan submissions are recorded in the institutional audit log.",
                                style={"color": "#94A3B8", "fontSize": "0.7rem", "display": "block", "marginTop": "4px"},
                            ),
                        ],
                        className="auth-footer text-center mt-4",
                    ),
                ],
                className="auth-wrapper",
                style={"maxWidth": "580px", "margin": "0 auto", "padding": "40px 16px"},
            )
        ],
        className="auth-page-container",
        style={"background": "#F5F7FA", "minHeight": "100vh"},
    )
