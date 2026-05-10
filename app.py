# -*- coding: utf-8 -*-
"""Streamlit research topic UI placeholder until real research is wired in."""

import streamlit as st


def run_research(topic: str) -> str:
    """Starter hook for research logic (LLM, search APIs, vector DB, etc.)."""
    cleaned_topic = topic.strip()
    return f"Researching: {cleaned_topic}..."


st.set_page_config(page_title="AI Research Agent", layout="centered")

with st.sidebar:
    st.title("AI Research Agent")
    st.markdown(
        """
        Enter a research topic and submit to preview how results will appear.
        This is a starter layout; plug in your retrieval or LLM pipeline next.
        """
    )

st.header("Research a topic")

if "submitted_topic" not in st.session_state:
    st.session_state.submitted_topic = ""

topic = st.text_input("Research topic", placeholder="e.g., causal inference in econometrics")

if st.button("Submit", type="primary"):
    st.session_state.submitted_topic = topic.strip()

if st.session_state.submitted_topic:
    result_message = run_research(st.session_state.submitted_topic)
    st.info(result_message)
else:
    st.caption("Submit a topic to see the placeholder results area.")
