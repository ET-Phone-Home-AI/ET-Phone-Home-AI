# 📡 RFID Student Attendance System
### Complete Beginner's Guide — Read This First!

---

## 🙋 Never coded before? That's okay. Read this whole page first.

This guide will tell you **exactly** what to click, what to type, and what to expect.
No guessing. No skipping steps. Just follow along.

---

## What Does This System Do?

Imagine this:
1. A student walks up and holds their RFID wristband near a USB reader.
2. The reader beeps. It automatically types a code into your computer.
3. The screen instantly shows: **"Alice Reyes — Computer Science — Section 3A — LOGGED"**
4. That scan is saved forever in a database file on your computer.

That's it. That's the whole system.

---

## What Is Each File? (The Big Picture)

> **You only ever need to run ONE file: `START_HERE.py`**
> It calls all the others for you automatically.

```
Your folder looks like this:
─────────────────────────────────────────────────────
 START_HERE.py        ← 🟢 YOU RUN THIS. Only this.
 ─────────────────────────────────────────────────────
 setup_database.py    ← Creates the database file
 seed_data.py         ← Fills in sample student data
 scan_lookup.py       ← Runs the terminal scanner
 register_tag.py      ← Links a bracelet to a student
 app.py               ← Runs the website in a browser
 ─────────────────────────────────────────────────────
 attendance.db        ← 🗄️ Created automatically. Your data lives here.
 requirements.txt     ← List of libraries to install
─────────────────────────────────────────────────────
```

### How the files talk to each other:

```
START_HERE.py
    │
    ├── auto-runs → setup_database.py  (creates attendance.db)
    ├── auto-runs → seed_data.py       (fills sample data)
    │
    ├── Menu Option 1 → scan_lookup.py   (scans bracelets in terminal)
    ├── Menu Option 2 → register_tag.py  (links bracelet to student)
    ├── Menu Option 3 → shows attendance log from attendance.db
    ├── Menu Option 4 → app.py           (opens the website)
    └── Menu Option 5 → shows student list from attendance.db
```

**All of them read/write to the same `attendance.db` file.**
Think of `attendance.db` as the shared notebook everyone writes in.

---

## What Is Flask?

Flask is a Python library that makes it possible for Python to run a website.

Normally a website needs:
- A server (a powerful computer)
- HTML files
- A complicated setup

Flask does all of that for you in your own computer. When you run `app.py`:
- Flask starts a tiny server **on your laptop**
- You open your browser and go to `http://127.0.0.1:5000`
- `127.0.0.1` means **"this computer"** (not the internet — just yours)
- `5000` is the "door number" (called a port)
- The RFID reader types into the webpage just like it types in the terminal

---

## What Is a Database?

A database is a file that stores data in organized tables.
Ours is called `attendance.db`. Think of it like an Excel file with 3 sheets:

| Sheet name    | What it stores                            |
|---------------|-------------------------------------------|
| `students`    | Student ID, Name, Department, Section     |
| `rfid_tags`   | Which bracelet belongs to which student   |
| `scan_events` | Every scan ever — date, time, who it was  |

Why not just one big table? Because:
- Alice's name is written **once** in `students`
- Every scan just saves a number (her tag ID)
- If her section changes, you fix **1 row**, not thousands

This is called **normalization** — keeping data clean and efficient.

---

## ⚡ QUICKSTART — Do Exactly This

### Step 1 — Make sure Python is installed

Open a terminal (Command Prompt on Windows, Terminal on Mac/Linux).

Type this and press Enter:
```
python --version
```

You should see something like `Python 3.10.0`.
If you see an error, download Python from https://python.org → Downloads.

---

### Step 2 — Download or copy this project folder

Make sure all these files are in the **same folder** on your computer:
- `START_HERE.py`
- `setup_database.py`
- `seed_data.py`
- `scan_lookup.py`
- `register_tag.py`
- `app.py`
- `requirements.txt`

---

### Step 3 — Open a terminal IN that folder

