# 📡 RFID Student Attendance System

---

## The Only Command You Need

Open a terminal in this folder and run:

```
python START_HERE.py
```

That's it. Everything else happens from the menu.

---

## What You'll See

```
╔══════════════════════════════════════════════╗
║       📡  RFID STUDENT ATTENDANCE SYSTEM    ║
╚══════════════════════════════════════════════╝
  Database is empty — no students added yet.

  ┌──────────────────────────────────────────┐
  │  1  →  Add New Entry to Database         │
  │  2  →  Scan a Tag                        │
  │  0  →  Exit                              │
  └──────────────────────────────────────────┘

  Choose 1, 2, or 0:
```

---

## Option 1 — Add New Entry to Database

Use this to register a new student and link their bracelet.

**The program will ask you 4 things:**

```
  Student name:   ← type the student's full name, press Enter
  Department  :   ← type their department, press Enter
  Fun fact    :   ← type a fun fact, press Enter

  Now scan the bracelet near the USB reader...
  Scan bracelet ▶ ← hold the bracelet near the reader, it types automatically
```

**What happens next:**
```
  ✔ Entry saved successfully!
  ✔ Name       : Alice Reyes
  ✔ Department : Computer Science
  ✔ Fun Fact   : Loves robotics
  ✔ Bracelet   : A1B2C3D4
```

The program goes back to the main menu. Add as many students as you want.

---

## Option 2 — Scan a Tag

Use this to look up who owns a bracelet.

```
  Scan bracelet ▶ ← hold the bracelet near the reader
```

**If the bracelet is registered:**
```
  ╔═════════════════════════════════════════════╗
  ║  ✔  TAG RECOGNIZED                         ║
  ╠═════════════════════════════════════════════╣
  ║  Name       :  Alice Reyes                 ║
  ║  Department :  Computer Science            ║
  ║  Fun Fact   :  Loves robotics              ║
  ║  Added on   :  2026-03-28 09:00:00         ║
  ╚═════════════════════════════════════════════╝
```

**If the bracelet is NOT registered:**
```
  ✘ Tag not found in database.
  ✘ UID scanned: FF00AA11

     This bracelet has not been registered yet.
     Go back to the menu and choose:
     Option 1 → Add New Entry to Database
```

---

## Your Data Is Saved Permanently

Your student data is stored in a file called `attendance.db` in this folder.

- Every time you run the program, it reads that file.
- Every time you add a student, it writes to that file.
- **Closing the program does NOT delete your data.**
- If you want a fresh start, delete `attendance.db` and run again.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `python is not recognized` | Install Python from https://python.org — on Windows, check "Add Python to PATH" |
| Reader types nothing | Click the terminal window first so it's focused, then scan |
| "Tag not found" for a bracelet you added | Make sure you're scanning the same bracelet — each one has a unique code |
| "That bracelet is already assigned" | That bracelet was registered before — scan a different one |
| Want to see all saved students | Open `attendance.db` with DB Browser for SQLite (free): https://sqlitebrowser.org |
| Want to start over | Delete the file `attendance.db` and run the program again |

---

## File Overview

```
START_HERE.py    ← run this. only this.
attendance.db    ← your data (created automatically on first run)
```

The other files (`app.py`, `scan_lookup.py`, etc.) are extra tools for
advanced use — you don't need them to get started.
