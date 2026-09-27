"""
face_id.py - ENGR-126 Project 5: Teaching a Webcam to Greet People by Name

What this program does
----------------------
  enroll NAME   Look at the camera. The program grabs 5 frames of your face,
                turns each one into 512 numbers (an "embedding"), averages them
                and saves   NAME -> 512 numbers   in faces.npz.
  enroll-folder PATH
                Same, but from photos. PATH is a folder named after the person
                (photos/Erdem/*.jpg), or a folder of such folders to enroll
                everyone at once (photos/Erdem/, photos/Ayse/, ...).
  run           Live webcam window. Every face gets a box, a name and a match
                score. Faces that match nobody well enough are "Unknown".
  list          Show who is enrolled.
  delete NAME   Remove one person.   delete --all   removes faces.npz.

The pipeline (the same six boxes from the lecture)
  webcam frame -> SCRFD finds face + 5 points -> warp the face straight
  -> 112x112 crop -> ResNet-50 (ArcFace) -> 512 numbers of length 1

Install once (in PyCharm: View > Tool Windows > Terminal):
    pip install insightface onnxruntime opencv-python numpy
  Windows: if pip says "Microsoft Visual C++ 14.0 or greater is required",
  install "Build Tools for Visual Studio" (C++ workload) and run pip again.

The first run downloads the buffalo_l model pack (~280 MB) to ~/.insightface.
After that, nothing leaves your laptop.

Run it:
    python face_id.py enroll Erdem
    python face_id.py enroll-folder photos/Erdem
    python face_id.py run
  Or press the green Run button in PyCharm with no arguments to get a menu.

Privacy: faces.npz is biometric data. Enroll only people who agree,
never upload it (it is in .gitignore), and delete it when the lab ends.
"""

import sys
import threading
import time
from pathlib import Path

import cv2
import numpy as np
from insightface.app import FaceAnalysis

# ---------------------------------------------------------------------------
# Settings - the knobs you are allowed to turn
# ---------------------------------------------------------------------------
THRESHOLD = 0.40          # match score needed to say a name (tune this in lab!)
CAMERA_INDEX = 0          # 0 = built-in webcam; try 1 if the window is black
DET_SIZE = 320            # detector input size: 320 = faster, 640 = finds faces farther away
ENROLL_FRAMES = 5         # how many frames to average when enrolling
ENROLL_GAP_SECONDS = 0.6  # wait between enrollment frames so they differ a bit
DB_FILE = Path(__file__).with_name("faces.npz")   # saved next to this script

GREEN = (80, 200, 60)     # OpenCV colors are (Blue, Green, Red)
ORANGE = (0, 140, 255)
WHITE = (255, 255, 255)
DARK = (40, 35, 14)


# ---------------------------------------------------------------------------
# 1. Load the face models (detector + recognizer) once
# ---------------------------------------------------------------------------
def load_face_app():
    """Load InsightFace's buffalo_l pack: SCRFD detector + ArcFace ResNet-50."""
    print("Loading face models (first time downloads ~280 MB)...")
    # buffalo_l contains 5 models; we only need 2 of them. Skipping the other
    # three (3D landmarks, 106 landmarks, age/gender) makes every frame faster.
    app = FaceAnalysis(name="buffalo_l", allowed_modules=["detection", "recognition"],
                       providers=["CPUExecutionProvider"])
    # ctx_id=-1 means "use the CPU" - no graphics card needed.
    app.prepare(ctx_id=-1, det_size=(DET_SIZE, DET_SIZE))
    return app


# ---------------------------------------------------------------------------
# 2. The face database: names + one 512-number vector per person
# ---------------------------------------------------------------------------
def load_db():
    """Return (names, vectors). vectors has shape (number_of_people, 512)."""
    if not DB_FILE.exists():
        return [], np.zeros((0, 512), dtype=np.float32)
    data = np.load(DB_FILE)
    return [str(n) for n in data["names"]], data["vectors"].astype(np.float32)


def save_db(names, vectors):
    """Write the database back to faces.npz (or delete it if it is empty)."""
    if len(names) == 0:
        DB_FILE.unlink(missing_ok=True)
        return
    np.savez(DB_FILE, names=np.array(names), vectors=np.asarray(vectors, dtype=np.float32))