**Windows:**
1. Open File Explorer
2. Go to the project folder
3. Click the address bar at the top
4. Type `cmd` and press Enter
5. A black Command Prompt window opens **already inside your folder** ✔

**Mac:**
1. Open Finder
2. Go to the project folder
3. Right-click the folder → "New Terminal at Folder"

**VS Code (any platform):**
1. Open VS Code
2. File → Open Folder → pick your project folder
3. Terminal → New Terminal

---

### Step 4 — Run the system

In the terminal, type exactly this and press Enter:

```
python START_HERE.py
```

**First time only** — you'll see this happen automatically:
```
  Flask not found. Installing it now (one-time setup)...
  Flask installed!

  First-time setup — creating database and loading sample data...

  ✔ Table created: students
  ✔ Table created: rfid_tags
  ✔ Table created: scan_events

  ✔ Added student: Alice Reyes (STU001)
  ✔ Added student: Ben Santos (STU002)
  ✔ Added student: Clara Mendoza (STU003)
  ✔ Added student: David Cruz (STU004)
  ✔ Added student: Eva Lim (STU005)

  ✔ Database is ready!

  Press Enter to continue to the main menu...
```

Press **Enter** and you'll see the main menu:

```
╔══════════════════════════════════════════════════════════════╗
║        📡  RFID STUDENT ATTENDANCE SYSTEM  📡               ║
╚══════════════════════════════════════════════════════════════╝

  What would you like to do?

    1  →  Scan bracelets (terminal mode)
    2  →  Register a new bracelet to a student
    3  →  View attendance log
    4  →  Start the web app (browser interface)
    5  →  List all students
    0  →  Exit
```

---

## Using the Menu

### Option 1 — Scan Bracelets (Terminal)

Choose this when you want to take attendance in the terminal window.

1. Type `1` and press Enter
2. The scanner starts:
   ```
   Scan bracelet ▶
   ```
3. Hold a bracelet near the reader — it types the UID automatically
4. You'll see the student info instantly:
   ```
   ── 2026-03-18 09:00:00 ──────────────────
   ✔  ATTENDANCE LOGGED
      Student ID  :  STU001
      Name        :  Alice Reyes
      Department  :  Computer Science
      Section     :  3A
      Bracelet    :  B001
   ```
5. Type `exit` to go back to the menu

> **No reader yet?** Just type one of these test codes and press Enter:
> `A1B2C3D4` / `E5F6A7B8` / `C9D0E1F2` / `G3H4I5J6` / `K7L8M9N0`

---

### Option 2 — Register a New Bracelet

Do this **once** for each new physical bracelet before using it for attendance.

1. Type `2` and press Enter
2. Follow the 4 steps on screen:

   ```
   STEP 1 of 4 — Enter the student ID
   Student ID: STU006
   ```
   > Type the student's ID (must already exist in the database)

   ```
   ✔ Found student: Maria Santos
     Department:    Computer Science
     Section:       3A

   STEP 3 of 4 — Scan the bracelet
   Hold the bracelet near the USB reader.
   UID (scanned by reader):
   ```
   > Hold the bracelet near the reader — it types the UID

   ```
   STEP 4 of 4 — Give the bracelet a label (optional)
   Bracelet label: B006
   ```
   > Type a name for the bracelet, or just press Enter to skip

   ```
   ✔ Bracelet registered successfully!
     Student   :  Maria Santos  (STU006)
     UID       :  FF00AA11
     Label     :  B006
   ```

---

### Option 3 — View Attendance Log

Shows a table of all recent scans:

```
  ALL RECORDED SCANS

  #    Date & Time           ID       Name               Section  Bracelet
  ────────────────────────────────────────────────────────────────────────
  5    2026-03-18 09:01:00   STU001   Alice Reyes        3A       B001
  4    2026-03-18 09:00:30   STU003   Clara Mendoza      3A       B003
  3    2026-03-18 09:00:00   STU002   Ben Santos         3B       B002
```

Press Enter to go back to the menu.

---

### Option 4 — Web App (Browser Interface)

This opens the website version — great for showing on a big screen during class.

