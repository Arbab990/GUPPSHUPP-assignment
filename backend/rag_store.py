# backend/rag_store.py
"""
Lightweight RAGStore using TF-IDF for demo purposes.
Avoids sentence-transformers / huggingface_hub dependency.
Good for a small memory store (30-200 short snippets).
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import numpy as np
import json
from models import Memory, init_db

class RAGStore:
    def __init__(self, db_url="sqlite:///memories.db"):
        self.Session = init_db(db_url)
        # TF-IDF vectorizer will be fit on stored memories when needed
        self.vectorizer = None
        self._cached_texts = []
        self._cached_matrix = None

    def add_memory(self, kind, content, metadata=None):
        session = self.Session()
        mem = Memory(kind=kind, content=content, meta_json=json.dumps(metadata or {}))
        session.add(mem)
        session.commit()
        mem_id = mem.id
        session.close()
        # invalidate cache
        self._cached_texts = []
        self._cached_matrix = None
        return mem_id

    def list_memories(self):
        session = self.Session()
        rows = session.query(Memory).all()
        out = [{"id": r.id, "kind": r.kind, "content": r.content, "metadata": json.loads(r.meta_json or "{}")} for r in rows]
        session.close()
        return out

    def _ensure_index(self):
        """
        Build or rebuild TF-IDF on current DB texts if cache is invalid.
        """
        session = self.Session()
        rows = session.query(Memory).all()
        session.close()
        texts = [r.content for r in rows]
        if texts == self._cached_texts and self._cached_matrix is not None:
            return  # cache still valid
        if not texts:
            self.vectorizer = None
            self._cached_texts = []
            self._cached_matrix = None
            return
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        self._cached_matrix = self.vectorizer.fit_transform(texts)
        self._cached_texts = texts

    def retrieve(self, query, top_k=5):
        """
        Return top_k memories most similar to query using cosine over TF-IDF.
        """
        self._ensure_index()
        session = self.Session()
        rows = session.query(Memory).all()
        session.close()
        if not rows or self._cached_matrix is None or self.vectorizer is None:
            return []
        q_vec = self.vectorizer.transform([query])
        sims = linear_kernel(q_vec, self._cached_matrix).flatten()
        top_idx = np.argsort(sims)[::-1][:top_k]
        results = []
        for i in top_idx:
            r = rows[i]
            results.append({
                "id": r.id,
                "kind": r.kind,
                "content": r.content,
                "score": float(sims[i]),
                "metadata": json.loads(r.meta_json or "{}")
            })
        return results



