# Cluely Execute

Turn conversational commitments into safe, approved, and verified actions.

## The idea

Cluely is strong at understanding conversational context. This prototype
explores the next step: what happens when a commitment made in a conversation
becomes a real-world action that is resolved, reviewed, executed, and checked.

For example:

> "Could you send me the pricing deck tomorrow morning?"

Cluely Execute detects the commitment, resolves the recipient and document,
asks the user for approval, sends the email through a deterministic API, and
verifies the outcome.

## Prototype boundary

Cluely's existing context and transcription capabilities are treated as an
upstream dependency. This prototype begins with conversational context and
focuses on the execution layer:

```text
resolve -> approve -> execute -> verify
```

It is not an attempt to reproduce microphone capture, system-audio capture,
screen understanding, or meeting transcription.

## Frozen MVP

The prototype supports only two consequential actions:

1. Send an email with a relevant attachment.
2. Create a calendar event or reminder.

The email flow is the hero experience and receives most of the implementation
and demo effort. Calendar is included only to show that the design can support
more than one action type.

## Design principles

1. LLMs interpret intent; application code resolves and executes it.
2. Ambiguity is surfaced to the user, never guessed.
3. Consequential actions require explicit approval.
4. An API response alone is not success; the outcome is verified.
5. Every state transition is recorded in an action log.

## Deliberate non-goals

To keep the prototype reliable and achievable, it does not include:

- microphone or system-audio capture
- screen capture or OCR
- RAG, embeddings, or a vector database
- browser/GUI automation or Playwright-driven Gmail
- a general-purpose autonomous agent
- CRM, Slack, Drive, or workflow-engine integrations

## Design

The initial product and engineering design is in
[docs/design.md](docs/design.md).
