# backend/personality_engine.py
from groq_client import groq_chat_completion

PERSONALITY_TEMPLATES = {
    "calm_mentor": "You are a calm, patient mentor. Reply in a supportive, slightly formal tone with clear step-by-step guidance. Keep responses concise and respectful.",
    "witty_friend": "You are a witty, playful friend. Use casual language, light humor, and keep it friendly while still being helpful.",
    "therapist_style": "You are empathetic and reflective like a therapist. Use validation and reflective listening, avoid commanding language, and offer gentle suggestions."
}

def transform_response(user_message, base_reply, target_personality, model=None):
    """
    Rewrites base_reply into the target personality. Returns rewritten text (string).
    """
    if target_personality not in PERSONALITY_TEMPLATES:
        raise ValueError("Unknown personality: " + str(target_personality))

    persona = PERSONALITY_TEMPLATES[target_personality]
    system = {"role":"system", "content": persona + " Output only the rewritten assistant reply, without any extra commentary or metadata."}
    user_prompt = (
        "Original assistant reply:\n"
        + base_reply
        + "\n\nUser message:\n"
        + user_message
        + "\n\nRewrite the assistant reply above to match the persona. Keep the factual content the same, only change tone and wording."
    )
    user = {"role":"user", "content": user_prompt}
    out = groq_chat_completion([system, user], model=model, temperature=0.7, max_tokens=400)
    return out.strip()

