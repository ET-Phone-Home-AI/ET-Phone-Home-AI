# save this as face_hello.py
# ENGR-126 · Project 5 — Teaching a Webcam to Greet People by Name
#
# INSTALL FIRST (in PyCharm's Terminal tab, one line):
#   pip install insightface onnxruntime opencv-python numpy piper-tts ffpyplayer
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
import shutil                                 # deletes the pictures folder
from pathlib import Path
import time                                   # countdown + frames-per-second
import cv2                                    # OpenCV: webcam, images, drawing
import numpy as np                            # math on the 512 numbers
from insightface.app import FaceAnalysis      # the face AI
from insightface.utils import face_align      # makes the 112x112 crop the model reads
from insightface.app.common import Face       # one found face (box, dots, 512 numbers)
from PIL import Image, ImageDraw, ImageFont   # draws the "how the AI saw it" pictures
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
SAVE_PIPELINE_VIEWS = True # save pictures showing each step the AI took (False = off)
VIEWS_DIR = Path("pipeline_views")     # those pictures (they show faces!) go ONLY here
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


# ---------- "how the AI saw it" pictures (pipeline views) ----------
# These pictures DO contain faces, so they live in their own folder,
# menu option 5 deletes a person's pictures, and option 6 deletes the whole folder.
BG, CARD, TEAL, GOLD = (13, 27, 52), (24, 42, 74), (38, 166, 176), (248, 184, 0)
WHITE, GREY, GREEN, RED = (240, 240, 240), (160, 175, 200), (60, 200, 110), (235, 80, 80)


def font(size, bold=False):
    """Find a font that exists on this computer (Windows, Mac or Linux)."""
    names = (["arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf"] if bold
             else ["arial.ttf", "Arial.ttf", "DejaVuSans.ttf"])
    for name in names + ["/System/Library/Fonts/Supplemental/" + n for n in names]:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default(size)


def safe(text):
    """Remove characters that Windows does not allow in file names."""
    return "".join("_" if c in '<>:"/\\|?*' else c for c in text)


def to_pil(bgr):
    return Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))   # OpenCV is BGR, PIL is RGB


