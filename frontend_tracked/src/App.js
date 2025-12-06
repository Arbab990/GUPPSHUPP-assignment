import React, { useState } from "react";
import MessageUploader from "./components/MessageUploader";
import ResultsView from "./components/ResultsView";

export default function App() {
  const [resultData, setResultData] = useState(null);

  return (
    <div className="app">
      <header className="app-header">
        <h1>Guppshupp — Memory & Personality Demo</h1>
        <p className="subtitle">Paste up to 30 user messages (one per line)</p>
      </header>

      <main className="main">
        <MessageUploader onResult={setResultData} />
        <ResultsView data={resultData} />
      </main>
    </div>
  );
}

