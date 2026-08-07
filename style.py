"""
style.py
Shared design system for Civic Sense AI.

Theme: "Neon Grid" — a dark, glassmorphic, sci-fi command-center look:
near-black space background, animated gradient glow, neon cyan/violet
accents, frosted-glass cards, and glowing borders. Orbitron for display
type (headings, hero), Space Grotesk for UI labels, Inter for body text.

Import and call inject_css() once near the top of every page (after
st.set_page_config). Use badge_html() / render_incident_card() to keep
incident displays visually consistent everywhere. Function names and
the .cs-* CSS classes are unchanged from the previous theme, so every
other page module keeps working without edits.
"""

import streamlit as st

# ---- Design tokens ----
BG = "#060A14"          # deep space background
BG_ALT = "#0A1122"       # secondary panels
GLASS = "rgba(255,255,255,0.045)"   # glassmorphic card fill
GLASS_BORDER = "rgba(255,255,255,0.09)"
INK = "#E9F3FF"          # primary light text on dark bg
INK_SOFT = "#8CA0C4"     # secondary text
NAVY = "#101B33"         # solid dark surface (sidebar base)

TEAL = "#00E5C7"         # primary neon accent (brand)
TEAL_DARK = "#00A98F"
CYAN = "#3AD7FF"         # secondary neon accent
VIOLET = "#8B5CF6"       # tertiary neon accent
AMBER = "#FFB020"        # pending / in-progress accent
CORAL = "#FF4D6D"        # high priority / danger
GREEN = "#26E39A"        # resolved / success

PAPER = BG               # kept for backward-compat with any old references
CARD = GLASS

STATUS_STYLE = {
    "Pending":     {"bg": "rgba(255,77,109,0.14)",  "fg": "#FF8FA3", "dot": CORAL},
    "In Progress": {"bg": "rgba(255,176,32,0.14)",  "fg": "#FFCA6B", "dot": AMBER},
    "Resolved":    {"bg": "rgba(38,227,154,0.14)",  "fg": "#7CF3C6", "dot": GREEN},
}

PRIORITY_STYLE = {
    "High":   {"bg": "rgba(255,77,109,0.14)", "fg": "#FF8FA3"},
    "Medium": {"bg": "rgba(255,176,32,0.14)", "fg": "#FFCA6B"},
    "Low":    {"bg": "rgba(58,215,255,0.14)", "fg": "#8FE3FF"},
}


