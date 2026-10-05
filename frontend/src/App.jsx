import { useState } from "react";
import "./App.css";

function App() {
  const [query, setQuery] = useState("");
  const [repoPath, setRepoPath] = useState(
    "https://github.com/tlab-580/LandGuardAI"
  );

  const [analyzing, setAnalyzing] = useState(false);
  const [status, setStatus] = useState("Ready");

  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState("");

  const analyzeRepository = async () => {
    if (!repoPath.trim()) {
      setStatus("Enter a GitHub repository URL");
      return;
    }

    if (!query.trim()) {
      setStatus("Enter a query first");
      return;
    }

    if (
      !repoPath.startsWith("https://github.com/")
    ) {
      setStatus("Enter a valid GitHub repository URL");
      return;
    }

    setAnalyzing(true);
    setStatus("Analyzing repository...");
    setError("");
    setAnalysis(null);

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/analyze`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            repository: repoPath.trim(),
            query: query.trim(),
          }),
        }
      );

      const data = await response.json();

      if (!response.ok || !data.success) {
        const message =
          data.error || `Request failed with status ${response.status}`;

        setError(message);
        setStatus("Analysis failed");
        return;
      }

      console.log("RepoMind Analysis:", data);

      setAnalysis(data);
      setStatus("Analysis complete");
    } catch (error) {
      console.error("RepoMind API error:", error);
      setError(error.message);
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
              <p>
                Enter a public GitHub repository RepoMind should understand.
              </p>
            </div>
          </div>

          <div className="repo-input">
            <input
              value={repoPath}
              onChange={(e) => setRepoPath(e.target.value)}
              placeholder="https://github.com/owner/repository"
            />

            <button
              onClick={() => {
                if (!repoPath.trim()) {
                  setStatus("Enter a GitHub repository URL");
                  return;
                }

                setStatus("Repository ready");
              }}
            >
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
              placeholder="Example: Find API mismatches in this repository"
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

          {error && (
            <div className="error-box">
              <strong>Analysis Error</strong>
              <p>{error}</p>
            </div>
          )}
        </section>

        {/* Results */}
        {analysis && (
          <>
            {/* Repository Results */}
            <section className="card">
              <div className="section-title">
                <span>📊</span>
                <div>
                  <h2>Analysis Results</h2>
                  <p>
                    Results generated from the repository by RepoMind.
                  </p>
                </div>
              </div>

              <div className="result-summary">
                <p>
                  <strong>Repository:</strong>{" "}
                  {analysis.repository}
                </p>

                <p>
                  <strong>Query:</strong>{" "}
                  {analysis.query}
                </p>
              </div>
            </section>

            {/* Code Intelligence */}
            <section className="card">
              <div className="section-title">
                <span>🔗</span>
                <div>
                  <h2>Code Intelligence</h2>
                  <p>
                    Repository relationships discovered by RepoMind.
                  </p>
                </div>
              </div>

              {analysis.relationships &&
              analysis.relationships.length > 0 ? (
                <div className="relationships">
                  {analysis.relationships
                    .slice(0, 10)
                    .map((relationship, index) => (
                      <div
                        className="relationship"
                        key={index}
                      >
                        <strong>
                          {relationship.source}
                        </strong>

                        <span className="arrow">
                          →
                        </span>

                        <strong>
                          {relationship.target}
                        </strong>

                        {relationship.relationship && (
                          <span className="relationship-type">
                            {relationship.relationship}
                          </span>
                        )}
                      </div>
                    ))}
                </div>
              ) : (
                <p>No repository relationships were discovered.</p>
              )}
            </section>

            {/* Relevant Files */}
            <section className="card">
              <div className="section-title">
                <span>📄</span>
                <div>
                  <h2>Relevant Files</h2>
                  <p>
                    Files ranked against your query.
                  </p>
                </div>
              </div>

              {analysis.files &&
              analysis.files.length > 0 ? (
                <div className="files-list">
                  {analysis.files.map((file, index) => (
                    <div
                      className="file-result"
                      key={index}
                    >
                      <span>{file.path}</span>

                      <strong>
                        {file.score}
                      </strong>
                    </div>
                  ))}
                </div>
              ) : (
                <p>No relevant files found.</p>
              )}
            </section>

            {/* Bug Diagnosis */}
            <section className="card">
              <div className="section-title">
                <span>🐛</span>
                <div>
                  <h2>Bug Diagnosis</h2>
                  <p>
                    Repository-aware analysis results.
                  </p>
                </div>
              </div>

              {analysis.mismatches &&
              analysis.mismatches.length > 0 ? (
                <div className="diagnosis">
                  <div className="badge danger">
                    API Mismatch
                  </div>

                  <pre>
                    {JSON.stringify(
                      analysis.mismatches,
                      null,
                      2
                    )}
                  </pre>
                </div>
              ) : (
                <div className="diagnosis">
                  <div className="badge">
                    No API Mismatch Detected
                  </div>

                  <p>
                    RepoMind did not report an API mismatch
                    for this analysis.
                  </p>
                </div>
              )}
            </section>

            {/* Memory */}
            <section className="card">
              <div className="section-title">
                <span>🧠</span>
                <div>
                  <h2>RepoMind Memory</h2>
                  <p>
                    Repository knowledge retrieved from memory.
                  </p>
                </div>
              </div>

              {analysis.memory &&
              analysis.memory.length > 0 ? (
                <pre>
                  {JSON.stringify(
                    analysis.memory,
                    null,
                    2
                  )}
                </pre>
              ) : (
                <p>
                  No stored repository memory was returned.
                </p>
              )}
            </section>

            {/* Verification */}
            <section className="card">
              <div className="section-title">
                <span>🧪</span>
                <div>
                  <h2>Verification</h2>
                  <p>
                    Results returned by the current analysis.
                  </p>
                </div>
              </div>

              <div className="verification">

                <div className="check">
                  <span>🔍 Repository Analysis</span>
                  <strong>PASS</strong>
                </div>

                <div className="check">
                  <span>🧠 Query Processing</span>
                  <strong>PASS</strong>
                </div>

                <div className="check">
                  <span>🔗 Relationship Analysis</span>
                  <strong>
                    {analysis.relationships
                      ? "PASS"
                      : "N/A"}
                  </strong>
                </div>

              </div>

              <div className="verified">
                ✅ ANALYSIS COMPLETED
              </div>
            </section>
          </>
        )}

      </main>
    </div>
  );
}

export default App;