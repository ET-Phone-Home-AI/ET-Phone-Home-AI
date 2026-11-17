---
name: animated-lecture
description: Erdem's animated lecture slides - a single HTML file presented from a browser with a remote, where each slide has a constant title and one or two boxes that appear one after another and each play their own animation with numbers computed live (a 7 turns into pixel numbers, a network lights up, a loss curve draws itself). Use this skill whenever Erdem asks for a presentation, slides, a lecture, a talk, a class demo, an explainer or "what's under the hood" material for any topic or course (ENGR-126, ENGR-125, EGRE 541, a conference talk), and whenever he says animated slides, animated presentation, "like the 7 network one", "the conference style", or wants the math and theory shown step by step. This is his default presentation format from now on; only use PowerPoint skills instead when he explicitly asks for a .pptx or PowerPoint file.
---

# Animated lecture slides

Erdem saw a conference talk where every slide was a small, carefully made animation on a white
background, driven with a clicker. This skill reproduces that format. The output is **one
self-contained HTML file** that he opens in a browser, makes full screen and presents with a
remote.

What makes this format work, and what to protect:

- **It looks like a slide.** The page is a 16:9 rectangle with a border, laid out the way Erdem
  sketched it: the title at the top, one or two bordered white animation boxes in the middle,
  and a note card under each box holding that box's heading and running caption. He rejected a
  version with heavy coloured bands for the title and notes because it clashed with the
  animations, so the template keeps those parts quiet: dark title text with a small blue label,
  pale tinted note cards with a numbered blue dot. The slide keeps its border, shadow and grey surround in
  full screen too, because he wants it to look like a PowerPoint slide there as well. The
  template already does all of this; do not restyle it or add filled colour bars.
- **The slide title stays put.** The left box and its note card appear and play; the right
  pair appears and plays when he presses Next. The audience always knows where to look.
- **Every box is an animation with beats**, not a picture that fades in. Something appears,
  changes into something else, moves, and ends on a result.
- **The numbers are computed, not typed.** A sum counts up to the real sum; a network's guess
  comes from real weights. This is why the audience trusts what they see, and why the slides
  never contain arithmetic mistakes.
- **It explains the theory.** Erdem wants what is under the hood: the mathematics and the
  reason it works, not a description of what a project does. Each box has a running caption
  that states the idea or formula for the beat currently on screen.
- **No controls on screen.** The remote does everything.

## Workflow

### 1. Storyboard before code

Write the storyboard as a short table and keep to it. For each slide: the title, then for each
box its heading, its beats in order with rough times, the caption for each beat, and what is
computed live. Aim for 2 to 5 beats and 6 to 12 seconds per box. A good beat list reads like
"the 7 appears, it breaks into pixels, each pixel becomes its number, the rows slide into one
vector".

If the request is clear, show the storyboard in one message and carry on building; do not wait
for approval unless the topic or scope is genuinely ambiguous. Erdem prefers to see a result and
correct it.

Pair the boxes on a slide so the second answers the first: cause then effect, problem then fix,
before then after, definition then example.

### 2. Copy the template and write the scenes

Copy `assets/stage-template.html` to the output file. It already contains the page, the styling,
the drawing helpers and the player. Replace only the demo code that sits between the two
banner comments containing `SCENES START` and `SCENES END` (keep both banner comments whole,
delete the demo scenes and the demo `SLIDES.push` lines between them, and write yours there),
and set the `<title>`. Leave the engine and player alone: they hold the
remote handling, sequencing and scaling that have been tested, and the checker script relies on
them.

A scene is a plain object:

```js
const myScene = {
  title: 'Heading shown at the top of the box',
  D: 8,                                   // seconds until the animation is finished
  caps: [[0, 'Caption from 0 s.'], [3.5, 'Caption from 3.5 s, with the formula for this beat.']],
  enter() { /* compute everything here: data, results, positions. Runs each time the box starts. */ },
  draw(t) { /* draw the whole picture for time t seconds. Called every frame. */ }
};
SLIDES.push({ title: 'The slide title', boxes: [sceneA, sceneB] });   // one or two boxes
DECK.label = 'ENGR-126 · Week 4';                                       // optional
```

Rules of the scene contract, with the reasons:

- **`draw(t)` must be a pure function of `t`.** Redraw everything from scratch each frame and
  derive every position and opacity from `t`. Do not accumulate state between frames. This is
  what lets Replay, Back and the checker jump to any moment and get the right picture.
  (Long-running work such as training can advance to a target step computed from `t`, as the
  example does.)
- **The drawing area is `W` × 900 logical units**: `W` is 1100 when the slide has two boxes and
  1900 when it has one. The engine scales it to the screen. Centre things with `W/2`. Keep
  everything inside the area with a margin of about 30.
- **Each caption is one step the presenter clicks through.** Erdem advances inside a box one
  step at a time: Next plays from the current caption to just before the next one and pauses
  there, and Back rewinds a step. So write the captions as the talking points, in the order he
  will explain them, and make sure the animation for one caption has finished before the next
  caption's time, because that is the frame he will be standing in front of while he talks.
  Three to five steps per box is typical. If the natural pause points differ from the caption
  times, give the scene `steps: [2.5, 4.2, 5.9]` (pause times in seconds) and those are used
  instead. A scene with one caption and no `steps` plays straight through.
