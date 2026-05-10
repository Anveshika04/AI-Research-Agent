# -*- coding: utf-8 -*-
"""Streamlit UI for topic research using a starter backend."""

import streamlit as st

from research import fetch_research
from storage import (
    list_reports,
    load_report,
    report_to_markdown,
    report_to_pdf_bytes,
    save_report,
)


def render_result(result: dict, report_id: str = "") -> None:
    """Render a research result payload to the Streamlit page."""
    st.success(f"Researching: {result['topic']}")
    if result.get("warning"):
        st.warning(result["warning"])
    confidence = result.get("confidence", {})
    st.caption(f"Confidence: {confidence.get('score', 'n/a')} ({confidence.get('label', 'unknown')})")

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

    st.subheader("Export")
    safe_topic = str(result.get("topic", "research-report")).strip().replace(" ", "-").lower()
    file_stem = f"{safe_topic}-{report_id}" if report_id else safe_topic
    markdown_content = report_to_markdown(result)
    pdf_bytes = report_to_pdf_bytes(result)
    col_md, col_pdf = st.columns(2)
    with col_md:
        st.download_button(
            "Download Markdown",
            data=markdown_content,
            file_name=f"{file_stem}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col_pdf:
        st.download_button(
            "Download PDF",
            data=pdf_bytes,
            file_name=f"{file_stem}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )


st.set_page_config(page_title="AI Research Agent", layout="centered")

with st.sidebar:
    st.title("AI Research Agent")
    st.markdown(
        """
        Enter a research topic and submit to preview how results will appear.
        This is a starter layout; plug in your retrieval or LLM pipeline next.
        """
    )
    st.divider()
    st.subheader("Saved reports")
    report_items = list_reports()
    if report_items:
        labels = [
            f"{item['created_at'][:19].replace('T', ' ')} | {item['topic']}" for item in report_items
        ]
        selected_label = st.selectbox("History", options=labels, index=0)
        selected_idx = labels.index(selected_label)
        selected_report_id = report_items[selected_idx]["id"]
        if st.button("Load selected report", use_container_width=True):
            payload = load_report(selected_report_id)
            st.session_state.active_result = payload["result"]
            st.session_state.submitted_topic = payload.get("topic", "")
            st.session_state.active_report_id = payload.get("id", selected_report_id)
    else:
        st.caption("No saved reports yet.")

st.header("Research a topic")

if "submitted_topic" not in st.session_state:
    st.session_state.submitted_topic = ""
if "active_result" not in st.session_state:
    st.session_state.active_result = None
if "active_report_id" not in st.session_state:
    st.session_state.active_report_id = ""

topic = st.text_input("Research topic", placeholder="e.g., causal inference in econometrics")

if st.button("Submit", type="primary"):
    st.session_state.submitted_topic = topic.strip()
    if st.session_state.submitted_topic:
        with st.spinner("Gathering results..."):
            result = fetch_research(st.session_state.submitted_topic)
        if result["status"] == "ok":
            report_id = save_report(st.session_state.submitted_topic, result)
            st.session_state.active_result = result
            st.session_state.active_report_id = report_id
        else:
            st.session_state.active_result = {"status": "error", "error": result["error"]}
            st.session_state.active_report_id = ""

if st.session_state.active_result:
    if st.session_state.active_result["status"] == "ok":
        if st.session_state.active_report_id:
            st.caption(f"Saved report ID: {st.session_state.active_report_id}")
        render_result(st.session_state.active_result, st.session_state.active_report_id)
    else:
        st.error(st.session_state.active_result["error"])
else:
    st.caption("Submit a topic to generate and save your first report.")
