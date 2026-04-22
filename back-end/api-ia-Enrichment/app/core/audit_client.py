import json
import logging
from typing import Any
from urllib import request
from urllib.error import URLError, HTTPError

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def send_audit_event(
    event_type: str,
    source_service: str,
    reference_id: str,
    payload_summary: dict[str, Any],
) -> bool:
    settings = get_settings()
    url = f"{settings.audit_service_url.rstrip('/')}/audit/events"

    payload = {
        "event_type": event_type,
        "source_service": source_service,
        "reference_id": reference_id,
        "payload_summary": payload_summary,
    }

    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url=url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=settings.audit_timeout_seconds) as response:
            return 200 <= response.status < 300
    except HTTPError as exc:
        logger.warning("Audit API HTTP error: %s", exc)
    except URLError as exc:
        logger.warning("Audit API connection error: %s", exc)
    except Exception as exc:
        logger.warning("Unexpected error sending audit event: %s", exc)

    return False
