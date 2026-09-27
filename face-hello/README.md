# FaceHello — ENGR-126 Project 5

Teaching a webcam to greet people by name. Everything runs offline on your laptop
after a one-time model download; no image or face fingerprint ever leaves the machine.

## Install (PyCharm Terminal tab)

```
pip install insightface onnxruntime opencv-python numpy piper-tts
```

## Run

```
python face_hello.py
```

Menu: 1) enroll with webcam · 2) enroll from a photo folder · 3) run recognition ·
4) list people · 5) delete a person · 6) delete ALL face data · `q` to quit.

In the video window: `+` / `-` change the recognition threshold, `Q` returns to the menu.

Face fingerprints are saved only in `face_fingerprints.json` next to the script
(ignored by git, so it is never uploaded).
