# Vibe Coding UNleashed — ENGR-126 promo video

A 78-second 1080p/30fps promo video for ENGR-126 *Vibe Coding with AI*. Everything is generated from code: the canvas animation, the motion graphics and the synthesized soundtrack.

## Files
- `index.html` + `stage.js`: the animation. `render(t)` draws the frame at time `t` (in seconds). The timeline is the `SCENES` array at the bottom of `stage.js`.
- `music.py`: synthesizes `music.wav` (120 BPM). The drops, impacts and typing clicks are timed to match the scenes.
- `render.js`: renders every frame in headless Chromium and pipes the frames to ffmpeg, which writes `VibeCodingUNleashed_ENGR126.mp4`.
- `stills.js`: renders single frames for quick checks, e.g. `node stills.js 14 45 72` (writes to `st/`).
- `rodney.png`: Rodney the Ram cut out from the original photo with `cutout2.py`.

## Rebuild
Requirements: Node with Playwright and Chromium, Python with numpy and scipy, ffmpeg. The page loads its fonts from Google Fonts, so rendering needs network access.

```bash
mkdir -p st
python3 music.py
node render.js
```

Rendering takes about 4 minutes.

## Vertical 9:16 version (Instagram Reels, TikTok, Shorts)
The same animation has a 1080x1920 layout, switched on by opening `index.html#v`. Every scene is re-laid out for the tall frame, and the important text stays clear of the top and bottom where the Instagram interface sits.

```bash
node render.js vertical
```

This writes `VibeCodingUNleashed_ENGR126_9x16.mp4`. For check frames: `node stills.js vertical 14 45 72`.
