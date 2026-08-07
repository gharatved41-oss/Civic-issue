"""
app.py
Civic Sense AI — single entry point.

This app is intentionally FLAT (no pages/ or .streamlit/ directories).
Navigation between sections is handled manually via a sidebar radio +
imported render() functions, instead of Streamlit's folder-based
multipage system.

Run with:
    streamlit run app.py
"""

import streamlit as st
import database as db
import auth
import style
import i18n
from i18n import t
import report_incident
import incident_map
import my_reports
import admin_dashboard
import assistant_page

st.set_page_config(
    page_title="Civic Sense AI",
    page_icon="🏙️",
    layout="wide",
)

db.init_db()
auth.init_session()
i18n.init_language()
style.inject_css()

# ---------------------------------------------------------------------------
# Internal navigation IDs are deliberately kept in plain English — they're
# used as session_state values / dict keys, never shown to the user directly.
# Their on-screen label is looked up via i18n.t() at render time, so the menu
# updates immediately when the citizen switches language.
# ---------------------------------------------------------------------------
NAV_HOME = "home"
NAV_REPORT = "report"
NAV_MAP = "map"
NAV_MY_REPORTS = "my_reports"
NAV_ASSISTANT = "assistant"
NAV_ADMIN = "admin"

NAV_LABEL_KEYS = {
    NAV_HOME: "nav_home",
    NAV_REPORT: "nav_report",
    NAV_MAP: "nav_map",
    NAV_MY_REPORTS: "nav_my_reports",
    NAV_ASSISTANT: "nav_assistant",
    NAV_ADMIN: "nav_admin",
}


def nav_label(nav_id):
    return t(NAV_LABEL_KEYS.get(nav_id, nav_id))


# IMPORTANT: "current_page" is a plain session_state variable, deliberately
# NOT tied to any widget's `key`. The sidebar radio below uses a *different*
# key ("nav_radio_widget"). Keeping these separate avoids Streamlit's
# restriction on writing to a widget's own state key, so buttons elsewhere
# in the app can freely redirect navigation without conflicting with the
# radio widget.
if "current_page" not in st.session_state:
    st.session_state.current_page = NAV_HOME


def go_to(section):
    """Safe to call from a button's on_click — updates plain state, not a widget key.
    Also syncs the sidebar radio's own key: once a keyed widget has a stored
    value, Streamlit ignores any `index` passed on later runs, so without this
    the radio would silently snap back to its last manually-selected value."""
    st.session_state.current_page = section
    st.session_state.nav_radio_widget = section


def home_view():
    user = st.session_state.user
    role_label = t("role_admin") if user["role"] == "admin" else t("role_citizen")
    style.hero(
        t("hero_title"),
        t("home_welcome", name=user["username"], role=role_label),
        eyebrow=t("eyebrow_community"),
    )

    st.markdown(t("home_what_todo"))
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f'<div class="cs-feature-card"><span class="cs-icon">📝</span>'
            f'<h4>{t("card_report_title")}</h4><p>{t("card_report_desc")}</p></div>',
            unsafe_allow_html=True,
        )
        st.button(t("btn_open_report"), use_container_width=True,
                  key="btn_open_report", on_click=go_to, args=(NAV_REPORT,))
        st.write("")
        st.markdown(
            f'<div class="cs-feature-card"><span class="cs-icon">🗺️</span>'
            f'<h4>{t("card_map_title")}</h4><p>{t("card_map_desc")}</p></div>',
            unsafe_allow_html=True,
        )
        st.button(t("btn_open_map"), use_container_width=True,
                  key="btn_open_map", on_click=go_to, args=(NAV_MAP,))
        st.write("")
        st.markdown(
            f'<div class="cs-feature-card"><span class="cs-icon">📄</span>'
            f'<h4>{t("card_my_reports_title")}</h4><p>{t("card_my_reports_desc")}</p></div>',
            unsafe_allow_html=True,
        )
        st.button(t("btn_open_my_reports"), use_container_width=True,
                  key="btn_open_my_reports", on_click=go_to, args=(NAV_MY_REPORTS,))
    with col2:
        st.markdown(
            f'<div class="cs-feature-card"><span class="cs-icon">🤖</span>'
            f'<h4>{t("card_assistant_title")}</h4><p>{t("card_assistant_desc")}</p></div>',
            unsafe_allow_html=True,
        )
        st.button(t("btn_open_assistant"), use_container_width=True,
                  key="btn_open_assistant", on_click=go_to, args=(NAV_ASSISTANT,))
        if user["role"] == "admin":
            st.write("")
            st.markdown(
                f'<div class="cs-feature-card"><span class="cs-icon">📊</span>'
                f'<h4>{t("card_admin_title")}</h4><p>{t("card_admin_desc")}</p></div>',
                unsafe_allow_html=True,
            )
            st.button(t("btn_open_admin"), use_container_width=True,
                      key="btn_open_admin", on_click=go_to, args=(NAV_ADMIN,))


