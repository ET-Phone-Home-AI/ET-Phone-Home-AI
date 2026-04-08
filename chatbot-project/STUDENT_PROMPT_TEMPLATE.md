# AI Business Chatbot — Student Instructions

---

## STEP 1 — Get Your Free API Key

1. Go to **console.groq.com** → Sign in with Google → use your **@vcu.edu** email
2. Click **API Keys** → **Create API Key** → name it anything → Submit
3. **Copy the key immediately** (starts with `gsk_...`) — shown only once!

---

## STEP 2 — Fill In Your Business & Paste into Claude.ai

**Replace the ONE line that says [DESCRIBE YOUR BUSINESS HERE]**
then copy the whole prompt and paste into **claude.ai**

---

Write a Python chatbot script for PyCharm. My business: [DESCRIBE YOUR BUSINESS HERE in 2-3 sentences — what you sell, hours, location, prices].

Use these exact lines, do not change them:
- from groq import AsyncGroq
- import gradio as gr
- import httpx
- GROQ_API_KEY = "YOUR_KEY_HERE"
- client = AsyncGroq(api_key=GROQ_API_KEY, http_client=httpx.AsyncClient(verify=False))
- async def smart_chatbot(message, history)
- for msg in history: messages.append({"role": msg["role"], "content": msg["content"]})
- model="llama-3.3-70b-versatile", max_tokens=300
- gr.ChatInterface(smart_chatbot, title="[Business Name] AI Assistant").launch()

Create a BUSINESS_CONTEXT variable describing my business for the AI to use as its instructions. Add error handling that returns "Too many messages! Try again in a moment." for rate limits and "Something went wrong. Check your API key." for other errors. Output Python code only.

---

## STEP 3 — Paste the Code into PyCharm

1. Open PyCharm → **File → New → Python File** → name it `my_chatbot.py`
2. Paste all the code Claude gave you

---

## STEP 4 — Install the Packages

Open the **PyCharm Terminal** (bottom of screen) and run:
```
pip install groq gradio httpx
```

---

## STEP 5 — Add Your API Key

Find this line in the code:
```
GROQ_API_KEY = "YOUR_KEY_HERE"
```
Replace `YOUR_KEY_HERE` with your `gsk_...` key

---

## STEP 6 — Run It!

Hit the green **Run** button → browser opens with your chatbot 🎉

> **Tip:** After typing a message, wait 3-5 seconds for the AI to respond before typing again.

---

## IF YOU GET AN ERROR

Copy the error from PyCharm, go back to **claude.ai** and say:
> *My Python code gave me this error. Please fix it:*
> [paste error here]

---

## AFTER CLASS

Go to `console.groq.com` → API Keys → **Delete** your key. Takes 10 seconds.
