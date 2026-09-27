# save this as face_hello.py
# ENGR-126 · Project 5 — Teaching a Webcam to Greet People by Name
#
# INSTALL FIRST (in PyCharm's Terminal tab, one line):
#   pip install insightface onnxruntime opencv-python numpy piper-tts
#
# The first run downloads the "buffalo_l" face models (~280 MB) and a
# natural female voice for Piper (~60 MB) ONE time.
# After that everything runs offline. No image and no face fingerprint
# ever leaves your laptop. Photos are read, never copied or saved.

import json                                   # saves fingerprints as a readable text file
import os                                     # files and folders
import sys                                    # tells us if we are on Windows
import subprocess                             # plays sound on Mac and Linux
import tempfile                               # a scratch file for each spoken greeting
import threading                              # speaks in the background so video never freezes
import wave                                   # writes the voice into a .wav sound file
from pathlib import Path
import time                                   # countdown + frames-per-second
import cv2                                    # OpenCV: webcam, images, drawing
import numpy as np                            # math on the 512 numbers
from insightface.app import FaceAnalysis      # the face AI
from piper import PiperVoice                  # the voice AI (runs on your laptop)
import requests                               # downloads files (comes with insightface)

# ---------------- SETTINGS YOU CAN CHANGE ----------------
THRESHOLD = 0.45           # THE one number: similarity needed to say a name (0 to 1)
DATA_FILE = "face_fingerprints.json"   # every stored face lives ONLY in this file
SAMPLES_PER_PERSON = 20    # webcam frames to learn from when enrolling
PROCESS_EVERY = 3          # SPEED: run the AI on every 3rd frame, reuse boxes in between
CAMERA_SIZE = (640, 480)   # SPEED: smaller camera frames = less work per frame
GREET_AGAIN_AFTER = 3      # seconds out of view before it counts as "leaving"
VOICE_NAME = "en_GB-jenny_dioco-medium"   # female voices: en_GB-jenny_dioco-medium, en_US-lessac-medium,
                                         # en_US-amy-medium
# ----------------------------------------------------------

print("Loading face models... (a few seconds)")
# Only turn on the two parts we need: finding faces + making fingerprints
app = FaceAnalysis(name="buffalo_l",
                   providers=["CPUExecutionProvider"],
                   allowed_modules=["detection", "recognition"])
app.prepare(ctx_id=-1, det_size=(320, 320))   # ctx_id=-1 means "use the CPU"

# ---------- getting the voice files (first run only) ----------
def voice_url(file_name):
    """Build the download link from the voice name, e.g. en_GB-jenny_dioco-medium."""
    lang, who, quality = VOICE_NAME.split("-")
    return ("https://huggingface.co/rhasspy/piper-voices/resolve/main/"
            f"{lang.split('_')[0]}/{lang}/{who}/{quality}/{file_name}")


def fetch(url, dest):
    """Download one file. Try Python first; if the network blocks that, try the
    computer's own downloader (curl), which uses the same settings as your browser."""
    part = dest.with_name(dest.name + ".part")            # half-done downloads never look finished
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, stream=True, timeout=30)
        r.raise_for_status()                              # stop if the site said no
        with open(part, "wb") as f:
            for chunk in r.iter_content(1 << 20):         # 1 MB at a time
                f.write(chunk)
    except Exception as err:
        print(f"  Python download failed ({err}). Trying curl...")
        cmd = ["curl", "-L", "--fail", "-o", str(part), url]   # curl.exe is built into Windows 10/11
        if sys.platform == "win32":
            cmd.insert(1, "--ssl-revoke-best-effort")     # avoids a common campus-network error
        subprocess.run(cmd, check=True)
    part.replace(dest)                                    # finished: give it its real name


print("Loading the voice...")
voice_dir = Path("voices")
model = voice_dir / f"{VOICE_NAME}.onnx"
config = voice_dir / f"{VOICE_NAME}.onnx.json"
voice = None                                              # None = use the computer's built-in voice
try:
    voice_dir.mkdir(exist_ok=True)
    for f in (config, model):
        if not f.exists():                                # first run only
            print(f"Downloading {f.name} one time...")
            fetch(voice_url(f.name), f)
    voice = PiperVoice.load(model)
    print("Voice ready.")
except Exception as err:                                  # nothing worked: keep going anyway
    print(f"Could not get the Piper voice: {err}")
    print("Using the computer's built-in voice for now. To fix it, open these two links in")
    print(f"a browser and put both files in the '{voice_dir.resolve()}' folder:")
    print(f"  {voice_url(model.name)}\n  {voice_url(config.name)}")
speaking = threading.Lock()                               # one greeting at a time


