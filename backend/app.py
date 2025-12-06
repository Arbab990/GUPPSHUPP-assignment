# backend/app.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from rag_store import RAGStore
from dotenv import load_dotenv

from memory_extractor import extract_memories
from personality_engine import transform_response
from groq_client import groq_chat_completion

load_dotenv()


def simple_base_reply_from_memories(user_message, retrieved):
    """
    Build a short deterministic reply summarizing relevant memories.
    This is used as a fallback when the LLM call fails.
    """
    if not retrieved:
        return f"I heard you: \"{user_message}\". I don't have any stored memories about you yet — tell me more!"
    # summarize by kind
    kinds = {}
    for r in retrieved:
        kinds.setdefault(r["kind"], []).append(r["content"])

    parts = []
    if "preferences" in kinds:
        parts.append("I see you like: " + ", ".join(kinds["preferences"][:3]) + ".")
    if "facts" in kinds:
        parts.append("Some facts I know: " + ", ".join(kinds["facts"][:3]) + ".")
    if "emotional_patterns" in kinds:
        parts.append("Emotional notes: " + ", ".join(kinds["emotional_patterns"][:2]) + ".")
    parts_text = " ".join(parts)
    # a minimal suggestion based on message and memories
    suggestion = f"Based on this, one suggestion: try planning a short activity connected to your interests."
    return f"{parts_text} {suggestion}"


app = Flask(__name__)
CORS(app)  # allow cross-origin requests from frontend dev server

DB_URL = os.getenv("DB_URL", "sqlite:///memories.db")
rag = RAGStore(db_url=DB_URL)

@app.route("/api/list_memories", methods=["GET"])
def list_memories():
    return jsonify(rag.list_memories())

@app.route("/api/extract_and_store", methods=["POST"])
def extract_and_store():
    body = request.get_json(force=True)
    messages = body.get("messages") or []
    if not isinstance(messages, list) or len(messages) == 0:
        return jsonify({"error": "Provide 'messages' as a non-empty list"}), 400

    # run extraction using LLM
    try:
        parsed = extract_memories(messages)
    except Exception as e:
        return jsonify({"error": "extraction_failed", "details": str(e)}), 500

    # insert extracted items into DB
    added = []
    for kind in ("preferences", "emotional_patterns", "facts"):
        for item in parsed.get(kind, []):
            text = item.get("text")
            meta = {"source_idx": item.get("source_idx"), "confidence": item.get("confidence")}
            mem_id = rag.add_memory(kind=kind, content=text, metadata=meta)
            added.append({"id": mem_id, "kind": kind, "text": text, "metadata": meta})

    return jsonify({"parsed": parsed, "added": added})

@app.route("/api/query_with_rag", methods=["POST"])
def query_with_rag():
    body = request.get_json(force=True)
    user_message = body.get("user_message", "")
    assistant_draft = body.get("assistant_draft", "")
    requested_personality = body.get("personality", None)

    if not user_message:
        return jsonify({"error": "Provide 'user_message'"}), 400

    # retrieve relevant memories
    retrieved = rag.retrieve(user_message, top_k=5)
    memory_texts = "\n".join([f"- ({r['kind']}) {r['content']} (score:{r['score']:.2f})" for r in retrieved]) or "None"

    base_reply = assistant_draft
    if not base_reply:
        # attempt to generate a base reply using GROQ; if it fails, use a simple deterministic fallback
        try:
            system_msg = {"role":"system", "content": "You are a helpful assistant. Use the known user memories provided below when crafting your reply.\nKnown user memories:\n" + memory_texts}
            user_msg = {"role":"user", "content": user_message}
            # groq_chat_completion is imported at top of file in the earlier version
            base_reply = groq_chat_completion([system_msg, user_msg], temperature=0.2, max_tokens=400)
        except Exception as e:
            # log the exception on server console and fallback to simple reply
            print("GROQ call failed inside /api/query_with_rag:", str(e))
            base_reply = simple_base_reply_from_memories(user_message, retrieved)

    # produce transformed personalities (attempts to rewrite)
    personalities_out = {}
    personalities_to_generate = ["calm_mentor", "witty_friend", "therapist_style"]
    if requested_personality:
        personalities_to_generate = [requested_personality] if requested_personality in personalities_to_generate else personalities_to_generate

    for p in personalities_to_generate:
        try:
            # If GROQ isn't available inside personality_engine, transform_response will raise.
            # We catch exceptions and return the base_reply as the personality variant (safe fallback).
            personalities_out[p] = transform_response(user_message, base_reply, p)
        except Exception as e:
            print(f"Personality transform failed for {p}:", str(e))
            # fallback: return the base reply with a short personality tag
            personalities_out[p] = f"[{p} fallback] {base_reply}"

    return jsonify({
        "memories_used": retrieved,
        "base_reply": base_reply,
        "personalities": personalities_out
    })
@app.route("/api/clear_memories", methods=["POST"])
def clear_memories():
    """
    Clears all memories from the DB. For test/dev only.
    """
    Session = rag.Session
    session = Session()
    try:
        deleted = session.query(rag.Session().bind.table_names()).all()  # placeholder to ensure session works
    except Exception:
        pass
    # simpler: drop and recreate table
    from models import Base, Memory, init_db
    engine = rag.Session().get_bind()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    return jsonify({"result":"cleared"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    # debug=True helps during development; set False in production
    app.run(host="0.0.0.0", port=port, debug=True)


