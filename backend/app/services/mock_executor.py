"""Deterministic stand-in for Gmail while the approval flow is being built."""

from uuid import uuid4

from app.models.actions import Action, ExecutionResult, VerificationCheck


def execute_email(action: Action) -> ExecutionResult:
    """Produce provider-like evidence only for an approved, resolved action.

    This isolates provider execution behind one function. Gmail API integration
    can later replace this implementation without changing approval policy,
    resolution logic, or the frontend contract.
    """
    resolution = action.resolution
    recipient_ok = resolution is not None and resolution.recipient is not None
    attachment_ok = resolution is not None and resolution.attachment is not None

    return ExecutionResult(
        provider="mock_gmail",
        provider_id=f"mock-message-{uuid4()}",
        verification_checks=[
            VerificationCheck(label="Recipient verified", passed=recipient_ok),
            VerificationCheck(label="Attachment verified", passed=attachment_ok),
            VerificationCheck(label="Provider message created", passed=True),
        ],
    )
