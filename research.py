# -*- coding: utf-8 -*-
"""Starter research backend using Wikipedia's public API."""

from __future__ import annotations

from typing import Dict, List

import requests

MIN_SUMMARY_LENGTH = 120

LOCAL_STARTER_KB = {
    "machine learning": (
        "Machine learning is a field of AI focused on building models that learn patterns "
        "from data and generalize to unseen examples."
    ),
    "artificial intelligence": (
        "Artificial intelligence covers methods that enable computers to perform tasks "
        "that usually require human reasoning, perception, and decision-making."
    ),
    "causal inference": (
        "Causal inference studies cause-and-effect relationships using experimental and "
        "observational data, often through assumptions encoded in causal graphs."
    ),
}


def _search_wikipedia(topic: str) -> List[Dict[str, str]]:
    """Return up to 3 candidate pages for the topic."""
    url = "https://en.wikipedia.org/w/rest.php/v1/search/title"
    response = requests.get(url, params={"q": topic, "limit": 3}, timeout=10)
    response.raise_for_status()
    payload = response.json()

    pages = []
    for item in payload.get("pages", []):
        key = item.get("key", "")
        title = item.get("title", "Untitled")
        if key:
            pages.append(
                {
                    "title": title,
                    "key": key,
                    "url": f"https://en.wikipedia.org/wiki/{key}",
                    "source": "Wikipedia",
                }
            )
    return pages


def _dedupe_references(references: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Remove duplicate references while preserving order."""
    deduped = []
    seen = set()
    for ref in references:
        url = ref.get("url", "")
        if not url or url in seen:
            continue
        seen.add(url)
        deduped.append(ref)
    return deduped


def _get_summary(page_key: str) -> str:
    """Get summary text for a selected Wikipedia page key."""
    summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_key}"
    response = requests.get(summary_url, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data.get("extract") or "No summary found for this topic."


def _build_key_points(summary: str) -> List[str]:
    """Create a few key points from summary text."""
    sentences = [part.strip() for part in summary.replace("\n", " ").split(".") if part.strip()]
    key_points = []
    for sentence in sentences[:3]:
        normalized = sentence.rstrip(".")
        key_points.append(normalized)
    if not key_points:
        key_points.append("No key points could be extracted yet.")
    return key_points


def _build_next_questions(topic: str, key_points: List[str]) -> List[str]:
    """Generate starter follow-up questions for deeper research."""
    return [
        f"What are the most important recent advances in {topic}?",
        f"What are common limitations or criticisms of current {topic} approaches?",
        f"Which datasets, benchmarks, or case studies are most useful for studying {topic}?",
    ]


def _score_confidence(references: List[Dict[str, str]], summary: str, warning: str = "") -> float:
    """Compute a simple confidence score from source quality signals."""
    score = 0.45
    score += min(len(references), 3) * 0.15
    if len(summary.strip()) >= MIN_SUMMARY_LENGTH:
        score += 0.15
    if warning:
        score -= 0.2
    return max(0.1, min(0.95, round(score, 2)))


def _confidence_label(score: float) -> str:
    if score >= 0.75:
        return "high"
    if score >= 0.5:
        return "medium"
    return "low"


def _build_key_point_evidence(
    key_points: List[str], references: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    """Attach source evidence metadata to each key point."""
    evidence = []
    primary = references[0] if references else {"title": "Unknown source", "url": ""}
    for idx, point in enumerate(key_points, start=1):
        evidence.append(
            {
                "id": f"kp-{idx}",
                "point": point,
                "source_title": primary.get("title", "Unknown source"),
                "source_url": primary.get("url", ""),
                "why": "Derived from the top summary source for this topic.",
            }
        )
    return evidence


def _build_research_brief(result: Dict[str, object]) -> str:
    """Create a copy-friendly research brief."""
    lines = [
        f"Topic: {result['topic']}",
        f"Confidence: {result['confidence']['score']} ({result['confidence']['label']})",
        "",
        "Summary:",
        str(result["summary"]),
        "",
        "Key points:",
    ]
    for item in result.get("key_point_evidence", []):
        lines.append(f"- {item['point']}")
    lines.append("")
    lines.append("References:")
    for ref in result.get("references", []):
        lines.append(f"- {ref['title']}: {ref['url']}")
    return "\n".join(lines)


def fetch_research(topic: str) -> Dict[str, object]:
    """Fetch starter research data for a topic from Wikipedia."""
    cleaned_topic = topic.strip()
    if not cleaned_topic:
        return {"status": "error", "error": "Please enter a research topic."}

    try:
        references = _dedupe_references(_search_wikipedia(cleaned_topic))
        if not references:
            return {"status": "error", "error": f"No results found for '{cleaned_topic}'."}

        summary = _get_summary(references[0]["key"])
        if len(summary.strip()) < MIN_SUMMARY_LENGTH:
            summary = (
                f"{summary}\n\nNote: The available summary is short. "
                "Treat this as a starting point and verify with additional sources."
            )
        key_points = _build_key_points(summary)
        next_questions = _build_next_questions(cleaned_topic, key_points)
        key_point_evidence = _build_key_point_evidence(key_points, references)
        confidence_score = _score_confidence(references, summary)
        result = {
            "status": "ok",
            "topic": cleaned_topic,
            "summary": summary,
            "key_points": key_points,
            "key_point_evidence": key_point_evidence,
            "next_questions": next_questions,
            "references": [{"title": ref["title"], "url": ref["url"]} for ref in references],
            "confidence": {
                "score": confidence_score,
                "label": _confidence_label(confidence_score),
            },
        }
        result["brief"] = _build_research_brief(result)
        return result
    except requests.RequestException as exc:
        # Fallback keeps the app useful in restricted-network environments.
        warning = f"Live source unavailable: {exc}"
        fallback_summary = LOCAL_STARTER_KB.get(
            cleaned_topic.lower(),
            (
                f"No live web result was available for '{cleaned_topic}'. "
                "This is a local fallback response; add your own corpus or API key-backed source next."
            ),
        )
        references = [
            {
                "title": "Local fallback (network unavailable)",
                "url": "https://en.wikipedia.org/",
            }
        ]
        key_points = _build_key_points(fallback_summary)
        fallback_score = _score_confidence(references, fallback_summary, warning=warning)
        result = {
            "status": "ok",
            "topic": cleaned_topic,
            "summary": fallback_summary,
            "key_points": key_points,
            "key_point_evidence": _build_key_point_evidence(key_points, references),
            "next_questions": _build_next_questions(cleaned_topic, key_points),
            "references": references,
            "confidence": {
                "score": fallback_score,
                "label": _confidence_label(fallback_score),
            },
            "warning": warning,
        }
        result["brief"] = _build_research_brief(result)
        return result
