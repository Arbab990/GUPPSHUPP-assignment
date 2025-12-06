import React, { useState } from "react";
import axios from "axios";

function JSONBox({ children }) {
  return (
    <pre className="jsonbox">
      {children}
    </pre>
  );
}

export default function ResultsView({ data }) {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  if (!data) return null;

  const parsed = data.parsed || {};
  const added = data.added || [];

  const runQuery = async (personality = null) => {
    if (!query) {
      alert("Type a user message to simulate a reply.");
      return;
    }
    setLoading(true);
    try {
      const payload = { user_message: query };
      if (personality) payload.personality = personality;
      const resp = await axios.post("/api/query_with_rag", payload);
      setResult(resp.data);
    } catch (e) {
      alert("Error: " + (e.response?.data?.error || e.message));
    } finally {
      setLoading(false);
    }
  };

  // NEW — Clear memories function
  const clearMemories = async () => {
    const yes = window.confirm(
      "Clear all memories? This cannot be undone during testing."
    );
    if (!yes) return;

    try {
      await axios.post("/api/clear_memories");
      alert("All memories cleared. Reloading page...");
      window.location.reload();
    } catch (e) {
      alert("Clear failed: " + (e.response?.data?.error || e.message));
    }
  };

  return (
    <section className="results">
      <div className="two-col">
        <div>
          <h3>Parsed Extraction</h3>
          <JSONBox>{JSON.stringify(parsed, null, 2)}</JSONBox>

          <h3>Stored Memories (added)</h3>
          <JSONBox>{JSON.stringify(added, null, 2)}</JSONBox>
        </div>

        <div>
          <h3>Try RAG + Personality</h3>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type a user message to simulate"
            className="input"
          />

          {/* UPDATED PERSONALITY + CLEAR BUTTONS */}
          <div className="personality-controls">
            <button onClick={() => runQuery("calm_mentor")} className="btn small">
              Calm Mentor
            </button>
            <button onClick={() => runQuery("witty_friend")} className="btn small">
              Witty Friend
            </button>
            <button onClick={() => runQuery("therapist_style")} className="btn small">
              Therapist Style
            </button>
            <button onClick={() => runQuery(null)} className="btn small">
              All Personalities
            </button>

            {/* NEW CLEAR BUTTON */}
            <button
              onClick={clearMemories}
              className="btn small"
              style={{ background: "#ffdddd", color: "#660000" }}
            >
              Clear Memories
            </button>
          </div>

          {loading && <div className="loader">Loading...</div>}

          {result && (
            <div className="reply-area">
              <h4>Memories Used</h4>
              <JSONBox>{JSON.stringify(result.memories_used, null, 2)}</JSONBox>

              <h4>Base Reply</h4>
              <JSONBox>{result.base_reply}</JSONBox>

              <h4>Transformed Personalities</h4>
              <JSONBox>{JSON.stringify(result.personalities, null, 2)}</JSONBox>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