1. Type `4` and press Enter
2. Press Enter again to start
3. Wait for this message in the terminal:
   ```
   * Running on http://127.0.0.1:5000
   ```
4. Open **Chrome** or **Firefox**
5. In the address bar (where you type web addresses), type:
   ```
   http://127.0.0.1:5000
   ```
   and press Enter
6. The webpage loads with a scan box
7. **Click the scan box once** (or it auto-focuses)
8. Hold a bracelet near the reader — it types and submits automatically
9. The page shows the student's info

To stop the web app: go back to the terminal and press **Ctrl+C**

---

### Option 5 — List All Students

Shows all students and which bracelet they have:

```
  ID       Name               Department                Sec   UID          Label
  ────────────────────────────────────────────────────────────────────────────────
  STU001   Alice Reyes        Computer Science          3A    A1B2C3D4     B001
  STU002   Ben Santos         Information Technology    3B    E5F6A7B8     B002
  STU003   Clara Mendoza      Computer Science          3A    C9D0E1F2     B003
  STU004   David Cruz         Electronics               2C    G3H4I5J6     B004
  STU005   Eva Lim            Information Technology    2A    K7L8M9N0     B005
  STU006   Maria Santos       Computer Science          3A    (no bracelet)  —
```

---

## Adding Real Students

The sample data (STU001–STU005) is just for testing.
To add your real students, open `seed_data.py` and edit the `students` list:

```python
students = [
    ("STU001", "Alice Reyes",    "Computer Science",       "3A"),
    # ↑         ↑                ↑                          ↑
    # ID        Full Name        Department                 Section

    ("STU006", "Maria Santos",   "Computer Science",       "3A"),   # ← add like this
]
```

Then run:
```
python seed_data.py
```

Or add them directly in the terminal using Option 2 after registering the bracelet.

---

## Troubleshooting

### "python is not recognized" / "command not found"
Python is not installed or not in your PATH.
- Download from https://python.org/downloads
- **Windows**: during install, check the box **"Add Python to PATH"**
- Then close and reopen the terminal

### The RFID reader does nothing when I scan
The reader needs to be focused — meaning the cursor must be inside the text box.
- **Terminal mode**: the terminal window must be open and active (click on it)
- **Web app**: click the scan box on the webpage once
- Try a different USB port
- On Windows: check Device Manager → the reader should appear as a keyboard (HID)
- On Linux: try `lsusb` in the terminal to see if it's detected

### "Unknown tag" for a bracelet I just registered
The UID might have extra spaces or be in a different case.
- In the terminal scanner, type the UID manually first to confirm it works
- Check `attendance.db` using DB Browser for SQLite (free tool) to see exactly what's stored

### "no such table" error
The database hasn't been created yet.
Run: `python START_HERE.py` — it creates everything automatically on first launch.

### The web app won't open in the browser
- Make sure you see `* Running on http://127.0.0.1:5000` in the terminal first
- Type `http://127.0.0.1:5000` exactly (not google, not bing — type it yourself)
- Try a different browser

### "database is locked"
Two scripts are trying to use the database at the same time.
Close all terminals running Python scripts, then try again.

### I want to start fresh / reset everything
Delete the `attendance.db` file and run `python START_HERE.py` again.

---

## Quick Reference — Test UIDs

No reader? Use these to test right now:

| Type this UID | Gets you           |
|---------------|--------------------|
| `A1B2C3D4`    | Alice Reyes — 3A   |
| `E5F6A7B8`    | Ben Santos — 3B    |
| `C9D0E1F2`    | Clara Mendoza — 3A |
| `G3H4I5J6`    | David Cruz — 2C    |
| `K7L8M9N0`    | Eva Lim — 2A       |

---

## Free Tools to Install (Optional but Helpful)

| Tool | What it does | Download |
|------|-------------|---------|
| **DB Browser for SQLite** | Opens `attendance.db` visually like Excel | https://sqlitebrowser.org |
| **VS Code** | A friendly code editor | https://code.visualstudio.com |

---

*Built with Python 3, SQLite, and Flask. No internet connection required to run.*
