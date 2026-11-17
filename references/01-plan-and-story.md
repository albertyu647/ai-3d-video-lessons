# Planning, story and feedback

## Front-load the brief

Two of the first three starts were thrown away within a minute because the director kept adding things: the
storyboard image, the TTS tool, the subtitle style, "check voice, music and picture are in sync". Before launching
anything, write a one-screen checklist and get one confirmation:

- references (storyboard, mood frames, logos, fonts)
- length, aspect, fps, delivery size limits (chat apps here rejected files over 30 MB, so every cut shipped as a
  ~95 MB master plus a ~25 MB phone copy)
- voice-over source and who operates it
- music and sound licence rules
- asset-download permission (see below)
- subtitle and on-screen text style

**Ask about downloading assets on turn 1.** The agent defaulted to "everything procedural, downloads need your OK"
and mentioned it only in a wrap-up note. Permission came 23 hours later, after three rounds of procedural materials
had plateaued.

**Resolve open decisions explicitly.** "40 s or 45 s?" was asked and never answered; the agent picked 45. Harmless
here, but length changes every frame number downstream. If a decision changes a contract (length, aspect, voice),
block on it or put the default in the plan's first line.

## Show a rough cut early

The director first saw the whole film about 25 hours in. By then three build/critic loops had cost ~$650 of a $964
session, chasing storyboard-match scores that sat in the 60s and 70s. None of the critics flagged what the director
raised within hours of watching:

- a jarring hard cut between two sets
- a new location that read as "sterile, not dramatic"
- the key product moment hidden inside a black box
- scenes too short to read
- details that would alienate the target audience

**Do this instead:** an animatic in the first hour or two (storyboard panels + voice + music + subtitles; a compositor
with a "placeholder mode" makes this nearly free), then a low-res full cut, then polish. Ask "does the message
land?", not "is it 90/100 realistic?".

When the director wants something to look at *now*, offer a composite of what exists and lay out the trade-offs as a
table (quarter res: 15 min, soft; every 3rd frame: choppy; add a second GPU: +25%). He picked quarter res and had a
cut in 15 minutes.

## Plan first on subjective feedback

The director said "don't act yet, tell me your plan" before every major round. Plans in this shape got a one-line
"Approve, go" every time, with no second round:

1. **What I found**, with frame numbers taken from a contact sheet of the last cut.
2. **Proposed changes**, numbered.
3. **Agent table**: agent, model, files it owns, job.
4. **Render footprint**: which frames re-render ("about 300 of 1146") and how long. The director asked about this
   every time.
5. **Your decisions**, each with my default.

Inspect actual frames before proposing. A note about a "random pan" was located at frames 890-910 (two leftover
camera keys) before any fix was planned.

## Turn vague stakeholder notes into an inventory

Feedback like "the middle is incoherent" or "drop theme X" or "one brand only" touches every layer. Grep and list each
occurrence across: voice-over, on-screen text in post, 3D signage and labels, props that illustrate the theme, sound
cues, and labels in code. Then have a fresh critic scan every visible word in the renders, because code search misses
baked textures and 1 cm signage (it found two leftovers the grep missed).

Watch for your own additions bringing the theme back. To explain a jargon term the director wanted, the agent wrote
a definition, and the definition pulled in exactly the concept the client wanted gone. Test each new line against
the core message before building picture for it.

Write labels for the audience. A technical label ("MEMORY BUS") was flagged as meaningless to business viewers and
renamed to the effect the viewer actually sees ("SHARED LEARNING").

## Coherence = you see what you hear, when you hear it

The fix for "the middle is incoherent" was not new copy. It was:

- **one idea per segment**, and
- **the picture keyed to the spoken words**: a dolly that centres each labelled block one frame after its word
  starts, read from the voice-over word times; the reveal lands on the line's last word; the product boots on the
  word "live".

A critic confirmed: "the labels land on the voice". Ask the narrator for an evenly paced list ("a short beat after
each item") when the camera will land on each item.

A beat shorter than its line is a story bug. One shot held a wide on unreadable labels and arrived at its subject 2.5 s
before the line about it, so the picture "waited". For every beat check: when the word lands, when the picture lands,
how long the payoff stays readable.

## Payoffs and physical plausibility

- **The payoff must look worth the effort that made it.** A line of robot arms working hard to output a white box
  with a label was "anticlimactic". The replacement: a touchscreen kiosk that boots on the key word into a live
  dashboard, light spills, and the factory's lights cascade down the line, held for an extra music bar.
- **Physical actions must read as plausible to a lay viewer.** A lever flipping a heavy robot arm into a skip was
  called out. The fix reused a machine the world already had (the overhead hoist that lowers new arms) with a scrap
  magnet, which also set up a later shot.
- **The whole action must be in frame.** The first version of that fix was physically correct but the magnet and
  the drop were mostly out of frame. Put "is the full action visible?" in the builder's checklist.

## Copy and taste belong to the human

- Give 4-5 options in one register, name your pick, and explain *why* something feels off when asked (the agent's
  proverb-pun end lines were "kinda cringe": puns read as a pitch and undercut a cinematic tone).
- Don't argue for your own copy. The director wrote the final line himself.
- Keep copy that may change in 2D post: the end card changed four times, each a ~5-minute recompose.
