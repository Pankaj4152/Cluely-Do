"""Endpoint for detecting supported commitments in transcript text."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.models.commitments import DetectionResult
from app.services.commitment_detector import detect_commitment


router = APIRouter(prefix="/api/commitments", tags=["commitments"])


class DetectCommitmentRequest(BaseModel):
    transcript: str = Field(min_length=1)


@router.post("/detect", response_model=DetectionResult)
def detect(request: DetectCommitmentRequest) -> DetectionResult:
    return detect_commitment(request.transcript)
