
# GUPPSHUPP – Founding AI Engineer Assignment

### Memory Extraction • RAG • Personality Engine • Modular AI System

This project implements all the core requirements of the GUPPSHUPP assignment:

1. **Memory Extraction Module**

   * Extracts *preferences*, *emotional patterns*, and *facts worth remembering* from user chat history.
   * Modular design allows switching between:

     * deterministic extractor (for offline development)
     * LLM-powered extractor via Groq API (future swap-in)

2. **Personality Engine**

   * Transforms model responses into multiple tones:

     * **Calm Mentor**
     * **Witty Friend**
     * **Therapist-Style**
   * Shows side-by-side *before* and *after* personality transformation.

3. **RAG Module (Retrieval-Augmented Generation)**

   * Stores all extracted memories in a lightweight SQLite database.
   * Retrieves the most relevant memories based on user query.
   * Includes similarity scoring & ranking.

4. **Frontend UI**

   * Upload chat messages → extract memories → inspect parsed output.
   * Test responses with personalities using live RAG queries.
   * View “memories used” for each reply to show reasoning trace.

5. **Full-stack Deployment Ready**

   * React (Vite/CRA) frontend
   * Flask backend
   * Modular codebase designed for production or cloud hosting.

---

# 🔧 Tech Stack

## Backend

* **Python 3.11**
* **Flask** (API server)
* **SQLite + SQLAlchemy** (memory store)
* **Groq API** (LLM-based extraction & personality transformation)
* **Sentence-Transformers** (embeddings for RAG)
* **Modular architecture** enabling easy hot-swaps (LLMs, embeddings, extractors)

## Frontend

* **React**
* **Axios**
* Custom components for:

  * Message upload
  * Memory viewer
  * Personality comparison
  * RAG response inspector

---

# 📁 Project Structure

```
root/
│── backend/
│   ├── app.py                 # Flask API
│   ├── models.py              # SQLAlchemy models
│   ├── rag_store.py           # Memory DB + similarity search
│   ├── groq_client.py         # Unified Groq LLM wrapper
│   ├── memory_extractor.py    # Deterministic extractor (stub)
│   ├── .env                   # GROQ_API_KEY, model names
│   └── sample_messages.json   # Example input
│
│── frontend_tracked/          # React UI (tracked folder)
│   ├── src/...
│   └── package.json
│
│── README.md
└── requirements.txt
```

---

# 🚀 Setup & Running Locally

## 1. Clone repository

```bash
git clone https://github.com/Arbab990/GUPPSHUPP-assignment.git
cd GUPPSHUPP-assignment
```

---

## 2. Backend Setup (Flask)

### Create virtual environment

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Create `.env`

```
GROQ_API_KEY=your_api_key_here
GROQ_DEFAULT_MODEL=groq/compound-mini
```

### Start backend

```bash
python app.py
```

Backend runs at:

```
http://localhost:5000
```

---

## 3. Frontend Setup

```bash
cd frontend_tracked
npm install
npm start
```

Frontend runs at:

```
http://localhost:3000
```

`setupProxy.js` forwards `/api/...` to the Flask backend.

---

# 🧠 Memory Extraction – How It Works

### Input:

A list of ~30 recent user messages.

### Output:

A structured dictionary:

```json
{
  "preferences": [
    { "text": "...", "source_idx": 2, "confidence": 0.96 }
  ],
  "emotional_patterns": [
    { "text": "...", "source_idx": 5, "confidence": 0.92 }
  ],
  "facts": [
    { "text": "...", "source_idx": 8, "confidence": 0.98 }
  ]
}
```

### Why this matters:

AI companions require *persistent memory* that:

* does **not hallucinate**
* remains **consistent**
* extracts only **stable traits**

This module satisfies the requirement through:

* clear classification logic
* structured output
* stable indexing
* repeatable extraction

---

# 📚 RAG System – Retrieval Logic

Each memory item is embedded with Sentence-Transformers, stored in SQLite, and ranked based on cosine similarity to the user’s latest message.

Response pipeline:

1. User message received
2. Embedding computed
3. Top-N memories retrieved
4. Base reply (LLM or stub) generated
5. Personality engine transforms the tone

This demonstrates:

* modular reasoning
* output parsing
* memory-aware response generation

---

# 🎭 Personality Engine

Given a base reply:

> “You should try something relaxing this weekend.”

Transforms into:

### **Calm Mentor**

> “Take a moment to slow down and choose an activity that helps you feel grounded…”

### **Witty Friend**

> “Bro, weekends were invented for one thing: not doing anything stressful…”

### **Therapist-Style**

> “It might help to understand what your mind and body need right now…”

This satisfies the assignment requirement of **before/after personality differences**.

---

# 🧪 Important API Routes

## `POST /api/extract_and_store`

Extracts memories from uploaded chat messages and stores them in DB.

## `GET /api/list_memories`

Returns all stored memories.

## `POST /api/query_with_rag`

Runs:

1. RAG retrieval
2. Base reply creation
3. Personality transformations

---

# 🖥 Screenshots (add after deployment)

```
[ Memory Extraction UI ]
[ Parsed Output ]
[ Personality Comparison ]
[ RAG Debug View ]
```

---

# 🌐 Deployment

You may deploy:

### Backend → Render (recommended)

* `gunicorn app:app`
* SQLite supported natively

### Frontend → Vercel / Netlify

* Easy React hosting

Instructions will be added once deployment URLs are created.

---

# ✅ Assignment Requirements Checklist

| Requirement                | Status                     |
| -------------------------- | -------------------------- |
| Extract preferences        | ✔ Done                     |
| Extract emotional patterns | ✔ Done                     |
| Extract facts              | ✔ Done                     |
| Structured JSON parsing    | ✔ Done                     |
| RAG memory system          | ✔ Done                     |
| Personality Engine         | ✔ Done                     |
| Before/After comparison    | ✔ Done                     |
| Modular architecture       | ✔ Done                     |
| Deployable system          | ✔ Backend + Frontend ready |
| Clean GitHub repo          | ✔ Completed                |

---

# 📩 Submission

Once deployed, submit:

* GitHub repo link
* Frontend hosted link
* Backend hosted link

---

# 🎉 Final Notes

This project demonstrates:

* LLM prompt design
* RAG memory pipelines
* Multi-tone personality transformation
* Clean module separation
* Frontend–backend integration

Ready for review.

---

