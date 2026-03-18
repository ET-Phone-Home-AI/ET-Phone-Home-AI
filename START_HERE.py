"""
╔══════════════════════════════════════════════════════════════╗
║           RFID STUDENT ATTENDANCE SYSTEM                     ║
║                  START HERE  ←  Run this first!              ║
╚══════════════════════════════════════════════════════════════╝

This is the ONLY file you need to run.
It will automatically:
  ✔ Install everything the system needs
  ✔ Create the database
  ✔ Load sample student data
  ✔ Show you a menu to choose what to do next

HOW TO RUN:
    python START_HERE.py

That's it. Nothing else to do first.
"""

# ─────────────────────────────────────────────────────────────────────────────
# STEP 0: Make sure Flask is installed.
#
# Flask is a tool that lets Python run a website.
# We try to import it. If it's not installed, we install it automatically.
# The user doesn't have to do anything — this script handles it.
# ─────────────────────────────────────────────────────────────────────────────
import sys           # sys lets us talk to the operating system
import subprocess    # subprocess lets us run terminal commands from Python

def install_flask():
    """Installs Flask using pip (Python's package installer)."""
    print("  Flask not found. Installing it now (one-time setup)...")
    # This is the same as typing  pip install flask  in the terminal.
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "--quiet"])
    print("  Flask installed!")

try:
    import flask        # Try to load Flask
except ImportError:
    install_flask()     # If it fails, install it, then try again

# ─────────────────────────────────────────────────────────────────────────────
# Now import the rest of the tools we need.
# These are all built into Python — no installation needed.
# ─────────────────────────────────────────────────────────────────────────────
import os            # os lets us check if files exist
import sqlite3       # sqlite3 lets us create and use a database
import time          # time lets us pause the program


# ─────────────────────────────────────────────────────────────────────────────
# HELPER: clear the screen so the menu always looks clean
# ─────────────────────────────────────────────────────────────────────────────
def clear():
    # 'cls' clears the screen on Windows, 'clear' does it on Mac/Linux
    os.system("cls" if os.name == "nt" else "clear")


