# 🏙️ Civic Sense AI

A Streamlit application for citizens to report civic issues (potholes, garbage,
water logging, streetlights, etc.), pinpoint them on an interactive map, track
them on a live incident map, and get help from an AI assistant. Admins get a
dashboard to manage and resolve reports.

This build is intentionally **flat** — every file lives directly in the
project root. There is no `pages/` folder and no `.streamlit/` folder.
Navigation between sections is handled manually inside `app.py` via a
sidebar selector, instead of Streamlit's folder-based multipage system.

## Features

- **Login / Registration** — session-based auth backed by SQLite, with a
  pre-seeded admin and citizen demo account.
- **Report Incident** — citizens submit issues; an AI layer auto-suggests the
  category and priority from the free-text description. An interactive map
  lets them click to pin the exact incident location (or search a place
  name), with manual latitude/longitude fields as a fallback.
- **Incident Map** — all reports plotted on an interactive map, color-coded
  by status (Pending / In Progress / Resolved), with filters.
- **Admin Dashboard** — KPI overview, category/priority charts, and controls
  to update status or delete reports (admin-only).
- **AI Assistant** — a chat interface that answers civic questions and
  guides users through the app. Works fully offline out of the box; if you
  set an `ANTHROPIC_API_KEY`, it automatically upgrades to a Claude-powered
  assistant.

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app will create a local `civic_sense.db` SQLite file on first run.

### Demo credentials

| Role    | Username | Password    |
|---------|----------|-------------|
| Admin   | admin    | admin123    |
| Citizen | citizen  | citizen123  |

### (Optional) Enable the Claude-powered AI Assistant

Set your Anthropic API key as an environment variable before launching:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
streamlit run app.py
```

Without a key, the assistant automatically falls back to a built-in
rule-based responder — no functionality is lost, responses are just simpler.

### Note on the location picker map

The Report Incident section's click-to-pin map uses `folium` +
`streamlit-folium` (already in `requirements.txt`). If those packages
aren't installed, it automatically falls back to manual latitude/longitude
number inputs — nothing breaks, you just lose the visual picker. The
"Search for a place" box uses the free OpenStreetMap Nominatim API and
requires the app server to have internet access.

### Note on theming

Since there's no `.streamlit/config.toml` in this flat layout, dark-mode
consistency is handled entirely through CSS in `style.py`, which forces
readable text colors on every light surface regardless of the visitor's
OS/browser theme.

## Project structure

```
civic_sense_ai/
├── app.py                 # Entry point + login/register + sidebar router
├── database.py             # SQLite persistence layer
├── auth.py                 # Session-based auth helpers
├── ai_assistant.py         # Classification + chatbot logic
├── style.py                 # Shared design system (CSS + badges/cards)
├── report_incident.py      # Report Incident section (render())
├── incident_map.py         # Incident Map section (render())
├── admin_dashboard.py      # Admin Dashboard section (render())
├── assistant_page.py       # AI Assistant chat section (render())
└── requirements.txt
```

All files sit directly in the project root — just drop them into one
folder and run `streamlit run app.py`.
