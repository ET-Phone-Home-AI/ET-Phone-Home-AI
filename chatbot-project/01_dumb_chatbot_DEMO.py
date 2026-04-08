# =============================================================
# THE DUMB CHATBOT — Instructor Demo
# =============================================================
# BEFORE RUNNING: Install gradio once in PyCharm
#   Go to: Settings > Python Interpreter > + > search "gradio" > Install
#   OR open PyCharm terminal and type: pip install gradio
# =============================================================

import gradio as gr

# -------------------------------------------------------
# THIS IS THE ENTIRE "AI" — just keyword matching.
# No intelligence. No understanding. Just a lookup table.
# -------------------------------------------------------

def dumb_chatbot(message, history):
    message = message.lower().strip()

    if "hours" in message or "open" in message or "close" in message:
        return "Our hours are Monday-Friday, 9am to 5pm."

    elif "delivery" in message or "deliver" in message:
        return "Yes, we offer delivery. Minimum order is $20."

    elif "price" in message or "cost" in message or "how much" in message:
        return "Please visit our website to view pricing."

    elif "cancel" in message or "refund" in message or "return" in message:
        return "For cancellations and refunds, please call us at 555-0100."

    elif "hello" in message or "hi" in message or "hey" in message:
        return "Hello! How can I help you today?"

    elif "thank" in message:
        return "You're welcome! Is there anything else I can help with?"

    else:
        # ← THIS IS THE PROBLEM. Everything else hits this wall.
        return "I'm sorry, I don't understand that. Please call us at 555-0100 for assistance."


# This opens a chat window in your browser automatically
gr.ChatInterface(
    dumb_chatbot,
    title="☕ Campus Coffee Shop — Customer Support",
    description="Ask me anything about our coffee shop!"
).launch()

# =============================================================
# TRY THESE QUESTIONS — watch it fail:
#   "Do you have oat milk?"
#   "My friend has a nut allergy, is it safe?"
#   "What's your most popular drink?"
#   "Are you open on Thanksgiving?"
#   "Can I pay with Apple Pay?"
# =============================================================
