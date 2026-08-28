from datetime import datetime
import unittest

from app.models.actions import (
    Action,
    ActionStatus,
    ActionType,
    EmailActionDetails,
)


def make_email_action() -> Action:
    return Action(
        type=ActionType.SEND_EMAIL,
        details=EmailActionDetails(
            recipient_query="Sarah",
            attachment_query="pricing deck",
            instructions="Send Sarah the pricing deck",
            execute_at=datetime(2026, 8, 30, 9, 0),
        ),
    )


class ActionLifecycleTests(unittest.TestCase):
    def test_email_action_starts_detected_and_requires_approval(self) -> None:
        action = make_email_action()

        self.assertEqual(action.status, ActionStatus.DETECTED)
        self.assertTrue(action.requires_approval)
        self.assertEqual(action.details.recipient_query, "Sarah")

    def test_valid_lifecycle_reaches_verified(self) -> None:
        action = make_email_action()

        for status in (
            ActionStatus.RESOLVING,
            ActionStatus.READY_FOR_APPROVAL,
            ActionStatus.EXECUTING,
            ActionStatus.VERIFIED,
        ):
            action.transition_to(status)

        self.assertEqual(action.status, ActionStatus.VERIFIED)

    def test_invalid_transition_is_rejected(self) -> None:
        action = make_email_action()

        with self.assertRaises(ValueError):
            action.transition_to(ActionStatus.EXECUTING)


if __name__ == "__main__":
    unittest.main()
