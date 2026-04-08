# =============================================================
# API KEY TEST — Run this first to confirm your key works
# =============================================================
# If this prints a response, your key is working correctly.
# If it prints an error, check that your key is pasted correctly.
# =============================================================

import httpx
from groq import Groq

# Paste your Groq API key here (starts with gsk_...)
GROQ_API_KEY = "YOUR_KEY_HERE"

client = Groq(
    api_key=GROQ_API_KEY,
    http_client=httpx.Client(verify=False)
)

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "say hello in one sentence"}],
    max_tokens=20
)

print("SUCCESS! API key works.")
print("Response:", response.choices[0].message.content)
