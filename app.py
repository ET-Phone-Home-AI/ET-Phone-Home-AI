"""
app.py
------
PART 6 — WEB APPLICATION (FLASK)

A simple web interface for the RFID attendance system.
- One input field on the page receives the UID typed by the RFID reader.
- On form submit it looks up the student and logs the scan.
- Shows student info or "Unknown tag".
- Uses render_template_string (no separate HTML files needed).

Requirements:
    pip install flask

Usage:
    python app.py
Then open http://127.0.0.1:5000 in your browser.
"""

from flask import Flask, request, render_template_string
import sqlite3
from datetime import datetime

# ── App setup ────────────────────────────────────────────────────────────────
app = Flask(__name__)
DB_NAME = "attendance.db"


# ─────────────────────────────────────────────────────────────────────────────
# HTML TEMPLATE
# Written as a Python string — no separate .html file needed.
# Jinja2 placeholders like {{ variable }} are filled in by Flask.
# ─────────────────────────────────────────────────────────────────────────────
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RFID Attendance System</title>
    <style>
        /* ── Basic, clean styling ── */
        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: Arial, sans-serif;
            background: #f0f4f8;
            display: flex;
            justify-content: center;
            padding: 40px 16px;
            min-height: 100vh;
        }

        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
            padding: 40px;
            width: 100%;
            max-width: 520px;
            height: fit-content;
        }

        h1 {
            font-size: 1.6rem;
            color: #1a202c;
            margin-bottom: 6px;
        }

        .subtitle {
            color: #718096;
            font-size: 0.9rem;
            margin-bottom: 32px;
        }

        label {
            display: block;
            font-weight: bold;
            color: #2d3748;
            margin-bottom: 8px;
        }

        input[type="text"] {
            width: 100%;
            padding: 14px 16px;
            font-size: 1.1rem;
            border: 2px solid #cbd5e0;
            border-radius: 8px;
            outline: none;
            transition: border-color 0.2s;
            letter-spacing: 2px;   /* Makes UIDs easier to read */
        }

        input[type="text"]:focus {
            border-color: #4299e1;
        }

        button {
            margin-top: 16px;
            width: 100%;
            padding: 14px;
            background: #4299e1;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            transition: background 0.2s;
        }

        button:hover { background: #3182ce; }

        /* ── Result boxes ── */
        .result {
            margin-top: 28px;
            padding: 20px;
            border-radius: 8px;
        }

        .result.found {
            background: #f0fff4;
            border: 2px solid #68d391;
        }

        .result.not-found {
            background: #fff5f5;
            border: 2px solid #fc8181;
        }

        .result h2 {
            margin-bottom: 12px;
            font-size: 1.1rem;
        }

        .result.found h2 { color: #276749; }
        .result.not-found h2 { color: #c53030; }

        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 6px 0;
            border-bottom: 1px solid #e2e8f0;
            font-size: 0.95rem;
        }

        .info-row:last-child { border-bottom: none; }
        .info-label { color: #718096; }
        .info-value { font-weight: bold; color: #2d3748; }

        .timestamp {
            margin-top: 10px;
            font-size: 0.8rem;
            color: #a0aec0;
            text-align: right;
        }

        .hint {
            margin-top: 24px;
            font-size: 0.82rem;
            color: #a0aec0;
            text-align: center;
        }
    </style>

    <script>
        // Auto-focus the UID input when the page loads.
        // This is important — the RFID reader types into whichever field is focused.
        window.onload = function() {
            document.getElementById("uid_input").focus();
        };

        // After a successful scan, re-focus the input automatically
        // so the next bracelet can be scanned immediately.
        window.onload = function() {
            var input = document.getElementById("uid_input");
            input.focus();
            input.select();  // Select all text so a new scan replaces the old UID.
        };
    </script>
</head>
<body>
    <div class="container">
        <h1>📡 RFID Attendance</h1>
        <p class="subtitle">Scan a bracelet or type a UID below and press Enter.</p>

        <!-- ── Scan form ── -->
        <form method="POST" action="/">
            <label for="uid_input">Tag UID</label>
            <input
                type="text"
                id="uid_input"
                name="uid"
                placeholder="Waiting for scan..."
                autocomplete="off"
                value="{{ uid or '' }}"
            >
            <button type="submit">Look Up</button>
        </form>

        <!-- ── Result area (shown only after a form submission) ── -->
        {% if result %}
            {% if result.found %}
                <div class="result found">
                    <h2>✔ Student Found</h2>
                    <div class="info-row">
                        <span class="info-label">Student ID</span>
                        <span class="info-value">{{ result.student_id }}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Full Name</span>
                        <span class="info-value">{{ result.full_name }}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Department</span>
                        <span class="info-value">{{ result.department }}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Section</span>
                        <span class="info-value">{{ result.section }}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Bracelet</span>
                        <span class="info-value">{{ result.label or '—' }}</span>
                    </div>
                    <p class="timestamp">Logged at {{ result.timestamp }}</p>
                </div>
            {% else %}
                <div class="result not-found">
                    <h2>✘ Unknown Tag</h2>
                    <p>UID <strong>{{ uid }}</strong> is not registered.</p>
                    <p style="margin-top:8px; font-size:0.9rem; color:#718096;">
                        Run <code>python register_tag.py</code> to register this bracelet.
                    </p>
                </div>
            {% endif %}
        {% endif %}

        <p class="hint">The input field stays focused so the next scan is captured automatically.</p>
    </div>
</body>
</html>
"""


# ─────────────────────────────────────────────────────────────────────────────
# DATABASE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def get_db_connection():
    """Opens and returns a database connection."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row   # Lets us access columns by name (row["name"])
    return conn


def lookup_student(uid):
    """
    Finds the student linked to this UID.
    Returns a dict with student info, or None if not found.
    """
    conn = get_db_connection()
    row = conn.execute("""
        SELECT
            s.student_id,
            s.full_name,
            s.department,
            s.section,
            t.tag_id,
            t.label
        FROM rfid_tags AS t
        JOIN students AS s ON t.student_id = s.student_id
        WHERE t.uid = ?
    """, (uid,)).fetchone()
    conn.close()
    return row


def log_scan(tag_id):
    """Inserts a scan event row."""
    conn = get_db_connection()
    conn.execute("INSERT INTO scan_events (tag_id) VALUES (?)", (tag_id,))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET", "POST"])
def index():
    """
    GET  → Show the empty scan page.
    POST → Process the submitted UID, look up student, log scan.
    """
    result = None
    uid = None

    if request.method == "POST":
        # Get the UID that was typed/scanned into the form field.
        uid = request.form.get("uid", "").strip()

        if uid:
            row = lookup_student(uid)

            if row:
                # ── Known tag ──────────────────────────
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
                # ── Unknown tag ────────────────────────
                result = {"found": False}

    return render_template_string(HTML_TEMPLATE, result=result, uid=uid)


# ─────────────────────────────────────────────────────────────────────────────
# START THE SERVER
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("  RFID ATTENDANCE — FLASK WEB APP")
    print("=" * 50)
    print("Open your browser and go to:")
    print("  http://127.0.0.1:5000")
    print("\nPress Ctrl+C to stop the server.")
    print("=" * 50)

    # debug=True reloads the server automatically when you edit this file.
    # Set debug=False for production use.
    app.run(debug=True)
