import { StrictMode, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";
const EXAMPLES = {
  resolved: "I'll send Sarah the Acme pricing deck tomorrow morning.",
  ambiguous: "I'll send Alex the Acme pricing deck tomorrow.",
  unsupported: "The pricing deck looked great.",
};

type Candidate = { id: string; name: string; email?: string; company?: string };
type VerificationCheck = { label: string; passed: boolean };
type LogEntry = { timestamp: string; message: string };
type ActionData = {
  id: string;
  status: "READY_FOR_APPROVAL" | "VERIFIED" | "CANCELLED";
  details: { execute_at: string | null };
  resolution: {
    recipient: Candidate | null;
    attachment: { id: string; name: string } | null;
    recipient_candidates: Candidate[];
    attachment_candidates: { id: string; name: string }[];
    missing_fields: string[];
  };
  execution: { provider: string; provider_id: string; verification_checks: VerificationCheck[] } | null;
  log: LogEntry[];
};
type ProcessResult =
  | { status: "UNSUPPORTED"; reason: string }
  | { status: "READY_FOR_APPROVAL" | "NEEDS_INPUT"; action: ActionData };
type GmailStatus = { connected: boolean; email: string | null };

function formatExecutionTime(value: string | null): string {
  if (!value) return "Time needs confirmation";
  return new Intl.DateTimeFormat(undefined, { weekday: "short", hour: "numeric", minute: "2-digit" }).format(new Date(value));
}

function App() {
  const [apiStatus, setApiStatus] = useState<"checking" | "connected" | "offline">("checking");
  const [gmailStatus, setGmailStatus] = useState<GmailStatus | null>(null);
  const [transcript, setTranscript] = useState(EXAMPLES.resolved);
  const [result, setResult] = useState<ProcessResult | null>(null);
  const [reviewAction, setReviewAction] = useState<ActionData | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSubmittingReview, setIsSubmittingReview] = useState(false);
  const [isSelecting, setIsSelecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/health`)
      .then((response) => setApiStatus(response.ok ? "connected" : "offline"))
      .catch(() => setApiStatus("offline"));
    fetch(`${API_BASE_URL}/api/integrations/gmail/status`)
      .then((response) => response.ok ? response.json() : null)
      .then((status) => setGmailStatus(status as GmailStatus | null))
      .catch(() => setGmailStatus(null));
  }, []);

  const statusCopy = { checking: "Checking API connection...", connected: "Execution API connected", offline: "Execution API unavailable" }[apiStatus];

  async function processTranscript() {
    setIsProcessing(true);
    setError(null);
    setResult(null);
    setReviewAction(null);
    try {
      const response = await fetch(`${API_BASE_URL}/api/commitments/process`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transcript }),
      });
      if (!response.ok) throw new Error("The API could not process this commitment.");
      setResult((await response.json()) as ProcessResult);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Something went wrong.");
    } finally {
      setIsProcessing(false);
    }
  }

  async function submitReview(decision: "approve" | "cancel") {
    if (!reviewAction) return;
    setIsSubmittingReview(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/api/actions/${reviewAction.id}/${decision}`, { method: "POST" });
      if (!response.ok) throw new Error(`Unable to ${decision} this action.`);
      setReviewAction((await response.json()) as ActionData);
      setResult(null);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Something went wrong.");
    } finally {
      setIsSubmittingReview(false);
    }
  }

  async function selectCandidate(kind: "recipient" | "attachment", candidateId: string) {
    if (!result || result.status !== "NEEDS_INPUT") return;
    setIsSelecting(true);
    setError(null);
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/actions/${result.action.id}/select-${kind}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ candidate_id: candidateId }),
        },
      );
      if (!response.ok) throw new Error("Unable to apply that selection.");
      const action = (await response.json()) as ActionData;
      setResult({ status: "READY_FOR_APPROVAL", action });
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Something went wrong.");
    } finally {
      setIsSelecting(false);
    }
  }

  return (
    <main className="app-shell">
      <p className="eyebrow">Cluely Execute</p>
      <h1>Turn commitments into completed actions.</h1>
      <p className="subtitle">Paste a conversational commitment. The system resolves it before a consequential action can be reviewed or approved.</p>
      <div className="gmail-connection">
        {gmailStatus?.connected ? <span>Gmail connected: {gmailStatus.email}</span> : <span>Gmail not connected</span>}
        {!gmailStatus?.connected && <a href={`${API_BASE_URL}/api/integrations/gmail/connect`}>Connect Gmail</a>}
      </div>

      <section className="transcript-panel" aria-label="Transcript input">
        <div className="panel-heading"><span>Meeting transcript</span><div className={`connection ${apiStatus}`}><span className="status-dot" />{statusCopy}</div></div>
        <textarea aria-label="Transcript" value={transcript} onChange={(event) => setTranscript(event.target.value)} />
        <div className="panel-footer">
          <div className="example-buttons">
            <button type="button" onClick={() => setTranscript(EXAMPLES.resolved)}>Resolved example</button>
            <button type="button" onClick={() => setTranscript(EXAMPLES.ambiguous)}>Ambiguous example</button>
            <button type="button" onClick={() => setTranscript(EXAMPLES.unsupported)}>Unsupported example</button>
          </div>
          <button className="primary-button" type="button" onClick={processTranscript} disabled={isProcessing || !transcript.trim()}>{isProcessing ? "Detecting..." : "Detect commitment"}</button>
        </div>
      </section>

      {error && <p className="error-message">{error}</p>}
      {result?.status === "UNSUPPORTED" && <section className="result-card unsupported"><p className="card-label">No action created</p><h2>No supported commitment detected.</h2><p>{result.reason}</p></section>}
      {result?.status === "READY_FOR_APPROVAL" && <section className="result-card ready"><p className="card-label">Commitment detected</p><h2>Send {result.action.resolution.attachment?.name.replace(".pdf", "")} to {result.action.resolution.recipient?.name}</h2><p className="scheduled">{formatExecutionTime(result.action.details.execute_at)}</p><div className="resolved-entities"><Entity label="Recipient" primary={result.action.resolution.recipient?.name ?? "Unresolved"} secondary={result.action.resolution.recipient?.email} /><Entity label="Attachment" primary={result.action.resolution.attachment?.name ?? "Unresolved"} /></div><button className="primary-button review-button" type="button" onClick={() => setReviewAction(result.action)}>Review action <span>-&gt;</span></button></section>}
      {result?.status === "NEEDS_INPUT" && <section className="result-card needs-input"><p className="card-label">Input required</p><h2>Which person or file did you mean?</h2>{result.action.resolution.recipient_candidates.length > 1 && <div className="candidate-group"><p>Choose a recipient</p>{result.action.resolution.recipient_candidates.map((candidate) => <button className="candidate" type="button" disabled={isSelecting} key={candidate.id} onClick={() => selectCandidate("recipient", candidate.id)}><span>{candidate.name}</span><small>{candidate.company} / {candidate.email}</small></button>)}</div>}{result.action.resolution.attachment_candidates.length > 1 && <div className="candidate-group"><p>Choose an attachment</p>{result.action.resolution.attachment_candidates.map((candidate) => <button className="candidate" type="button" disabled={isSelecting} key={candidate.id} onClick={() => selectCandidate("attachment", candidate.id)}>{candidate.name}</button>)}</div>}{result.action.resolution.missing_fields.length > 0 && <p>Missing: {result.action.resolution.missing_fields.join(", ")}</p>}</section>}

      {reviewAction && <section className="review-card">
        <p className="card-label">{reviewAction.status === "READY_FOR_APPROVAL" ? "Review action" : "Action result"}</p>
        <h2>{reviewAction.status === "VERIFIED" ? "Action verified." : reviewAction.status === "CANCELLED" ? "Action cancelled." : "Confirm before executing."}</h2>
        <div className="review-details"><Entity label="To" primary={reviewAction.resolution.recipient?.name ?? "Unresolved"} secondary={reviewAction.resolution.recipient?.email} /><Entity label="Attachment" primary={reviewAction.resolution.attachment?.name ?? "Unresolved"} /><Entity label="Scheduled" primary={formatExecutionTime(reviewAction.details.execute_at)} /></div>
        {reviewAction.status === "READY_FOR_APPROVAL" && <div className="review-actions"><button className="secondary-button" type="button" disabled={isSubmittingReview} onClick={() => submitReview("cancel")}>Cancel</button><button className="primary-button" type="button" disabled={isSubmittingReview} onClick={() => submitReview("approve")}>{isSubmittingReview ? "Processing..." : "Approve and execute"}</button></div>}
        {reviewAction.execution && <div className="verification"><p>Verification</p>{reviewAction.execution.verification_checks.map((check) => <span key={check.label}>{check.passed ? "[OK]" : "[FAIL]"} {check.label}</span>)}</div>}
        <div className="action-log"><p>Action log</p>{reviewAction.log.map((entry, index) => <div key={`${entry.timestamp}-${index}`}><time>{new Date(entry.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}</time><span>{entry.message}</span></div>)}</div>
      </section>}
    </main>
  );
}

function Entity({ label, primary, secondary }: { label: string; primary: string; secondary?: string }) {
  return <div className="entity"><span>{label}</span><strong>{primary} <b>[OK]</b></strong>{secondary && <small>{secondary}</small>}</div>;
}

createRoot(document.getElementById("root")!).render(<StrictMode><App /></StrictMode>);
