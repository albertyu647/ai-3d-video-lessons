# The timing contract

One JSON file is the single source of truth for time. Scene modules, camera paths, physics start frames, sound
cues, the mixer, the subtitle chunker, title cards and render ranges all read it. A retime touches one file.

Template: [`../templates/timing.example.json`](../templates/timing.example.json).

## What goes in it

- `fps`, `frame_start`, `frame_end`, `resolution`
- `shots`: `{s1: {t0, t1, f0, f1, title}, ...}`
- `events`: named beats **in seconds** (`s1_clank_1`, `s7_app_boot`), plus derived `event_frames`
- `vo`: one entry per line, `{line, start, file, words: [{text, t, end}]}` with word-level times from forced alignment
- `music`: track, licence, credit line, BPM grid
- the convention, written in the file: `frame = round(t*fps) + 1`, inverse `t = (f - 1) / fps`

```python
T = json.load(open("timing.json")); FPS = T["fps"]
def f(t): return int(round(t * FPS)) + 1
def ev(name): return T["events"][name]
key_at(obj, f(ev("s7_stamp")))          # picture
place_sfx("stamp", at=ev("s7_stamp"))   # sound: the sample's measured attack lands on the event
subs = chunks_from_words(T["vo"])       # text
```

## Build it from the voice, snap it to the music

The first version came from the voice-over word timestamps, then events were snapped to the music's beat grid
(133.33 BPM, 1.8 s bars). Retiming 40 -> 46 -> 47.75 -> 49.5 s never needed a new music search or a new opening,
because events moved by name.

## Never hard-code frames

The event constants read the file, but animation keys didn't. When one shot grew by 42 frames, about 60 hard-coded
keys (arm, carrier, camera, pulses) were still on the old clock, and ~90 literals across 8 files had earlier forced a
dedicated "retime agent". The patch was an offset helper `S(f) = f + D`. From day one write keys as
`event + offset`.

## Key picture to words

Once the voice is locked, write a word -> frame table into the agents' brief. Animation keyed to `vo[line].words`
retimes itself when the voice changes.

## Sound-only events

Physics doesn't land exactly where you planned. When a simulated arm landed 2 frames before its planned clank,
the fix was a sound-only event (`s1_clank_1_snd`) at the measured landing, leaving the animation untouched. Builders
report contact, lift-off, release and landing times per object; sound follows them.

## Changing length

- **Insert time at a shot's tail** and shift everything after it as a block: shot ranges, events, later voice lines.
  The later shot's frames are then *renumbered*, not re-rendered.
- **Extend by whole music bars.** A payoff hold was extended by one bar (1.8 s at 133 BPM = 43 frames). The music
  edit gained one bar on the grid, and the seams were checked numerically for clicks. If a bar isn't an integer
  number of frames, shift by the integer and accept ~8 ms of grid drift.
- Keep a backup of the previous timing file before every retime, and rebuild `event_frames` after edits.
