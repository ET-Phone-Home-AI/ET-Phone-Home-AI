"""
╔══════════════════════════════════════════════════════════════╗
║  app.py  —  The Web App                                      ║
║                                                              ║
║  What this file does:                                        ║
║    Runs a tiny WEBSITE on your own computer.                 ║
║    You open it in Chrome/Firefox.                            ║
║    The RFID reader types into the webpage's input box.       ║
║    The page shows who scanned and logs the attendance.       ║
║                                                              ║
║  NOTE: START_HERE.py → Option 4 launches this for you.       ║
║  Manual run:  python app.py                                  ║
║  Then open:   http://127.0.0.1:5000                          ║
╚══════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT IS FLASK?
  Flask is a Python library that lets you build websites.
  Normally making a website needs HTML + CSS + JavaScript +
  a server + a lot of setup. Flask does all that server work
  for you in a few lines of Python code.

  pip install flask   ←  installs it (START_HERE.py does this automatically)

WHAT IS  http://127.0.0.1:5000 ?
  127.0.0.1 = "this computer" (also called localhost)
  5000      = the "door number" (port) Flask listens on
  So this address means: "open the website running on MY computer, door 5000"
  It only works on your machine — not the internet.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────────────────────

# Flask   = the web framework (library that makes websites easy)
# request = lets us read what the user submitted in the form
# render_template_string = turns a Python HTML string into a real webpage
from flask import Flask, request, render_template_string

import sqlite3                   # talks to our database
from datetime import datetime    # gets the current date and time

# ─────────────────────────────────────────────────────────────────────────────
# CREATE THE APP
# Flask(__name__) creates our web application object.
# __name__ tells Flask which file it's running from.
# ─────────────────────────────────────────────────────────────────────────────
app = Flask(__name__)

DB_NAME = "attendance.db"


# ─────────────────────────────────────────────────────────────────────────────
# THE HTML PAGE
#
# This is the entire webpage written as a Python string.
# {{ variable }} = Flask fills this in with a Python value
# {% if ... %}   = Flask's version of  if  (runs inside HTML)
# ─────────────────────────────────────────────────────────────────────────────
PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RFID Attendance</title>
    <style>
        /* CSS = styling rules for how the page looks */

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .card {
            background: white;
            border-radius: 16px;
            padding: 40px;
            width: 100%;
            max-width: 480px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.4);
        }

        .header {
            text-align: center;
            margin-bottom: 32px;
        }

        .header .icon { font-size: 3rem; }

        .header h1 {
            font-size: 1.5rem;
            color: #1a202c;
            margin-top: 8px;
        }

        .header p {
            color: #718096;
            font-size: 0.9rem;
            margin-top: 4px;
        }

        /* The scan input field */
        .scan-box {
            background: #f7fafc;
            border: 3px dashed #4299e1;
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            margin-bottom: 20px;
        }

        .scan-box label {
            display: block;
            font-size: 0.85rem;
            font-weight: 600;
            color: #4a5568;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .scan-box input {
            width: 100%;
            padding: 14px;
            font-size: 1.2rem;
            text-align: center;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            letter-spacing: 3px;
            font-family: monospace;
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
        }

        .scan-box input:focus {
            border-color: #4299e1;
            box-shadow: 0 0 0 3px rgba(66,153,225,0.2);
        }

        .pulse {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #48bb78;
            border-radius: 50%;
            margin-right: 6px;
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50%       { opacity: 0.4; transform: scale(0.8); }
        }

        button {
            width: 100%;
            padding: 14px;
            background: #4299e1;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s, transform 0.1s;
        }

        button:hover   { background: #3182ce; }
        button:active  { transform: scale(0.98); }

        /* Result cards */
        .result {
            margin-top: 24px;
            border-radius: 12px;
            overflow: hidden;
        }

        .result-header {
            padding: 14px 20px;
            font-weight: 700;
            font-size: 1rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .found   .result-header { background: #c6f6d5; color: #22543d; }
        .unknown .result-header { background: #fed7d7; color: #742a2a; }

        .result-body { padding: 16px 20px; background: #f7fafc; }

        .row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #e2e8f0;
            font-size: 0.95rem;
        }

        .row:last-child   { border-bottom: none; }
        .row .key         { color: #718096; }
        .row .val         { font-weight: 600; color: #2d3748; }

        .timestamp {
            text-align: right;
            font-size: 0.78rem;
            color: #a0aec0;
            padding-top: 8px;
        }

        .footer {
            text-align: center;
            margin-top: 24px;
            font-size: 0.8rem;
            color: #a0aec0;
        }
    </style>

    <script>
        // JavaScript runs in the BROWSER (not Python).
        // This small script auto-focuses the input field when the page loads.
        // Without this, you'd have to click the box before scanning.
        window.onload = function() {
            var box = document.getElementById("uid_box");
            box.focus();    // move cursor into the box
            box.select();   // highlight any old text so new scan replaces it
        };
    </script>
</head>
<body>
    <div class="card">

        <!-- PAGE HEADER -->
        <div class="header">
            <div class="icon">📡</div>
            <h1>RFID Attendance System</h1>
            <p><span class="pulse"></span> Ready to scan</p>
        </div>

        <!-- SCAN FORM
             method="POST" means: when submitted, send data to the server (Python).
             action="/"    means: send it to the main page route.
        -->
        <form method="POST" action="/">
            <div class="scan-box">
                <label>Scan bracelet or type UID</label>
                <input
                    type="text"
                    id="uid_box"
                    name="uid"
                    placeholder="Waiting for scan..."
                    autocomplete="off"
                    value="{{ uid or '' }}"
                >
            </div>
            <button type="submit">Look Up Student ▶</button>
        </form>

        <!-- RESULT SECTION
             This section only appears if the form was submitted.
             {% if result %} is Flask's if statement inside HTML.
        -->
        {% if result %}

            {% if result.found %}
                <!-- ── STUDENT FOUND ── -->
                <div class="result found">
                    <div class="result-header">
                        ✔ Student Found — Attendance Logged
                    </div>
                    <div class="result-body">
                        <div class="row">
                            <span class="key">Student ID</span>
                            <span class="val">{{ result.student_id }}</span>
                        </div>
                        <div class="row">
                            <span class="key">Full Name</span>
                            <span class="val">{{ result.full_name }}</span>
                        </div>
                        <div class="row">
                            <span class="key">Department</span>
                            <span class="val">{{ result.department }}</span>
                        </div>
                        <div class="row">
                            <span class="key">Section</span>
                            <span class="val">{{ result.section }}</span>
                        </div>
                        <div class="row">
                            <span class="key">Bracelet</span>
                            <span class="val">{{ result.label or '—' }}</span>
                        </div>
                        <p class="timestamp">Logged at {{ result.timestamp }}</p>
                    </div>
                </div>

            {% else %}
                <!-- ── UNKNOWN TAG ── -->
                <div class="result unknown">
                    <div class="result-header">
                        ✘ Unknown Tag
                    </div>
                    <div class="result-body">
                        <p style="color:#c53030;">
                            UID <strong>{{ uid }}</strong> is not registered.
                        </p>
                        <p style="margin-top:8px; color:#718096; font-size:0.9rem;">
                            Run the app → Option 2 to register this bracelet.
                        </p>
                    </div>
                </div>
            {% endif %}

        {% endif %}

        <p class="footer">
            The input field auto-focuses so every scan is captured automatically.
        </p>

    </div>
</body>
</html>
"""


