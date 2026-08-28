import { StrictMode, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

function App() {
  const [apiStatus, setApiStatus] = useState<"checking" | "connected" | "offline">("checking");

  useEffect(() => {
    fetch("http://localhost:8000/api/health")
      .then((response) => {
        if (!response.ok) throw new Error("Health check failed");
        setApiStatus("connected");
      })
      .catch(() => setApiStatus("offline"));
  }, []);

  const statusCopy = {
    checking: "Checking API connection…",
    connected: "Execution API connected",
    offline: "Execution API unavailable",
  }[apiStatus];

  return (
    <main className="app-shell">
      <p className="eyebrow">CLUEly Execute</p>
      <h1>Turn commitments into completed actions.</h1>
      <p className="subtitle">
        The first build checkpoint is ready: the interface exists and will soon
        connect to the execution API.
      </p>
      <div className={`status-card ${apiStatus}`}>
        <span className="status-dot" />
        {statusCopy}
      </div>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode><App /></StrictMode>);
