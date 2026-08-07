"""
assistant_page.py
AI Assistant chat section — rendered inline by app.py's sidebar router.
(Named separately from ai_assistant.py, which holds the classification/
chatbot logic this page calls into.)
"""

import streamlit as st
import style
from i18n import t
from ai_assistant import get_ai_response


def render():
    style.hero(t("assistant_hero_title"),
               t("assistant_hero_subtitle"),
               eyebrow=t("eyebrow_always_online"))

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            ("assistant", "Hi! I'm your Civic Sense AI Assistant. Ask me how to report an issue, "
                          "track a complaint, or anything about civic responsibility.")
        ]

    for role, content in st.session_state.chat_history:
        avatar = "🤖" if role == "assistant" else "🧑"
        with st.chat_message(role, avatar=avatar):
            st.markdown(content)

    prompt = st.chat_input("Type your question here...")
    if prompt:
        st.session_state.chat_history.append(("user", prompt))
        with st.chat_message("user", avatar="🧑"):
            st.markdown(prompt)

        api_history = [("user" if r == "user" else "assistant", c) for r, c in st.session_state.chat_history[:-1]]

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                response = get_ai_response(prompt, history=api_history)
            st.markdown(response)

        st.session_state.chat_history.append(("assistant", response))

    st.divider()
    with st.expander("💡 Try asking..."):
        qcol1, qcol2 = st.columns(2)
        with qcol1:
            st.markdown("- How do I report a pothole?\n- Where can I see nearby incidents?")
        with qcol2:
            st.markdown("- How do I track my complaint?\n- What is civic sense?")
