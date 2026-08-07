"""
my_reports.py
My Reports section — rendered inline by app.py's sidebar router.

Shows the logged-in citizen every incident *they personally* submitted,
with status/category filters and a quick per-status count summary. Admins
see this page too (it just filters to their own username, same as anyone).
"""

import os
import streamlit as st
import database as db
import style
from i18n import t

STATUS_EMOJI = {"Pending": "🔴", "In Progress": "🟡", "Resolved": "🟢"}


def render():
    user = st.session_state.user

    style.hero(
        t("my_reports_hero_title"),
        t("my_reports_hero_subtitle"),
        eyebrow=t("eyebrow_your_activity"),
    )

    my_df = db.get_incidents(username=user["username"])

    if my_df.empty:
        st.info(t("no_reports_yet"))
        return

    # ---- Quick summary of the citizen's own reports ----
    total = len(my_df)
    pending = len(my_df[my_df["status"] == "Pending"])
    in_progress = len(my_df[my_df["status"] == "In Progress"])
    resolved = len(my_df[my_df["status"] == "Resolved"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", total)
    c2.metric("🔴 Pending", pending)
    c3.metric("🟡 In Progress", in_progress)
    c4.metric("🟢 Resolved", resolved)

    st.write("")
    st.divider()

    fcol1, fcol2 = st.columns(2)
    with fcol1:
        status_filter = st.selectbox(t("filter_status"), ["All", "Pending", "In Progress", "Resolved"])
    with fcol2:
        categories = ["All"] + sorted(my_df["category"].unique().tolist())
        category_filter = st.selectbox(t("filter_category"), categories)

    df = db.get_incidents(status=status_filter, category=category_filter, username=user["username"])

    if df.empty:
        st.info(t("no_match_filters"))
        return

    for _, row in df.iterrows():
        st.markdown(style.render_incident_card(row), unsafe_allow_html=True)
        image_field = row.get("image_name")
        if image_field:
            for image_path in str(image_field).split(","):
                image_path = image_path.strip()
                if image_path and os.path.exists(image_path):
                    st.image(image_path, caption="Attached photo", width=320)
