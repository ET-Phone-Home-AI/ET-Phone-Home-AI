# Student Prompt — AI Business Chatbot
## Use this with Claude.ai to generate your Python chatbot code

---

### YOUR STEPS:

1. Read the prompt below
2. Fill in YOUR business description where it says [WRITE YOUR BUSINESS HERE]
3. Copy the entire prompt and paste it into **claude.ai**
4. Copy the Python code Claude gives you
5. Open PyCharm → New File → save as `my_chatbot.py`
6. Paste the code in
7. Find the line that says `GROQ_API_KEY = "YOUR_KEY_HERE"` and replace with your key
8. Run it — a browser tab opens with your chatbot

---

## THE PROMPT — Copy everything below this line and paste into claude.ai

---

I need you to write a Python script for a smart AI business chatbot that I will run in PyCharm. Here is my business:

[WRITE YOUR BUSINESS HERE — describe it in 4 to 6 sentences. Include what you sell, your hours, location, prices, any special options like delivery or dietary choices, and how customers can reach you. Make it up and be creative. Examples: a sneaker store, a campus gym, a food truck, a nail salon, a tutoring service, a travel agency.]

Please generate one complete Python file using these exact requirements:

1. At the very top, add a comment block listing the two install commands the student needs to run first:
   pip install groq
   pip install gradio

2. Import groq and gradio

3. Add this exact line so the student can paste their API key:
   GROQ_API_KEY = "YOUR_KEY_HERE"

4. Create a variable called BUSINESS_CONTEXT. This is a detailed description of the business above written as instructions for an AI assistant. The AI should:
   - Be helpful, friendly, and stay on topic for this business
   - Give real, specific answers — never just say "call us" or "visit our website" as the only response
   - If it does not know something very specific like today's special or current inventory, suggest a helpful alternative like checking social media or coming in person
   - Keep responses concise since customers may be on their phones

5. Create a function called smart_chatbot that takes message and history as parameters and does the following:
   - Builds a messages list that starts with the BUSINESS_CONTEXT as the system role
   - Loops through the history and adds each past message pair to the list so the AI remembers the full conversation
   - Appends the current user message
   - Calls the Groq API using the model named llama-3.3-70b-versatile with max_tokens set to 300
   - Returns the AI response text
   - Has a try except block that catches errors and returns this message if rate_limit appears in the error: "Too many messages at once! Wait a moment and try again." and returns this for any other error: "Something went wrong. Make sure your API key is correct in the code."

6. At the bottom, launch a Gradio ChatInterface with:
   - The function smart_chatbot
   - A title that uses my business name
   - A short description line
   - .launch() to start it

7. After the launch line, add a commented section with 6 suggested test questions specific to my business that a real customer might ask — including at least one tricky follow-up question that tests whether the chatbot remembers context.

Rules for the code you generate:
- Output only the Python code — no explanation text outside the code
- Use comments inside the code to label each section clearly
- The BUSINESS_CONTEXT section must be clearly marked so I can edit it later
- The code must run in PyCharm with no changes other than replacing YOUR_KEY_HERE with a real API key

---

### AFTER YOU GET THE CODE:

- Paste it into PyCharm
- Open the PyCharm Terminal at the bottom and run:
  ```
  pip install groq gradio
  ```
- Replace `YOUR_KEY_HERE` with your Groq API key
- Hit the green Run button
- Your chatbot opens in the browser automatically

### IF YOU GET AN ERROR:

Copy the full error from PyCharm, go back to claude.ai, and say:

> My Python code gave me this error. Please fix it and give me the corrected full script:
> [paste error here]

### AFTER CLASS — DELETE YOUR API KEY:

Go to console.groq.com → API Keys → click Delete next to your key.
This is what developers do with keys they no longer need. Takes 10 seconds.
