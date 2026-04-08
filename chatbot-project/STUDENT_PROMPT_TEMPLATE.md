# 📋 Student Prompt Template
## Copy this into Claude.ai to generate your chatbot code

---

### HOW TO USE THIS:

1. Copy everything inside the box below
2. **Replace the lines under "MY BUSINESS" with YOUR business idea**
3. Paste the whole thing into **claude.ai**
4. Copy the code Claude gives you
5. Open PyCharm → create a new file called `my_chatbot.py`
6. Paste the code in → Run it

---

## ✂️ COPY FROM HERE ↓

```
I am a college student building an AI chatbot in Python using PyCharm.

MY BUSINESS:
[REPLACE THIS with 3-5 sentences describing your business.
Include: what you sell, where you are located, hours, prices,
any special features like delivery or vegan options.
Make it up — be creative!]

EXAMPLE (do not use this — write your own):
"My business is called RamFit, a gym near VCU campus in Richmond Virginia.
We offer 24/7 access, group fitness classes, and personal training.
Monthly membership is $25 for students with a valid VCU ID.
We have a smoothie bar open 7am to 9pm. Parking is free after 5pm."

---

Please generate a complete Python script (.py file) for PyCharm
using these EXACT requirements:

1. Import: groq and gradio

2. API key line (use exactly this):
   GROQ_API_KEY = "YOUR_KEY_HERE"

3. Create a variable called BUSINESS_CONTEXT that contains a detailed
   system prompt based on my business above. Make it sound professional.
   Tell the AI to:
   - Be helpful and friendly
   - Give direct, useful answers — never just say "call us"
   - If it truly does not know something, suggest where to find out
   - Keep responses short since customers may be on mobile

4. Create a function called smart_chatbot(message, history) that:
   - Builds a list of messages starting with the system BUSINESS_CONTEXT
   - Adds the full conversation history so the AI remembers context
   - Calls the Groq API using model "llama-3.3-70b-versatile" with max_tokens=300
   - Has a try/except block:
       If "rate_limit" is in the error return:
         "Getting too many messages right now! Try again in a minute."
       For any other error return:
         "Something went wrong. Check that your API key is correct."

5. Launch a Gradio ChatInterface with:
   - title = the name of my business + " — AI Assistant"
   - description = "Ask me anything!"
   - .launch() at the end

IMPORTANT RULES:
- Output a single clean .py file only — no explanations outside the code
- Add a comment at the top listing which packages to install:
  pip install groq gradio
- Clearly mark the BUSINESS_CONTEXT section so I can edit it easily
- Add a comment at the bottom with 5 sample questions to test the chatbot
- The script must run perfectly in PyCharm with zero changes
  other than replacing YOUR_KEY_HERE with a real API key
```

## ✂️ COPY UP TO HERE ↑

---

### AFTER YOU GET THE CODE FROM CLAUDE:

1. In PyCharm, go to **File → New → Python File** → name it `my_chatbot.py`
2. Paste Claude's code into the file
3. Install the packages:
   - Open the PyCharm **Terminal** (bottom of screen)
   - Type: `pip install groq gradio` → press Enter
4. Replace `YOUR_KEY_HERE` with your actual Groq API key
5. Press the **green Run button** (top right)
6. A browser tab will open automatically with your chatbot!

---

### IF THE CODE DOESN'T WORK:

Copy the error message from PyCharm and go back to Claude.ai and say:

```
This Python code gave me the following error in PyCharm. Please fix it:

[paste the error here]
```

Claude will fix it. This is normal — even professional developers do this.
