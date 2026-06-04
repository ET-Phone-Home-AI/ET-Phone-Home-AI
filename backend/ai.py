import httpx
import re

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3"

SYSTEM_PROMPT = """You are a knowledgeable and caring orthodontic assistant at a university dental clinic.
Your role is to help patients understand their orthodontic treatment, answer questions about braces,
aligners, retainers, and general oral hygiene during treatment.

Guidelines:
- Be warm, reassuring, and easy to understand — avoid heavy jargon.
- If a patient reports pain, swelling, a broken bracket, or a poking wire, advise them to contact the clinic immediately and provide the clinic number: (804) 555-0100.
- Never diagnose conditions or prescribe medication.
- For questions requiring clinical judgment, tell the patient you will pass the message to their professor/doctor.
- Keep answers concise (2-4 short paragraphs max).
- Always end with an offer to help with any other questions."""

ESCALATION_KEYWORDS = [
    "pain", "hurts", "swelling", "swollen", "bleeding", "broken", "poking",
    "wire", "lost", "fell off", "infection", "fever", "emergency", "severe"
]

RULE_BASED_RESPONSES = {
    "braces": "Braces use brackets and wires to gradually move your teeth into the correct position. Each adjustment appointment tightens or changes the wires to keep applying gentle pressure. The process typically takes 12–24 months depending on your case.",
    "aligner": "Clear aligners like Invisalign are removable trays that shift your teeth incrementally. You wear each set for about 1–2 weeks. Remember to wear them 20–22 hours per day for best results.",
    "retainer": "Retainers hold your teeth in their new positions after braces or aligners. Your doctor will advise how long to wear them — often full-time at first, then nightly. Always store your retainer in its case when not in use.",
    "brush": "With braces, brush after every meal using a soft-bristled toothbrush. Angle the brush along the gumline and around each bracket. Floss daily using a floss threader or orthodontic flosser to clean between teeth and wires.",
    "food": "Avoid hard, sticky, or crunchy foods: popcorn, hard candy, ice, bagels, carrots, and gum. These can break brackets or bend wires. Cut apples and other firm fruits into small pieces.",
    "appointment": "Your adjustment appointments are usually scheduled every 4–8 weeks. These visits let us monitor your progress and make necessary wire changes. Please contact us if you need to reschedule.",
    "soreness": "Some soreness for 2–5 days after each adjustment is completely normal. Over-the-counter pain relievers like ibuprofen and a soft-food diet can help. If pain is severe or unusual, please call us.",
    "color": "You can choose the color of the elastic bands (ligatures) on your brackets at each appointment — it is a fun way to personalize your braces! Colors are changed at every visit.",
    "cost": "For specific cost or insurance questions, please contact our front desk at (804) 555-0100 or ask your professor at your next visit.",
    "hello": "Hello! I am your orthodontic assistant. Feel free to ask me anything about your braces, aligners, or treatment.",
    "hi": "Hi there! How can I help you with your orthodontic treatment today?",
    "thank": "You are very welcome! Do not hesitate to reach out if you have more questions.",
}


def check_escalation(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in ESCALATION_KEYWORDS)


def rule_based_response(text: str) -> str | None:
    text_lower = text.lower()
    for keyword, response in RULE_BASED_RESPONSES.items():
        if keyword in text_lower:
            return response
    return None


async def get_ai_response(messages: list[dict]) -> dict:
    """Try Ollama first, fall back to rule-based engine."""
    user_text = messages[-1]["content"] if messages else ""

    if check_escalation(user_text):
        return {
            "content": (
                "I noticed your message may involve discomfort or an urgent issue. "
                "Please contact the clinic immediately at **(804) 555-0100**. "
                "Your professor has also been notified. If this is after hours and the issue is severe, "
                "please visit an urgent care or emergency facility."
            ),
            "source": "rule"
        }

    try:
        payload = {
            "model": OLLAMA_MODEL,
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            "stream": False
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(OLLAMA_URL, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return {
                "content": data["message"]["content"],
                "source": "ollama"
            }
    except Exception:
        pass

    # Rule-based fallback
    rule_resp = rule_based_response(user_text)
    if rule_resp:
        return {"content": rule_resp, "source": "rule"}

    return {
        "content": (
            "Thank you for your question! This is a great topic to discuss with your orthodontist. "
            "If you have an urgent concern, please call our clinic at **(804) 555-0100**. "
            "Your professor will review your question and follow up at your next appointment. "
            "Is there anything else I can help you with?"
        ),
        "source": "rule"
    }
