import unittest

from app.services.resolution import resolve_contact, resolve_document


class ResolutionTests(unittest.TestCase):
    def test_sarah_resolves_to_one_contact(self) -> None:
        result = resolve_contact("Sarah")

        self.assertTrue(result.is_resolved)
        self.assertEqual(result.resolved.email, "sarah@acme.com")

    def test_alex_is_ambiguous_and_never_auto_selected(self) -> None:
        result = resolve_contact("Alex")

        self.assertTrue(result.is_ambiguous)
        self.assertIsNone(result.resolved)
        self.assertEqual([contact.name for contact in result.matches], ["Alex Kim", "Alex Morgan"])

    def test_unknown_contact_is_missing(self) -> None:
        result = resolve_contact("Priya")

        self.assertTrue(result.is_missing)

    def test_pricing_deck_is_ambiguous(self) -> None:
        result = resolve_document("pricing deck")

        self.assertTrue(result.is_ambiguous)

    def test_acme_pricing_deck_resolves_uniquely(self) -> None:
        result = resolve_document("Acme pricing deck")

        self.assertTrue(result.is_resolved)
        self.assertEqual(result.resolved.name, "Acme Pricing Deck.pdf")


if __name__ == "__main__":
    unittest.main()
