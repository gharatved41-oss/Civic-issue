"""
auth.py
Session-state based authentication helpers for the Streamlit app.
"""

import streamlit as st
import database as db


def init_session():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user" not in st.session_state:
        st.session_state.user = None


def login(username, password):
    user = db.verify_user(username, password)
    if user:
        st.session_state.logged_in = True
        st.session_state.user = user
        return True
    return False


def logout():
    st.session_state.logged_in = False
    st.session_state.user = None


def is_logged_in():
    return st.session_state.get("logged_in", False)


def is_admin():
    user = st.session_state.get("user")
    return bool(user and user["role"] == "admin")


def require_login():
    """Call at the top of protected pages. Stops rendering if not logged in."""
    init_session()
    if not is_logged_in():
        st.warning("Please log in from the main page to access this feature.")
        st.stop()


def require_admin():
    require_login()
    if not is_admin():
        st.error("This page is restricted to administrators only.")
        st.stop()
