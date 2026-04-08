# Student Prompt — AI Business Chatbot
## Use this with Claude.ai to build your own smart chatbot in PyCharm

---

## BEFORE YOU START — Get Your Free API Key (5 minutes)

1. Open a new browser tab → go to **console.groq.com**
2. Click **"Sign in with Google"** → select your **@vcu.edu** email
3. Click **"API Keys"** in the top navigation bar
4. Click **"Create API Key"** → name it anything (e.g. `VCU-Chatbot`)
5. Click **Submit**
6. **COPY THE KEY IMMEDIATELY** — it starts with `gsk_` and is shown only once
7. Paste it somewhere safe (Notes app, email to yourself) — you'll need it in a moment

> ⚠️ **Do NOT add a credit card. You don't need one. It's completely free.**

---

## YOUR STEPS

1. Fill in YOUR business description in the prompt below
2. Copy the entire prompt and paste it into **claude.ai**
3. Copy ALL the Python code Claude gives you
4. Open **PyCharm** → File → New → Python File → name it `my_chatbot.py`
5. Paste the code in
6. Open the **PyCharm Terminal** (bottom of screen) and run:
   ```
   pip install groq gradio httpx
   ```
7. Find the line `GROQ_API_KEY = "YOUR_KEY_HERE"` → replace with your `gsk_...` key
8. Hit the green **Run** button → a browser tab opens with your chatbot!

---

## THE PROMPT — Copy everything in the box below and paste into claude.ai

---

I need you to write a complete Python script for a smart AI business chatbot that I will run in PyCharm on a Windows computer connected to a university network.

MY BUSINESS:
[REPLACE THIS with 4 to 6 sentences describing your business. Include: what you sell, hours, location, prices, any special features like delivery or dietary options, and how customers contact you. Make it up and be creative! Examples: sneaker store, campus gym, food truck, nail salon, tutoring service, travel agency, gaming lounge.]

Please generate one complete Python file using these EXACT requirements. Do not change any of the technical lines — they are required to make the code work on a university network.

IMPORTS — use exactly these:
```
from groq import AsyncGroq
import gradio as gr
import httpx
```

API KEY LINE — use exactly this:
```
GROQ_API_KEY = "YOUR_KEY_HERE"
```

CLIENT LINE — use exactly this (the verify=False is required for university WiFi):
```
client = AsyncGroq(api_key=GROQ_API_KEY, http_client=httpx.AsyncClient(verify=False))
```

BUSINESS CONTEXT — create a variable called BUSINESS_CONTEXT with a detailed system prompt based on my business above. The AI assistant should:
- Be helpful, friendly, and stay on topic
- Give real, specific answers — NEVER just say "call us" or "visit our website" as the only answer
- If it doesn't know something specific (like today's special), suggest a helpful alternative like checking Instagram
- Keep responses short since customers may be on their phones

CHATBOT FUNCTION — use exactly this structure:
```
async def smart_chatbot(message, history):
    messages = [{"role": "system", "content": BUSINESS_CONTEXT}]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": message})
    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        if "rate_limit" in str(e).lower():
            return "Too many messages at once! Wait a moment and try again."
        return "Something went wrong. Double-check that your API key is correct."
```

LAUNCH — use exactly this at the bottom (do not add type="messages"):
```
gr.ChatInterface(
    smart_chatbot,
    title="[Business Name] AI Assistant",
    description="Powered by Llama 3.3 via Groq — Ask me anything!"
).launch()
```

After the launch line, add a commented block with 6 test questions specific to my business — including at least one follow-up question that tests if the chatbot remembers the conversation.

Rules:
- Output only the Python code — no explanation text outside the code
- Add a comment at the very top: # pip install groq gradio httpx
- Clearly label the BUSINESS_CONTEXT section so I can edit it
- Do not change any of the exact lines specified above

---

## AFTER YOU GET THE CODE

- Paste into PyCharm
- Run in terminal: `pip install groq gradio httpx`
- Replace `YOUR_KEY_HERE` with your real `gsk_...` key
- Hit the green Run button
- Browser opens automatically with your chatbot

## KNOWN BEHAVIOR — READ THIS

> After you type a message and press Enter, **wait 3-5 seconds**.
> The AI is thinking — you will see a loading indicator.
> Do not type again until the response appears.
> If nothing happens after 10 seconds, press Enter once with an empty box.

## IF YOU GET AN ERROR

Copy the full error from PyCharm, go back to claude.ai and say:

> My Python code gave me this error in PyCharm on a university network. Please fix it and give me the corrected full script:
> [paste error here]

## AFTER CLASS — DELETE YOUR API KEY

Go to `console.groq.com` → API Keys → click **Delete** next to your key.
This is what real developers do with keys they no longer need. Takes 10 seconds.
