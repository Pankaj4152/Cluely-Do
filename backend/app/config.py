"""Local configuration. Secrets remain in ignored files, never source control."""

import os
from pathlib import Path

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")

GMAIL_CLIENT_SECRET_PATH = BACKEND_DIR / os.environ.get(
    "GMAIL_CLIENT_SECRET_PATH", "secrets/gmail-client.json"
)
GMAIL_TOKEN_PATH = BACKEND_DIR / os.environ.get(
    "GMAIL_TOKEN_PATH", "secrets/gmail-token.json"
)
GMAIL_OAUTH_REDIRECT_URI = os.environ.get(
    "GMAIL_OAUTH_REDIRECT_URI",
    "http://127.0.0.1:8000/api/integrations/gmail/callback",
)
FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")
