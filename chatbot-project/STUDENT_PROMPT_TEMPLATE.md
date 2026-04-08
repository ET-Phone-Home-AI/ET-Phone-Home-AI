# AI Chatbot — Class Instructions

---

## STEP 1 — Get Your Groq API Key (2 min)
1. Go to **console.groq.com** → Sign in with Google → **@vcu.edu**
2. Click **API Keys** → **Create API Key** → Submit
3. **Copy the key** (starts with `gsk_`) — shown only ONCE

---

## STEP 2 — Type This Into claude.ai (2 min)

> Change only the line that says **[YOUR BUSINESS]**

```
Write a Python chatbot for PyCharm on university WiFi.
My business: [YOUR BUSINESS — one sentence, what you sell, hours, price]
Use: from groq import AsyncGroq, import gradio as gr, import httpx
GROQ_API_KEY = "YOUR_KEY_HERE"
client = AsyncGroq(api_key=GROQ_API_KEY, http_client=httpx.AsyncClient(verify=False))
async def smart_chatbot(message, history)
for msg in history: messages.append({"role": msg["role"], "content": msg["content"]})
model="llama-3.3-70b-versatile", max_tokens=300
gr.ChatInterface(smart_chatbot, title="My Business AI Assistant").launch()
Output Python code only.
```

---

## STEP 3 — Run It (1 min)
1. PyCharm → New File → `my_chatbot.py` → paste the code
2. PyCharm Terminal: `pip install groq gradio httpx`
3. Replace `YOUR_KEY_HERE` with your `gsk_...` key
4. Hit **Run** → browser opens → your chatbot is live 🎉

---

> After typing a message wait 3-5 seconds for the AI to respond.
> If stuck: copy the error → go back to claude.ai → paste it and say *"fix this"*
> After class: console.groq.com → API Keys → Delete your key
