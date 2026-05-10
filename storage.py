# -*- coding: utf-8 -*-
"""Persistence helpers for saved research reports."""

from __future__ import annotations

import json
from io import BytesIO
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List
from uuid import uuid4

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

REPORTS_DIR = Path(__file__).parent / "data" / "reports"


def _ensure_reports_dir() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def save_report(topic: str, result: Dict[str, object]) -> str:
    """Persist a research result and return report id."""
    _ensure_reports_dir()
    created_at = datetime.now(timezone.utc).isoformat()
    report_id = f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:8]}"
    payload = {
        "id": report_id,
        "topic": topic,
        "created_at": created_at,
        "result": result,
    }
    path = REPORTS_DIR / f"{report_id}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return report_id


def list_reports() -> List[Dict[str, str]]:
    """List saved reports, newest first."""
    _ensure_reports_dir()
    reports = []
    for path in sorted(REPORTS_DIR.glob("*.json"), reverse=True):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            reports.append(
                {
                    "id": payload.get("id", path.stem),
                    "topic": payload.get("topic", "unknown topic"),
                    "created_at": payload.get("created_at", ""),
                }
            )
        except json.JSONDecodeError:
            continue
    return reports


def load_report(report_id: str) -> Dict[str, object]:
    """Load one report payload by id."""
    path = REPORTS_DIR / f"{report_id}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload


def report_to_markdown(result: Dict[str, object]) -> str:
    """Convert a research result payload into Markdown."""
    lines = [
        f"# Research Report: {result.get('topic', 'Unknown topic')}",
        "",
        f"Confidence: **{result.get('confidence', {}).get('score', 'n/a')}** "
        f"({result.get('confidence', {}).get('label', 'unknown')})",
        "",
        "## Summary",
        str(result.get("summary", "")),
        "",
        "## Key Points",
    ]
    for item in result.get("key_point_evidence", []):
        lines.append(f"- {item.get('point', '')}")
    lines.extend(["", "## Next Questions"])
    for question in result.get("next_questions", []):
        lines.append(f"- {question}")
    lines.extend(["", "## References"])
    for ref in result.get("references", []):
        lines.append(f"- [{ref.get('title', 'ref')}]({ref.get('url', '')})")
    return "\n".join(lines)


def report_to_pdf_bytes(result: Dict[str, object]) -> bytes:
    """Convert a research result payload into a downloadable PDF."""
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER
    y = height - 50
    line_height = 14

    def write_line(text: str) -> None:
        nonlocal y
        if y < 50:
            pdf.showPage()
            y = height - 50
        pdf.drawString(50, y, text[:110])
        y -= line_height

    write_line(f"Research Report: {result.get('topic', 'Unknown topic')}")
    confidence = result.get("confidence", {})
    write_line(
        f"Confidence: {confidence.get('score', 'n/a')} ({confidence.get('label', 'unknown')})"
    )
    write_line("")
    write_line("Summary:")
    for line in str(result.get("summary", "")).split("\n"):
        write_line(line)
    write_line("")
    write_line("Key Points:")
    for item in result.get("key_point_evidence", []):
        write_line(f"- {item.get('point', '')}")
    write_line("")
    write_line("References:")
    for ref in result.get("references", []):
        write_line(f"- {ref.get('title', 'ref')}: {ref.get('url', '')}")

    pdf.save()
    return buffer.getvalue()
