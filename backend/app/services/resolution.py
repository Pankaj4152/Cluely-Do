"""Deterministic contact and document resolution for the prototype."""

from dataclasses import dataclass
import re
from typing import Generic, TypeVar

from app.services.demo_data import CONTACTS, DOCUMENTS, Contact, DemoDocument


T = TypeVar("T")


@dataclass(frozen=True)
class ResolutionResult(Generic[T]):
    """The result of looking up one entity without ever silently guessing."""

    query: str
    matches: tuple[T, ...]

    @property
    def is_resolved(self) -> bool:
        return len(self.matches) == 1

    @property
    def is_ambiguous(self) -> bool:
        return len(self.matches) > 1

    @property
    def is_missing(self) -> bool:
        return not self.matches

    @property
    def resolved(self) -> T | None:
        return self.matches[0] if self.is_resolved else None


def normalise(value: str) -> set[str]:
    """Turn human input into comparable lowercase word tokens.

    This is intentionally simple lexical search, not semantic search or RAG.
    For the small demo set, predictable matching is a feature.
    """
    return set(re.findall(r"[a-z0-9]+", value.lower()))


def resolve_contact(query: str) -> ResolutionResult[Contact]:
    """Find contacts whose name contains every word from the query."""
    query_tokens = normalise(query)
    matches = tuple(
        contact
        for contact in CONTACTS
        if query_tokens and query_tokens.issubset(normalise(contact.name))
    )
    return ResolutionResult(query=query, matches=matches)


def resolve_document(query: str) -> ResolutionResult[DemoDocument]:
    """Find documents whose filename contains every meaningful query word."""
    query_tokens = normalise(query)
    matches = tuple(
        document
        for document in DOCUMENTS
        if query_tokens and query_tokens.issubset(normalise(document.name))
    )
    return ResolutionResult(query=query, matches=matches)