# ---------- saving and loading fingerprints ----------
def load_people():
    """Read {name: {"vector": [512 numbers], "samples": count}} from disk."""
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE) as f:
        return json.load(f)


def save_people(people):
    with open(DATA_FILE, "w") as f:
        json.dump(people, f)


def add_samples(people, name, samples):
    """Average new fingerprints into a person (works for new AND existing people)."""
    old = people.get(name)
    total = np.sum(samples, axis=0)                  # add up the new fingerprints
    count = len(samples)
    if old:                                          # already enrolled? blend old + new
        total += np.array(old["vector"]) * old["samples"]
        count += old["samples"]
    avg = total / count
    avg = avg / np.linalg.norm(avg)                  # rescale to length 1
    people[name] = {"vector": avg.tolist(), "samples": count}
    save_people(people)
    print(f"Saved {name}: {count} total samples.")


def ask_name_and_consent():
    """Ask for a name, then require the person to type I agree. Returns name or None."""
    name = input("Person's name (Enter to cancel): ").strip()
    if not name:
        return None
    print(f"{name}'s face fingerprint will be stored ONLY on this laptop in")
    print(f"'{DATA_FILE}' and can be deleted anytime (menu 5 or 6).")
    if input(f"{name}, type  I agree  to continue: ").strip().lower() != "i agree":
        print("No consent given. Nothing was captured.")
        return None
    return name


# ---------- the voice: say a greeting out loud ----------
def builtin_voice(text):
    """Backup plan: the voice already built into the computer (robotic, but always works)."""
    if sys.platform == "win32":
        safe = text.replace("'", "''")                    # protect names like O'Brien
        cmd = ("Add-Type -AssemblyName System.Speech; $s = New-Object "
               "System.Speech.Synthesis.SpeechSynthesizer; "
               "$s.SelectVoiceByHints('Female'); $s.Speak('" + safe + "')")
        subprocess.run(["powershell", "-NoProfile", "-Command", cmd],
                       creationflags=subprocess.CREATE_NO_WINDOW)
    elif sys.platform == "darwin":
        subprocess.run(["say", "-v", "Samantha", text])
    else:
        subprocess.run(["espeak", text])


def speak_now(text):
    """Turn text into speech with Piper, play it, then delete the sound file."""
    with speaking:                                        # wait if someone is still being greeted
        if voice is None:                                 # Piper not available? use the backup
            builtin_voice(text)
            return
        path = os.path.join(tempfile.gettempdir(), "facehello_greeting.wav")
        with wave.open(path, "wb") as wav:
            voice.synthesize_wav(text, wav)               # the AI makes the voice here
        if sys.platform == "win32":
            import winsound                               # built into Windows Python
            winsound.PlaySound(path, winsound.SND_FILENAME)
        elif sys.platform == "darwin":
            subprocess.run(["afplay", path])              # built into every Mac
        else:
            subprocess.run(["aplay", "-q", path])         # Linux
        os.remove(path)                                   # nothing is kept


def say(text):
    """Speak in the background so the video keeps running."""
    print(text)                                           # also show it in the Run panel
    threading.Thread(target=speak_now, args=(text,), daemon=True).start()


# ---------- camera helper ----------
def open_camera():
    # On Windows, the DirectShow backend opens the webcam much faster
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW) if sys.platform == "win32" else cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_SIZE[0])
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_SIZE[1])
    return cam


# ---------- menu option 1: enroll with the webcam ----------
def enroll_webcam(people):
    name = ask_name_and_consent()
    if not name:
        return
    cam = open_camera()
    samples, start = [], time.time()
    while len(samples) < SAMPLES_PER_PERSON:
        ok, frame = cam.read()
        if not ok:
            print("Could not read the webcam.")
            break
        faces = app.get(frame)
        ready = time.time() - start > 2                    # 2-second "get ready"
        if len(faces) == 1 and ready:
            samples.append(faces[0].normed_embedding)      # keep this fingerprint
        if len(faces) != 1:
            msg = "Exactly ONE face please"
        elif not ready:
            msg = "Get ready..."
        else:
            msg = f"Slowly turn your head  {len(samples)}/{SAMPLES_PER_PERSON}"
        cv2.putText(frame, msg, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
        cv2.imshow("FaceHello", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):              # Q cancels
            break
    cam.release()
    cv2.destroyAllWindows()
    if samples:
        add_samples(people, name, samples)


# ---------- menu option 2: enroll from a photo folder ----------
def read_image(path):
    # np.fromfile + imdecode also works with Turkish letters (ç, ş, ğ...) in paths
    return cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)