def save_pipeline_view(img, face, title, file_name, scores=None, enrolled_as=None):
    """Draw one picture showing every step: frame -> crop -> pixels -> 512 numbers -> result."""
    S, GAP, TOP = 330, 46, 95                     # panel size, space for arrows, top margin
    canvas = Image.new("RGB", (30 * 2 + 5 * S + 4 * GAP, TOP + S + 105), BG)
    d = ImageDraw.Draw(canvas)
    d.text((30, 25), title, font=font(30, True), fill=WHITE)
    xs = [30 + i * (S + GAP) for i in range(5)]   # left edge of each panel

    def caption(i, big, small):
        d.text((xs[i], TOP + S + 16), big, font=font(20, True), fill=WHITE)
        d.text((xs[i], TOP + S + 46), small, font=font(15), fill=GREY)

    # PANEL 1: the full picture, with the face box and the 5 landmark dots
    h, w = img.shape[:2]
    k = S / max(w, h)                             # shrink to fit the panel
    small = to_pil(cv2.resize(img, (int(w * k), int(h * k))))
    ox, oy = xs[0] + (S - small.width) // 2, TOP + (S - small.height) // 2
    canvas.paste(small, (ox, oy))
    x1, y1, x2, y2 = face.bbox * k
    x1, x2 = max(x1, 0), min(x2, small.width - 1)     # keep the box inside the picture
    y1, y2 = max(y1, 0), min(y2, small.height - 1)
    d.rectangle([ox + x1, oy + y1, ox + x2, oy + y2], outline=GREEN, width=3)
    for px, py in face.kps * k:
        d.ellipse([ox + px - 4, oy + py - 4, ox + px + 4, oy + py + 4], fill=GOLD)
    caption(0, f"1. Full frame {w}×{h}", f"face found (confidence {face.det_score:.2f})\n"
                                         "gold dots: eyes, nose, mouth corners")

    # PANEL 2: the 112x112 crop the model actually reads
    crop = face_align.norm_crop(img, landmark=face.kps, image_size=112)   # rotate + scale + cut
    canvas.paste(to_pil(crop).resize((S, S), Image.NEAREST), (xs[1], TOP))
    z = S / 112
    for px, py in face_align.arcface_dst:          # the 5 fixed spots every face is moved to
        d.ellipse([xs[1] + px * z - 4, TOP + py * z - 4, xs[1] + px * z + 4, TOP + py * z + 4], fill=GOLD)
    ZX, ZY, ZN = 31, 45, 14                        # a 14x14 patch around the left eye
    d.rectangle([xs[1] + ZX * z, TOP + ZY * z, xs[1] + (ZX + ZN) * z, TOP + (ZY + ZN) * z],
                outline=TEAL, width=3)
    caption(1, "2. 112×112×3 crop", "turned and scaled so the 5 dots always\n"
                                    "land in the same spots. Room is gone.")

    # PANEL 3: zoom into the teal square: every cell is ONE pixel
    patch = crop[ZY:ZY + ZN, ZX:ZX + ZN]
    canvas.paste(to_pil(patch).resize((S, S), Image.NEAREST), (xs[2], TOP))
    cell = S / ZN
    for i in range(ZN + 1):                         # grid lines
        d.line([xs[2] + i * cell, TOP, xs[2] + i * cell, TOP + S], fill=BG, width=1)
        d.line([xs[2], TOP + i * cell, xs[2] + S, TOP + i * cell], fill=BG, width=1)
    c = ZN // 2
    d.rectangle([xs[2] + c * cell, TOP + c * cell, xs[2] + (c + 1) * cell, TOP + (c + 1) * cell],
                outline=GOLD, width=3)
    b, g, r = [int(v) for v in patch[c, c]]
    caption(2, "3. One cell = one RGB pixel", f"gold pixel: R {r}  G {g}  B {b}\n"
                                               f"whole crop = 37,632 numbers")

    # PANEL 4: the fingerprint, 512 numbers drawn as colors (blue = negative, red = positive)
    emb = face.normed_embedding
    top = np.abs(emb).max()
    cw, ch = S / 32, 150 / 16                      # 32 columns x 16 rows = 512 cells
    d.rectangle([xs[3], TOP, xs[3] + S, TOP + S], fill=CARD)
    for i, v in enumerate(emb):
        t = v / top                                # -1 .. +1
        col = (255, int(255 * (1 - t)), int(255 * (1 - t))) if t > 0 else \
              (int(255 * (1 + t)), int(255 * (1 + t)), 255)
        x, y = xs[3] + (i % 32) * cw, TOP + 20 + (i // 32) * ch
        d.rectangle([x, y, x + cw, y + ch], fill=col)
    first = ", ".join(f"{v:+.3f}" for v in emb[:4])
    d.text((xs[3] + 10, TOP + 190), f"[{first},\n  ... 508 more ]", font=font(16), fill=WHITE)
    caption(3, "4. Fingerprint: 512 numbers", "all those pixels squeezed into 512.\n"
                                              "Similar faces give similar numbers.")

    # PANEL 5: the result
    d.rectangle([xs[4], TOP, xs[4] + S, TOP + S], fill=CARD)
    if enrolled_as is not None:                    # enrollment picture
        d.text((xs[4] + 20, TOP + 40), "Added to:", font=font(20), fill=GREY)
        d.text((xs[4] + 20, TOP + 70), enrolled_as, font=font(34, True), fill=GREEN)
        d.text((xs[4] + 20, TOP + 140), "Only the 512 numbers are\naveraged into\n"
               f"{DATA_FILE}.\nThe photo is not stored there.", font=font(16), fill=WHITE)
        caption(4, "5. Saved", "enrolling = averaging the fingerprints\nof every good photo")
    else:                                          # recognition picture
        ranked = sorted(scores.items(), key=lambda kv: -kv[1])[:6]
        for i, (n, s) in enumerate(ranked):
            y = TOP + 20 + i * 38
            d.text((xs[4] + 12, y), n[:12], font=font(16), fill=WHITE)
            length = max(0.0, s) * 180
            d.rectangle([xs[4] + 115, y + 2, xs[4] + 115 + length, y + 20],
                        fill=GREEN if (i == 0 and s >= THRESHOLD) else GREY)
            d.text((xs[4] + 120 + length, y), f"{s:.2f}", font=font(14), fill=WHITE)
        tx = xs[4] + 115 + THRESHOLD * 180
        d.line([tx, TOP + 12, tx, TOP + 250], fill=GOLD, width=3)
        d.text((tx - 40, TOP + 254), f"threshold {THRESHOLD:.2f}", font=font(14), fill=GOLD)
        best = ranked[0] if ranked else ("nobody", 0.0)
        decision = best[0] if best[1] >= THRESHOLD else "Unknown"
        d.text((xs[4] + 12, TOP + S - 35), f"Decision: {decision}", font=font(20, True),
               fill=GREEN if decision != "Unknown" else RED)
        caption(4, "5. Compare to everyone", "score = how alike the 512 numbers are.\n"
                                             "Past the gold line = a name.")

    for i in range(4):                             # arrows between panels
        ax, ay = xs[i] + S + 8, TOP + S // 2
        d.polygon([(ax, ay - 14), (ax + 24, ay), (ax, ay + 14)], fill=TEAL)

    VIEWS_DIR.mkdir(exist_ok=True)
    path = VIEWS_DIR / safe(file_name)
    canvas.save(path)
    print(f"  saved picture: {path}")


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
        if SAVE_PIPELINE_VIEWS:                            # picture of every step for this photo
            save_pipeline_view(img, faces[0], f"How FaceHello learned {name} from {file}",
                               f"enroll_{name}_{Path(file).stem}.png", enrolled_as=name)
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
    last_frame, last_faces = None, []  # the last frame the AI looked at (for pictures)
                                       # (not in here yet = never seen = first visit)
    print("Recognition running. Keys in the video window: + / - threshold,")
    print("S save a picture of each step, Q back to menu (also saves a picture).")
    while True:
        ok, frame = cam.read()
        if not ok:
            print("Could not read the webcam.")
            break
        frame_no += 1
        if frame_no % PROCESS_EVERY == 1:                  # only run the AI on some frames
            results = []
            last_frame, last_faces = frame.copy(), app.get(frame)   # clean copy, before drawing
            for face in last_faces:
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
                    greetings.append(f"Hi {n}! Welcome to the best AI class in the universe!")
                elif now - last_seen[n] > GREET_AGAIN_AFTER:   # they left and came back
                    greetings.append(f"Welcome back {n}!")
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
        cv2.putText(frame, f"Threshold {THRESHOLD:.2f} | {len(names)} enrolled | {fps:.0f} fps | + - S Q",
                    (10, frame.shape[0] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        cv2.imshow("FaceHello", frame)
        key = cv2.waitKey(1) & 0xFF
        if key in (ord("s"), ord("q")) and SAVE_PIPELINE_VIEWS and last_faces:
            stamp = time.strftime("%Y%m%d-%H%M%S")
            for i, face in enumerate(last_faces, 1):       # one picture per face in the frame
                scores = {n: float(v) for n, v in zip(names, matrix @ face.normed_embedding)}
                best = max(scores, key=scores.get) if scores else "Unknown"
                who = best if scores and scores[best] >= THRESHOLD else "Unknown"
                save_pipeline_view(last_frame, face, f"How FaceHello recognized {who}",
                                   f"live_{stamp}_face{i}_{who}.png", scores=scores)
        if key == ord("q"):
            break
        elif key in (ord("+"), ord("=")):
            THRESHOLD = min(0.95, THRESHOLD + 0.01)
        elif key in (ord("-"), ord("_")):
            THRESHOLD = max(0.05, THRESHOLD - 0.01)
    cam.release()
    cv2.destroyAllWindows()


# ---------- menu option 7: recognize faces in a video clip ----------


def clock(seconds):
    """Turn 75.4 into '1:15' for the report."""
    return f"{int(seconds) // 60}:{int(seconds) % 60:02d}"


def recognize_video(people):
    global THRESHOLD
    path = input("Video file (for example clip.mp4): ").strip().strip('"')
    video = cv2.VideoCapture(path)
    if not video.isOpened():
        print("Could not open that video. Check the path (avoid special letters in folder names).")
        return
    fps = video.get(cv2.CAP_PROP_FPS) or 25               # frames per second of the clip
    total = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    names = list(people)
    matrix = np.array([people[n]["vector"] for n in names]).reshape(len(names), 512)

    # Save a copy of the clip with the boxes drawn in (it shows faces, so it goes in VIEWS_DIR)
    VIEWS_DIR.mkdir(exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_path = VIEWS_DIR / safe(f"video_{stamp}_{Path(path).stem}_boxes.mp4")
    writer = None

    seen_at = {}        # name -> list of times (seconds) they were seen
    best = {}           # name -> (score, frame, face) of their best moment

    # SMOOTH PLAYBACK: the AI works in the BACKGROUND (a "thread") on the newest
    # frame it is given, while the main loop just plays the video at normal speed
    # and draws the latest boxes the AI finished. The video never waits for the AI.
    shared = {"frame": None, "t": 0.0, "results": [], "results_t": -1.0, "last_frame": None,
              "last_faces": [], "stop": False, "cut_t": -1.0}
    lock = threading.Lock()                               # stops the two sides colliding

    RECHECK_EVERY = 2.0   # seconds: re-check WHO a tracked face is this often

    def iou(a, b):
        """How much two boxes overlap (0 = not at all, 1 = the same box)."""
        x1, y1 = max(a[0], b[0]), max(a[1], b[1])
        x2, y2 = min(a[2], b[2]), min(a[3], b[3])
        inter = max(0, x2 - x1) * max(0, y2 - y1)
        area = lambda r: (r[2] - r[0]) * (r[3] - r[1])
        return inter / (area(a) + area(b) - inter + 1e-6)

    def ai_worker():
        while not shared["stop"]:
            try:
                ai_steps()
            except Exception as err:                      # never let the AI die silently
                print(f"(AI hiccup, continuing: {err})")

    def ai_steps():
        """Two-step AI, like a detective:
        1) FIND faces in every frame it can (fast), and follow them from frame to frame.
        2) ask WHO each face is (slow) only for new faces, and re-check each face every 2 seconds."""
        tracks = []           # faces we are following: box, name, score, when last checked
        tracks_t = -1.0       # clip time of the frame the tracks came from
        while not shared["stop"]:
            with lock:
                frame, t, cut_t = shared["frame"], shared["t"], shared["cut_t"]
                shared["frame"] = None                    # take the frame waiting for us
            if frame is None:
                time.sleep(0.005)                         # nothing new yet
                continue
            if tracks_t < cut_t <= t:                     # a new shot started: forget old faces
                tracks = []
            bboxes, kpss = app.models["detection"].detect(frame, max_num=0, metric="default")
            new_tracks = []
            for i in range(bboxes.shape[0]):              # STEP 1: every face found
                face = Face(bbox=bboxes[i, :4], kps=kpss[i], det_score=bboxes[i, 4])
                old = max(tracks, key=lambda tr: iou(tr["box"], face.bbox), default=None)
                if old and iou(old["box"], face.bbox) > 0.3:   # same face as before: keep its name
                    tr = dict(old, box=face.bbox, face=old["face"])
                    tracks = [x for x in tracks if x is not old]   # each old face is used once
                else:
                    tr = {"box": face.bbox, "name": None, "score": 0.0, "checked": -99.0, "face": None}
                tr["new_face"] = face
                new_tracks.append(tr)
            # STEP 2: ask WHO for the faces that need it (new ones first, biggest first)
            todo = [tr for tr in new_tracks if t - tr["checked"] >= RECHECK_EVERY]
            todo.sort(key=lambda tr: (tr["name"] is not None, -(tr["box"][2] - tr["box"][0])))
            for tr in todo[:1]:                           # one per frame keeps the boxes moving
                face = tr["new_face"]
                app.models["recognition"].get(frame, face)   # the 512 numbers
                if not names:
                    tr.update(name="Unknown", score=0.0, checked=t, face=face)
                    continue
                scores = matrix @ face.normed_embedding
                i = int(np.argmax(scores))
                score = float(scores[i])
                tr.update(name=names[i] if score >= THRESHOLD else "Unknown", score=score,
                          checked=t, face=face)
                if tr["name"] != "Unknown" and score > best.get(tr["name"], (0,))[0]:
                    best[tr["name"]] = (score, frame, face)   # remember their best frame
            tracks, tracks_t = new_tracks, t
            for tr in tracks:                             # for the report: who is on screen now
                if tr["name"] not in (None, "Unknown"):
                    seen_at.setdefault(tr["name"], []).append(t)
            results = [(tr["box"].astype(int), tr["name"] or "Checking...", tr["score"]) for tr in tracks]
            with lock:
                shared["results"], shared["results_t"] = results, t
                shared["last_frame"] = frame
                shared["last_faces"] = [tr["face"] for tr in tracks if tr["face"] is not None]

    worker = threading.Thread(target=ai_worker, daemon=True)
    worker.start()
    print("Playing. Keys in the video window: + / - threshold, S save a picture, Q stop.")

    # SOUND: OpenCV only reads pictures, so a small player plays the clip's sound.
    try:
        from ffpyplayer.player import MediaPlayer          # pip install ffpyplayer
        sound = MediaPlayer(path, ff_opts={"vn": True, "paused": True})   # sound only, wait for us
    except Exception:
        sound = None
        print("(No sound: run  pip install ffpyplayer  to hear the clip.)")

    def clip_clock():
        """Where the SOUND is right now (seconds). The picture follows this clock.
        If the sound player can't tell us, use the real clock instead."""
        wall = time.time() - start
        if sound:
            p = sound.get_pts()
            if p and p > 0.1 and abs(p - wall) < 2:       # a sensible answer from the sound
                return p
        return wall

    frame_no, last_show, prev_tiny, cut_t = 0, 0.0, None, -1.0
    if sound:
        sound.set_pause(False)                             # start sound and picture together
    start = time.time()
    while True:
        ok, frame = video.read()
        if not ok:
            break                                          # end of the clip
        t = frame_no / fps                                 # where the picture is, in seconds
        frame_no += 1

        # Big frames cost a lot to process, show and save: shrink to at most 1280 wide
        if frame.shape[1] > 1280:
            k = 1280 / frame.shape[1]
            frame = cv2.resize(frame, None, fx=k, fy=k)

        # SCENE CUT? Compare the colors of this frame with the last one.
        # Colors change a lot at a new shot but little when people move,
        # so old boxes can disappear the moment the shot changes.
        hsv = cv2.cvtColor(cv2.resize(frame, (160, 90)), cv2.COLOR_BGR2HSV)
        tiny = cv2.calcHist([hsv], [0, 1], None, [16, 8], [0, 180, 0, 256])
        cv2.normalize(tiny, tiny)
        if prev_tiny is not None and cv2.compareHist(prev_tiny, tiny, cv2.HISTCMP_BHATTACHARYYA) > 0.3:
            cut_t = t
        prev_tiny = tiny

        with lock:                                         # give the AI the NEWEST frame
            shared["frame"], shared["t"], shared["cut_t"] = frame.copy(), t, cut_t
            results, results_t = shared["results"], shared["results_t"]
        # Only draw boxes from THIS shot that are less than a second old
        if results_t < cut_t or t - results_t > 1.0:
            results = []
        for (x1, y1, x2, y2), name, score in results:
            color = {"Unknown": (0, 0, 255), "Checking...": (0, 220, 255)}.get(name, (0, 200, 0))
            label = name if name == "Checking..." else f"{name}  {score:.2f}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, max(20, y1 - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.putText(frame, f"Threshold {THRESHOLD:.2f} | {clock(t)} / {clock(total / fps)} | + - S Q",
                    (10, frame.shape[0] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        if writer is None:
            h, w = frame.shape[:2]
            writer = cv2.VideoWriter(str(out_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
        writer.write(frame)

        # KEEP PICTURE AND SOUND TOGETHER
        ahead = t - clip_clock()                           # + = picture early, - = picture late
        if ahead < -0.1 and time.time() - last_show < 0.25:
            key = cv2.waitKey(1) & 0xFF                    # late: skip showing to catch up
        else:
            cv2.imshow("FaceHello", frame)
            last_show = time.time()
            wait_ms = int((ahead + 1 / fps) * 1000)        # early: wait for the sound
            key = cv2.waitKey(max(1, min(wait_ms, 100))) & 0xFF   # waiting here keeps the window alive

        if key == ord("s") and SAVE_PIPELINE_VIEWS:
            with lock:
                snap_frame, snap_faces = shared["last_frame"], shared["last_faces"]
            for i, face in enumerate(snap_faces, 1):
                scores = {n: float(v) for n, v in zip(names, matrix @ face.normed_embedding)}
                top = max(scores, key=scores.get) if scores else "Unknown"
                who = top if scores and scores[top] >= THRESHOLD else "Unknown"
                save_pipeline_view(snap_frame, face, f"How FaceHello recognized {who} at {clock(t)}",
                                   f"video_{stamp}_snap{frame_no}_face{i}_{who}.png", scores=scores)
        if key == ord("q"):
            break
        elif key in (ord("+"), ord("=")):
            THRESHOLD = min(0.95, THRESHOLD + 0.01)
        elif key in (ord("-"), ord("_")):
            THRESHOLD = max(0.05, THRESHOLD - 0.01)

    shared["stop"] = True                                  # tell the AI to finish
    worker.join(timeout=5)
    video.release()
    if writer:
        writer.release()
    if sound:                                              # stop the sound
        try:
            sound.set_pause(True)
        except Exception:
            pass
        # closing can be slow on some computers, so do it in the background
        threading.Thread(target=sound.close_player, daemon=True).start()
    cv2.destroyAllWindows()

    # ----- the report -----
    print(f"\n--- REPORT for {Path(path).name} (threshold {THRESHOLD:.2f}) ---")
    if not seen_at:
        print("  Nobody enrolled was found in this clip.")
    gap = 1.5                                              # a break longer than 1.5 s starts a new scene
    for name, times in seen_at.items():
        scenes, start, prev = [], times[0], times[0]
        on_screen = 0.0
        for x in times[1:] + [None]:
            if x is None or x - prev > gap:                # scene ended
                end = prev + 0.2
                scenes.append(f"{clock(start)}-{clock(end)}")
                on_screen += end - start                   # add up the length of each scene
                if x is not None:
                    start = x
            if x is not None:
                prev = x
        print(f"  {name}: about {on_screen:.1f} s on screen, best score {best[name][0]:.2f}")
        print(f"     appears at {', '.join(scenes)}")
        if SAVE_PIPELINE_VIEWS:                            # picture of their best moment
            score, frame, face = best[name]
            scores = {n: float(v) for n, v in zip(names, matrix @ face.normed_embedding)}
            save_pipeline_view(frame, face, f"How FaceHello found {name} in {Path(path).name}",
                               f"video_{stamp}_best_{name}.png", scores=scores)
    print(f"  video with boxes saved: {out_path}")


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
        for pic in list(VIEWS_DIR.glob(f"enroll_{safe(name)}_*.png")) + \
                   list(VIEWS_DIR.glob(f"*_{safe(name)}.png")):
            pic.unlink()                                   # their step-by-step pictures too
        print(f"Deleted {name}.")
    elif name:
        print("No one by that name.")


def delete_all(people):
    # .lower() means "delete", "DELETE" and "Delete" all work
    if input("Type DELETE to erase ALL face data: ").strip().lower() == "delete":
        people.clear()
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)                           # the whole face database is gone
        shutil.rmtree(VIEWS_DIR, ignore_errors=True)       # and every step-by-step picture
        print("All face data deleted.")
    else:
        print("Cancelled. Nothing was deleted.")           # always say what happened


# ---------------- MAIN MENU ----------------
people = load_people()
actions = {"1": enroll_webcam, "2": enroll_folder, "3": run_recognition, "7": recognize_video,
           "4": list_people, "5": delete_person, "6": delete_all}
while True:
    print("\n1) Enroll a person with the webcam\n2) Enroll from a photo folder\n3) Run recognition"
          "\n4) List people\n5) Delete a person\n6) Delete ALL face data\n7) Recognize faces in a video clip")
    choice = input("Choose 1-7: ").strip().lower()
    if choice == "q":                                      # type q to quit the program
        break
    if choice in actions:
        actions[choice](people)
