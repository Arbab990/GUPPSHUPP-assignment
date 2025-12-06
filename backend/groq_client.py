# backend/groq_client.py
import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
# prefer a working model discovered earlier
DEFAULT_MODEL = os.getenv("GROQ_DEFAULT_MODEL", "groq/compound-mini")
GROQ_BASE = "https://api.groq.com/openai/v1"

def _raise_for_bad_response(resp):
    try:
        body = resp.text
    except Exception:
        body = "<no body>"
    raise RuntimeError(f"HTTP {resp.status_code} from Groq: {body}")

def groq_chat_completion(messages, model=None, temperature=0.0, max_tokens=512, n=1, timeout=60):
    """
    messages: list of {"role":"system"/"user"/"assistant","content":"..."}
    Returns: assistant reply string on success, otherwise raises RuntimeError.
    """
    if model is None:
        model = DEFAULT_MODEL

    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY environment variable not set")

    url = f"{GROQ_BASE}/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "n": n
    }
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
    if not (200 <= resp.status_code < 300):
        _raise_for_bad_response(resp)

    # parse response robustly
    try:
        data = resp.json()
    except Exception:
        # return raw text if JSON can't be parsed
        return resp.text

    # typical OpenAI-style: choices[0].message.content
    try:
        if isinstance(data, dict) and "choices" in data and data["choices"]:
            first = data["choices"][0]
            # OpenAI-style message content
            if "message" in first and isinstance(first["message"], dict) and "content" in first["message"]:
                return first["message"]["content"]
            # older style text field
            if "text" in first:
                return first["text"]
        # alternative structures
        if isinstance(data, dict) and "output" in data:
            out = data["output"]
            return out if isinstance(out, str) else json.dumps(out)
        if isinstance(data, dict) and "result" in data:
            res = data["result"]
            return res if isinstance(res, str) else json.dumps(res)
        # fallback: stringify full JSON
        return json.dumps(data)
    except Exception:
        return json.dumps(data)