def inject_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;600;700;800&family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        html, body, [class*="css"] {{
            color-scheme: dark;
            font-family: 'Inter', sans-serif;
        }}
        :root {{
            color-scheme: dark;
        }}

        h1, h2, h3, .cs-display {{
            font-family: 'Orbitron', sans-serif !important;
            letter-spacing: 0.01em;
        }}
        h4, h5, h6 {{
            font-family: 'Space Grotesk', sans-serif !important;
            letter-spacing: 0.01em;
        }}

        /* ---- Animated deep-space app background ---- */
        .stApp {{
            background:
                radial-gradient(1100px 550px at 12% -8%, rgba(0,229,199,0.16), transparent 60%),
                radial-gradient(900px 500px at 105% 8%, rgba(139,92,246,0.16), transparent 55%),
                radial-gradient(800px 480px at 50% 115%, rgba(58,215,255,0.10), transparent 55%),
                linear-gradient(180deg, {BG} 0%, #050810 100%);
            background-attachment: fixed;
        }}
        .stApp::before {{
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            background-image:
                linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px);
            background-size: 42px 42px;
            mask-image: radial-gradient(circle at 50% 0%, rgba(0,0,0,0.55), transparent 70%);
            z-index: 0;
        }}
        .block-container {{
            position: relative;
            z-index: 1;
        }}

        /* ---- Sidebar ---- */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {NAVY} 0%, #060A14 100%);
            border-right: 1px solid {GLASS_BORDER};
        }}
        section[data-testid="stSidebar"] * {{
            color: {INK} !important;
        }}
        section[data-testid="stSidebar"] .stButton button {{
            background: {GLASS};
            border: 1px solid {GLASS_BORDER};
            backdrop-filter: blur(8px);
        }}
        section[data-testid="stSidebar"] .stButton button:hover {{
            border-color: {TEAL};
            box-shadow: 0 0 16px rgba(0,229,199,0.35);
        }}
        div[role="radiogroup"] label {{
            border-radius: 10px;
            padding: 6px 10px;
            transition: background 0.15s ease, box-shadow 0.15s ease;
        }}
        div[role="radiogroup"] label:hover {{
            background: rgba(0,229,199,0.10);
        }}

        /* ---- Buttons ---- */
        .stButton > button, .stFormSubmitButton > button {{
            background: linear-gradient(135deg, {TEAL} 0%, {CYAN} 60%, {VIOLET} 130%);
            color: #04141A;
            border: none;
            border-radius: 10px;
            font-weight: 700;
            letter-spacing: 0.01em;
            padding: 0.6em 1.25em;
            transition: transform 0.08s ease, box-shadow 0.2s ease, filter 0.2s ease;
            box-shadow: 0 0 0 1px rgba(0,229,199,0.25), 0 6px 20px rgba(0,229,199,0.22);
        }}
        .stButton > button:hover, .stFormSubmitButton > button:hover {{
            transform: translateY(-1px);
            filter: brightness(1.08);
            box-shadow: 0 0 0 1px rgba(0,229,199,0.4), 0 10px 30px rgba(58,215,255,0.35);
            color: #04141A;
        }}
        .stButton > button:active, .stFormSubmitButton > button:active {{
            transform: translateY(0px) scale(0.99);
        }}

        /* ---- Metrics as glass cards ---- */
        div[data-testid="stMetric"] {{
            background: {GLASS};
            backdrop-filter: blur(10px);
            border: 1px solid {GLASS_BORDER};
            border-left: 3px solid {TEAL};
            border-radius: 14px;
            padding: 14px 18px 10px 18px;
            box-shadow: 0 0 24px rgba(0,229,199,0.06), 0 8px 24px rgba(0,0,0,0.35);
        }}
        div[data-testid="stMetricValue"] {{
            font-family: 'Orbitron', sans-serif;
            text-shadow: 0 0 18px rgba(0,229,199,0.35);
        }}
        div[data-testid="stMetricLabel"] {{
            color: {INK_SOFT} !important;
        }}

        /* ---- Tabs ---- */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 6px;
            border-bottom: 1px solid {GLASS_BORDER};
        }}
        .stTabs [data-baseweb="tab"] {{
            border-radius: 10px 10px 0 0;
            padding: 8px 18px;
            font-weight: 600;
            color: {INK_SOFT};
            background: transparent;
        }}
        .stTabs [aria-selected="true"] {{
            background: {GLASS};
            color: {TEAL} !important;
            border-bottom: 2px solid {TEAL};
            box-shadow: 0 -6px 18px rgba(0,229,199,0.10);
        }}

        /* ---- Inputs ---- */
        .stTextInput input, .stTextArea textarea, .stNumberInput input,
        div[data-baseweb="select"] > div {{
            background: rgba(255,255,255,0.03) !important;
            color: {INK} !important;
            border-radius: 10px !important;
            border: 1px solid {GLASS_BORDER} !important;
            backdrop-filter: blur(6px);
        }}
        .stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus {{
            border-color: {TEAL} !important;
            box-shadow: 0 0 0 3px rgba(0,229,199,0.18) !important;
        }}
        .stTextInput input::placeholder, .stTextArea textarea::placeholder {{
            color: {INK_SOFT} !important;
            opacity: 0.8;
        }}
        .stTextInput div[data-baseweb="input"] {{
            background: transparent !important;
        }}
        .stTextInput button {{
            background: transparent !important;
        }}
        .stTextInput button svg {{
            fill: {INK_SOFT} !important;
        }}

        /* ---- Folium map component ---- */
        iframe {{
            background: {BG_ALT} !important;
            border-radius: 14px;
        }}
        div[data-testid="stIFrame"], div[data-testid="stCustomComponentV1"] {{
            background: {BG_ALT} !important;
            border-radius: 14px;
            overflow: hidden;
            border: 1px solid {GLASS_BORDER};
        }}

        /* ---- File uploader ---- */
        section[data-testid="stFileUploaderDropzone"] {{
            background: {GLASS} !important;
            border: 1px dashed {GLASS_BORDER} !important;
            border-radius: 14px;
        }}
        section[data-testid="stFileUploaderDropzone"]:hover {{
            border-color: {TEAL} !important;
        }}
        section[data-testid="stFileUploaderDropzone"] * {{
            color: {INK} !important;
        }}
        section[data-testid="stFileUploaderDropzone"] button {{
            background: rgba(255,255,255,0.05) !important;
            border: 1px solid {GLASS_BORDER} !important;
            color: {INK} !important;
        }}

        /* ---- Expander (admin incident cards) ---- */
        details {{
            background: {GLASS};
            backdrop-filter: blur(10px);
            border: 1px solid {GLASS_BORDER} !important;
            border-radius: 14px !important;
            box-shadow: 0 8px 24px rgba(0,0,0,0.35);
            margin-bottom: 10px;
        }}
        details summary {{
            color: {INK} !important;
        }}

        /* ---- Chat message bubbles ---- */
        .stChatMessage {{
            background: {GLASS} !important;
            border: 1px solid {GLASS_BORDER} !important;
            border-radius: 14px !important;
            backdrop-filter: blur(10px);
        }}

        /* ---- Custom classes ---- */
        @keyframes cs-hero-glow {{
            0%, 100% {{ box-shadow: 0 0 40px rgba(0,229,199,0.18), 0 18px 50px rgba(0,0,0,0.45); }}
            50% {{ box-shadow: 0 0 60px rgba(139,92,246,0.22), 0 18px 50px rgba(0,0,0,0.45); }}
        }}
        .cs-hero {{
            position: relative;
            background:
                linear-gradient(135deg, rgba(0,229,199,0.14) 0%, rgba(139,92,246,0.14) 55%, rgba(58,215,255,0.14) 100%),
                linear-gradient(160deg, #0A1226 0%, #060A14 100%);
            border: 1px solid {GLASS_BORDER};
            border-radius: 22px;
            padding: 40px 36px;
            color: {INK};
            margin-bottom: 22px;
            backdrop-filter: blur(14px);
            animation: cs-hero-glow 6s ease-in-out infinite;
            overflow: hidden;
        }}
        .cs-hero::after {{
            content: "";
            position: absolute;
            top: -50%; right: -10%;
            width: 340px; height: 340px;
            background: radial-gradient(circle, rgba(0,229,199,0.25), transparent 70%);
            pointer-events: none;
        }}
        .cs-hero h1 {{
            color: {INK} !important;
            font-size: 2.3rem;
            margin-bottom: 8px;
            text-shadow: 0 0 30px rgba(0,229,199,0.25);
        }}
        .cs-hero p {{
            color: {INK_SOFT};
            font-size: 1.05rem;
            margin: 0;
            max-width: 62ch;
        }}
        .cs-eyebrow {{
            display: inline-block;
            background: rgba(255,176,32,0.14);
            color: {AMBER};
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            font-size: 0.72rem;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            padding: 4px 12px;
            border: 1px solid rgba(255,176,32,0.3);
            border-radius: 999px;
            margin-bottom: 14px;
        }}

        .cs-feature-card {{
            background: {GLASS};
            border: 1px solid {GLASS_BORDER};
            border-radius: 16px;
            padding: 18px 16px;
            height: 100%;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
        }}
        .cs-feature-card:hover {{
            transform: translateY(-2px);
            border-color: rgba(0,229,199,0.4);
            box-shadow: 0 0 30px rgba(0,229,199,0.12), 0 12px 28px rgba(0,0,0,0.35);
        }}
        .cs-feature-card .cs-icon {{
            font-size: 1.6rem;
            filter: drop-shadow(0 0 10px rgba(0,229,199,0.35));
        }}
        .cs-feature-card h4 {{
            margin: 8px 0 4px 0;
            color: {INK};
        }}
        .cs-feature-card p {{
            color: {INK_SOFT};
            font-size: 0.88rem;
            margin: 0;
        }}

        .cs-card {{
            background: {GLASS};
            border: 1px solid {GLASS_BORDER};
            border-left: 3px solid {TEAL};
            border-radius: 14px;
            padding: 14px 18px;
            margin-bottom: 12px;
            backdrop-filter: blur(10px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }}
        .cs-card-title {{
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            color: {INK};
            font-size: 1.02rem;
            margin-bottom: 4px;
        }}
        .cs-card-meta {{
            color: {INK_SOFT};
            font-size: 0.82rem;
            margin-bottom: 8px;
        }}
        .cs-card-desc {{
            color: #C8D6EC;
            font-size: 0.92rem;
        }}

        .cs-badge {{
            display: inline-block;
            font-family: 'Space Grotesk', sans-serif;
            font-size: 0.72rem;
            font-weight: 700;
            padding: 3px 10px;
            border-radius: 999px;
            margin-right: 6px;
            letter-spacing: 0.02em;
            border: 1px solid rgba(255,255,255,0.08);
        }}
        .cs-dot {{
            display: inline-block;
            width: 7px; height: 7px;
            border-radius: 50%;
            margin-right: 5px;
            box-shadow: 0 0 8px currentColor;
        }}

        .cs-legend-item {{
            display: inline-flex;
            align-items: center;
            margin-right: 18px;
            font-size: 0.85rem;
            color: {INK_SOFT};
        }}

        /* ---- Force light, readable text on the dark theme, overriding      ---- */
        /* ---- the visitor's OS/browser light-mode preference if any        ---- */
        .stApp, .stApp p, .stApp span, .stApp li, .stApp label,
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5,
        .stMarkdown, .stMarkdown p {{
            color: {INK};
        }}
        details, details *,
        div[data-testid="stMetricValue"], div[data-testid="stMetricDelta"],
        div[data-testid="stMetricLabel"],
        .stDataFrame, .stDataFrame * ,
        .stChatMessage, .stChatMessage p,
        .stTextInput label, .stTextArea label, .stSelectbox label,
        .stNumberInput label, .stFileUploader label,
        div[data-baseweb="select"] * ,
        .cs-card, .cs-card *:not(.cs-badge):not(.cs-dot),
        .cs-feature-card, .cs-feature-card p, .cs-feature-card h4 {{
            color: {INK} !important;
        }}
        /* Sidebar already forced light-on-dark above; re-assert after the block */
        section[data-testid="stSidebar"], section[data-testid="stSidebar"] * {{
            color: {INK} !important;
        }}
        /* Hero banner text */
        .cs-hero, .cs-hero h1, .cs-hero p, .cs-hero *, .cs-hero h1 * {{
            color: {INK} !important;
            -webkit-text-fill-color: {INK} !important;
        }}
        .cs-hero p {{
            color: {INK_SOFT} !important;
            -webkit-text-fill-color: {INK_SOFT} !important;
        }}
        .cs-eyebrow {{
            -webkit-text-fill-color: {AMBER} !important;
        }}

        /* ---- Scrollbar ---- */
        ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
        ::-webkit-scrollbar-track {{ background: {BG}; }}
        ::-webkit-scrollbar-thumb {{
            background: linear-gradient(180deg, {TEAL}, {VIOLET});
            border-radius: 8px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def status_badge(status: str) -> str:
    s = STATUS_STYLE.get(status, {"bg": "rgba(255,255,255,0.08)", "fg": "#CCC", "dot": "#999"})
    return (f'<span class="cs-badge" style="background:{s["bg"]};color:{s["fg"]};">'
            f'<span class="cs-dot" style="background:{s["dot"]};color:{s["dot"]};"></span>{status}</span>')


def priority_badge(priority: str) -> str:
    p = PRIORITY_STYLE.get(priority, {"bg": "rgba(255,255,255,0.08)", "fg": "#CCC"})
    return f'<span class="cs-badge" style="background:{p["bg"]};color:{p["fg"]};">{priority} priority</span>'


def category_badge(category: str) -> str:
    return f'<span class="cs-badge" style="background:rgba(58,215,255,0.14);color:#8FE3FF;">{category}</span>'


def render_incident_card(row) -> str:
    """Build an HTML card for a single incident row (dict-like with the usual fields)."""
    return f"""
    <div class="cs-card">
        <div class="cs-card-title">#{row['id']} — {row['category']}</div>
        <div class="cs-card-meta">📍 {row.get('location_text', '—')} &nbsp;•&nbsp; 🕒 {str(row.get('created_at',''))[:16]}
        &nbsp;•&nbsp; 👤 {row.get('username','—')}</div>
        {status_badge(row['status'])}{priority_badge(row['priority'])}
        <div class="cs-card-desc" style="margin-top:8px;">{row.get('description','')}</div>
    </div>
    """


def hero(title: str, subtitle: str, eyebrow: str = None):
    eyebrow_html = f'<span class="cs-eyebrow">{eyebrow}</span><br/>' if eyebrow else ""
    st.markdown(
        f"""
        <div class="cs-hero">
            {eyebrow_html}
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
