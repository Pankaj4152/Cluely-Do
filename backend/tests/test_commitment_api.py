import unittest

from fastapi.testclient import TestClient

from app.main import app


class CommitmentApiTests(unittest.TestCase):
    def setUp(self) -> None:
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


if __name__ == "__main__":
    unittest.main()