def login_register_view():
    # Citizens can pick their language before they've even logged in.
    lang_col, _ = st.columns([1, 3])
    with lang_col:
        i18n.language_selector(key="lang_code_logged_out")

    style.hero(
        t("hero_title"),
        t("hero_subtitle_logged_out"),
        eyebrow=t("eyebrow_community"),
    )

    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        st.markdown(
            f'<div class="cs-feature-card"><span class="cs-icon">📝</span>'
            f'<h4>{t("feat_report_title")}</h4><p>{t("feat_report_desc")}</p></div>',
            unsafe_allow_html=True,
        )
    with fcol2:
        st.markdown(
            f'<div class="cs-feature-card"><span class="cs-icon">🗺️</span>'
            f'<h4>{t("feat_track_title")}</h4><p>{t("feat_track_desc")}</p></div>',
            unsafe_allow_html=True,
        )
    with fcol3:
        st.markdown(
            f'<div class="cs-feature-card"><span class="cs-icon">🤖</span>'
            f'<h4>{t("feat_help_title")}</h4><p>{t("feat_help_desc")}</p></div>',
            unsafe_allow_html=True,
        )

    st.write("")
    tab_login, tab_register = st.tabs([t("tab_login"), t("tab_register")])

    with tab_login:
        with st.form("login_form"):
            username = st.text_input(t("username"))
            password = st.text_input(t("password"), type="password")
            submitted = st.form_submit_button(t("login_btn"), use_container_width=True)
            if submitted:
                if auth.login(username, password):
                    st.rerun()
                else:
                    st.error(t("login_error"))

    with tab_register:
        with st.form("register_form"):
            new_username = st.text_input(t("choose_username"))
            new_email = st.text_input(t("email"))
            new_password = st.text_input(t("choose_password"), type="password")
            confirm_password = st.text_input(t("confirm_password"), type="password")
            submitted = st.form_submit_button(t("create_account"), use_container_width=True)
            if submitted:
                if not new_username or not new_password:
                    st.error(t("register_required"))
                elif new_password != confirm_password:
                    st.error(t("register_mismatch"))
                else:
                    ok, msg = db.create_user(new_username, new_password, new_email, role="citizen")
                    if ok:
                        st.success(msg + t("register_success_suffix"))
                    else:
                        st.error(msg)


def do_logout():
    auth.logout()
    st.session_state.current_page = NAV_HOME
    st.session_state.nav_radio_widget = NAV_HOME


def sidebar_nav():
    user = st.session_state.user
    with st.sidebar:
        st.markdown(
            f'<div style="padding:8px 0 18px 0;">'
            f'<div style="font-family:\'Space Grotesk\',sans-serif;font-size:1.3rem;font-weight:700;">🏙️ Civic Sense AI</div>'
            f'<div style="color:#9FB4C4;font-size:0.85rem;">{user["username"]} · {user["role"].capitalize()}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        options = [NAV_HOME, NAV_REPORT, NAV_MAP, NAV_MY_REPORTS, NAV_ASSISTANT]
        if user["role"] == "admin":
            options.append(NAV_ADMIN)

        current = st.session_state.current_page
        if current not in options:
            current = NAV_HOME
            st.session_state.current_page = NAV_HOME
        default_index = options.index(current)

        # Deliberately a DIFFERENT key from "current_page" — see note above.
        selected = st.radio(
            "Navigate", options, index=default_index,
            key="nav_radio_widget", label_visibility="collapsed",
            format_func=nav_label,
        )
        if selected != st.session_state.current_page:
            st.session_state.current_page = selected

        st.divider()
        # Citizens can change their language from any page, at any time.
        i18n.language_selector(key="lang_code_sidebar")
        st.divider()
        st.button(t("logout"), use_container_width=True, on_click=do_logout)

    return st.session_state.current_page


def render_page(current):
    """Render the selected section, catching errors so a broken section
    shows a clear message instead of an empty/blank page."""
    try:
        if current == NAV_HOME:
            home_view()
        elif current == NAV_REPORT:
            report_incident.render()
        elif current == NAV_MAP:
            incident_map.render()
        elif current == NAV_MY_REPORTS:
            my_reports.render()
        elif current == NAV_ASSISTANT:
            assistant_page.render()
        elif current == NAV_ADMIN:
            admin_dashboard.render()
    except Exception as e:
        st.error(f"⚠️ Something went wrong while loading this section: {e}")
        st.exception(e)


# ---------------- ROUTER ----------------
if not auth.is_logged_in():
    login_register_view()
else:
    current_section = sidebar_nav()
    render_page(current_section)