# ---------------------------------------------------------------------------
# 3. Matching: one multiply-and-add per enrolled person
# ---------------------------------------------------------------------------
def best_match(embedding, names, vectors):
    """
    Compare one face (512 numbers, length 1) with everyone in the database.

    Because every vector has length 1, the dot product IS the cosine
    similarity: about 1.0 = same direction (same person), about 0 = unrelated.
    Returns (name, score); name is "Unknown" if the best score < THRESHOLD.
    """
    if len(names) == 0:
        return "Unknown", 0.0
    scores = vectors @ embedding          # one dot product per enrolled person
    i = int(np.argmax(scores))            # index of the highest score
    score = float(scores[i])
    if score < THRESHOLD:
        return "Unknown", score
    return names[i], score


def average_embedding(embeddings):
    """Average several unit vectors and stretch the result back to length 1."""
    mean = np.mean(embeddings, axis=0)
    # An average of length-1 vectors is a bit SHORTER than 1, which would
    # quietly lower every future score. Dividing by its length fixes that.
    return mean / np.linalg.norm(mean)


# ---------------------------------------------------------------------------
# 4. Small drawing helpers
# ---------------------------------------------------------------------------
def draw_label(frame, text, x, y, color):
    """Draw text on a filled rectangle so it is readable on any background."""
    (w, h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
    y = max(y, h + 10)
    cv2.rectangle(frame, (x, y - h - 10), (x + w + 10, y), color, -1)
    cv2.putText(frame, text, (x + 5, y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.7, WHITE, 2)


def draw_banner(frame, text):
    """Dark strip across the top of the window with one line of text."""
    cv2.rectangle(frame, (0, 0), (frame.shape[1], 40), DARK, -1)
    cv2.putText(frame, text, (12, 27), cv2.FONT_HERSHEY_SIMPLEX, 0.75, WHITE, 2)


class Camera:
    """
    Reads the webcam in a background thread and keeps ONLY the newest frame.

    Why: the camera delivers ~30 frames per second, but face recognition
    handles only a few per second on a laptop CPU. If we read frames one by
    one, the unread ones pile up in a queue and the picture lags seconds
    behind reality. Throwing old frames away keeps the video live.
    """

    def __init__(self):
        self.cam = cv2.VideoCapture(CAMERA_INDEX)
        ok, frame = self.cam.read()
        if not ok:
            self.cam.release()
            sys.exit(f"Could not read from camera {CAMERA_INDEX}. Try CAMERA_INDEX = 1, "
                     "close other apps using the camera, or allow camera access "
                     "(macOS: System Settings > Privacy > Camera > PyCharm/Terminal).")
        self.frame = frame
        self.lock = threading.Lock()      # stops two threads touching self.frame at once
        self.running = True
        threading.Thread(target=self._keep_reading, daemon=True).start()

    def _keep_reading(self):
        while self.running:
            ok, frame = self.cam.read()
            if ok:
                with self.lock:
                    self.frame = frame    # overwrite: older frames are simply dropped

    def read(self):
        """Return a copy of the newest frame."""
        with self.lock:
            return self.frame.copy()

    def release(self):
        self.running = False
        time.sleep(0.1)                   # let the reading thread finish its last read
        self.cam.release()


# ---------------------------------------------------------------------------
# 5. ENROLL: learn a new person from a few webcam frames
# ---------------------------------------------------------------------------
def enroll(name):
    answer = input(f"Does {name} agree to have their face stored on this laptop? (y/n): ")
    if answer.strip().lower() != "y":
        print("Not enrolled. Only enroll people who say yes.")
        return

    app = load_face_app()
    cam = Camera()
    collected = []
    last_grab = 0.0
    print(f"Look at the camera, {name}. Move your head a little between captures. Press q to cancel.")

    while len(collected) < ENROLL_FRAMES:
        frame = cam.read()
        faces = app.get(frame)            # detect + align + embed, all in one call

        if len(faces) == 1:
            face = faces[0]
            x1, y1, x2, y2 = face.bbox.astype(int)
            cv2.rectangle(frame, (x1, y1), (x2, y2), GREEN, 2)
            for (px, py) in face.kps.astype(int):   # the 5 landmark points
                cv2.circle(frame, (px, py), 3, ORANGE, -1)
            # Grab a frame every ENROLL_GAP_SECONDS while exactly one face is visible
            if time.time() - last_grab > ENROLL_GAP_SECONDS:
                collected.append(face.normed_embedding)
                last_grab = time.time()
            status = f"Enrolling {name}: {len(collected)}/{ENROLL_FRAMES}"
        elif len(faces) == 0:
            status = "No face found - move closer / add light"
        else:
            status = f"{len(faces)} faces - only {name} should be in view"

        draw_banner(frame, status)
        cv2.imshow("Enroll (q = cancel)", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cam.release()
    cv2.destroyAllWindows()

    if len(collected) < ENROLL_FRAMES:
        print("Enrollment cancelled - nothing saved.")
        return

    add_person(name, average_embedding(np.array(collected)))


def add_person(name, vector):
    """Store one person's vector in faces.npz (re-enrolling replaces the old one)."""
    names, vectors = load_db()
    if name in names:
        vectors[names.index(name)] = vector
    else:
        names.append(name)
        vectors = np.vstack([vectors, vector])
    save_db(names, vectors)
    print(f"Saved {name}. {len(names)} people enrolled in {DB_FILE.name}.")


# ---------------------------------------------------------------------------
# 5b. ENROLL FROM A FOLDER: learn people from photos instead of the webcam
# ---------------------------------------------------------------------------
IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def read_image(path):
    """Like cv2.imread, but also works with accents/spaces in Windows paths."""
    data = np.fromfile(str(path), dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def embeddings_from_folder(app, folder):
    """Return one embedding per photo in the folder that shows a face."""
    found = []
    for path in sorted(folder.iterdir()):
        if path.suffix.lower() not in IMAGE_TYPES:
            continue
        image = read_image(path)
        if image is None:
            print(f"  skip {path.name}: could not open the image")
            continue
        faces = app.get(image)
        if not faces:
            print(f"  skip {path.name}: no face found")
            continue
        if len(faces) > 1:
            print(f"  {path.name}: {len(faces)} faces - using the biggest one")
        # The biggest box (width x height) is most likely the person the folder is about
        face = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
        found.append(face.normed_embedding)
        print(f"  ok   {path.name}")
    return found


def enroll_folder(folder_path):
    """
    Two ways to organize photos:
      photos/Erdem/*.jpg          -> enrolls "Erdem" (the folder name is the name)
      photos/ with subfolders     -> enrolls every subfolder as one person
          Erdem/*.jpg
          Ayse/*.jpg
    """
    folder = Path(folder_path).expanduser()
    if not folder.is_dir():
        print(f"Folder not found: {folder}")
        return

    has_images = any(p.suffix.lower() in IMAGE_TYPES for p in folder.iterdir())
    people = [folder] if has_images else sorted(p for p in folder.iterdir() if p.is_dir())
    if not people:
        print(f"No photos or person folders inside {folder}")
        return

    who = ", ".join(p.name for p in people)
    answer = input(f"Do these people agree to have their face stored on this laptop: {who}? (y/n): ")
    if answer.strip().lower() != "y":
        print("Not enrolled. Only enroll people who say yes.")
        return

    app = load_face_app()
    for person in people:
        print(f"{person.name}:")
        found = embeddings_from_folder(app, person)
        if not found:
            print(f"  No usable photos - {person.name} not enrolled.")
            continue
        if len(found) < 3:
            print(f"  Only {len(found)} usable photo(s); 3-10 photos give steadier results.")
        add_person(person.name, average_embedding(np.array(found)))


# ---------------------------------------------------------------------------
# 6. RUN: live recognition with a greeting
# ---------------------------------------------------------------------------
class FaceWorker:
    """
    Runs face recognition in a background thread, over and over, on the
    newest camera frame. The main loop can then show smooth live video and
    simply draw the most recent results on top of it.
    """

    def __init__(self, app, cam, names, vectors):
        self.app, self.cam = app, cam
        self.names, self.vectors = names, vectors
        self.results = []                 # list of (box, name, score)
        self.ai_fps = 0.0
        self.running = True
        threading.Thread(target=self._keep_recognizing, daemon=True).start()

    def _keep_recognizing(self):
        while self.running:
            start = time.time()
            results = []
            for face in self.app.get(self.cam.read()):
                name, score = best_match(face.normed_embedding, self.names, self.vectors)
                results.append((face.bbox.astype(int), name, score))
            self.results = results        # replace the whole list in one step
            # How many frames per second the AI manages (smoothed)
            self.ai_fps = 0.8 * self.ai_fps + 0.2 / max(time.time() - start, 1e-6)

    def stop(self):
        self.running = False


def run():
    global THRESHOLD
    names, vectors = load_db()
    if not names:
        print("Nobody is enrolled yet - everyone will be 'Unknown'. "
              "Try: python face_id.py enroll YourName")

    app = load_face_app()
    cam = Camera()
    worker = FaceWorker(app, cam, names, vectors)
    print("Running. Keys:  q = quit   + / - = raise / lower THRESHOLD")

    while True:
        frame = cam.read()                # always the newest frame -> no lag

        greeted = []
        for (x1, y1, x2, y2), name, score in worker.results:
            color = ORANGE if name == "Unknown" else GREEN
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            # Always show the score: that is the data you record in the lab
            draw_label(frame, f"{name}  {score:.2f}", x1, y1, color)
            if name != "Unknown":
                greeted.append(name)

        greeting = "Hello, " + ", ".join(greeted) + "!" if greeted else "Hello... who are you?"
        draw_banner(frame, f"{greeting}    threshold {THRESHOLD:.2f}   AI {worker.ai_fps:.1f} fps")
        cv2.imshow("Face ID (q = quit, +/- = threshold)", frame)

        key = cv2.waitKey(30) & 0xFF      # ~30 screen updates per second
        if key == ord("q"):
            break
        elif key in (ord("+"), ord("=")):
            THRESHOLD = min(THRESHOLD + 0.02, 1.0)
        elif key in (ord("-"), ord("_")):
            THRESHOLD = max(THRESHOLD - 0.02, 0.0)

    worker.stop()
    time.sleep(0.5)                       # let the last recognition finish
    cam.release()
    cv2.destroyAllWindows()


# ---------------------------------------------------------------------------
# 7. LIST and DELETE: seeing and removing the stored face data
# ---------------------------------------------------------------------------
def list_people():
    names, _ = load_db()
    if names:
        print("Enrolled:", ", ".join(names))
    else:
        print("Nobody is enrolled.")


def delete(name):
    if name == "--all":
        DB_FILE.unlink(missing_ok=True)
        print(f"Deleted {DB_FILE.name}. No face data remains.")
        return
    names, vectors = load_db()
    if name not in names:
        print(f"{name} is not enrolled.")
        return
    i = names.index(name)
    names.pop(i)
    vectors = np.delete(vectors, i, axis=0)
    save_db(names, vectors)
    print(f"Deleted {name}.")


# ---------------------------------------------------------------------------
# 8. Command line + a simple menu for the PyCharm Run button
# ---------------------------------------------------------------------------
def menu():
    """Used when the script is started without arguments."""
    print("\n1) Enroll a person with the webcam\n2) Enroll from a photo folder\n3) Run recognition"
          "\n4) List people\n5) Delete a person\n6) Delete ALL face data")
    choice = input("Choose 1-6: ").strip()
    if choice == "1":
        enroll(input("Name: ").strip())
    elif choice == "2":
        # Strip quotes in case the path was pasted as "C:\...\Erdem"
        enroll_folder(input("Folder path: ").strip().strip('"').strip("'"))
    elif choice == "3":
        run()
    elif choice == "4":
        list_people()
    elif choice == "5":
        delete(input("Name to delete: ").strip())
    elif choice == "6":
        delete("--all")


def main():
    args = sys.argv[1:]
    if not args:
        menu()
    elif args[0] == "enroll-folder" and len(args) >= 2:
        enroll_folder(" ".join(args[1:]))
    elif args[0] == "enroll" and len(args) >= 2:
        enroll(" ".join(args[1:]))
    elif args[0] == "run":
        run()
    elif args[0] == "list":
        list_people()
    elif args[0] == "delete" and len(args) == 2:
        delete(args[1])
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
