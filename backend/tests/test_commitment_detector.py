from datetime import datetime
import unittest

from app.models.commitments import DetectedCommitment, UnsupportedCommitment
from app.services.commitment_detector import detect_commitment


class CommitmentDetectorTests(unittest.TestCase):
    def test_detects_supported_email_commitment(self) -> None:
        result = detect_commitment(
            "I'll send Sarah the Acme pricing deck tomorrow morning.",
            reference_time=datetime(2026, 8, 29, 14, 30),
        )

        self.assertIsInstance(result, DetectedCommitment)
        self.assertEqual(result.details.recipient_query, "Sarah")
        self.assertEqual(result.details.attachment_query, "Acme pricing deck")
        self.assertEqual(result.details.execute_at, datetime(2026, 8, 30, 9, 0))

    def test_does_not_treat_someone_elses_request_as_a_commitment(self) -> None:
        result = detect_commitment("Sarah: Could you send me the pricing deck tomorrow?")

        self.assertIsInstance(result, UnsupportedCommitment)

    def test_rejects_unrelated_conversation(self) -> None:
        result = detect_commitment("The pricing deck looked great in the meeting.")

        self.assertIsInstance(result, UnsupportedCommitment)


if __name__ == "__main__":
    unittest.main()
