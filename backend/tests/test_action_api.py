import unittest

from fastapi.testclient import TestClient

from app.main import app
from app.services.action_store import action_store


class ActionApiTests(unittest.TestCase):
    def setUp(self) -> None:
        action_store.clear()
        self.client = TestClient(app)

    def create_email_action(self, recipient: str, attachment: str) -> dict:
        response = self.client.post(
            "/api/actions",
            json={
                "details": {
                    "recipient_query": recipient,
                    "attachment_query": attachment,
                    "instructions": f"Send {attachment} to {recipient}",
                    "execute_at": "2026-08-30T09:00:00",
                }
            },
        )
        self.assertEqual(response.status_code, 201)
        return response.json()

    def test_create_fetch_and_resolve_unique_action(self) -> None:
        created = self.create_email_action("Sarah", "Acme pricing deck")
        self.assertEqual(created["status"], "DETECTED")

        fetched = self.client.get(f"/api/actions/{created['id']}")
        self.assertEqual(fetched.status_code, 200)
        self.assertEqual(fetched.json()["id"], created["id"])

        resolved = self.client.post(f"/api/actions/{created['id']}/resolve")
        body = resolved.json()
        self.assertEqual(resolved.status_code, 200)
        self.assertEqual(body["status"], "READY_FOR_APPROVAL")
        self.assertEqual(body["resolution"]["recipient"]["email"], "sarah@acme.com")
        self.assertEqual(
            body["resolution"]["attachment"]["name"], "Acme Pricing Deck.pdf"
        )

    def test_ambiguous_recipient_needs_input(self) -> None:
        created = self.create_email_action("Alex", "Acme pricing deck")

        resolved = self.client.post(f"/api/actions/{created['id']}/resolve")
        body = resolved.json()

        self.assertEqual(resolved.status_code, 200)
        self.assertEqual(body["status"], "NEEDS_INPUT")
        self.assertEqual(len(body["resolution"]["recipient_candidates"]), 2)
        self.assertIsNone(body["resolution"]["recipient"])

    def test_unknown_action_returns_not_found(self) -> None:
        response = self.client.get("/api/actions/00000000-0000-0000-0000-000000000000")

        self.assertEqual(response.status_code, 404)

    def test_approve_ready_action_runs_mock_execution_and_verifies(self) -> None:
        created = self.create_email_action("Sarah", "Acme pricing deck")
        self.client.post(f"/api/actions/{created['id']}/resolve")

        approved = self.client.post(f"/api/actions/{created['id']}/approve")
        body = approved.json()

        self.assertEqual(approved.status_code, 200)
        self.assertEqual(body["status"], "VERIFIED")
        self.assertEqual(body["execution"]["provider"], "mock_gmail")
        self.assertTrue(all(check["passed"] for check in body["execution"]["verification_checks"]))
        self.assertIn("Action approved by user", [entry["message"] for entry in body["log"]])
        self.assertIn("Action complete", [entry["message"] for entry in body["log"]])

    def test_cannot_approve_action_before_resolution(self) -> None:
        created = self.create_email_action("Sarah", "Acme pricing deck")

        response = self.client.post(f"/api/actions/{created['id']}/approve")

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["detail"], "Only actions ready for approval can be approved.")

    def test_cancel_ready_action_and_block_later_approval(self) -> None:
        created = self.create_email_action("Sarah", "Acme pricing deck")
        self.client.post(f"/api/actions/{created['id']}/resolve")

        cancelled = self.client.post(f"/api/actions/{created['id']}/cancel")
        approval_attempt = self.client.post(f"/api/actions/{created['id']}/approve")

        self.assertEqual(cancelled.status_code, 200)
        self.assertEqual(cancelled.json()["status"], "CANCELLED")
        self.assertEqual(approval_attempt.status_code, 409)


if __name__ == "__main__":
    unittest.main()