# ─────────────────────────────────────────────────────────────────────────────
# DATABASE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def lookup_student(uid):
    """
    Opens the database, finds the student for this UID, closes, returns result.
    Returns a sqlite3.Row object (dict-like) or None.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    # row_factory = sqlite3.Row lets us access columns by name:  row["full_name"]
    # instead of by position:  row[1]

    row = conn.execute("""
        SELECT
            s.student_id, s.full_name, s.department, s.section,
            t.tag_id, t.label
        FROM rfid_tags AS t
        JOIN students  AS s ON t.student_id = s.student_id
        WHERE t.uid = ?
    """, (uid,)).fetchone()

    conn.close()
    return row


def log_scan(tag_id):
    """Saves one scan event to the database."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("INSERT INTO scan_events (tag_id) VALUES (?)", (tag_id,))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# THE ROUTE
#
# A "route" is a web address (URL) that Flask listens to.
# @app.route("/") means: when someone visits  http://127.0.0.1:5000/
# call the function below.
#
# methods=["GET", "POST"]
#   GET  = when you first open the page (just show the form)
#   POST = when you click the button / scanner submits (process the UID)
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    uid = None

    if request.method == "POST":
        # request.form is a dictionary of everything submitted in the form.
        # We get the value from the field named "uid".
        uid = request.form.get("uid", "").strip()

        if uid:
            row = lookup_student(uid)

            if row:
                log_scan(row["tag_id"])
                result = {
                    "found":      True,
                    "student_id": row["student_id"],
                    "full_name":  row["full_name"],
                    "department": row["department"],
                    "section":    row["section"],
                    "label":      row["label"],
                    "timestamp":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            else:
                result = {"found": False}

    # render_template_string(PAGE, ...) takes the HTML string above,
    # fills in all the {{ }} placeholders, and sends it to the browser.
    return render_template_string(PAGE, result=result, uid=uid)


# ─────────────────────────────────────────────────────────────────────────────
# START THE SERVER (runs only when called directly: python app.py)
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  RFID ATTENDANCE — WEB APP")
    print("=" * 50)
    print("\n  Open your browser and go to:")
    print("  ▶  http://127.0.0.1:5000")
    print("\n  Press Ctrl+C to stop.\n")
    app.run(debug=True)
