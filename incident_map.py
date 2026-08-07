"""
incident_map.py
Incident Map section — rendered inline by app.py's sidebar router.
"""

import streamlit as st
import database as db
import style
from i18n import t

try:
    import folium
    from streamlit_folium import st_folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

# Public, key-free satellite tile source (Esri World Imagery). Passed to
# folium.TileLayer directly (with its required attribution) rather than
# relying on pydeck's TileLayer, which needs a Mapbox-backed WebGL context
# and fails silently in the browser with no key configured.
SATELLITE_TILE_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
SATELLITE_ATTRIBUTION = "Tiles &copy; Esri — Source: Esri, Maxar, Earthstar Geographics"

STATUS_HEX = {
    "Pending": "#E4572E",
    "In Progress": "#F2A93B",
    "Resolved": "#2E9E64",
}


def render():
    style.hero(t("map_hero_title"),
               t("map_hero_subtitle"),
               eyebrow=t("eyebrow_live_overview"))

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        status_filter = st.selectbox(t("filter_status"), ["All", "Pending", "In Progress", "Resolved"])
    with col2:
        all_incidents_df = db.get_incidents()
        categories = ["All"] + sorted(all_incidents_df["category"].unique().tolist()) if not all_incidents_df.empty else ["All"]
        category_filter = st.selectbox(t("filter_category"), categories)
    with col3:
        view_mode = st.radio(
            t("map_view_toggle"),
            [t("map_view_street"), t("map_view_satellite")],
            horizontal=True,
        )
        satellite_on = view_mode == t("map_view_satellite")

    df = db.get_incidents(status=status_filter, category=category_filter)
    df = df.dropna(subset=["lat", "lon"])

    if df.empty:
        st.info(t("no_incidents_filters"))
        return

    if satellite_on:
        _render_satellite_map(df)
    else:
        _render_street_map(df)

    st.markdown(
        f"""
        <div style="margin: 4px 0 18px 0;">
            <span class="cs-legend-item"><span class="cs-dot" style="background:{style.CORAL};"></span>Pending</span>
            <span class="cs-legend-item"><span class="cs-dot" style="background:{style.AMBER};"></span>In Progress</span>
            <span class="cs-legend-item"><span class="cs-dot" style="background:{style.GREEN};"></span>Resolved</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()
    st.markdown(t("incident_list"))
    for _, row in df.iterrows():
        st.markdown(style.render_incident_card(row), unsafe_allow_html=True)


def _render_street_map(df):
    """Default colored-scatter view over the standard basemap (unchanged from before)."""
    STATUS_COLORS_RGB = {
        "Pending": [228, 87, 46],
        "In Progress": [242, 169, 59],
        "Resolved": [46, 158, 100],
    }
    map_df = df.copy()
    map_df["color"] = map_df["status"].map(STATUS_COLORS_RGB)

    try:
        import pydeck as pdk

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position="[lon, lat]",
            get_fill_color="color",
            get_radius=120,
            get_line_color=[255, 255, 255],
            line_width_min_pixels=2,
            stroked=True,
            pickable=True,
        )
        view_state = pdk.ViewState(
            latitude=map_df["lat"].mean(),
            longitude=map_df["lon"].mean(),
            zoom=11,
        )
        tooltip = {
            "html": "<b>{category}</b> ({priority})<br/>{location_text}<br/>Status: {status}",
            "style": {"backgroundColor": style.INK, "color": "white", "borderRadius": "8px"},
        }
        st.pydeck_chart(pdk.Deck(
            layers=[layer], initial_view_state=view_state, tooltip=tooltip,
        ))
    except Exception:
        st.map(map_df.rename(columns={"lat": "latitude", "lon": "longitude"}))


def _render_satellite_map(df):
    """Real satellite imagery via folium + Esri tiles — works with no API key."""
    if not FOLIUM_AVAILABLE:
        st.warning("Install `folium` and `streamlit-folium` (see requirements.txt) to enable "
                   "the satellite view. Showing the street map instead.")
        _render_street_map(df)
        return

    center_lat = df["lat"].mean()
    center_lon = df["lon"].mean()

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=13,
        tiles=None,
    )
    folium.TileLayer(
        tiles=SATELLITE_TILE_URL,
        attr=SATELLITE_ATTRIBUTION,
        name="Satellite",
        overlay=False,
        control=False,
    ).add_to(m)

    for _, row in df.iterrows():
        color = STATUS_HEX.get(row["status"], "#999999")
        popup_html = (
            f"<b>{row['category']}</b> ({row['priority']})<br/>"
            f"{row['location_text']}<br/>Status: {row['status']}"
        )
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=8,
            color="white",
            weight=2,
            fill=True,
            fill_color=color,
            fill_opacity=0.95,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{row['category']} · {row['status']}",
        ).add_to(m)

    st_folium(m, height=420, width=None, returned_objects=[], key="satellite_incident_map")
