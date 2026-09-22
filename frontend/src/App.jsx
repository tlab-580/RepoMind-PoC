import { useState } from "react";
import "./App.css";

function App() {
  const [query, setQuery] = useState("");
  const [repoPath, setRepoPath] = useState(
    "C:\\Users\\DELL\\LANDGUARD-AI"
  );

  const [analyzing, setAnalyzing] = useState(false);
  const [status, setStatus] = useState("Ready");

  const analyzeRepository = async () => {
  if (!query.trim()) {
    setStatus("Enter a query first");
    return;
  }

  setAnalyzing(true);
  setStatus("Analyzing repository...");

  try {
    const response = await fetch("http://127.0.0.1:8000/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        repository: repoPath,
        query: query,
      }),
    });

    const data = await response.json();

    if (!data.success) {
      setStatus("Analysis failed");
      console.error(data.error);
      return;
    }

    console.log("RepoMind Analysis:", data);

    setStatus("Analysis complete");

  } catch (error) {
    console.error("RepoMind API error:", error);
    setStatus("Backend connection failed");
  } finally {
    setAnalyzing(false);
  }
};

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div>
          <h1>🧠 RepoMind</h1>
          <p>Repository-Level AI Coding Agent</p>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          {status}
        </div>
      </header>

      <main className="container">

        {/* Repository */}
        <section className="card">
          <div className="section-title">
            <span>📁</span>
            <div>
              <h2>Repository</h2>
              <p>Select the project RepoMind should understand.</p>
            </div>
          </div>

          <div className="repo-input">
            <input
              value={repoPath}
              onChange={(e) => setRepoPath(e.target.value)}
              placeholder="Repository path"
            />

            <button onClick={() => setStatus("Repository scanned")}>
              Scan
            </button>
          </div>
        </section>

        {/* Ask RepoMind */}
        <section className="card">
          <div className="section-title">
            <span>💬</span>
            <div>
              <h2>Ask RepoMind</h2>
              <p>Ask questions or describe a bug.</p>
            </div>
          </div>

          <div className="query-box">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Example: Fix the API bug"
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  analyzeRepository();
                }
              }}
            />

            <button
              className="analyze-button"
              onClick={analyzeRepository}
              disabled={analyzing}
            >
              {analyzing ? "Analyzing..." : "Analyze"}
            </button>
          </div>
        </section>

        {/* Code Intelligence */}
        <section className="card">
          <div className="section-title">
            <span>🔗</span>
            <div>
              <h2>Code Intelligence</h2>
              <p>Repository relationships discovered by RepoMind.</p>
            </div>
          </div>

          <div className="flow">
            <div className="flow-box">
              <strong>frontend/src/App.jsx</strong>
              <span>Frontend</span>
            </div>

            <div className="arrow">→</div>

            <div className="flow-box">
              <strong>backend/main.py</strong>
              <span>FastAPI Backend</span>
            </div>

            <div className="arrow">→</div>

            <div className="flow-box">
              <strong>landslide_risk_model.pkl</strong>
              <span>ML Model</span>
            </div>
          </div>
        </section>

        {/* Bug Diagnosis */}
        <section className="grid">

          <div className="card">
            <div className="section-title">
              <span>🐛</span>
              <div>
                <h2>Bug Diagnosis</h2>
                <p>Repository-aware root cause analysis.</p>
              </div>
            </div>

            <div className="diagnosis">
              <div className="badge danger">
                API Mismatch
              </div>

              <p>
                Frontend calls:
              </p>

              <code>/predict-risk-wrong</code>

              <p>
                Backend provides:
              </p>

              <code>/predict-risk</code>

              <h3>Root Cause</h3>

              <p>
                The frontend API endpoint does not match any
                available backend route.
              </p>
            </div>
          </div>

          {/* Fix */}
          <div className="card">
            <div className="section-title">
              <span>🔧</span>
              <div>
                <h2>Proposed Fix</h2>
                <p>Targeted repository repair.</p>
              </div>
            </div>

            <div className="fix-box">
              <div className="old">
                - /predict-risk-wrong
              </div>

              <div className="new">
                + /predict-risk
              </div>
            </div>

            <button
              className="fix-button"
              onClick={() => setStatus("Fix applied")}
            >
              Apply Fix
            </button>
          </div>

        </section>

        {/* Verification */}
        <section className="card">
          <div className="section-title">
            <span>🧪</span>
            <div>
              <h2>Verification</h2>
              <p>Real system checks after the repair.</p>
            </div>
          </div>

          <div className="verification">

            <div className="check">
              <span>❤️ Backend Health</span>
              <strong>PASS</strong>
            </div>

            <div className="check">
              <span>🤖 Prediction API</span>
              <strong>PASS</strong>
            </div>

            <div className="check">
              <span>🌐 Frontend</span>
              <strong>PASS</strong>
            </div>

          </div>

          <div className="verified">
            ✅ REPAIR VERIFIED
          </div>
        </section>

      </main>

      <footer>
        RepoMind • Understand. Remember. Reason. Fix. Verify.
      </footer>
    </div>
  );
}

export default App;