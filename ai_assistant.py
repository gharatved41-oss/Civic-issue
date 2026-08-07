"""
ai_assistant.py
A lightweight "civic sense" AI layer.

- classify_incident(): keyword-based auto-categorization + priority suggestion
  for incident reports (works fully offline, no API key required).
- get_ai_response(): a rule-based civic assistant chatbot. If an
  ANTHROPIC_API_KEY is available (env var or st.secrets), it will
  automatically upgrade to a real Claude-powered assistant; otherwise it
  falls back to the built-in rule-based responder so the app always works
  out of the box.
"""

import os
import re
import base64

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "road damage", "broken road", "crater", "road crack"],
    "Garbage": ["garbage", "trash", "waste", "litter", "dump", "rubbish"],
    "Streetlight": ["streetlight", "street light", "lamp post", "no light", "dark street"],
    "Water Logging": ["water logging", "flooding", "flood", "drain overflow", "stagnant water"],
    "Sewage": ["sewage", "drainage", "manhole", "gutter", "sewer"],
    "Electricity": ["power cut", "electricity", "wire", "transformer", "short circuit"],
    "Stray Animals": ["stray dog", "stray cattle", "stray animal", "animal menace"],
    "Illegal Construction": ["illegal construction", "encroachment", "unauthorized building"],
    "Tree/Vegetation": ["fallen tree", "tree branch", "overgrown", "tree fall"],
    "Traffic": ["traffic signal", "traffic jam", "signal not working", "encroached footpath"],
}

HIGH_PRIORITY_WORDS = ["accident", "injury", "fire", "collapse", "danger", "electrocution",
                        "child", "hospital", "emergency", "death", "flood"]
MEDIUM_PRIORITY_WORDS = ["overflow", "broken", "leak", "blocked", "damaged"]


def classify_incident(description: str):
    """Return (category, priority) suggested from free-text description."""
    text = description.lower()

    category = "Other"
    best_hits = 0
    for cat, keywords in CATEGORY_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in text)
        if hits > best_hits:
            best_hits = hits
            category = cat

    if any(word in text for word in HIGH_PRIORITY_WORDS):
        priority = "High"
    elif any(word in text for word in MEDIUM_PRIORITY_WORDS):
        priority = "Medium"
    else:
        priority = "Low"

    return category, priority