def enroll_folder(people):
    name = ask_name_and_consent()
    if not name:
        return
    folder = input("Folder with photos of ONLY this person: ").strip().strip('"')
    if not os.path.isdir(folder):
        print("That folder does not exist.")
        return
    samples = []
    for file in sorted(os.listdir(folder)):
        if not file.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".webp")):
            continue                                       # skip non-photos
        img = read_image(os.path.join(folder, file))
        if img is None:
            print(f"  {file}: could not open, skipped")
            continue
        faces = app.get(img)
        if len(faces) != 1:                                # 0 or 2+ faces = can't be sure who
            print(f"  {file}: {len(faces)} faces found, skipped")
            continue
        samples.append(faces[0].normed_embedding)
        print(f"  {file}: OK")
    if samples:
        add_samples(people, name, samples)
    else:
        print("No usable photos (each photo needs exactly one face).")


# ---------- menu option 3: live recognition ----------
def run_recognition(people):
    global THRESHOLD
    names = list(people)
    # One row per person. With nobody enrolled this is empty, and every face is Unknown.
    matrix = np.array([people[n]["vector"] for n in names]).reshape(len(names), 512)
    cam = open_camera()
    results, frame_no, fps, last = [], 0, 0.0, time.time()
    last_seen = {}                     # name -> the last time we saw that person
                                       # (not in here yet = never seen = first visit)
    print("Recognition running. Keys in the video window: + / - threshold, Q back to menu.")
    while True:
        ok, frame = cam.read()
        if not ok:
            print("Could not read the webcam.")
            break
        frame_no += 1
        if frame_no % PROCESS_EVERY == 1:                  # only run the AI on some frames
            results = []
            for face in app.get(frame):
                if not names:                              # nobody enrolled: everyone is Unknown
                    results.append((face.bbox.astype(int), "Unknown", 0.0))
                    continue
                scores = matrix @ face.normed_embedding    # cosine similarity to EVERYONE at once
                best = int(np.argmax(scores))
                score = float(scores[best])
                name = names[best] if score >= THRESHOLD else "Unknown"
                results.append((face.bbox.astype(int), name, score))
            # GREETING: say hello to anyone who just arrived (not seen for a while)
            now = time.time()
            greetings = []
            for _, n, _ in results:
                if n == "Unknown":
                    continue                               # we never greet strangers
                if n not in last_seen:                     # first time we see this person
                    greetings.append(f"Hi {n}, welcome!")
                elif now - last_seen[n] > GREET_AGAIN_AFTER:   # they left and came back
                    greetings.append(f"Hi {n}, welcome back!")
                last_seen[n] = now                         # remember we just saw them
            if greetings:
                say(" ".join(greetings))                   # one sentence per person
        for (x1, y1, x2, y2), name, score in results:      # draw the latest results
            color = (0, 200, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{name}  {score:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        now = time.time()
        fps = 0.9 * fps + 0.1 * (1 / max(now - last, 1e-6))   # smoothed frames per second
        last = now
        cv2.putText(frame, f"Threshold {THRESHOLD:.2f} | {len(names)} enrolled | {fps:.0f} fps | + - Q",
                    (10, frame.shape[0] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        cv2.imshow("FaceHello", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key in (ord("+"), ord("=")):
            THRESHOLD = min(0.95, THRESHOLD + 0.01)
        elif key in (ord("-"), ord("_")):
            THRESHOLD = max(0.05, THRESHOLD - 0.01)
    cam.release()
    cv2.destroyAllWindows()


# ---------- menu options 4, 5, 6 ----------
def list_people(people):
    if not people:
        print("Nobody is enrolled.")
    for name, info in people.items():
        print(f"  {name}  ({info['samples']} samples)")


def delete_person(people):
    list_people(people)
    name = input("Name to delete (Enter to cancel): ").strip()
    if name in people:
        del people[name]
        save_people(people)
        print(f"Deleted {name}.")
    elif name:
        print("No one by that name.")


def delete_all(people):
    # .lower() means "delete", "DELETE" and "Delete" all work
    if input("Type DELETE to erase ALL face data: ").strip().lower() == "delete":
        people.clear()
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)                           # the whole face database is gone
        print("All face data deleted.")
    else:
        print("Cancelled. Nothing was deleted.")           # always say what happened


# ---------------- MAIN MENU ----------------
people = load_people()
actions = {"1": enroll_webcam, "2": enroll_folder, "3": run_recognition,
           "4": list_people, "5": delete_person, "6": delete_all}
while True:
    print("\n1) Enroll a person with the webcam\n2) Enroll from a photo folder\n3) Run recognition"
          "\n4) List people\n5) Delete a person\n6) Delete ALL face data")
    choice = input("Choose 1-6: ").strip().lower()
    if choice == "q":                                      # type q to quit the program
        break
    if choice in actions:
        actions[choice](people)
