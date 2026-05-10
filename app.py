# -*- coding: utf-8 -*-
"""Streamlit UI for topic research using a starter backend."""

import streamlit as st

from research import fetch_research


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
    with st.spinner("Gathering results..."):
        result = fetch_research(st.session_state.submitted_topic)

    if result["status"] == "ok":
        st.success(f"Researching: {result['topic']}")
        if result.get("warning"):
            st.warning(result["warning"])
        confidence = result.get("confidence", {})
        st.caption(
            f"Confidence: {confidence.get('score', 'n/a')} ({confidence.get('label', 'unknown')})"
        )

        st.subheader("Summary")
        st.write(result["summary"])

        st.subheader("Key points")
        for idx, item in enumerate(result.get("key_point_evidence", []), start=1):
            st.markdown(f"- {item.get('point', 'No key point')}")
            with st.expander(f"Evidence for key point {idx}"):
                st.markdown(
                    f"Source: [{item.get('source_title', 'Unknown')}]({item.get('source_url', '#')})"
                )
                st.write(item.get("why", "No rationale provided."))

        st.subheader("Next questions")
        for question in result.get("next_questions", []):
            st.markdown(f"- {question}")

        st.subheader("References")
        for ref in result["references"]:
            st.markdown(f"- [{ref['title']}]({ref['url']})")

        st.subheader("Research brief")
        st.text_area(
            "Copy-ready brief",
            value=result.get("brief", ""),
            height=240,
            disabled=False,
        )
    else:
        st.error(result["error"])
else:
    st.caption("Submit a topic to see the placeholder results area.")
