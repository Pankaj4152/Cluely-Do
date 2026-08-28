"""Endpoint for detecting supported commitments in transcript text."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.models.actions import Action, ActionType
from app.models.commitments import (
    DetectionResult,
    ProcessCommitmentResult,
    ProcessedCommitment,
)
from app.services.commitment_detector import detect_commitment
from app.services.action_store import action_store


router = APIRouter(prefix="/api/commitments", tags=["commitments"])


class DetectCommitmentRequest(BaseModel):
    transcript: str = Field(min_length=1)


@router.post("/detect", response_model=DetectionResult)
def detect(request: DetectCommitmentRequest) -> DetectionResult:
    return detect_commitment(request.transcript)


@router.post("/process", response_model=ProcessCommitmentResult)
def process(request: DetectCommitmentRequest) -> ProcessCommitmentResult:
    """Detect, create, and resolve a commitment as one safe backend workflow."""
    detection = detect_commitment(request.transcript)
    if not hasattr(detection, "details"):
        return detection

    action = action_store.create(
        Action(type=ActionType.SEND_EMAIL, details=detection.details)
    )
    resolved_action = action_store.resolve(action.id)
    if resolved_action is None:  # Defensive: a just-created action must exist.
        raise RuntimeError("Created action could not be found for resolution.")

    return ProcessedCommitment(status=resolved_action.status, action=resolved_action)
