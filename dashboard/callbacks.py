import pandas as pd
"""
Dashboard Callbacks — Multi-panchayat routing, cascading selectors, multilingual switcher,
authentication management (login/register/logout), and interactive visualization updates.
"""

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, html, dcc
from data.kerala_geography import KERALA_DISTRICTS_DATA
from services.i18n import t, LANGUAGES
from services.auth_service import authenticate_user, register_user
from services.cache_service import get_cached_layout, clear_layout_cache
from dashboard.pages.overview import create_overview_layout
from dashboard.pages.about import create_about_layout
from dashboard.pages.vulnerability import create_vulnerability_layout, create_radar_chart
from dashboard.pages.budget import create_budget_layout, create_budget_charts
from dashboard.pages.explanations import create_explanations_layout, create_ward_explanation
from dashboard.pages.comparison import create_comparison_layout, create_comparison_content
from dashboard.pages.training import create_training_layout
from dashboard.pages.auth import create_auth_layout
from dashboard.layout import create_government_footer


def register_callbacks(app, engine):
    """Register all dashboard callbacks."""

    # ─── 1. Header, Navigation, Subbar & Footer Reactive Localization ──────
    @app.callback(
        Output("header-lbl-state", "children"),
        Output("header-lbl-district", "children"),
        Output("header-lbl-panchayat", "children"),
        Output("header-lbl-language", "children"),
        Output("header-brand-title", "children"),
        Output("header-brand-sub", "children"),
        Output("sidebar-brand-title", "children"),
        Output("sidebar-brand-sub", "children"),
        Output("header-state-selector", "options"),
        Output("header-lbl-year", "children"),
        Output("subbar-jurisdiction-label", "children"),
        Output("nav-lbl-home", "children"),
        Output("nav-lbl-about", "children"),
        Output("nav-lbl-dashboard", "children"),
        Output("nav-lbl-planning", "children"),
        Output("nav-lbl-insights", "children"),
        Output("nav-lbl-reports", "children"),
        Output("nav-lbl-contact", "children"),
        Output("officer-portal-label", "children"),
        Output("topbar-gov-india", "children"),
        Output("topbar-min-panchayat", "children"),
        Output("topbar-screen-reader", "children"),
        Output("dynamic-footer-container", "children"),
        Input("current-lang-store", "data"),
    )
    def update_header_and_sidebar_language(lang):
        lang = lang or "en"
        states = engine.get_states()
        state_opts = [{"label": f"🌟 {t('all_states', lang)}", "value": "ALL"}] + [
            {"label": f"📍 {s}", "value": s} for s in states
        ]
        return (
            t("lbl_state", lang),
            t("lbl_district", lang),
            t("lbl_panchayat", lang),
            t("lbl_language", lang),
            t("brand_title", lang),
            t("header_brand_sub", lang),
            t("brand_title", lang),
            t("sidebar_subtitle", lang),
            state_opts,
            t("lbl_fy", lang),
            t("admin_jurisdiction", lang),
            t("nav_home", lang),
            t("nav_about", lang),
            t("nav_dashboard", lang),
            t("nav_planning", lang),
            t("nav_insights", lang),
            t("nav_reports", lang),
            t("nav_contact", lang),
            t("officer_portal", lang),
            t("gov_india", lang),
            t("min_panchayati_raj", lang),
            t("screen_reader_access", lang),
            create_government_footer(lang=lang),
        )

    # ─── 2a. State Card Quick Actions on Home Page ────────────────────────────
    @app.callback(
        Output("header-state-selector", "value", allow_duplicate=True),
        Input("state-btn-kerala", "n_clicks"),
        Input("state-btn-karnataka", "n_clicks"),
        Input("state-btn-tamil-nadu", "n_clicks"),
        Input("state-btn-andhra-pradesh", "n_clicks"),
        Input("state-btn-maharashtra", "n_clicks"),
        prevent_initial_call=True,
    )
    def handle_state_card_click(n_ker, n_kar, n_tn, n_ap, n_mah):
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        btn_map = {
            "state-btn-kerala": "Kerala",
            "state-btn-karnataka": "Karnataka",
            "state-btn-tamil-nadu": "Tamil Nadu",
            "state-btn-andhra-pradesh": "Andhra Pradesh",
            "state-btn-maharashtra": "Maharashtra",
        }
        clicks = {
            "state-btn-kerala": n_ker,
            "state-btn-karnataka": n_kar,
            "state-btn-tamil-nadu": n_tn,
            "state-btn-andhra-pradesh": n_ap,
            "state-btn-maharashtra": n_mah,
        }
        if not clicks.get(trigger_id):
            return dash.no_update
        return btn_map.get(trigger_id, dash.no_update)

    # ─── 2b. Cascading District Selector (Scoped to Selected State) ───────────
    @app.callback(
        Output("header-district-selector", "options"),
        Output("header-district-selector", "value"),
        Input("header-state-selector", "value"),
        Input("current-lang-store", "data"),
        State("header-district-selector", "value"),
    )
    def cascade_district_selector(selected_state, lang, current_district):
        lang = lang or "en"
        st = selected_state or "ALL"
        valid_states = engine.get_states()
        if st != "ALL" and st not in valid_states:
            st = "ALL"

        districts = engine.get_districts(state=st)
        dist_all_label = f"🌟 {t('all_districts', lang)}" if st == "ALL" else f"🌟 {st} — {t('all_districts', lang)}"
        dist_options = [{"label": dist_all_label, "value": "ALL"}] + [
            {"label": f"📍 {d}", "value": d} for d in districts
        ]
        valid_values = [opt["value"] for opt in dist_options]
        # Strict hierarchy rule: changing State resets District and Panchayat to "ALL"
        from dash import ctx
        if ctx.triggered_id == "header-state-selector":
            new_val = "ALL"
        else:
            new_val = current_district if current_district in valid_values else "ALL"
        return dist_options, new_val

    # ─── 2c. Cascading Panchayat Selector (Scoped to District & State) ────────
    @app.callback(
        Output("header-panchayat-selector", "options"),
        Output("header-panchayat-selector", "value"),
        Input("header-district-selector", "value"),
        Input("header-state-selector", "value"),
        Input("current-lang-store", "data"),
        State("header-panchayat-selector", "value"),
    )
    def cascade_panchayat_selector(selected_district, selected_state, lang, current_panchayat):
        lang = lang or "en"
        st = selected_state or "ALL"
        dist = selected_district or "ALL"

        from dash import ctx
        is_reset_trigger = ctx.triggered_id in ["header-state-selector", "header-district-selector"]

        # Strict hierarchy rule: Panchayat options only loaded after a valid District is selected
        if dist == "ALL":
            panch_options = [{"label": f"🌟 {t('all_panchayats', lang)}", "value": "ALL"}]
            new_val = "ALL"
        else:
            panchayats = engine.get_panchayats(district=dist, state=st)
            panch_options = [{"label": f"🌟 {dist} — {t('all_panchayats', lang)}", "value": "ALL"}] + [
                {"label": f"🏘️ {p} {t('th_panchayat', lang)}", "value": p} for p in panchayats
            ]
            valid_values = [opt["value"] for opt in panch_options]
            if is_reset_trigger:
                new_val = "ALL"
            else:
                new_val = current_panchayat if current_panchayat in valid_values else "ALL"
        return panch_options, new_val

    # ─── 3. Master Global Location Synchronizer (One-Way Store Trigger) ───────
    @app.callback(
        Output("global-location-store", "data"),
        Output("selected-state-store", "data"),
        Output("selected-district-store", "data"),
        Output("selected-panchayat-store", "data"),
        Output("selected-year-store", "data"),
        Input("header-state-selector", "value"),
        Input("header-district-selector", "value"),
        Input("header-panchayat-selector", "value"),
        Input("header-year-selector", "value"),
        State("global-location-store", "data"),
    )
    def sync_master_location_store(st_val, dist_val, panch_val, yr_val, curr_store):
        st = st_val or "ALL"
        dist = dist_val or "ALL"
        panch = panch_val or "ALL"
        yr = yr_val or "2026-27"

        # Validate hierarchy and sanitize combinations
        is_valid, err, meta = engine.validate_hierarchy(state=st, district=dist, panchayat=panch, year=yr)
        if not is_valid:
            if dist != "ALL" and dist not in engine.get_districts(state=st):
                dist = "ALL"
                panch = "ALL"
            if panch != "ALL" and panch not in engine.get_panchayats(district=dist, state=st):
                panch = "ALL"
            meta = engine.get_location_metadata(state=st, district=dist, panchayat=panch, year=yr)

        curr_data = curr_store or {}
        curr_s = curr_data.get("state_name") or curr_data.get("state", "ALL")
        curr_d = curr_data.get("district_name") or curr_data.get("district", "ALL")
        curr_p = curr_data.get("panchayat_name") or curr_data.get("panchayat", "ALL")
        curr_y = curr_data.get("financial_year") or curr_data.get("year", "2026-27")

        # Skip update if location is unchanged to prevent redundant downstream rendering
        if (meta.get("state_name") == curr_s and
            meta.get("district_name") == curr_d and
            meta.get("panchayat_name") == curr_p and
            meta.get("financial_year") == curr_y):
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

        return meta, meta["state_name"], meta["district_name"], meta["panchayat_name"], meta["financial_year"]

    # ─── 5a. URL Search (?lang=...) to Language Selector ───────────────────
    @app.callback(
        Output("header-lang-selector", "value"),
        Input("url", "search"),
        State("header-lang-selector", "value"),
    )
    def sync_url_to_language(search_str, current_val):
        if search_str:
            import urllib.parse
            try:
                qs = urllib.parse.parse_qs(search_str.lstrip("?"))
                if "lang" in qs and qs["lang"]:
                    code = qs["lang"][0].lower()
                    if code in LANGUAGES and code != current_val:
                        return code
            except Exception:
                pass
        return dash.no_update

    # ─── 5b. Language Selector to Store ────────────────────────────────────
    @app.callback(
        Output("current-lang-store", "data"),
        Input("header-lang-selector", "value"),
    )
    def update_language_store(selected_lang):
        return selected_lang or "en"

    # ─── 6. Sidebar Dynamic Context & Nav Labels ───────────────────────────
    @app.callback(
        Output("sidebar-context-label", "children"),
        Output("sidebar-context-sub", "children"),
        Input("global-location-store", "data"),
        Input("current-lang-store", "data"),
    )
    def update_sidebar_context(loc_data, lang):
        lang = lang or "en"
        loc_data = loc_data or {}
        state = loc_data.get("state", "ALL")
        district = loc_data.get("district", "ALL")
        panchayat = loc_data.get("panchayat", "ALL")
        if panchayat and panchayat != "ALL":
            return f"{panchayat} GP", f"{district or state or ''}"
        elif district and district != "ALL":
            return f"{district} {t('th_district', lang)}", f"{state if state != 'ALL' else t('all_states', lang)}"
        elif state and state != "ALL":
            return f"{state} {t('th_state', lang)}", t("all_districts", lang)
        return t("all_panchayats", lang), f"5 {t('th_state', lang)} • 32 {t('th_district', lang)}"

    @app.callback(
        Output("nav-lbl-overview", "children"),
        Output("nav-lbl-vulnerability", "children"),
        Output("nav-lbl-budget", "children"),
        Output("nav-lbl-explanations", "children"),
        Output("nav-lbl-compare", "children"),
        Output("nav-lbl-auth", "children"),
        Input("current-lang-store", "data"),
        Input("current-user-store", "data"),
    )
    def update_sidebar_labels(lang, user):
        lang = lang or "en"
        auth_label = t("my_account", lang) if user else t("nav_login", lang)
        return (
            t("nav_overview", lang),
            t("nav_vulnerability", lang),
            t("nav_budget", lang),
            t("nav_explanations", lang),
            t("nav_compare", lang),
            auth_label,
        )

    # ─── 6. Top Header User Widget ─────────────────────────────────────────
    @app.callback(
        Output("header-user-widget", "children"),
        Input("current-user-store", "data"),
        Input("current-lang-store", "data"),
    )
    def update_user_widget(user, lang):
        lang = lang or "en"
        if user:
            role_name = user.get("role", "Officer").split("/")[0].strip()
            govt_id_str = f" • ID: {user['govt_id']}" if user.get("govt_id") else ""
            return html.Div(
                [
                    html.Span("👤", style={"fontSize": "1.2rem"}),
                    html.Div(
                        [
                            html.Span(user.get("full_name", user.get("username", "User")), className="user-badge-name"),
                            html.Small(f"{role_name} • {user.get('district', 'Kerala')}{govt_id_str}", className="user-badge-role"),
                        ]
                    ),
                    dbc.Button(
                        "Logout",
                        id="btn-logout",
                        size="sm",
                        color="link",
                        className="p-0 ms-2 text-danger",
                        style={"fontSize": "0.75rem", "textDecoration": "none"},
                    ),
                ],
                className="user-badge-container",
            )
        return html.A(
            [html.Span("🔑 "), t("btn_signin", lang)],
            href="/dashboard/auth",
            className="btn-sign-in-top",
        )

    # ─── 7. Page Routing (Optimized Instant Routing with Single Store Trigger & Cache) ─
    @app.callback(
        Output("page-content", "children"),
        Input("url", "pathname"),
        Input("global-location-store", "data"),
        Input("current-lang-store", "data"),
    )
    def display_page(pathname, loc_data, lang):
        lang = lang or "en"
        loc_data = loc_data or {}
        state = loc_data.get("state_name") or loc_data.get("state", "ALL")
        district = loc_data.get("district_name") or loc_data.get("district", "ALL")
        panchayat = loc_data.get("panchayat_name") or loc_data.get("panchayat", "ALL")
        year = loc_data.get("financial_year") or loc_data.get("year", "2026-27")
        state_id = loc_data.get("state_id", "ALL")
        district_id = loc_data.get("district_id", "ALL")
        panchayat_id = loc_data.get("panchayat_id", "ALL")

        clean_path = (pathname or "/dashboard/").rstrip("/").lower()
        if not clean_path.startswith("/dashboard"):
            clean_path = "/dashboard"

        common_kwargs = dict(
            state=state, district=district, panchayat=panchayat, year=year, lang=lang,
            state_id=state_id, district_id=district_id, panchayat_id=panchayat_id
        )

        if clean_path in ["/dashboard", "/dashboard/home", "/dashboard/overview"]:
            return get_cached_layout(
                "overview", create_overview_layout, engine, **common_kwargs
            )
        elif clean_path == "/dashboard/about":
            return get_cached_layout(
                "about", create_about_layout, **common_kwargs
            )
        elif clean_path in ["/dashboard/vulnerability", "/dashboard/panchayat-dashboard"]:
            return get_cached_layout(
                "vulnerability", create_vulnerability_layout, engine, **common_kwargs
            )
        elif clean_path in ["/dashboard/budget", "/dashboard/planning", "/dashboard/budget-allocation", "/dashboard/development-planning"]:
            return get_cached_layout(
                "budget", create_budget_layout, engine, **common_kwargs
            )
        elif clean_path in ["/dashboard/explanations", "/dashboard/ai-insights", "/dashboard/insights"]:
            return get_cached_layout(
                "explanations", create_explanations_layout, engine, **common_kwargs
            )
        elif clean_path in ["/dashboard/compare", "/dashboard/reports", "/dashboard/reporting"]:
            return get_cached_layout(
                "comparison", create_comparison_layout, engine, **common_kwargs
            )
        elif clean_path in ["/dashboard/training", "/dashboard/models", "/dashboard/ml"]:
            return get_cached_layout(
                "training", create_training_layout, engine, **common_kwargs
            )
        elif clean_path in ["/dashboard/auth", "/dashboard/login", "/dashboard/register", "/dashboard/contact"]:
            return get_cached_layout(
                "auth", create_auth_layout,
                lang=lang
            )
        else:
            return get_cached_layout(
                "overview", create_overview_layout, engine, **common_kwargs
            )

    # ─── 8. Auth Tabs Switcher (Clientside 0ms Toggle) ─────────────────────
    app.clientside_callback(
        """
        function(active_tab) {
            if (active_tab === "tab-register") {
                return [{"display": "none"}, {"display": "block"}];
            }
            return [{"display": "block"}, {"display": "none"}];
        }
        """,
        Output("login-container", "style"),
        Output("register-container", "style"),
        Input("auth-tabs", "active_tab"),
        prevent_initial_call=True,
    )

    # ─── 9. Auth Actions (Login, Register, Logout) ─────────────────────────
    @app.callback(
        Output("auth-alert-container", "children"),
        Output("current-user-store", "data"),
        Input("btn-login-submit", "n_clicks"),
        Input("btn-register-submit", "n_clicks"),
        Input("btn-logout", "n_clicks"),
        State("login-username", "value"),
        State("login-password", "value"),
        State("reg-username", "value"),
        State("reg-govtid", "value"),
        State("reg-email", "value"),
        State("reg-password", "value"),
        State("reg-confirm-password", "value"),
        State("reg-fullname", "value"),
        State("reg-role", "value"),
        State("reg-district", "value"),
        State("reg-panchayat", "value"),
        State("current-user-store", "data"),
        State("current-lang-store", "data"),
        prevent_initial_call=True,
    )
    def handle_auth_actions(
        n_login, n_reg, n_logout,
        login_user, login_pass,
        reg_user, reg_govtid, reg_email, reg_pass, reg_confirm,
        reg_fullname, reg_role, reg_dist, reg_panch,
        curr_user, lang,
    ):
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update, dash.no_update

        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # Handle Logout
        if trigger_id == "btn-logout":
            if not n_logout:
                return dash.no_update, dash.no_update
            alert = dbc.Alert("👋 You have been logged out successfully.", color="info", dismissable=True)
            return alert, None

        # Handle Login
        if trigger_id == "btn-login-submit":
            if not n_login:
                return dash.no_update, dash.no_update
            if not login_user or not login_pass:
                alert = dbc.Alert("Please enter both username and password.", color="warning", dismissable=True)
                return alert, curr_user

            success, msg, user_dict = authenticate_user(login_user, login_pass)
            if success:
                alert = dbc.Alert(
                    [
                        html.Span("✅ "),
                        html.B(f"Welcome back, {user_dict['full_name']}! "),
                        html.Span(f"Logged in as {user_dict['role']} ({user_dict['district']}) [ID: {user_dict.get('govt_id', 'N/A')}]."),
                    ],
                    color="success",
                    dismissable=True,
                )
                return alert, user_dict
            else:
                alert = dbc.Alert(f"❌ {msg}", color="danger", dismissable=True)
                return alert, curr_user

        # Handle Register
        if trigger_id == "btn-register-submit":
            if not n_reg:
                return dash.no_update, dash.no_update
            if not reg_user or not reg_email or not reg_pass:
                alert = dbc.Alert("Please fill in all required fields.", color="warning", dismissable=True)
                return alert, curr_user

            if not reg_govtid or len(str(reg_govtid).strip()) < 3:
                alert = dbc.Alert("Please provide a valid Government / Employee ID (e.g. PEN / Aadhaar / KILA ID / Voter ID).", color="warning", dismissable=True)
                return alert, curr_user

            if reg_pass != reg_confirm:
                alert = dbc.Alert("Passwords do not match. Please verify.", color="warning", dismissable=True)
                return alert, curr_user

            success, msg, user_dict = register_user(
                username=reg_user,
                email=reg_email,
                password=reg_pass,
                full_name=reg_fullname or reg_user,
                govt_id=reg_govtid,
                role=reg_role or "Citizen / Researcher",
                district=reg_dist or "Kasaragod",
                panchayat=reg_panch or "Manjeshwar",
            )
            if success:
                alert = dbc.Alert(
                    [
                        html.Span("🎉 "),
                        html.B(f"Account created successfully for {user_dict['full_name']}! "),
                        html.Span(f"Official ID: {user_dict.get('govt_id', 'N/A')} verified. You are now signed in."),
                    ],
                    color="success",
                    dismissable=True,
                )
                return alert, user_dict
            else:
                alert = dbc.Alert(f"❌ {msg}", color="danger", dismissable=True)
                return alert, curr_user

        return dash.no_update, dash.no_update

    # ─── 10. ML Retraining Action ──────────────────────────────────────────
    @app.callback(
        Output("retrain-status-output", "children"),
        Input("btn-trigger-retrain", "n_clicks"),
        prevent_initial_call=True,
    )
    def trigger_retrain(n_clicks):
        if not n_clicks:
            return ""
        try:
            metrics = engine.retrain_models()
            clear_layout_cache()  # Evict cached pre-rendered pages to reflect new metrics
            rf_acc = metrics.get("models", {}).get("random_forest", {}).get("accuracy", 0)
            gb_acc = metrics.get("models", {}).get("gradient_boosting", {}).get("accuracy", 0)
            return dbc.Alert(
                f"✅ Model retrained successfully! RF Accuracy: {rf_acc:.1f}% | GB Accuracy: {gb_acc:.1f}% across 1,208 Kerala wards.",
                color="success",
                dismissable=True,
                className="mt-2 text-start",
            )
        except Exception as e:
            return dbc.Alert(f"❌ Retraining failed: {str(e)}", color="danger", dismissable=True, className="mt-2")

    # ─── 11. Interactive Visualizations ────────────────────────────────────
    @app.callback(
        Output("vulnerability-radar-container", "children"),
        Input("vulnerability-ward-selector", "value"),
        State("global-location-store", "data"),
        Input("current-lang-store", "data"),
        prevent_initial_call=True,
    )
    def update_vulnerability_radar(ward_name, loc_data, lang):
        lang = lang or "en"
        loc_data = loc_data or {}
        state = loc_data.get("state_name") or loc_data.get("state", "ALL")
        district = loc_data.get("district_name") or loc_data.get("district", "ALL")
        panchayat = loc_data.get("panchayat_name") or loc_data.get("panchayat", "ALL")
        
        valid_df = engine.get_filtered_df(state=state, district=district, panchayat=panchayat)
        if valid_df.empty:
            return html.P("No ward data available for the selected jurisdiction.", className="text-muted p-3")

        valid_wards = valid_df["ward_name"].dropna().tolist()
        if not ward_name or ward_name not in valid_wards:
            ward_name = valid_wards[0] if valid_wards else None

        if not ward_name:
            return html.P(t("no_ward_selected", lang))

        return create_radar_chart(engine, ward_name, lang=lang, state=state, district=district, panchayat=panchayat)

    @app.callback(
        Output("budget-charts-container", "children"),
        Input("budget-ward-selector", "value"),
        Input("budget-input", "value"),
        State("global-location-store", "data"),
        Input("current-lang-store", "data"),
        prevent_initial_call=True,
    )
    def update_budget(ward_name, budget_lakhs, loc_data, lang):
        lang = lang or "en"
        loc_data = loc_data or {}
        state = loc_data.get("state_name") or loc_data.get("state", "ALL")
        district = loc_data.get("district_name") or loc_data.get("district", "ALL")
        panchayat = loc_data.get("panchayat_name") or loc_data.get("panchayat", "ALL")
        
        valid_df = engine.get_filtered_df(state=state, district=district, panchayat=panchayat)
        if valid_df.empty:
            return html.P("No planning data available for the selected jurisdiction.", className="text-muted p-3")

        valid_wards = valid_df["ward_name"].dropna().tolist()
        if not ward_name or ward_name not in valid_wards:
            ward_name = valid_wards[0] if valid_wards else None

        if not ward_name:
            return html.P(t("no_ward_selected", lang))

        if budget_lakhs is None or budget_lakhs < 1:
            budget_lakhs = 50
        return create_budget_charts(engine, ward_name, budget_lakhs, lang=lang, state=state, district=district, panchayat=panchayat)

    @app.callback(
        Output("explanation-content-container", "children"),
        Input("explain-ward-selector", "value"),
        State("global-location-store", "data"),
        Input("current-lang-store", "data"),
        prevent_initial_call=True,
    )
    def update_explanation(ward_name, loc_data, lang):
        lang = lang or "en"
        loc_data = loc_data or {}
        state = loc_data.get("state_name") or loc_data.get("state", "ALL")
        district = loc_data.get("district_name") or loc_data.get("district", "ALL")
        panchayat = loc_data.get("panchayat_name") or loc_data.get("panchayat", "ALL")
        
        valid_df = engine.get_filtered_df(state=state, district=district, panchayat=panchayat)
        if valid_df.empty:
            return html.P("No AI insights available for the selected jurisdiction.", className="text-muted p-3")

        valid_wards = valid_df["ward_name"].dropna().tolist()
        if not ward_name or ward_name not in valid_wards:
            ward_name = valid_wards[0] if valid_wards else None

        if not ward_name:
            return html.P(t("no_ward_selected", lang))

        return create_ward_explanation(engine, ward_name, lang=lang, state=state, district=district, panchayat=panchayat)

    @app.callback(
        Output("comparison-content-container", "children"),
        Input("compare-ward-a", "value"),
        Input("compare-ward-b", "value"),
        Input("global-location-store", "data"),
        Input("current-lang-store", "data"),
        prevent_initial_call=True,
    )
    def update_comparison(ward_a, ward_b, loc_data, lang):
        lang = lang or "en"
        loc_data = loc_data or {}
        state = loc_data.get("state_name") or loc_data.get("state", "ALL")
        district = loc_data.get("district_name") or loc_data.get("district", "ALL")
        panchayat = loc_data.get("panchayat_name") or loc_data.get("panchayat", "ALL")
        year = loc_data.get("financial_year") or loc_data.get("year", "2026-27")
        
        valid_df = engine.get_filtered_df(state=state, district=district, panchayat=panchayat)
        if valid_df.empty:
            return html.P("No comparative report available for the selected jurisdiction.", className="text-muted p-3")

        valid_wards = valid_df["ward_name"].dropna().tolist()
        if not ward_a or ward_a not in valid_wards:
            ward_a = valid_wards[0] if valid_wards else None
        if not ward_b or ward_b not in valid_wards:
            ward_b = valid_wards[1] if len(valid_wards) > 1 else ward_a

        if not ward_a or not ward_b:
            return html.P(t("select_two_wards", lang))
        if ward_a == ward_b and len(valid_wards) > 1:
            ward_b = valid_wards[1]
        return create_comparison_content(engine, ward_a, ward_b, lang=lang, state=state, district=district, panchayat=panchayat, year=year)

    # ─── 11b. Export Official Governance & Disparity Report CSV ───
    @app.callback(
        Output("download-comparison-csv", "data"),
        Input("btn-export-csv", "n_clicks"),
        State("compare-ward-a", "value"),
        State("compare-ward-b", "value"),
        State("report-type-selector", "value"),
        State("global-location-store", "data"),
        prevent_initial_call=True,
    )
    def export_comparison_csv(n_clicks, ward_a, ward_b, report_type, loc_data):
        if not n_clicks:
            raise dash.exceptions.PreventUpdate

        loc_data = loc_data or {}
        state = loc_data.get("state_name") or loc_data.get("state", "ALL")
        district = loc_data.get("district_name") or loc_data.get("district", "ALL")
        panchayat = loc_data.get("panchayat_name") or loc_data.get("panchayat", "ALL")
        year = loc_data.get("financial_year") or loc_data.get("year", "2026-27")

        df_scope = engine.get_filtered_df(state=state, district=district, panchayat=panchayat)
        df = df_scope if (df_scope is not None and not df_scope.empty) else engine.df_processed

        if report_type in ["STATE_REPORT", "DISTRICT_REPORT", "PANCHAYAT_REPORT"]:
            export_cols = [
                c for c in [
                    "ward_id", "state", "district", "panchayat_name", "ward_number", "ward_name",
                    "population", "vulnerability_index", "vulnerability_category",
                    "priority_sector_1", "priority_sector_2", "priority_sector_3",
                    "taluk", "assembly_constituency", "mla_name", "mla_party"
                ] if c in df.columns
            ]
            score_cols = [c for c in df.columns if c.startswith("score_")]
            export_cols.extend(score_cols)
            df_export = df[export_cols].copy()
            clean_name = f"{panchayat if panchayat != 'ALL' else (district if district != 'ALL' else state)}"
            filename = f"governance_report_{clean_name}_{year}.csv"
        elif report_type == "BUDGET_REPORT":
            score_cols = [c for c in df.columns if c.startswith("score_")]
            raw_labels = [c.replace("score_", "").replace("_", " ").title() for c in score_cols]
            mean_scores = [float(df[c].mean()) if c in df.columns else 0.0 for c in score_cols]
            total_score = sum(mean_scores) if sum(mean_scores) > 0 else 1.0
            total_budget = 5000000.0  # ₹50 Lakhs baseline
            allocations = [(s / total_score) * total_budget for s in mean_scores]

            df_export = pd.DataFrame({
                "Sector_No": list(range(1, len(raw_labels) + 1)),
                "Development_Sector": raw_labels,
                "Average_Vulnerability_Score": [round(s, 4) for s in mean_scores],
                "LP_Optimal_Allocation_Percentage": [f"{(s / total_score) * 100:.2f}%" for s in mean_scores],
                "Recommended_Budget_INR": [round(a, 2) for a in allocations],
                "Planning_Cycle": [f"FY {year}"] * len(raw_labels),
                "Administrative_Jurisdiction": [f"{panchayat} GP, {district}, {state}"] * len(raw_labels),
            })
            clean_name = f"{panchayat if panchayat != 'ALL' else (district if district != 'ALL' else state)}"
            filename = f"budget_allocation_report_{clean_name}_{year}.csv"
        elif report_type == "AI_REPORT":
            export_cols = [
                c for c in [
                    "ward_id", "state", "district", "panchayat_name", "ward_name", "population",
                    "vulnerability_index", "vulnerability_category",
                    "priority_sector_1", "priority_sector_2", "priority_sector_3",
                    "ml_predicted_priority", "ml_confidence_score"
                ] if c in df.columns
            ]
            df_export = df[export_cols].copy() if export_cols else df.copy()
            clean_name = f"{panchayat if panchayat != 'ALL' else (district if district != 'ALL' else state)}"
            filename = f"ai_recommendations_report_{clean_name}_{year}.csv"
        else:
            # Default: DISPARITY_BENCHMARK between Ward A and Ward B
            row_a = df[df["ward_name"].astype(str).str.strip().str.lower() == str(ward_a).strip().lower()]
            row_b = df[df["ward_name"].astype(str).str.strip().str.lower() == str(ward_b).strip().lower()]

            if row_a.empty:
                row_a = df.iloc[0:1]
            if row_b.empty:
                row_b = df.iloc[1:2] if len(df) > 1 else row_a

            actual_ward_a = row_a["ward_name"].values[0] if "ward_name" in row_a.columns else str(ward_a)
            actual_ward_b = row_b["ward_name"].values[0] if "ward_name" in row_b.columns else str(ward_b)

            score_cols = [c for c in df.columns if c.startswith("score_")]
            raw_labels = [c.replace("score_", "").replace("_", " ").title() for c in score_cols]
            vals_a = row_a[score_cols].values[0].tolist() if not row_a.empty else [0.0] * len(score_cols)
            vals_b = row_b[score_cols].values[0].tolist() if not row_b.empty else [0.0] * len(score_cols)

            disparity_rows = []
            for idx, (raw_label, va, vb) in enumerate(zip(raw_labels, vals_a, vals_b), 1):
                diff = va - vb
                if diff > 0.05:
                    status = "CRITICAL DEFICIT (WARD A)"
                    directive = f"Priority capital transfer to {actual_ward_a} under SFC Untied Grants"
                elif diff < -0.05:
                    status = "CRITICAL DEFICIT (WARD B)"
                    directive = f"Priority capital transfer to {actual_ward_b} under SFC Untied Grants"
                else:
                    status = "COMPARABLE PARITY"
                    directive = "Maintain routine operational maintenance expenditure"

                disparity_rows.append({
                    "Sector_No": idx,
                    "Development_Sector": raw_label,
                    f"Score_{actual_ward_a}": round(va, 4),
                    f"Score_{actual_ward_b}": round(vb, 4),
                    "Net_Variance_A_minus_B": round(diff, 4),
                    "Allocation_Status": status,
                    "Statutory_Planning_Directive": directive,
                    "State": row_a["state"].values[0] if "state" in row_a.columns else state,
                    "District": row_a["district"].values[0] if "district" in row_a.columns else district,
                    "Grama_Panchayat": row_a["panchayat_name"].values[0] if "panchayat_name" in row_a.columns else panchayat,
                    "Financial_Year": f"FY {year}",
                })

            df_export = pd.DataFrame(disparity_rows)
            filename = f"disparity_benchmark_{actual_ward_a}_vs_{actual_ward_b}_{year}.csv"

        filename = filename.replace(" ", "_").replace("/", "_").replace("\\", "_")
        return dcc.send_data_frame(df_export.to_csv, filename=filename, index=False)

    # ─── 11c. Synchronize Ward Selectors Across Modules on Location Change ─
    @app.callback(
        Output("compare-ward-a", "options"),
        Output("compare-ward-a", "value"),
        Output("compare-ward-b", "options"),
        Output("compare-ward-b", "value"),
        Input("global-location-store", "data"),
        prevent_initial_call=True,
    )
    def sync_comparison_dropdowns(loc_data):
        loc_data = loc_data or {}
        state = loc_data.get("state_name") or loc_data.get("state", "ALL")
        district = loc_data.get("district_name") or loc_data.get("district", "ALL")
        panchayat = loc_data.get("panchayat_name") or loc_data.get("panchayat", "ALL")
        df = engine.get_filtered_df(state=state, district=district, panchayat=panchayat)
        if df is None or df.empty:
            df = engine.df_processed
        valid_wards = sorted(df["ward_name"].dropna().unique().tolist())
        opts_a = [{"label": f"Ward A: {w}", "value": w} for w in valid_wards]
        opts_b = [{"label": f"Ward B: {w}", "value": w} for w in valid_wards]
        val_a = valid_wards[0] if valid_wards else None
        val_b = valid_wards[1] if len(valid_wards) > 1 else val_a
        return opts_a, val_a, opts_b, val_b

    @app.callback(
        Output("vulnerability-ward-selector", "options"),
        Output("vulnerability-ward-selector", "value"),
        Input("global-location-store", "data"),
        prevent_initial_call=True,
    )
    def sync_vulnerability_dropdown(loc_data):
        loc_data = loc_data or {}
        state = loc_data.get("state_name") or loc_data.get("state", "ALL")
        district = loc_data.get("district_name") or loc_data.get("district", "ALL")
        panchayat = loc_data.get("panchayat_name") or loc_data.get("panchayat", "ALL")
        df = engine.get_filtered_df(state=state, district=district, panchayat=panchayat)
        if df is None or df.empty:
            df = engine.df_processed
        valid_wards = sorted(df["ward_name"].dropna().unique().tolist())
        opts = [{"label": w, "value": w} for w in valid_wards]
        val = valid_wards[0] if valid_wards else None
        return opts, val

    @app.callback(
        Output("budget-ward-selector", "options"),
        Output("budget-ward-selector", "value"),
        Input("global-location-store", "data"),
        prevent_initial_call=True,
    )
    def sync_budget_dropdown(loc_data):
        loc_data = loc_data or {}
        state = loc_data.get("state_name") or loc_data.get("state", "ALL")
        district = loc_data.get("district_name") or loc_data.get("district", "ALL")
        panchayat = loc_data.get("panchayat_name") or loc_data.get("panchayat", "ALL")
        df = engine.get_filtered_df(state=state, district=district, panchayat=panchayat)
        if df is None or df.empty:
            df = engine.df_processed
        valid_wards = sorted(df["ward_name"].dropna().unique().tolist())
        opts = [{"label": w, "value": w} for w in valid_wards]
        val = valid_wards[0] if valid_wards else None
        return opts, val

    @app.callback(
        Output("explain-ward-selector", "options"),
        Output("explain-ward-selector", "value"),
        Input("global-location-store", "data"),
        prevent_initial_call=True,
    )
    def sync_explain_dropdown(loc_data):
        loc_data = loc_data or {}
        state = loc_data.get("state_name") or loc_data.get("state", "ALL")
        district = loc_data.get("district_name") or loc_data.get("district", "ALL")
        panchayat = loc_data.get("panchayat_name") or loc_data.get("panchayat", "ALL")
        df = engine.get_filtered_df(state=state, district=district, panchayat=panchayat)
        if df is None or df.empty:
            df = engine.df_processed
        valid_wards = sorted(df["ward_name"].dropna().unique().tolist())
        opts = [{"label": w, "value": w} for w in valid_wards]
        val = valid_wards[0] if valid_wards else None
        return opts, val

    # ─── 12. Active Navigation Pill Link Highlight (Clientside 0ms Toggle) 
    app.clientside_callback(
        """
        function(pathname) {
            var p = (pathname || "/dashboard/").replace(/\\/+$/, "").toLowerCase();
            if (!p.startsWith("/dashboard")) {
                p = "/dashboard";
            }
            var home = (p === "/dashboard" || p === "/dashboard/home" || p === "/dashboard/overview") ? "nav-pill-link active" : "nav-pill-link";
            var about = (p === "/dashboard/about") ? "nav-pill-link active" : "nav-pill-link";
            var dash = (p === "/dashboard/vulnerability" || p === "/dashboard/panchayat-dashboard") ? "nav-pill-link active" : "nav-pill-link";
            var plan = (p === "/dashboard/budget" || p === "/dashboard/planning" || p === "/dashboard/budget-allocation" || p === "/dashboard/development-planning") ? "nav-pill-link active" : "nav-pill-link";
            var ins = (p === "/dashboard/explanations" || p === "/dashboard/ai-insights" || p === "/dashboard/insights") ? "nav-pill-link active" : "nav-pill-link";
            var rep = (p === "/dashboard/compare" || p === "/dashboard/reports" || p === "/dashboard/reporting") ? "nav-pill-link active" : "nav-pill-link";
            var cnt = (p === "/dashboard/auth" || p === "/dashboard/login" || p === "/dashboard/register" || p === "/dashboard/contact") ? "nav-pill-link active" : "nav-pill-link";
            return [home, about, dash, plan, ins, rep, cnt];
        }
        """,
        Output("pill-nav-home", "className"),
        Output("pill-nav-about", "className"),
        Output("pill-nav-dashboard", "className"),
        Output("pill-nav-planning", "className"),
        Output("pill-nav-insights", "className"),
        Output("pill-nav-reports", "className"),
        Output("pill-nav-contact", "className"),
        Input("url", "pathname"),
    )

    # ─── 13. Subbar Scope & Location Breadcrumb Synchronization ───────────
    @app.callback(
        Output("subbar-scope-text", "children"),
        Output("subbar-fy-text", "children"),
        Input("global-location-store", "data"),
        Input("current-lang-store", "data"),
    )
    def update_subbar_scope_text(loc_data, lang):
        loc_data = loc_data or {}
        state = loc_data.get("state_name") or loc_data.get("state", "ALL")
        district = loc_data.get("district_name") or loc_data.get("district", "ALL")
        panchayat = loc_data.get("panchayat_name") or loc_data.get("panchayat", "ALL")
        year = loc_data.get("financial_year") or loc_data.get("year", "2026-27")
        fy_text = f" | FY {year}"
        df = engine.get_filtered_df(state=state, district=district, panchayat=panchayat)
        num_wards = len(df)
        total_pop = int(df["population"].sum()) if (df is not None and "population" in df.columns and len(df) > 0) else 0
        gov = engine.get_panchayat_governance(state=state, district=district, panchayat=panchayat)

        if panchayat and panchayat != "ALL":
            return f"🇮🇳 {state} • {district} • {panchayat} GP ({num_wards} Wards • {total_pop:,} Pop)", fy_text
        elif district and district != "ALL":
            return f"🇮🇳 {state} • {district} District ({num_wards:,} Wards • {total_pop:,} Pop)", fy_text
        elif state and state != "ALL":
            return f"🇮🇳 {state} Statewide ({num_wards:,} Wards • {total_pop:,} Pop)", fy_text
        return f"🇮🇳 National Coverage (5 States • {num_wards:,} Wards)", fy_text

    # ─── 14. Data Provenance & Traceability Modal Controller (Clientside 0ms) ─
    app.clientside_callback(
        """
        function(n_open, n_close, is_open) {
            return !is_open;
        }
        """,
        Output("provenance-modal", "is_open"),
        Input("btn-provenance-open", "n_clicks"),
        Input("btn-close-provenance-modal", "n_clicks"),
        State("provenance-modal", "is_open"),
        prevent_initial_call=True,
    )