- **After `t > D` the picture must hold its final state**, because the box stays on screen while
  the next one plays. A gentle idle motion after the end (a soft pulse on active nodes) keeps it
  alive.
- **Time each beat with `seg(t, a, b)`**, which gives 0 to 1 progress between seconds `a` and
  `b`, usually wrapped in `ease(...)`. Stagger groups of things by adding a small offset per
  item (`seg(t, 1 + i*0.05, 2 + i*0.05)`); staggering is most of what makes it look crafted.
- **Count numbers up** by multiplying the final value by the eased progress.

Helpers available inside scenes: `txt(str, x, y, size, color, align, weight, font)`,
`circle`, `line`, `rect`, `arrow`, `travel` (a dot moving along a wire), `flash` (expanding ring
when something fires), `A(alpha, fn)` (draw at an opacity), `lerp`, `clamp`, `seg`, `ease`,
`mulberry(seed)` (seeded random, so every run looks the same), `randn`, the palette `C`
(`ink, mut, line, pale, blue, org, grn, red, pur, bg`) and fonts `MONO`, `DISP`. `g` is the
canvas 2D context for anything else.

Read `references/example-seven-network.html` when the topic needs live computation on real
data, many moving parts, or a scene that reuses another scene's results; its SCENES region is a
complete worked deck (a digit becomes numbers, forward pass, loss, backpropagation, live
training). Skim it for patterns rather than copying its content.

**Start every deck with a cover slide.** The engine has a ready-made one; push it first:

```js
SLIDES.push({ cover: true, title: '', boxes: [coverScene({
  label: 'ENGR-126 · VIBE CODING WITH AI',            // course or event, in capitals
  title: ['How a Neural', 'Network Learns'],          // one or two short lines, about 14 characters each
  subtitle: 'Forward and backward propagation, one number at a time',
  author: 'Prof. Erdem Topsakal', affil: 'College of Engineering, VCU' })] });
```

Use that author and affiliation unless Erdem gives different ones. Name the deck for what the
audience will learn, and set the page `<title>` to the same name.

### 3. Design rules

- This format has its own look. Do not apply the black-and-gold PowerPoint style from the
  `vcu-slides` skill here unless Erdem asks for it; that style belongs to `.pptx` decks.
- **White background, dark ink, and one colour per concept**, kept the same through the whole
  deck (in the example: blue is the forward pass, orange is error and gradients, green is
  updates and correct answers, red is wrong). Decide the colour meanings in the storyboard.
- **Text size**: the boxes are half the screen, so nothing smaller than 20 logical units; labels
  22 to 28, key numbers 48 and up. Put sentences in the captions, not on the canvas.
- **Captions carry the theory.** One or two sentences per beat, at most about 170 characters
  because the note card under the box holds three lines and cuts off anything longer, with the formula written in
  plain Unicode (`h = max(0, w·x + b)`, `L = −ln(p₇)`, `w ← w − η·∂L/∂w`). Say why, not only
  what.
- **Be honest on screen** about simplifications: if the data is synthetic or the model is a toy,
  a caption or the hidden controls note says so.
- **Keep flicker gentle** and never flash the whole box; some viewers are photosensitive.
- Typical decks are 3 to 8 slides. One idea per box.

### 4. Check it

Run the checker; it plays every box to the end, reports script errors and saves one picture per
slide:

```bash
node scripts/check.js deck.html check-out
```

Then look at each saved picture once for overlapping text, things running off the box and
unreadable sizes, and fix what you see. The pictures show only the end of each slide, so things
that exist only mid-animation (a travelling wave, a label that fades out) are not in them: reason
through those from the code, and make sure the end state still tells the story on its own. If Playwright is not available, say so and ask Erdem to
step through the file once. Verify any computed result you describe to him (for example "the
network guesses 7") by reading it from the page rather than assuming.

### 5. Deliver

- Give him the **standalone `.html` file** as a download. That is the thing he presents from. It
  works offline; without internet the fonts fall back to Arial and Courier.
- If a publishing tool that adds its own page wrapper is available (Claude Code's Artifact
  tool), also publish it: `python scripts/to_artifact.py deck.html fragment.html` produces the
  version without the `<html>` wrapper.
- Remind him briefly how to drive it the first time, then not again:

| Key or remote button | Action |
|---|---|
| Next / Page Down / → / Space / click | Play the next step of the box, then show the next box, then go to the next slide |
| Back / Page Up / ← | Replay the step that is showing; pressed again within 1.5 s, go back one step (then one box, then to the previous slide shown complete) |
| R | Replay the slide |
| F (or F11) | Full screen on and off |
| H | Show or hide the on-screen controls |

- The second box never starts by itself: a slide opens with only the left box, and the right
  box appears when Erdem presses Next. He asked for this so he controls the pace. It is the
  `AUTO_CHAIN = false` setting at the top of the engine; leave it unless he asks.
- Do not convert to PowerPoint unless he asks. If he does, say plainly that a `.pptx` can only
  hold recordings of the animations, not the live version.
