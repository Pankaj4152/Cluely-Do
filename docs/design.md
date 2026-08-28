# Cluely Execute — Product and Engineering Design

## 1. Product contract

**Question being explored:** Can a meeting assistant turn a commitment made in
natural conversation into a safe, reviewable, and verified real-world action?

**Promise to the user:** The system will not guess when a person or document is
ambiguous, and it will not perform a consequential action without approval.

**Primary demo scenario:**

```text
Sarah: Could you send me the pricing deck tomorrow morning?
Pankaj: Absolutely, I'll send it over.
```

Expected result:

```text
Commitment detected
  Send the pricing deck to Sarah Chen tomorrow at 9:00 AM

Recipient resolved: Sarah Chen <sarah@acme.com>
Attachment resolved: Acme Pricing Deck.pdf

User reviews and approves

Email is sent/scheduled and then verified
```

## 2. Supported actions

| Action | Natural-language example | Required information |
| --- | --- | --- |
| `SEND_EMAIL` | "I'll send Sarah the pricing deck tomorrow." | recipient, attachment, message, execution time |
| `CREATE_CALENDAR_EVENT` | "Let's meet again Thursday at 3 PM." | title, start time, attendees if known |

`SEND_EMAIL` is the first and most polished implementation. Calendar is built
only after the email flow is complete.

## 3. System flow

```text
Transcript/context
        |
        v
Commitment detector
        |
        v
Structured action
        |
        v
Entity resolution + validation
        |
        +---- unresolved or ambiguous ----> user supplies/chooses information
        |
        v
Review and explicit approval
        |
        v
Deterministic provider API execution
        |
        v
Provider-result verification
        |
        v
Action log + final status
```

The language model may identify a possible commitment and produce structured
fields. It never chooses among ambiguous entities and never directly controls
Gmail or Calendar.

## 4. Action lifecycle

```text
DETECTED
  -> RESOLVING
  -> NEEDS_INPUT
  -> READY_FOR_APPROVAL
  -> EXECUTING
  -> VERIFIED
```

Terminal states:

```text
VERIFIED   Execution completed and provider data passed verification.
FAILED     Resolution, execution, or verification failed.
CANCELLED  The user rejected or cancelled the pending action.
```

Allowed transitions:

| From | To | Trigger |
| --- | --- | --- |
| `DETECTED` | `RESOLVING` | A supported commitment is parsed. |
| `RESOLVING` | `NEEDS_INPUT` | A required value is missing or has multiple candidates. |
| `RESOLVING` | `READY_FOR_APPROVAL` | All required fields resolve uniquely. |
| `NEEDS_INPUT` | `RESOLVING` | User selects or provides the missing information. |
| `READY_FOR_APPROVAL` | `EXECUTING` | User explicitly approves the reviewed action. |
| `READY_FOR_APPROVAL` | `CANCELLED` | User cancels. |
| `EXECUTING` | `VERIFIED` | Provider result satisfies verification checks. |
| `EXECUTING` | `FAILED` | Provider call or verification fails. |

## 5. Resolution and validation rules

### Recipient

- A single matching contact may be selected automatically.
- Multiple matches require the user to choose.
- No match blocks the action and asks for an email address or another contact.

### Attachment

- Local demo files are searched by normalized filename and simple metadata.
- A single relevant match may be selected automatically.
- Multiple or zero results require user input; sending is blocked until resolved.

### Time

- A fully specified time can be normalized to an ISO-8601 timestamp.
- Relative language such as "tomorrow morning" uses an explicitly displayed
  default (for the demo: 9:00 AM, local timezone) that the user can edit.
- A calendar action without enough time information remains `NEEDS_INPUT`.

### Approval policy

All supported actions write to an external service and therefore require
explicit approval. Drafting and resolution can happen before approval; sending
an email or creating an event cannot.

## 6. Verification contract

For an email action:

1. Save the provider message ID returned by Gmail.
2. Retrieve the provider record using that ID.
3. Confirm the recipient equals the approved recipient.
4. Confirm the expected attachment is present.
5. Record the checks and mark `VERIFIED` only if all pass.

For a calendar event:

1. Save the provider event ID returned by Google Calendar.
2. Retrieve the event using that ID.
3. Confirm title and start time equal the approved values.
4. Record the checks and mark `VERIFIED` only if all pass.

## 7. Initial data for development

Use local seeded data before connecting external APIs:

```text
Contacts
- Sarah Chen — sarah@acme.com
- Alex Kim — alex@northstar.com
- Alex Morgan — alex@stripe.com

Files
- Acme Pricing Deck.pdf
- Enterprise Pricing Deck.pdf
- Q3 Product Roadmap.pdf
```

This supports the hero scenario plus deliberate ambiguity and missing-file
tests without making external authentication a prerequisite.

## 8. User-interface screens

### A. Transcript + detected action

Show a short transcript and a compact action card with action, timing, and
resolution status.

### B. Resolve ambiguity

If two contacts match "Alex," show only those candidates and require a choice.

### C. Review action

Show the exact recipient, attachment/event data, message body, time, and clear
`Cancel` and `Approve` actions.

### D. Execution result

Show timestamped log entries and individual verification checks, for example:

```text
✓ Recipient verified
✓ Attachment verified
✓ Gmail message found
✓ Action complete
```

## 9. Acceptance criteria for the first build

- Given the primary transcript, the UI creates one `SEND_EMAIL` action.
- Sarah Chen and Acme Pricing Deck resolve from local seeded data.
- The user sees the complete action before approval.
- Cancelling produces no execution call.
- Approval runs a mocked executor and displays a verified result.
- A request involving "Alex" requires a human choice.
- A nonexistent document cannot reach approval.

## 10. Explicit non-goals

- No real-time transcription or capture pipeline.
- No browser-control automation.
- No automatic sending without review.
- No background autonomy or retries.
- No AI-generated confidence score used as a decision mechanism.