# ---------------- PHOTO ANALYSIS + HELPLINES ----------------
#
# Contacts below are deliberately generated from this fixed table rather than
# asked of the AI model — an LLM describing a photo has no way to actually
# know a real phone number, so letting it invent one would risk showing a
# citizen a wrong emergency contact. The numbers here are the commonly-used
# *national/state-level* Indian helplines; local municipal wards often also
# have their own number, so the UI reminds citizens to confirm locally.
CATEGORY_HELPLINES = {
    "Pothole": {
        "advice": "Avoid driving straight over the pothole, especially on two-wheelers, and warn "
                   "other road users if it's safe to do so. If it's on a busy or high-speed stretch, "
                   "report it as High priority so the roads department can barricade or fill it quickly.",
        "contacts": [
            ("Municipal Corporation – Roads / PWD", "Local ward office"),
            ("Traffic Police", "103"),
        ],
    },
    "Garbage": {
        "advice": "Keep the area clear of children and pets, don't attempt to burn or move waste "
                   "yourself (especially if it looks medical or hazardous), and note whether it's "
                   "attracting stray animals or blocking drainage nearby.",
        "contacts": [
            ("Municipal Solid Waste / Sanitation Dept.", "Local ward office"),
            ("Swachh Bharat Mission Helpline", "1969"),
        ],
    },
    "Streetlight": {
        "advice": "Take extra care walking or driving through the area after dark until it's fixed — "
                   "use a torch/phone light if needed and avoid the spot at night if an alternative "
                   "route exists.",
        "contacts": [
            ("Municipal Electrical / Streetlight Dept.", "Local ward office"),
            ("State Electricity Board Complaint Line", "1912"),
        ],
    },
    "Water Logging": {
        "advice": "Don't wade through standing water if depth or current is unclear — it can hide open "
                   "manholes or electrical hazards. Keep children away, and if it's rising fast or "
                   "near homes, treat it as an emergency.",
        "contacts": [
            ("Municipal Disaster Management Cell", "1078"),
            ("Fire Brigade", "101"),
        ],
    },
    "Sewage": {
        "advice": "Avoid direct contact with sewage overflow — it's a health hazard. Keep children and "
                   "pets away, and if a manhole cover is missing or broken, treat it as an immediate "
                   "danger and flag it as High priority.",
        "contacts": [
            ("Municipal Sewerage / Drainage Dept.", "Local ward office"),
            ("Public Health Helpline", "104"),
        ],
    },
    "Electricity": {
        "advice": "Stay well away from exposed wires, sparking equipment, or a leaning/damaged "
                   "transformer or pole — treat any downed line as live even if it looks dead, and "
                   "keep others away too. If there's smoke or fire risk, call the fire brigade "
                   "immediately.",
        "contacts": [
            ("State Electricity Board Complaint Line", "1912"),
            ("Fire Brigade", "101"),
        ],
    },
    "Stray Animals": {
        "advice": "Keep a safe distance, don't corner or provoke the animal(s), and keep children away. "
                   "If someone has been bitten, seek medical attention right away rather than waiting "
                   "for the report to be actioned.",
        "contacts": [
            ("Animal Birth Control / Municipal Veterinary Cell", "Local ward office"),
            ("Ambulance (for bites/injury)", "102 / 108"),
        ],
    },
    "Illegal Construction": {
        "advice": "Keep a safe distance if the structure looks unstable, and avoid confronting anyone "
                   "on-site directly — document what you can from a public area and let the municipal "
                   "authority handle enforcement.",
        "contacts": [
            ("Town Planning / Encroachment Dept.", "Local ward office"),
            ("Police (if safety is at risk)", "100"),
        ],
    },
    "Tree/Vegetation": {
        "advice": "Keep clear of a leaning tree or hanging branch, especially in wind or rain, and warn "
                   "others nearby. If it's blocking a road or has damaged wires, mark it High priority.",
        "contacts": [
            ("Municipal Garden / Tree Authority", "Local ward office"),
            ("Fire Brigade (if blocking a road/wires)", "101"),
        ],
    },
    "Traffic": {
        "advice": "Follow any traffic police or manual signals in the area, and drive/cross with extra "
                   "caution while the issue persists.",
        "contacts": [
            ("Traffic Police", "103"),
            ("Municipal Traffic Engineering Cell", "Local ward office"),
        ],
    },
    "_default": {
        "advice": "Keep a safe distance from the issue, warn others nearby if it looks hazardous, and "
                   "avoid trying to fix or move anything yourself. Include a clear photo and precise "
                   "location so the response team can act quickly.",
        "contacts": [
            ("Police", "100"),
            ("Fire Brigade", "101"),
            ("Ambulance", "102 / 108"),
        ],
    },
}


def get_helpline_info(category: str):
    """Returns (advice_text, contacts_list) for a category. Falls back to a
    generic emergency-services set for categories not in the table."""
    info = CATEGORY_HELPLINES.get(category, CATEGORY_HELPLINES["_default"])
    return info["advice"], info["contacts"]


def _rule_based_photo_advice(category: str) -> str:
    advice, _ = get_helpline_info(category)
    return advice


def analyze_incident_photos(photos, description: str, category: str) -> str:
    """
    photos: list of dicts like {"bytes": <raw image bytes>, "mime_type": "image/jpeg"}
    description / category: the citizen's report text and (suggested) category.

    Returns a short natural-language safety/mitigation suggestion. Uses Claude's
    vision capability when an API key is configured; otherwise falls back to the
    fixed per-category advice in CATEGORY_HELPLINES so the feature still works
    offline. Contact numbers are never generated by the model — see
    get_helpline_info() — only this descriptive advice text is AI-written.
    """
    if not photos:
        return _rule_based_photo_advice(category)

    api_key = _get_api_key()
    if not api_key:
        return _rule_based_photo_advice(category)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        content = []
        for p in photos[:4]:  # cap number of images per request
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": p.get("mime_type") or "image/jpeg",
                    "data": base64.b64encode(p["bytes"]).decode(),
                },
            })
        content.append({
            "type": "text",
            "text": (
                f"This photo (or these photos) was attached to a civic incident report. "
                f"Reported category: {category}. Citizen's description: "
                f"{description.strip() if description and description.strip() else '(none given)'}. "
                "In 3-5 short sentences: (1) briefly note what the photo shows, (2) give any immediate "
                "safety precaution bystanders should take, and (3) suggest a practical way to reduce "
                "harm until the municipal team fixes it. Do not invent or state any phone number or "
                "contact detail — those are handled separately."
            ),
        })

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{"role": "user", "content": content}],
        )
        return response.content[0].text
    except Exception as e:
        fallback = _rule_based_photo_advice(category)
        return f"{fallback}\n\n_(Note: AI photo analysis failed — showing general guidance. {e})_"


