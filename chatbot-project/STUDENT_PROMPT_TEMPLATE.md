# 📋 Student Prompt Template
## Copy this into Claude.ai to generate your chatbot code

---

### HOW TO USE THIS:

1. Copy everything inside the box below
2. **Replace the lines under "MY BUSINESS" with YOUR business idea**
3. Paste the whole thing into **claude.ai**
4. Copy the code Claude gives you into your Google Colab notebook
5. Follow the steps in `02_smart_chatbot_YOUR_TURN.ipynb` to run it

---

## ✂️ COPY FROM HERE ↓

```
I am a college student building an AI chatbot for a class project.
I need you to write complete Python code for Google Colab.

MY BUSINESS:
[REPLACE THIS LINE with 3-5 sentences describing your business.
Include: what you sell, where you are located, hours, prices,
any special features like delivery or vegan options, and how
customers can contact you. Make it up — be creative!]

EXAMPLE (do not use this — write your own):
"My business is called RamFit, a gym near VCU campus in Richmond Virginia.
We offer 24/7 access, group fitness classes, and personal training.
Monthly membership is $25 for students with a VCU ID. We have a smoothie bar
open 7am to 9pm. Parking is free after 5pm."

---

Please generate a complete Google Colab notebook using these EXACT requirements:

CELL 1 — Install libraries:
- Run: !pip install groq gradio -q
- Print: "Libraries installed!" when done

CELL 2 — The full chatbot code:
- Import: groq, gradio, and google.colab userdata
- Load the API key EXACTLY like this (do not change this line):
    GROQ_API_KEY = userdata.get('GROQ_API_KEY')
- Create a variable called BUSINESS_CONTEXT that contains a rich, detailed
  system prompt based on my business description above. Make it sound
  professional. Tell the AI to:
    * Be helpful and friendly
    * Give direct, useful answers — never just say "call us"
    * If it truly does not know something, suggest where to find out
      (like checking Instagram or the website)
    * Keep responses short since customers are on mobile
- Create a function called smart_chatbot(message, history) that:
    * Builds a list of messages starting with the system BUSINESS_CONTEXT
    * Adds the full conversation history so the AI remembers context
    * Calls the Groq API using model "llama-3.3-70b-versatile" with max_tokens=300
    * Has a try/except block:
        - If "rate_limit" is in the error, return:
          "Getting too many messages right now! Try again in a minute."
        - For any other error, return:
          "Something went wrong. Check that your GROQ_API_KEY is saved in Colab Secrets."
- Launch a Gradio ChatInterface with:
    * title = the name of my business + "— AI Assistant"
    * description = "Ask me anything!"
    * .launch() at the end

IMPORTANT RULES for the code you generate:
- Add beginner-friendly comments explaining what each section does
- Mark the BUSINESS_CONTEXT section clearly so I can edit it easily
- Output ONLY the code cells — no explanations outside the code
- Make sure the code runs perfectly in Google Colab with zero changes
  except for whatever is inside BUSINESS_CONTEXT
```

## ✂️ COPY UP TO HERE ↑

---

### AFTER YOU GET THE CODE FROM CLAUDE:

1. Go back to your Google Colab notebook (`02_smart_chatbot_YOUR_TURN.ipynb`)
2. Make sure you completed **Steps 1–3** (Groq account + API key + Colab Secrets)
3. **Delete** the code cell that's already in the notebook
4. **Add a new code cell** and paste Claude's code in
5. Run it — your chatbot should appear at the bottom!

---

### IF CLAUDE'S CODE DOESN'T WORK:

Copy the error message and go back to Claude.ai and say:

```
This code gave me the following error in Google Colab. Please fix it:

[paste the error here]
```

Claude will fix it. This is normal — even professional developers do this.
