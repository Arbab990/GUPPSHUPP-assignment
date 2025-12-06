# backend/memory_extractor.py
import json
import re
from groq_client import groq_chat_completion

EXTRACTION_PROMPT_TEMPLATE = """
You are an assistant that analyzes a sequence of user messages and outputs EXACTLY
one JSON object (no explanatory text) with three arrays: preferences, emotional_patterns, facts.

Input: a numbered list of messages from the same user.

Task:
- preferences: short phrases about likes/dislikes/habits (food, hobbies, formats). Keep each as a brief phrase.
- emotional_patterns: behavioral or emotional tendencies (e.g., "often anxious about deadlines").
- facts: objective facts worth remembering (job title, DOB, location, recurring constraints).

Each item must be an object with fields:
  - text (string)
  - source_idx (integer index of the source message)
  - confidence (float between 0.0 and 1.0)

Return JSON exactly in this format:
{
  "preferences": [{"text":"...","source_idx":1,"confidence":0.95}, ...],
  "emotional_patterns": [{"text":"...","source_idx":2,"confidence":0.88}, ...],
  "facts": [{"text":"...","source_idx":3,"confidence":0.98}, ...]
}

Now analyze the following messages:
{messages_block}
"""

def _extract_json_from_text(raw_text):
    """
    Try to parse JSON directly; otherwise extract the first {...} substring and parse it.
    Raises ValueError if unable to parse.
    """
    try:
        return json.loads(raw_text)
    except Exception:
        m = re.search(r"(\{(?:.|\s)*\})", raw_text)
        if m:
            candidate = m.group(1)
            try:
                return json.loads(candidate)
            except Exception as e:
                raise ValueError(f"Could not parse JSON substring: {e}\nSubstring was:\n{candidate[:2000]}")
        raise ValueError("Model output did not contain valid JSON. Raw output:\n" + raw_text[:2000])

def extract_memories(messages_list, model=None):
    """
    messages_list: list[str]
    returns dict with keys: preferences, emotional_patterns, facts
    """
    if not isinstance(messages_list, list):
        raise ValueError("messages_list must be a list of strings")

    # prepare numbered block
    numbered = "\n".join([f"{i+1}. {m}" for i, m in enumerate(messages_list)])
    prompt = EXTRACTION_PROMPT_TEMPLATE.replace("{messages_block}", numbered)

    system_msg = {"role": "system", "content": "You are a memory extraction system. Output must be valid JSON only."}
    user_msg = {"role": "user", "content": prompt}

    raw = groq_chat_completion([system_msg, user_msg], model=model, temperature=0.0, max_tokens=800)

    parsed = _extract_json_from_text(raw)

    # Validate structure and normalize
    for key in ("preferences", "emotional_patterns", "facts"):
        if key not in parsed or not isinstance(parsed[key], list):
            parsed[key] = []

    # Ensure each item has text, source_idx, confidence (fill defaults if missing)
    def _normalize_item(it, idx):
        text = it.get("text") if isinstance(it, dict) else str(it)
        source_idx = int(it.get("source_idx", idx+1)) if isinstance(it, dict) and it.get("source_idx") else idx+1
        confidence = float(it.get("confidence", 0.8)) if isinstance(it, dict) and it.get("confidence") is not None else 0.8
        return {"text": text, "source_idx": source_idx, "confidence": confidence}

    for key in ("preferences", "emotional_patterns", "facts"):
        normalized = []
        for i, item in enumerate(parsed.get(key, [])):
            try:
                normalized.append(_normalize_item(item, i))
            except Exception:
                # skip malformed item
                continue
        parsed[key] = normalized

    return parsed



