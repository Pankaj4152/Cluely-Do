"""Real Gmail execution, invoked only after explicit approval."""

import base64
from email.message import EmailMessage
from pathlib import Path

from googleapiclient.discovery import build

from app.config import PROJECT_ROOT
from app.models.actions import Action, ExecutionResult, VerificationCheck
from app.services.gmail_oauth import get_valid_credentials


def execute_email(action: Action) -> ExecutionResult:
    resolution = action.resolution
    if resolution is None or resolution.recipient is None or resolution.attachment is None:
        raise ValueError("Gmail execution requires a resolved recipient and attachment.")
    credentials = get_valid_credentials()
    if credentials is None:
        raise ValueError("Gmail is not connected.")

    attachment_path = PROJECT_ROOT / resolution.attachment.path
    if not attachment_path.exists():
        raise ValueError(f"Attachment file is missing: {resolution.attachment.name}")

    message = EmailMessage()
    message["To"] = resolution.recipient.email
    message["Subject"] = resolution.attachment.name.removesuffix(".pdf")
    first_name = resolution.recipient.name.split()[0]
    message.set_content(f"Hi {first_name},\n\nAs promised, I have attached the requested deck.\n\nBest,\nPankaj")
    message.add_attachment(attachment_path.read_bytes(), maintype="application", subtype="pdf", filename=resolution.attachment.name)

    service = build("gmail", "v1", credentials=credentials)
    sent = service.users().messages().send(userId="me", body={"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}).execute()
    fetched = service.users().messages().get(userId="me", id=sent["id"], format="full").execute()
    headers = {header["name"].lower(): header["value"] for header in fetched.get("payload", {}).get("headers", [])}
    filenames = [part.get("filename") for part in fetched.get("payload", {}).get("parts", [])]

    return ExecutionResult(
        provider="gmail",
        provider_id=sent["id"],
        verification_checks=[
            VerificationCheck(label="Recipient verified", passed=resolution.recipient.email in headers.get("to", "")),
            VerificationCheck(label="Attachment verified", passed=resolution.attachment.name in filenames),
            VerificationCheck(label="Gmail message fetched", passed=bool(fetched.get("id"))),
        ],
    )
