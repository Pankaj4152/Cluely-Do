import unittest

from fastapi.testclient import TestClient

from app.main import app
from app.services.action_store import action_store


class CommitmentApiTests(unittest.TestCase):
    def setUp(self) -> None:
        action_store.clear()
        self.client = TestClient(app)

    def test_detect_endpoint_returns_structured_email_intent(self) -> None:
        response = self.client.post(
            "/api/commitments/detect",
            json={
                "transcript": "I'll send Sarah the Acme pricing deck tomorrow morning."
            },
        )

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["status"], "DETECTED")
        self.assertEqual(body["action_type"], "SEND_EMAIL")
        self.assertEqual(body["details"]["recipient_query"], "Sarah")
        self.assertEqual(body["details"]["attachment_query"], "Acme pricing deck")

    def test_detect_endpoint_returns_unsupported_for_non_commitment(self) -> None:
        response = self.client.post(
            "/api/commitments/detect",
            json={"transcript": "The pricing deck looked great."},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "UNSUPPORTED")

    def test_process_endpoint_returns_action_ready_for_approval(self) -> None:
        response = self.client.post(
            "/api/commitments/process",
            json={
                "transcript": "I'll send Sarah the Acme pricing deck tomorrow morning."
            },
        )

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["status"], "READY_FOR_APPROVAL")
        self.assertEqual(body["action"]["resolution"]["recipient"]["name"], "Sarah Chen")
        self.assertEqual(
            body["action"]["resolution"]["attachment"]["name"],
            "Acme Pricing Deck.pdf",
        )

    def test_process_endpoint_returns_needs_input_for_ambiguous_contact(self) -> None:
        response = self.client.post(
            "/api/commitments/process",
            json={"transcript": "I'll send Alex the Acme pricing deck tomorrow."},
        )

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["status"], "NEEDS_INPUT")
        self.assertEqual(len(body["action"]["resolution"]["recipient_candidates"]), 2)

    def test_process_endpoint_does_not_create_action_for_unsupported_text(self) -> None:
        response = self.client.post(
            "/api/commitments/process",
            json={"transcript": "The pricing deck looked great."},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "UNSUPPORTED")
        self.assertEqual(len(action_store._actions), 0)


if __name__ == "__main__":
    unittest.main()
