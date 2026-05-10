# -*- coding: utf-8 -*-
"""Persistence helpers for saved research reports."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List
from uuid import uuid4

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
