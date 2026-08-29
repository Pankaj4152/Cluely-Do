"""OAuth connection for the user's Gmail account in the local prototype."""

from __future__ import annotations

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

from app.config import GMAIL_CLIENT_SECRET_PATH, GMAIL_OAUTH_REDIRECT_URI, GMAIL_TOKEN_PATH


# Needed for sending later and reading the sent message for verification.
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
_pending_oauth_state: str | None = None


def _flow() -> Flow:
    if not GMAIL_CLIENT_SECRET_PATH.exists():
        raise RuntimeError("Gmail OAuth client file is missing from backend/secrets.")
    return Flow.from_client_secrets_file(
        str(GMAIL_CLIENT_SECRET_PATH),
        scopes=GMAIL_SCOPES,
        redirect_uri=GMAIL_OAUTH_REDIRECT_URI,
    )


def get_valid_credentials() -> Credentials | None:
    """Load and refresh the locally stored user token when possible."""
    if not GMAIL_TOKEN_PATH.exists():
        return None
    credentials = Credentials.from_authorized_user_file(str(GMAIL_TOKEN_PATH), GMAIL_SCOPES)
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        GMAIL_TOKEN_PATH.write_text(credentials.to_json(), encoding="utf-8")
    return credentials if credentials.valid else None


def begin_authorization() -> str:
    """Return Google's consent URL and remember state for the local callback."""
    global _pending_oauth_state
    flow = _flow()
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    _pending_oauth_state = state
    return authorization_url


def complete_authorization(code: str, state: str | None) -> None:
    """Exchange Google's callback code for a local, ignored refresh token."""
    if not state or state != _pending_oauth_state:
        raise ValueError("OAuth state did not match the connection request.")
    flow = _flow()
    flow.fetch_token(code=code)
    GMAIL_TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    GMAIL_TOKEN_PATH.write_text(flow.credentials.to_json(), encoding="utf-8")
