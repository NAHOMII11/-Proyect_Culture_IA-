"""Registro de eventos en el Audit Service."""
from __future__ import annotations

import json
import logging
import os
from typing import Any
from urllib import request
from urllib.error import HTTPError, URLError

logger = logging.getLogger(__name__)


def _audit_events_url() -> str:
    base = os.getenv("AUDIT_SERVICE_URL", "http://audit_api:8008").rstrip("/")
    if base.endswith("/audit/events"):
        return base
    return f"{base}/audit/events"


def send_audit_event(
    event_type: str,
    source_service: str,
    reference_id: str,
    payload_summary: dict[str, Any] | None = None,
) -> bool:
    payload = {
        "event_type": event_type,
        "source_service": source_service,
        "reference_id": reference_id,
        "payload_summary": payload_summary or {},
    }

    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url=_audit_events_url(),
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        timeout = float(os.getenv("AUDIT_TIMEOUT_SECONDS", "5"))
        with request.urlopen(req, timeout=timeout) as response:
            return 200 <= response.status < 300
    except HTTPError as exc:
        logger.warning("Audit API HTTP error (%s): %s", event_type, exc)
    except URLError as exc:
        logger.warning("Audit API connection error (%s): %s", event_type, exc)
    except Exception as exc:
        logger.warning("Audit API unexpected error (%s): %s", event_type, exc)

    return False
