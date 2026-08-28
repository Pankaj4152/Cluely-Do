"""Small, local data set used to make the prototype deterministic."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Contact:
    """A person who can receive an email in the demo environment."""
    id: str
    name: str
    email: str
    company: str


@dataclass(frozen=True)
class DemoDocument:
    """A file the prototype can resolve and later attach to a message."""
    id: str
    name: str
    path: str


CONTACTS: tuple[Contact, ...] = (
    Contact(
        id="contact_sarah_chen",
        name="Sarah Chen",
        email="sarah@acme.com",
        company="Acme",
    ),
    Contact(
        id="contact_alex_kim",
        name="Alex Kim",
        email="alex@northstar.com",
        company="Northstar",
    ),
    Contact(
        id="contact_alex_morgan",
        name="Alex Morgan",
        email="alex@stripe.com",
        company="Stripe",
    ),
)

DOCUMENTS: tuple[DemoDocument, ...] = (
    DemoDocument(
        id="document_acme_pricing_deck",
        name="Acme Pricing Deck.pdf",
        path="demo-files/Acme Pricing Deck.pdf",
    ),
    DemoDocument(
        id="document_enterprise_pricing_deck",
        name="Enterprise Pricing Deck.pdf",
        path="demo-files/Enterprise Pricing Deck.pdf",
    ),
    DemoDocument(
        id="document_q3_roadmap",
        name="Q3 Product Roadmap.pdf",
        path="demo-files/Q3 Product Roadmap.pdf",
    ),
)

