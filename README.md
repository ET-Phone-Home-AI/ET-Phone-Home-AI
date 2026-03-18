# RFID Student Attendance System

A complete, beginner-friendly RFID attendance system built with Python, SQLite, and Flask.
The USB RFID reader acts as a keyboard (HID device) — it automatically types the tag UID
into whatever input field is focused.

---

## Project Structure

```
attendance.db        ← SQLite database (created by setup_database.py)
setup_database.py    ← Creates the database and tables
seed_data.py         ← Inserts 5 sample students and tags for testing
scan_lookup.py       ← Terminal scanner: scan → look up → log
register_tag.py      ← Links a physical bracelet UID to a student
app.py               ← Flask web interface for scanning
```

---

## PART 1 — Database Design

### Entities and Relationships

```
students ──< rfid_tags ──< scan_events
  (1)          (1..*)          (*)
```

| Table        | Purpose                                      | Primary Key             |
|--------------|----------------------------------------------|-------------------------|
| students     | One row per student (name, dept, section)    | student_id (TEXT)       |
| rfid_tags    | One row per physical bracelet                | tag_id (INTEGER AUTO)   |
| scan_events  | One row per scan event (timestamp + tag)     | scan_id (INTEGER AUTO)  |

### Foreign Keys

| Table       | Column     | References              |
|-------------|------------|-------------------------|
| rfid_tags   | student_id | students(student_id)    |
| scan_events | tag_id     | rfid_tags(tag_id)       |

### Why Separate Tables? (Normalization)

- **No repeated data**: The student's name is stored once in `students`. All scans
  reference the tag_id — they do not repeat the name or department in every row.
- **Easy updates**: Changing a student's section means updating ONE row in `students`,
  not touching hundreds of scan records.
- **Clean queries**: Use SQL JOIN to combine tables when needed.

---

## PART 2 — SQL Statements

### CREATE TABLE

```sql
CREATE TABLE IF NOT EXISTS students (
    student_id  TEXT PRIMARY KEY,
    full_name   TEXT NOT NULL,
    department  TEXT NOT NULL,
    section     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS rfid_tags (
    tag_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id  TEXT NOT NULL UNIQUE,
    uid         TEXT NOT NULL UNIQUE,
    label       TEXT,
    created_at  TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

CREATE TABLE IF NOT EXISTS scan_events (
    scan_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_id      INTEGER NOT NULL,
    scanned_at  TEXT DEFAULT (datetime('now')),
    notes       TEXT,
    FOREIGN KEY (tag_id) REFERENCES rfid_tags(tag_id)
);
```

### Sample INSERT

```sql
-- Students
INSERT INTO students VALUES ('STU001', 'Alice Reyes',   'Computer Science',       '3A');
INSERT INTO students VALUES ('STU002', 'Ben Santos',    'Information Technology', '3B');
INSERT INTO students VALUES ('STU003', 'Clara Mendoza', 'Computer Science',       '3A');
INSERT INTO students VALUES ('STU004', 'David Cruz',    'Electronics',            '2C');
INSERT INTO students VALUES ('STU005', 'Eva Lim',       'Information Technology', '2A');

-- RFID Tags
INSERT INTO rfid_tags (student_id, uid, label) VALUES ('STU001', 'A1B2C3D4', 'B001');
INSERT INTO rfid_tags (student_id, uid, label) VALUES ('STU002', 'E5F6A7B8', 'B002');
INSERT INTO rfid_tags (student_id, uid, label) VALUES ('STU003', 'C9D0E1F2', 'B003');
INSERT INTO rfid_tags (student_id, uid, label) VALUES ('STU004', 'G3H4I5J6', 'B004');
INSERT INTO rfid_tags (student_id, uid, label) VALUES ('STU005', 'K7L8M9N0', 'B005');
```

---

## PART 7 — Step-by-Step Usage Guide

### Prerequisites

```bash
# Python 3 is required (check your version)
python --version

# Install Flask (only needed for the web app)
pip install flask
```

### Step 1 — Create the Database

```bash
python setup_database.py
```

This creates `attendance.db` with three empty tables.

