"""Connection endpoints for external services."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from googleapiclient.discovery import build
from pydantic import BaseModel

from app.config import FRONTEND_ORIGIN
from app.services.gmail_oauth import begin_authorization, complete_authorization, get_valid_credentials


router = APIRouter(prefix="/api/integrations/gmail", tags=["integrations"])


class GmailConnectionStatus(BaseModel):
    connected: bool
    email: str | None = None


@router.get("/status", response_model=GmailConnectionStatus)
def gmail_status() -> GmailConnectionStatus:
    credentials = get_valid_credentials()
    if credentials is None:
        return GmailConnectionStatus(connected=False)
    service = build("gmail", "v1", credentials=credentials)
    profile = service.users().getProfile(userId="me").execute()
    return GmailConnectionStatus(connected=True, email=profile.get("emailAddress"))


@router.get("/connect")
def connect_gmail() -> RedirectResponse:
    try:
        return RedirectResponse(begin_authorization())
    except RuntimeError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.get("/callback")
def gmail_callback(code: str | None = None, state: str | None = None, error: str | None = None) -> RedirectResponse:
    if error:
        return RedirectResponse(f"{FRONTEND_ORIGIN}?gmail=denied")
    if not code:
        return RedirectResponse(f"{FRONTEND_ORIGIN}?gmail=failed")
    try:
        complete_authorization(code, state)
    except Exception:
        return RedirectResponse(f"{FRONTEND_ORIGIN}?gmail=failed")
    return RedirectResponse(f"{FRONTEND_ORIGIN}?gmail=connected")
