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

## Current prototype status

The first email vertical slice is implemented with local demo data and a
deterministic mock executor.

```text
Transcript
  -> commitment detection
  -> action creation
  -> contact and attachment resolution
  -> explicit approval or cancellation
  -> mock execution
  -> verification checks and action log
```

Implemented now:

- A React screen for submitting a transcript and viewing resolved, ambiguous,
  or unsupported outcomes.
- Deterministic detection of the demo phrase: `I'll send Sarah the Acme pricing
  deck tomorrow morning.`
- Safe local resolution: `Sarah` resolves uniquely; `Alex` and generic pricing
  deck requests require a candidate choice that the backend validates.
- Approval, cancellation, a mock Gmail provider result, and verification logs.
- A review screen that can approve or cancel the resolved email action and then
  displays verification evidence plus the action log.
When Gmail is connected, the approved email path sends a real message with the
demo PDF attachment, fetches the Gmail message by provider ID, and verifies the
recipient and attachment. Automated tests keep using the mock executor.

## Gmail connection setup (local demo)

The application provides a **Connect Gmail** button. The person using the app
only signs in to Google and approves access. The developer configures the OAuth
client once, locally:

1. Create a Google OAuth **Web application** client and enable Gmail API.
2. Add `http://127.0.0.1:8000/api/integrations/gmail/callback` as an authorized
   redirect URI.
3. Store the downloaded client file at `backend/secrets/gmail-client.json`.

`backend/secrets/`, OAuth tokens, and `backend/.env` are ignored by Git. The
connection flow and real Gmail send-and-verify executor are implemented.

## Run locally

In one terminal, start the API:

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8001
```

In another terminal, start the frontend:

```powershell
cd frontend
npm run dev
```

Open `http://localhost:5173`. The frontend reads its local API URL from
`frontend/.env.development`.

Run backend tests with:

```powershell
cd backend
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Run the frontend build check with:

```powershell
cd frontend
npm run build
```

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
