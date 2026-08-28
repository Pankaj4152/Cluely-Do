"""Schemas for turning transcript text into proposed action intent."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from app.models.actions import ActionType, EmailActionDetails


class DetectionStatus(StrEnum):
    DETECTED = "DETECTED"
    UNSUPPORTED = "UNSUPPORTED"


class DetectedCommitment(BaseModel):
    """A commitment that the demo detector can safely turn into an action."""

    status: DetectionStatus = DetectionStatus.DETECTED
    action_type: ActionType = ActionType.SEND_EMAIL
    details: EmailActionDetails


class UnsupportedCommitment(BaseModel):
    """A transcript the detector intentionally does not claim to understand."""

    status: DetectionStatus = DetectionStatus.UNSUPPORTED
    reason: str


DetectionResult = DetectedCommitment | UnsupportedCommitment
