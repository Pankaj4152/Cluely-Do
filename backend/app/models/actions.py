"""The reliable, structured representation of a proposed user action."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

class ActionType(StrEnum):
    """The deliberately small set of actions supported by the MVP."""

    SEND_EMAIL = "SEND_EMAIL"
    CREATE_CALENDAR_EVENT = "CREATE_CALENDAR_EVENT"


class ActionStatus(StrEnum):
    """Every meaningful point in an action's lifecycle."""

    DETECTED = "DETECTED"                           # The action has been detected but not yet processed.
    RESOLVING = "RESOLVING"                         # The action is being processed to determine if it can be executed.
    NEEDS_INPUT = "NEEDS_INPUT"                     # The action requires additional information from the user before it can be executed.
    READY_FOR_APPROVAL = "READY_FOR_APPROVAL"       # The action is ready for user approval before it can be executed.
    EXECUTING = "EXECUTING"                         # The action is currently being executed.
    VERIFIED = "VERIFIED"                           # The action has been executed and verified to have completed successfully.
    FAILED = "FAILED"                               # The action has been executed but failed to complete successfully.
    CANCELLED = "CANCELLED"                         # The action has been cancelled.  


# This map is the state machine. Keeping it in code makes invalid transitions
# impossible regardless of whether they come from a UI click or future API call.
ALLOWED_TRANSITIONS: dict[ActionStatus, set[ActionStatus]] = {
    ActionStatus.DETECTED: {ActionStatus.RESOLVING},
    ActionStatus.RESOLVING: {
        ActionStatus.NEEDS_INPUT,
        ActionStatus.READY_FOR_APPROVAL,
        ActionStatus.FAILED,
    },
    ActionStatus.NEEDS_INPUT: {
        ActionStatus.RESOLVING,
        ActionStatus.CANCELLED,
    },
    ActionStatus.READY_FOR_APPROVAL: {
        ActionStatus.EXECUTING,
        ActionStatus.CANCELLED,
    },
    ActionStatus.EXECUTING: {ActionStatus.VERIFIED, ActionStatus.FAILED},
    ActionStatus.VERIFIED: set(),
    ActionStatus.FAILED: set(),
    ActionStatus.CANCELLED: set(),
}


class EmailActionDetails(BaseModel):
    """Information extracted from a commitment to send an email.

    These are *queries*, not resolved facts. For example, ``recipient_query``
    can be "Sarah" until contact resolution finds exactly one Sarah.
    """

    recipient_query: str = Field(min_length=1, examples=["Sarah"])
    attachment_query: str = Field(min_length=1, examples=["pricing deck"])
    instructions: str = Field(min_length=1, examples=["Send the pricing deck"])
    execute_at: datetime | None = None


class CalendarEventDetails(BaseModel):
    """Information extracted from a commitment to create an event."""

    title: str = Field(min_length=1, examples=["Follow-up with Sarah"])
    start_at: datetime | None = None
    attendee_queries: list[str] = Field(default_factory=list)


class ResolvedContact(BaseModel):
    """A contact selected only after deterministic resolution."""

    id: str
    name: str
    email: str
    company: str


class ResolvedDocument(BaseModel):
    """A document selected only after deterministic resolution."""

    id: str
    name: str
    path: str


class ActionResolution(BaseModel):
    """Evidence produced while resolving a proposed action."""

    recipient: ResolvedContact | None = None
    attachment: ResolvedDocument | None = None
    recipient_candidates: list[ResolvedContact] = Field(default_factory=list)
    attachment_candidates: list[ResolvedDocument] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)


class Action(BaseModel):
    """A proposed action, from detection through a verified result.

    ``details`` stays generic for now because each action type has different
    fields. Step 2.4 will validate the correct detail model at the API boundary.
    """

    id: UUID = Field(default_factory=uuid4)
    type: ActionType
    status: ActionStatus = ActionStatus.DETECTED
    details: EmailActionDetails | CalendarEventDetails
    resolution: ActionResolution | None = None
    requires_approval: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def transition_to(self, next_status: ActionStatus) -> None:
        """Move forward only through a valid lifecycle transition.

        Raises:
            ValueError: if the requested transition skips a required safety step.
        """
        allowed = ALLOWED_TRANSITIONS[self.status]
        if next_status not in allowed:
            raise ValueError(
                f"Cannot transition action from {self.status} to {next_status}."
            )
        self.status = next_status
        self.updated_at = datetime.now()