# ─────────────────────────────────────────────────────────────────────────────
# HELPER: print a fancy header banner
# ─────────────────────────────────────────────────────────────────────────────
def banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║        📡  RFID STUDENT ATTENDANCE SYSTEM  📡               ║
╚══════════════════════════════════════════════════════════════╝""")


# ─────────────────────────────────────────────────────────────────────────────
# AUTO-SETUP: Create the database and load sample data on first run.
#
# A "database" is just a file that stores information in organized tables.
# Think of it like an Excel spreadsheet saved as a file called attendance.db
# ─────────────────────────────────────────────────────────────────────────────
DB_FILE = "attendance.db"   # This is the name of our database file

def setup_is_done():
    """Returns True if the database already exists with data inside."""
    if not os.path.exists(DB_FILE):
        return False   # The file doesn't exist yet
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM students")
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0   # True if we already have students in the database
    except:
        conn.close()
        return False


def auto_setup():
    """
    Creates all three database tables and inserts sample students.
    This runs automatically the very first time START_HERE.py is launched.
    """
    print("\n  First-time setup — creating database and loading sample data...")
    print()

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # ── Create the three tables ───────────────────────────────────────────────
    #
    # TABLE 1: students
    #   Stores each student's information.
    #   student_id is the "primary key" — a unique label like STU001.
    #
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id  TEXT PRIMARY KEY,
            full_name   TEXT NOT NULL,
            department  TEXT NOT NULL,
            section     TEXT NOT NULL
        )
    """)
    print("  ✔ Table created: students")

    # TABLE 2: rfid_tags
    #   Stores each physical bracelet and links it to a student.
    #   uid is the code the USB reader types when a bracelet is scanned.
    #
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rfid_tags (
            tag_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id  TEXT NOT NULL UNIQUE,
            uid         TEXT NOT NULL UNIQUE,
            label       TEXT,
            created_at  TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    """)
    print("  ✔ Table created: rfid_tags")

    # TABLE 3: scan_events
    #   Every single time a bracelet is scanned, one row is added here.
    #   This is your attendance log.
    #
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_events (
            scan_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_id      INTEGER NOT NULL,
            scanned_at  TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (tag_id) REFERENCES rfid_tags(tag_id)
        )
    """)
    print("  ✔ Table created: scan_events")

    # ── Insert 5 sample students ──────────────────────────────────────────────
    print()
    print("  Loading sample students...")

    students = [
        ("STU001", "Alice Reyes",    "Computer Science",       "3A"),
        ("STU002", "Ben Santos",     "Information Technology", "3B"),
        ("STU003", "Clara Mendoza",  "Computer Science",       "3A"),
        ("STU004", "David Cruz",     "Electronics",            "2C"),
        ("STU005", "Eva Lim",        "Information Technology", "2A"),
    ]

    for s in students:
        try:
            cursor.execute(
                "INSERT INTO students (student_id, full_name, department, section) VALUES (?,?,?,?)",
                s
            )
            print(f"  ✔ Added student: {s[1]} ({s[0]})")
        except sqlite3.IntegrityError:
            pass   # Already exists — skip quietly

    # ── Insert 5 sample RFID tags ─────────────────────────────────────────────
    print()
    print("  Loading sample RFID tags...")

    tags = [
        ("STU001", "A1B2C3D4", "B001"),
        ("STU002", "E5F6A7B8", "B002"),
        ("STU003", "C9D0E1F2", "B003"),
        ("STU004", "G3H4I5J6", "B004"),
        ("STU005", "K7L8M9N0", "B005"),
    ]

    for t in tags:
        try:
            cursor.execute(
                "INSERT INTO rfid_tags (student_id, uid, label) VALUES (?,?,?)",
                t
            )
            print(f"  ✔ Tag {t[2]} linked to student {t[0]}  (UID: {t[1]})")
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()

    print()
    print("  ✔ Database is ready!")
    print()
    print("  TEST UIDs you can type to try the system:")
    print("    A1B2C3D4   →  Alice Reyes")
    print("    E5F6A7B8   →  Ben Santos")
    print("    C9D0E1F2   →  Clara Mendoza")
    print("    G3H4I5J6   →  David Cruz")
    print("    K7L8M9N0   →  Eva Lim")
    print()
    input("  Press Enter to continue to the main menu...")


