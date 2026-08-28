"""Temporary action storage for the first end-to-end prototype slice."""

from uuid import UUID

from app.models.actions import (
    Action,
    ActionResolution,
    ActionStatus,
    EmailActionDetails,
    ResolvedContact,
    ResolvedDocument,
)
from app.services.resolution import resolve_contact, resolve_document


class ActionStore:
    """Keeps actions in memory until the core flow is proven.

    This intentionally loses data when FastAPI restarts. SQLite will replace
    this class after creation, resolution, approval, and execution work together.
    """

    def __init__(self) -> None:
        self._actions: dict[UUID, Action] = {}

    def create(self, action: Action) -> Action:
        self._actions[action.id] = action
        return action

    def get(self, action_id: UUID) -> Action | None:
        return self._actions.get(action_id)

    def clear(self) -> None:
        """Used by tests to guarantee each scenario starts clean."""
        self._actions.clear()

    def resolve(self, action_id: UUID) -> Action | None:
        action = self.get(action_id)
        if action is None:
            return None

        if action.status is not ActionStatus.DETECTED:
            raise ValueError("Only newly detected actions can be resolved.")
        if not isinstance(action.details, EmailActionDetails):
            raise ValueError("Only email resolution is supported in this checkpoint.")

        action.transition_to(ActionStatus.RESOLVING)
        contact_result = resolve_contact(action.details.recipient_query)
        document_result = resolve_document(action.details.attachment_query)

        action.resolution = ActionResolution(
            recipient=(
                ResolvedContact(**contact_result.resolved.__dict__)
                if contact_result.is_resolved
                else None
            ),
            attachment=(
                ResolvedDocument(**document_result.resolved.__dict__)
                if document_result.is_resolved
                else None
            ),
            recipient_candidates=[
                ResolvedContact(**contact.__dict__) for contact in contact_result.matches
            ],
            attachment_candidates=[
                ResolvedDocument(**document.__dict__)
                for document in document_result.matches
            ],
            missing_fields=[
                field
                for field, result in (
                    ("recipient", contact_result),
                    ("attachment", document_result),
                )
                if result.is_missing
            ],
        )

        if contact_result.is_resolved and document_result.is_resolved:
            action.transition_to(ActionStatus.READY_FOR_APPROVAL)
        else:
            action.transition_to(ActionStatus.NEEDS_INPUT)

        return action


action_store = ActionStore()
