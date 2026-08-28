"""A deliberately small, deterministic commitment detector for the demo."""

from datetime import datetime, timedelta
import re

from app.models.actions import EmailActionDetails
from app.models.commitments import (
    DetectedCommitment,
    DetectionResult,
    UnsupportedCommitment,
)


# We recognise a single clear commitment form spoken by the action owner.
# This avoids treating Sarah's request ("Could you send…") as proof that the
# user agreed to perform it.
EMAIL_COMMITMENT_PATTERN = re.compile(
    r"\b(?:i['’]ll|i will)\s+send\s+"
    r"(?P<recipient>[A-Za-z]+)\s+"
    r"(?:the\s+)?(?P<attachment>.+?)"
    r"[.!?]?$",
    re.IGNORECASE,
)

RELATIVE_TIME_SUFFIX = re.compile(r"\s+(?:tomorrow(?:\s+morning)?|today)$", re.IGNORECASE)


def _normalise_phrase(value: str) -> str:
    return " ".join(value.strip().split())


def _execution_time(transcript: str, reference_time: datetime) -> datetime | None:
    """Use an explicit, reviewable demo default for relative dates."""
    lower_transcript = transcript.lower()
    if "tomorrow" in lower_transcript:
        tomorrow = reference_time.date() + timedelta(days=1)
        return datetime.combine(tomorrow, datetime.min.time()).replace(hour=9)
    if "today" in lower_transcript:
        return reference_time.replace(hour=9, minute=0, second=0, microsecond=0)
    return None


def detect_commitment(
    transcript: str, *, reference_time: datetime | None = None
) -> DetectionResult:
    """Return structured intent only when the supported pattern is unambiguous.

    The caller can inject ``reference_time`` in tests. In the real app, the
    current local time is used and the proposed time remains visible/editable
    on the approval screen.
    """
    match = EMAIL_COMMITMENT_PATTERN.search(transcript.strip())
    if match is None:
        return UnsupportedCommitment(
            reason=(
                "No supported first-person email commitment was found. "
                "Try: 'I'll send Sarah the Acme pricing deck tomorrow morning.'"
            )
        )

    recipient = _normalise_phrase(match.group("recipient"))
    attachment_without_time = RELATIVE_TIME_SUFFIX.sub("", match.group("attachment"))
    attachment = _normalise_phrase(attachment_without_time)
    if not recipient or not attachment:
        return UnsupportedCommitment(reason="Recipient or attachment is missing.")

    reference = reference_time or datetime.now()
    return DetectedCommitment(
        details=EmailActionDetails(
            recipient_query=recipient,
            attachment_query=attachment,
            instructions=f"Send {attachment} to {recipient}",
            execute_at=_execution_time(transcript, reference),
        )
    )
