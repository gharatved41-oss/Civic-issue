"""
report_incident.py
Report Incident section — rendered inline by app.py's sidebar router
(no pages/ directory; this is a plain importable module).
"""

import os
import uuid
import streamlit as st
import database as db
import style
from i18n import t
from ai_assistant import (
    classify_incident,
    CATEGORY_KEYWORDS,
    analyze_incident_photos,
    get_helpline_info,
)

try:
    import folium
    from streamlit_folium import st_folium
    MAP_PICKER_AVAILABLE = True
except ImportError:
    MAP_PICKER_AVAILABLE = False

DEFAULT_LAT, DEFAULT_LON = 19.4559, 72.8117

# Where uploaded incident photos are actually saved. Previously only the
# photo's *filename* was recorded in the DB and the file itself was
# discarded — nothing was ever available to display later. Now the bytes
# are written here, and the saved (unique) relative path is what gets
# stored in incidents.image_name.
UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Same key-free Esri satellite source used on the Incident Map page.
SATELLITE_TILE_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
SATELLITE_ATTRIBUTION = "Tiles &copy; Esri — Source: Esri, Maxar, Earthstar Geographics"
STREET_TILE_URL = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
STREET_ATTRIBUTION = "&copy; OpenStreetMap contributors"


def render():
    user = st.session_state.user

    style.hero(t("report_hero_title"),
               t("report_hero_subtitle"),
               eyebrow=t("eyebrow_new_report"))

    if "report_lat" not in st.session_state:
        st.session_state.report_lat = DEFAULT_LAT
    if "report_lon" not in st.session_state:
        st.session_state.report_lon = DEFAULT_LON

    categories = list(CATEGORY_KEYWORDS.keys()) + ["Other"]

    description_preview = st.text_area(
        "Describe the issue",
        key="description_input",
        placeholder="e.g. Large pothole near the bus stop causing two-wheeler accidents...",
        height=120,
    )

    suggested_category, suggested_priority = ("Other", "Low")
    if description_preview.strip():
        suggested_category, suggested_priority = classify_incident(description_preview)
        st.markdown(
            f'<div class="cs-card" style="border-left-color:{style.AMBER};">'
            f'🤖 <b>AI suggests:</b> {style.category_badge(suggested_category)}'
            f'{style.priority_badge(suggested_priority)}'
            f'<div class="cs-card-meta" style="margin-top:6px;">You can override this below.</div></div>',
            unsafe_allow_html=True,
        )

    # ---------------- PHOTO UPLOAD + AI SAFETY ANALYSIS ----------------
    # Deliberately placed OUTSIDE the form (like description_preview above) so
    # it reacts immediately when a citizen attaches photo(s), rather than only
    # after the whole report is submitted.
    st.markdown("#### 📸 Attach Photo(s)")
    photos = st.file_uploader(
        "Attach photo(s) of the issue (optional)",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key="incident_photos",
    )

    if photos:
        # Signature of the current upload set, so we only re-run the (possibly
        # paid/slow) analysis when the actual files change, not on every rerun.
        photo_signature = tuple((p.name, p.size) for p in photos)
        analysis_category = suggested_category  # best guess before the form's own category picker

        if st.session_state.get("_photo_advice_sig") != photo_signature:
            with st.spinner("🔍 Analyzing photo(s) for safety tips..."):
                photo_payload = [
                    {"bytes": p.getvalue(), "mime_type": p.type or "image/jpeg"} for p in photos
                ]
                advice_text = analyze_incident_photos(photo_payload, description_preview, analysis_category)
            st.session_state._photo_advice_sig = photo_signature
            st.session_state._photo_advice_text = advice_text
            st.session_state._photo_advice_category = analysis_category

        _, contacts = get_helpline_info(st.session_state.get("_photo_advice_category", analysis_category))
        contacts_html = "".join(
            f'<div style="margin:3px 0;">☎️ <b>{name}:</b> {number}</div>' for name, number in contacts
        )
        st.markdown(
            f'<div class="cs-card" style="border-left-color:{style.CORAL};">'
            f'🩺 <b>AI Safety Tip:</b>'
            f'<div class="cs-card-desc" style="margin-top:6px;">{st.session_state._photo_advice_text}</div>'
            f'<div class="cs-card-meta" style="margin-top:12px;">'
            f'<b>Who to contact</b> — general helplines, please confirm the exact local number for your '
            f'area/ward where possible:</div>{contacts_html}</div>',
            unsafe_allow_html=True,
        )

    # ---------------- LOCATION PICKER MAP ----------------
    st.markdown("#### 📍 Pinpoint the Location")

    if MAP_PICKER_AVAILABLE:
        st.caption("Click anywhere on the map to mark exactly where the incident occurred, "
                   "or search for a place below.")

        search_col, btn_col = st.columns([4, 1])
        with search_col:
            search_query = st.text_input(
                "Search for a place", placeholder="e.g. MG Road, Virar", label_visibility="collapsed"
            )
        with btn_col:
            search_clicked = st.button("🔍 Search", use_container_width=True)

        view_mode = st.radio(
            t("map_view_toggle"),
            [t("map_view_street"), t("map_view_satellite")],
            horizontal=True,
            key="report_map_view_mode",
        )
        satellite_on = view_mode == t("map_view_satellite")

        if search_clicked and search_query.strip():
            try:
                import requests
                resp = requests.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"q": search_query, "format": "json", "limit": 1},
                    headers={"User-Agent": "civic-sense-ai-app"},
                    timeout=6,
                )
                results = resp.json()
                if results:
                    st.session_state.report_lat = float(results[0]["lat"])
                    st.session_state.report_lon = float(results[0]["lon"])
                    st.success(f"📍 Found: {results[0].get('display_name', search_query)}")
                else:
                    st.warning("No matching place found. Try a different search or click the map directly.")
            except Exception:
                st.warning("Couldn't reach the location search service. Please click the map directly instead.")

        m = folium.Map(
            location=[st.session_state.report_lat, st.session_state.report_lon],
            zoom_start=14,
            tiles=None,
        )
        if satellite_on:
            folium.TileLayer(
                tiles=SATELLITE_TILE_URL, attr=SATELLITE_ATTRIBUTION,
                name="Satellite", overlay=False, control=False,
            ).add_to(m)
        else:
            folium.TileLayer(
                tiles=STREET_TILE_URL, attr=STREET_ATTRIBUTION,
                name="Street", overlay=False, control=False,
            ).add_to(m)
        folium.Marker(
            [st.session_state.report_lat, st.session_state.report_lon],
            tooltip="Incident location",
            icon=folium.Icon(color="red", icon="exclamation-triangle", prefix="fa"),
        ).add_to(m)

        map_state = st_folium(m, height=380, width=None, key="incident_location_picker")

        if map_state and map_state.get("last_clicked"):
            clicked_lat = map_state["last_clicked"]["lat"]
            clicked_lon = map_state["last_clicked"]["lng"]
            if (round(clicked_lat, 6), round(clicked_lon, 6)) != (
                round(st.session_state.report_lat, 6), round(st.session_state.report_lon, 6)
            ):
                st.session_state.report_lat = clicked_lat
                st.session_state.report_lon = clicked_lon
                st.rerun()

        st.markdown(
            f'<div class="cs-card" style="padding:10px 16px;">📌 <b>Selected coordinates:</b> '
            f'{st.session_state.report_lat:.6f}, {st.session_state.report_lon:.6f}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("Install `folium` and `streamlit-folium` (see requirements.txt) to enable the "
                "click-to-pin map. Using manual coordinate entry for now.")

    # ---------------- REPORT FORM ----------------
    with st.form("report_form", clear_on_submit=True):
        default_index = categories.index(suggested_category) if suggested_category in categories else len(categories) - 1
        category = st.selectbox("Category", categories, index=default_index)

        priority_options = ["Low", "Medium", "High"]
        priority = st.selectbox(
            "Priority",
            priority_options,
            index=priority_options.index(suggested_priority) if suggested_priority in priority_options else 0,
        )

        location_text = st.text_input("Location (landmark / street / area)")

        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input(
                "Latitude", value=float(st.session_state.report_lat), format="%.6f",
                help="Auto-filled from the map above — fine-tune here if needed.",
            )
        with col2:
            lon = st.number_input(
                "Longitude", value=float(st.session_state.report_lon), format="%.6f",
                help="Auto-filled from the map above — fine-tune here if needed.",
            )

        if photos:
            st.caption(f"📎 {len(photos)} photo(s) attached (uploaded above).")

        submitted = st.form_submit_button("🚀 Submit Report", use_container_width=True)

        if submitted:
            if not description_preview.strip() or not location_text.strip():
                st.error("Please provide both a description and a location.")
            else:
                image_name = None
                if photos:
                    saved_paths = []
                    for photo in photos:
                        ext = os.path.splitext(photo.name)[1]
                        saved_filename = f"{uuid.uuid4().hex}{ext}"
                        saved_path = os.path.join(UPLOAD_DIR, saved_filename)
                        with open(saved_path, "wb") as f:
                            f.write(photo.getbuffer())
                        saved_paths.append(saved_path)
                    # Multiple photos are stored as a comma-separated list of
                    # paths in the single image_name column (no schema change).
                    image_name = ",".join(saved_paths)
                incident_id = db.add_incident(
                    user_id=user["id"],
                    username=user["username"],
                    category=category,
                    description=description_preview.strip(),
                    location_text=location_text.strip(),
                    lat=lat,
                    lon=lon,
                    priority=priority,
                    image_name=image_name,
                )
                st.success(f"✅ Incident #{incident_id} reported successfully! Thank you for helping your community.")
                st.balloons()
                st.session_state.report_lat = DEFAULT_LAT
                st.session_state.report_lon = DEFAULT_LON
                st.session_state.pop("_photo_advice_sig", None)
                st.session_state.pop("_photo_advice_text", None)
                st.session_state.pop("_photo_advice_category", None)
                # Note: the photo uploader lives outside the form, so unlike the
                # form's own fields it isn't auto-cleared by clear_on_submit —
                # citizens can remove the attached files manually before their
                # next report.

    st.divider()
    st.info(t("past_reports_pointer"))