### Step 2 — Insert Sample Data

```bash
python seed_data.py
```

Inserts 5 students and 5 RFID tags so you can test immediately.

### Step 3a — Terminal Scanner

```bash
python scan_lookup.py
```

- Type a UID (or scan a bracelet near the reader) and press Enter.
- The script prints the student's info and logs the scan.
- Test UIDs: `A1B2C3D4`, `E5F6A7B8`, `C9D0E1F2`, `G3H4I5J6`, `K7L8M9N0`
- Type `exit` to quit.

### Step 3b — Register a New Bracelet

```bash
python register_tag.py
```

1. Enter the student's ID (e.g. `STU001`).
2. Scan the physical bracelet near the reader (it types the UID).
3. Enter a label (e.g. `B006`) or press Enter to skip.
4. The bracelet is now linked to the student.

### Step 3c — Flask Web App

```bash
python app.py
```

1. Open your browser at **http://127.0.0.1:5000**
2. Click the UID input field (it auto-focuses on load).
3. Hold a bracelet near the reader — it types the UID and submits the form.
4. The page shows student info and logs the scan.
5. Press Ctrl+C in the terminal to stop the server.

---

## Script Explanations

### setup_database.py
Uses Python's built-in `sqlite3` module to connect to (or create) `attendance.db`
and runs `CREATE TABLE IF NOT EXISTS` statements. Safe to run multiple times — it
won't overwrite existing data.

### seed_data.py
Inserts sample rows using parameterized queries (`?` placeholders).
`IntegrityError` is caught so duplicate inserts are skipped gracefully.

### scan_lookup.py
Runs an infinite `while True` loop. Each iteration calls `input()` which blocks
until the RFID reader types a UID and presses Enter. A SQL JOIN across `rfid_tags`
and `students` retrieves the student. The scan is immediately committed to
`scan_events`.

### register_tag.py
Guides the operator through linking a bracelet to a student in four steps.
Duplicate detection uses `UNIQUE` constraints in the database — the script
checks before inserting to give a friendly error message.

### app.py
A Flask app with a single route (`/`) that handles both `GET` (show form) and
`POST` (process UID). `render_template_string` is used so no external HTML files
are needed. The JavaScript `window.onload` auto-focuses the input field so the
RFID reader can type directly into it.

---

## Debugging Tips

### RFID Reader Not Typing

| Symptom | Fix |
|---------|-----|
| Nothing appears when scanning | Make sure the input field or terminal is focused (click on it) |
| Reader types strange characters | Check if the reader is set to the correct keyboard layout |
| Reader shows as unknown device | Try a different USB port; check Device Manager (Windows) or `lsusb` (Linux) |
| Extra characters at the end | Some readers append `\r\n` — `input()` handles this automatically |

### Unknown Tags

| Symptom | Fix |
|---------|-----|
| "Unknown tag" for a bracelet you registered | Check if `seed_data.py` was run; verify the UID matches exactly |
| UID looks different each time | The reader may be sending inconsistent output — test with a fixed string first |
| Can't find the UID in the database | Open `attendance.db` with DB Browser for SQLite and inspect `rfid_tags` |

### Database Issues

| Symptom | Fix |
|---------|-----|
| `no such table` error | Run `python setup_database.py` first |
| `database is locked` | Another script is still connected — close it first |
| Data not saving | Check that `connection.commit()` is called after every INSERT |
| Want to reset everything | Delete `attendance.db` and run `setup_database.py` + `seed_data.py` again |

---

## Useful Tools

- **DB Browser for SQLite** — free GUI to view/edit your `.db` file visually.
  Download at https://sqlitebrowser.org/
- **Flask documentation** — https://flask.palletsprojects.com/

---

## Quick Reference — Test UIDs

| UID        | Student         | Section |
|------------|-----------------|---------|
| A1B2C3D4   | Alice Reyes     | 3A      |
| E5F6A7B8   | Ben Santos      | 3B      |
| C9D0E1F2   | Clara Mendoza   | 3A      |
| G3H4I5J6   | David Cruz      | 2C      |
| K7L8M9N0   | Eva Lim         | 2A      |