# ─────────────────────────────────────────────────────────────────────────────
# MENU OPTION 1: Terminal Scanner
#
# Waits for the RFID reader to type a UID, looks up the student,
# prints their info, and saves the scan to the attendance log.
# ─────────────────────────────────────────────────────────────────────────────
def run_terminal_scanner():
    clear()
    banner()
    print("""
  ┌─────────────────────────────────────────────┐
  │   TERMINAL SCANNER                          │
  │   Hold a bracelet near the reader.          │
  │   It will type the UID automatically.       │
  │   Type  exit  to go back to the menu.       │
  └─────────────────────────────────────────────┘
""")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    while True:
        try:
            uid = input("  Scan bracelet (or type UID): ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if uid.lower() == "exit":
            break

        if not uid:
            continue   # ignore accidental Enter presses

        print()

        # Look up the student by joining rfid_tags and students tables
        cursor.execute("""
            SELECT s.student_id, s.full_name, s.department, s.section,
                   t.tag_id, t.label
            FROM rfid_tags AS t
            JOIN students AS s ON t.student_id = s.student_id
            WHERE t.uid = ?
        """, (uid,))

        row = cursor.fetchone()

        if row:
            # ── Found! Print student card ──────────────────────────────
            print("  ┌───────────────────────────────────────┐")
            print("  │  ✔  ATTENDANCE LOGGED                 │")
            print("  ├───────────────────────────────────────┤")
            print(f"  │  ID         {row[0]:<26}│")
            print(f"  │  Name       {row[1]:<26}│")
            print(f"  │  Department {row[2]:<26}│")
            print(f"  │  Section    {row[3]:<26}│")
            print(f"  │  Bracelet   {(row[5] or '—'):<26}│")
            print("  └───────────────────────────────────────┘")

            # Save the scan to scan_events
            cursor.execute("INSERT INTO scan_events (tag_id) VALUES (?)", (row[4],))
            conn.commit()

        else:
            # ── Not found ──────────────────────────────────────────────
            print("  ✘  Unknown tag — this bracelet is not registered.")
            print("     Go back to the menu and choose  Register New Bracelet.")

        print()

    conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# MENU OPTION 2: Register a New Bracelet
#
# Links a physical RFID bracelet to a student ID in the database.
# You do this once per bracelet before you can use it for attendance.
# ─────────────────────────────────────────────────────────────────────────────
def run_register_tag():
    clear()
    banner()
    print("""
  ┌─────────────────────────────────────────────┐
  │   REGISTER A NEW BRACELET                   │
  │   You only do this ONCE per bracelet.       │
  └─────────────────────────────────────────────┘
""")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    while True:
        # ── Step 1: student ID ──────────────────────────────────────────
        student_id = input("  Enter student ID (e.g. STU001) or 'exit': ").strip().upper()
        if student_id == "EXIT":
            break
        if not student_id:
            continue

        # ── Step 2: check student exists ───────────────────────────────
        cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
        student = cursor.fetchone()

        if not student:
            print(f"\n  ✘ No student found with ID '{student_id}'.")
            print("    Check the ID and try again.\n")
            continue

        print(f"\n  Found: {student[1]}  |  {student[2]}  |  Section {student[3]}")

        # ── Check if already has a tag ─────────────────────────────────
        cursor.execute("SELECT tag_id FROM rfid_tags WHERE student_id = ?", (student_id,))
        if cursor.fetchone():
            print("  ✘ This student already has a bracelet registered.\n")
            continue

        # ── Step 3: scan the bracelet ───────────────────────────────────
        print("\n  Now hold the bracelet near the reader.")
        print("  It will type the UID automatically and press Enter.")
        uid = input("  UID: ").strip()

        if not uid:
            print("  ✘ Nothing received. Try again.\n")
            continue

        # ── Check UID not already used ──────────────────────────────────
        cursor.execute("SELECT tag_id FROM rfid_tags WHERE uid = ?", (uid,))
        if cursor.fetchone():
            print(f"  ✘ UID '{uid}' is already assigned to someone else.\n")
            continue

        # ── Step 4: optional bracelet label ────────────────────────────
        label = input("  Bracelet label (e.g. B006) — press Enter to skip: ").strip()
        if not label:
            label = None

        # ── Save ────────────────────────────────────────────────────────
        cursor.execute(
            "INSERT INTO rfid_tags (student_id, uid, label) VALUES (?,?,?)",
            (student_id, uid, label)
        )
        conn.commit()

        print(f"\n  ✔ Done! Bracelet {label or uid} is now linked to {student[1]}.\n")

        again = input("  Register another bracelet? (y/n): ").strip().lower()
        if again != "y":
            break
        print()

    conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# MENU OPTION 3: View Attendance Log
#
# Shows all scan events in a simple table — who scanned, when.
# ─────────────────────────────────────────────────────────────────────────────
def view_attendance_log():
    clear()
    banner()
    print("\n  ATTENDANCE LOG — all recorded scans\n")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            se.scan_id,
            se.scanned_at,
            s.student_id,
            s.full_name,
            s.section,
            t.label
        FROM scan_events AS se
        JOIN rfid_tags AS t ON se.tag_id = t.tag_id
        JOIN students  AS s ON t.student_id = s.student_id
        ORDER BY se.scanned_at DESC
        LIMIT 50
    """)

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("  No scans recorded yet.")
        print("  Use the terminal scanner or web app to log attendance.")
    else:
        # Print a simple table header
        print(f"  {'#':<4} {'Date & Time':<20} {'ID':<8} {'Name':<18} {'Section':<8} {'Bracelet'}")
        print("  " + "─" * 72)
        for r in rows:
            print(f"  {r[0]:<4} {r[1]:<20} {r[2]:<8} {r[3]:<18} {r[4]:<8} {r[5] or '—'}")

    print()
    input("  Press Enter to go back to the menu...")


# ─────────────────────────────────────────────────────────────────────────────
# MENU OPTION 4: Web App (Flask)
#
# Starts a mini website on your computer at http://127.0.0.1:5000
# The RFID reader types into the webpage input field.
# ─────────────────────────────────────────────────────────────────────────────
def run_web_app():
    clear()
    banner()
    print("""
  ┌─────────────────────────────────────────────────────────┐
  │   STARTING WEB APP                                      │
  │                                                         │
  │   1. Wait for the message "Running on http://..."       │
  │   2. Open your browser                                  │
  │   3. Go to:  http://127.0.0.1:5000                      │
  │   4. Click the scan box on the webpage                  │
  │   5. Hold a bracelet near the reader                    │
  │                                                         │
  │   Press Ctrl+C  to stop the web app and return here.   │
  └─────────────────────────────────────────────────────────┘
""")
    input("  Press Enter to start the web app...")

    # Import the Flask app from app.py and run it.
    # We do this import here (not at the top) so the menu shows before Flask loads.
    try:
        import app as flask_app
        flask_app.app.run(debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n  Web app stopped. Returning to menu...")
        time.sleep(1)


# ─────────────────────────────────────────────────────────────────────────────
# MENU OPTION 5: List All Students
#
# Shows every student in the database with their linked bracelet UID.
# ─────────────────────────────────────────────────────────────────────────────
def list_students():
    clear()
    banner()
    print("\n  ALL REGISTERED STUDENTS\n")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            s.student_id,
            s.full_name,
            s.department,
            s.section,
            t.uid,
            t.label
        FROM students AS s
        LEFT JOIN rfid_tags AS t ON s.student_id = t.student_id
        ORDER BY s.student_id
    """)

    rows = cursor.fetchall()
    conn.close()

    print(f"  {'ID':<8} {'Name':<18} {'Department':<25} {'Sec':<5} {'UID':<12} {'Label'}")
    print("  " + "─" * 78)

    for r in rows:
        uid   = r[4] if r[4] else "(no bracelet)"
        label = r[5] if r[5] else "—"
        print(f"  {r[0]:<8} {r[1]:<18} {r[2]:<25} {r[3]:<5} {uid:<12} {label}")

    print()
    input("  Press Enter to go back to the menu...")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN MENU
#
# This is the control center. The user picks a number, the right function runs.
# ─────────────────────────────────────────────────────────────────────────────
def main_menu():
    while True:
        clear()
        banner()
        print("""
  What would you like to do?

    1  →  Scan bracelets (terminal mode)
    2  →  Register a new bracelet to a student
    3  →  View attendance log
    4  →  Start the web app (browser interface)
    5  →  List all students
    0  →  Exit
""")
        choice = input("  Type a number and press Enter: ").strip()

        if   choice == "1": run_terminal_scanner()
        elif choice == "2": run_register_tag()
        elif choice == "3": view_attendance_log()
        elif choice == "4": run_web_app()
        elif choice == "5": list_students()
        elif choice == "0":
            clear()
            print("\n  Goodbye! 👋\n")
            break
        else:
            print("  Please type a number from the list above.")
            time.sleep(1)


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
#
# When Python runs this file, it starts here.
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    clear()
    banner()

    # Run first-time setup if the database doesn't exist yet
    if not setup_is_done():
        print("\n  Welcome! Setting up your system for the first time...\n")
        auto_setup()

    # Show the main menu
    main_menu()
