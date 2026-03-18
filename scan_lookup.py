"""
╔══════════════════════════════════════════════════════════════╗
║  scan_lookup.py                                              ║
║  What this file does:                                        ║
║    Runs a loop waiting for RFID scans in the terminal.       ║
║    When a bracelet is scanned, it:                           ║
║      1. Finds the matching student in the database           ║
║      2. Prints the student's info on screen                  ║
║      3. Saves the scan to the attendance log                 ║
║                                                              ║
║  NOTE: START_HERE.py → Option 1 runs this for you.          ║
║  Manual run:  python scan_lookup.py                          ║
╚══════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HOW THE RFID USB READER WORKS:
  It looks like a USB stick.
  When you plug it in, your computer thinks it's a keyboard.
  When a student holds their bracelet near the reader,
  it automatically TYPES the bracelet's UID (like "A1B2C3D4")
  and presses ENTER — just like someone typing on a keyboard.
  Python's  input()  function waits for that typed text.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sqlite3              # talks to the database
from datetime import datetime   # gets the current date and time

DB_NAME = "attendance.db"


def find_student_by_uid(cursor, uid):
    """
    Searches the database for a student linked to this UID.

    HOW:
      We use a SQL JOIN — this means we connect two tables together.
      rfid_tags has the uid.
      students has the name and department.
      JOIN links them where student_id matches in both tables.

    RETURNS:
      A dictionary with student info, or None if not found.
    """

    # This is a SQL query — a question we ask the database.
    # SELECT means "give me these columns"
    # FROM ... JOIN ... means "look in these two connected tables"
    # WHERE means "but only rows where this condition is true"
    cursor.execute("""
        SELECT
            s.student_id,
            s.full_name,
            s.department,
            s.section,
            t.tag_id,
            t.label
        FROM rfid_tags AS t
        JOIN students  AS s ON t.student_id = s.student_id
        WHERE t.uid = ?
    """, (uid,))
    # The (uid,) at the end fills in the ? placeholder — safely, without SQL injection.

    row = cursor.fetchone()   # fetchone() gets the first (and only) result row

    if row is None:
        return None   # No match found — bracelet not registered

    # Turn the row (a list of values) into a dictionary (named values)
    # so we can access them like  student["full_name"]  instead of  row[1]
    return {
        "student_id": row[0],
        "full_name":  row[1],
        "department": row[2],
        "section":    row[3],
        "tag_id":     row[4],
        "label":      row[5],
    }


def save_scan(cursor, connection, tag_id):
    """
    Inserts one new row into scan_events to record this attendance.
    The database automatically fills in the timestamp.
    """
    cursor.execute("""
        INSERT INTO scan_events (tag_id)
        VALUES (?)
    """, (tag_id,))
    connection.commit()   # commit = "save it to the file right now"


def main():
    # Open the database (keep it open for the whole session)
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    print("=" * 52)
    print("  RFID ATTENDANCE SCANNER — TERMINAL MODE")
    print("=" * 52)
    print("  Hold a bracelet near the reader, or type a UID.")
    print('  Type  exit  to return to the menu.\n')

    # ─────────────────────────────────────────────────────────────────────────
    # THE MAIN LOOP
    # "while True" means: keep running forever until we say break or exit.
    # This is why the program keeps waiting for the next scan.
    # ─────────────────────────────────────────────────────────────────────────
    while True:

        try:
            # input() stops here and waits for the user to press Enter.
            # The RFID reader types the UID and presses Enter automatically.
            uid = input("  Scan bracelet ▶ ").strip()
            #                                .strip() removes any spaces or
            #                                newline characters from the edges

        except (EOFError, KeyboardInterrupt):
            # EOFError = input stream ended unexpectedly
            # KeyboardInterrupt = user pressed Ctrl+C
            # Both mean: stop the loop gracefully
            print("\n  Scanner stopped.")
            break

        # ── Skip empty lines ───────────────────────────────────────────────
        if not uid:
            continue   # "continue" jumps back to the top of the while loop

        # ── Handle exit command ────────────────────────────────────────────
        if uid.lower() == "exit":
            # .lower() converts to lowercase so "EXIT", "Exit", "exit" all work
            print("  Returning to menu...")
            break

        # ── Print a separator line with timestamp ──────────────────────────
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n  ── {now} ─────────────────────────")

        # ── Look up the student ────────────────────────────────────────────
        student = find_student_by_uid(cursor, uid)

        if student:
            # ── FOUND ──────────────────────────────────────────────────────
            print(f"  ✔  ATTENDANCE LOGGED")
            print(f"     Student ID  :  {student['student_id']}")
            print(f"     Name        :  {student['full_name']}")
            print(f"     Department  :  {student['department']}")
            print(f"     Section     :  {student['section']}")
            print(f"     Bracelet    :  {student['label'] or '—'}")

            save_scan(cursor, connection, student["tag_id"])

        else:
            # ── NOT FOUND ──────────────────────────────────────────────────
            print(f"  ✘  Unknown tag: {uid}")
            print("     This bracelet is not registered.")
            print("     Go to the main menu → option 2 to register it.")

        print()

    connection.close()


# Runs only when executed directly: python scan_lookup.py
# When imported by START_HERE.py, main() is called from there instead.
if __name__ == "__main__":
    main()