# ---------------- CHATBOT ----------------

FAQ_RESPONSES = {
    r"\b(hi|hello|hey)\b": "Hello! I'm your Civic Sense AI Assistant. Ask me how to report an issue, "
                            "check incident status, or learn about civic responsibilities.",
    r"report.*(pothole|road)": "To report a pothole: go to **Report Incident**, choose category "
                                "'Pothole', describe the location clearly, and attach a photo if possible. "
                                "It will automatically be marked with a priority level.",
    r"report.*(garbage|trash|waste)": "To report a garbage issue: open **Report Incident**, select "
                                       "'Garbage', and mention the exact street/landmark so sanitation "
                                       "teams can locate it quickly.",
    r"(status|track).*(incident|report|complaint)": "You can track your reports from the **Report "
                                                      "Incident** page — your past submissions and their "
                                                      "current status are listed at the bottom.",
    r"(who|what).*(admin|resolve)": "Reported incidents are reviewed by municipal admins through the "
                                     "**Admin Dashboard**, where they update status to In Progress or "
                                     "Resolved.",
    r"(map|near me|nearby)": "Check the **Incident Map** page to see all reported civic issues plotted "
                              "by location, color-coded by status.",
    r"(civic sense|responsibility|clean|litter)": "Civic sense means taking small daily actions — not "
                                                    "littering, reporting hazards, conserving water and "
                                                    "electricity, and respecting public property — that "
                                                    "collectively keep our community safe and clean.",
    r"(thank|thanks)": "You're welcome! Together we can build a cleaner, safer community. 🙂",
}


def _rule_based_response(query: str) -> str:
    q = query.lower().strip()
    for pattern, response in FAQ_RESPONSES.items():
        if re.search(pattern, q):
            return response

    # Try to at least suggest a category if it looks like an incident description
    category, priority = classify_incident(q)
    if category != "Other":
        return (f"That sounds like it could be a **{category}** issue "
                f"(suggested priority: **{priority}**). Head to the Report Incident page to file it, "
                f"or ask me anything else about civic reporting.")

    return ("I can help with reporting civic issues (potholes, garbage, streetlights, water logging, "
            "sewage, and more), tracking complaint status, or explaining how the platform works. "
            "Could you rephrase your question?")


def _get_api_key():
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key
    try:
        import streamlit as st
        return st.secrets.get("ANTHROPIC_API_KEY")
    except Exception:
        return None


def get_ai_response(query: str, history=None) -> str:
    """
    Main entry point used by the AI Assistant page.
    Uses Claude via the Anthropic API if a key is configured, otherwise
    falls back to the offline rule-based assistant.
    """
    api_key = _get_api_key()
    if not api_key:
        return _rule_based_response(query)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        messages = []
        if history:
            for role, content in history[-6:]:
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": query})

        system_prompt = (
            "You are Civic Sense AI, a helpful assistant embedded in a citizen incident-reporting "
            "platform. Help users report civic issues (potholes, garbage, water logging, streetlights, "
            "sewage, illegal construction, stray animals, etc.), understand app features (Report "
            "Incident, Incident Map, Admin Dashboard), and encourage civic responsibility. Keep answers "
            "concise and practical."
        )

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=400,
            system=system_prompt,
            messages=messages,
        )
        return response.content[0].text
    except Exception as e:
        # Fail gracefully to the offline assistant rather than breaking the app
        fallback = _rule_based_response(query)
        return f"{fallback}\n\n_(Note: AI API call failed — using offline assistant. {e})_"
