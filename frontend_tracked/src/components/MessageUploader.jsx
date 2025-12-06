import React, { useState } from "react";
import axios from "axios";

export default function MessageUploader({ onResult }) {
  const [messagesText, setMessagesText] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    const msgs = messagesText
      .split("\n")
      .map((s) => s.trim())
      .filter(Boolean)
      .slice(0, 30);
    if (msgs.length === 0) {
      alert("Paste the user messages, one per line.");
      return;
    }

    setLoading(true);
    try {
      const resp = await axios.post("/api/extract_and_store", { messages: msgs });
      onResult(resp.data);
    } catch (e) {
      const msg = e.response?.data?.error || e.message || "Unknown error";
      alert("Error: " + msg);
    } finally {
      setLoading(false);
    }
  };

  const pasteSample = () => {
    const sample = [
      "I love spicy food and always choose hot sauce.",
      "I play cricket every weekend with friends.",
      "I'm worried about an upcoming exam next month.",
      "I prefer video calls to texting my team.",
      "My birthday is on 2nd September.",
      "I work as a product analyst at a fintech startup."
    ].join("\n");
    setMessagesText(sample);
  };

  return (
    <section className="uploader">
      <textarea
        value={messagesText}
        onChange={(e) => setMessagesText(e.target.value)}
        rows={12}
        placeholder="Paste user messages here (one per line)."
        className="textarea"
      />
      <div className="controls">
        <button onClick={handleSubmit} disabled={loading} className="btn primary">
          {loading ? "Processing..." : "Extract & Store"}
        </button>
        <button onClick={pasteSample} className="btn">Paste Sample</button>
        <div className="note">Max 30 messages — first 30 lines used.</div>
      </div>
    </section>
  );
}
