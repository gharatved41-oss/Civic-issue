"""
admin_dashboard.py
Admin Dashboard section — rendered inline by app.py's sidebar router.
Only reachable via the nav when the logged-in user's role is 'admin';
includes a defensive check here too.
"""

import os
import streamlit as st
import pandas as pd
import database as db
import style
from i18n import t

STATUS_EMOJI = {"Pending": "🔴", "In Progress": "🟡", "Resolved": "🟢"}


def render():
    user = st.session_state.user
    if user["role"] != "admin":
        st.error("This section is restricted to administrators only.")
        return

    style.hero(t("admin_hero_title"),
               t("admin_hero_subtitle"),
               eyebrow=t("role_admin"))

    stats, full_df = db.get_stats()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Incidents", stats["total"])
    c2.metric("🔴 Pending", stats["pending"])
    c3.metric("🟡 In Progress", stats["in_progress"])
    c4.metric("🟢 Resolved", stats["resolved"])

    st.write("")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### By Category")
        if stats["by_category"]:
            cat_df = pd.DataFrame(list(stats["by_category"].items()), columns=["Category", "Count"]).set_index("Category")
            st.bar_chart(cat_df, color=style.TEAL)
        else:
            st.caption("No data yet.")

    with col2:
        st.markdown("##### By Priority")
        if stats["by_priority"]:
            pr_df = pd.DataFrame(list(stats["by_priority"].items()), columns=["Priority", "Count"]).set_index("Priority")
            st.bar_chart(pr_df, color=style.AMBER)
        else:
            st.caption("No data yet.")

    st.divider()
    st.markdown("#### 🛠️ Manage Incidents")

    fcol1, fcol2 = st.columns(2)
    with fcol1:
        status_filter = st.selectbox("Filter by status", ["All", "Pending", "In Progress", "Resolved"])
    with fcol2:
        categories = ["All"] + sorted(full_df["category"].unique().tolist()) if not full_df.empty else ["All"]
        category_filter = st.selectbox("Filter by category", categories)

    df = db.get_incidents(status=status_filter, category=category_filter)

    if df.empty:
        st.info("No incidents match the selected filters.")
        return

    for _, row in df.iterrows():
        label = f"{STATUS_EMOJI.get(row['status'], '⚪')}  #{row['id']} · {row['category']} · {row['priority']} priority · {row['status']}"
        with st.expander(label):
            st.markdown(
                f"{style.category_badge(row['category'])}{style.priority_badge(row['priority'])}{style.status_badge(row['status'])}",
                unsafe_allow_html=True,
            )
            st.write("")
            st.write(f"**Reported by:** {row['username']}")
            st.write(f"**Location:** {row['location_text']}  (lat: {row['lat']}, lon: {row['lon']})")
            st.write(f"**Description:** {row['description']}")
            st.write(f"**Reported at:** {row['created_at']}")

            image_field = row.get("image_name")
            if image_field:
                for image_path in str(image_field).split(","):
                    image_path = image_path.strip()
                    if image_path and os.path.exists(image_path):
                        st.image(image_path, caption="Attached photo", width=320)

            colA, colB, colC = st.columns([2, 1, 1])
            with colA:
                new_status = st.selectbox(
                    "Update status",
                    ["Pending", "In Progress", "Resolved"],
                    index=["Pending", "In Progress", "Resolved"].index(row["status"]),
                    key=f"status_{row['id']}",
                )
            with colB:
                st.write("")
                st.write("")
                if st.button("💾 Save", key=f"save_{row['id']}", use_container_width=True):
                    db.update_incident_status(row["id"], new_status)
                    st.success("Status updated.")
                    st.rerun()
            with colC:
                st.write("")
                st.write("")
                if st.button("🗑️ Delete", key=f"delete_{row['id']}", use_container_width=True):
                    db.delete_incident(row["id"])
                    st.warning("Incident deleted.")
                    st.rerun()
