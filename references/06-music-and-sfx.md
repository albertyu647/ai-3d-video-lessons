# Music and sound effects

## Music: ask for structure, not a link

A music-search agent returned, in ~20 minutes, a CC BY 4.0 cinematic track with the exact attribution string (with
"(edited)" added, since CC BY asks you to note changes), a constant 133.33 BPM grid and its offset, a section map with
LUFS per section, the strongest drop located to ±5 ms, and an edit plan with every source cut on a downbeat and ~10 ms
crossfades. Picture events were snapped to the beat grid, and later retimes re-edited the music in code with no new
search.

Edit the music in code from a film-time -> source-time table: hard cuts on downbeats, a dropout before a drop, a riser,
a "stop hit" placed on the last downbeat ≥ 0.5 s before the final chord, a low-pass sweep while the camera is
underground. Extending a shot by one bar then just means one more source bar in the table.

## Sound effects: real recordings, not synthesis

Numpy-synthesised clanks, whooshes and stamps sounded "very typical of AI sounds" to the director. They were replaced
with 56 CC0 field recordings (49 used), layered and EQ'd per space with room tones per location and a credits file.
Find out on day 1 which sound libraries need the human's login (Freesound and Pixabay did, Mixkit didn't); the agent
must not sign in.

Pick sounds by measurement before anyone listens: duration, peak, RMS, noise floor, spectral centroid, onsets. A
recording titled "scanner" was a 96 Hz rumble.

## Placement and sync

- Cut every cue on its **measured attack** (onset ~20 dB below the loudest 1 ms peak) and put that attack exactly on
  the timing-file event.
- Varispeed pitch for weight (heavier = slower), a convolution reverb per space from generated impulse responses
  (old hall RT 2.1 s, modern hall 1.35 s, underground 2.8 s, end studio 0.9 s).
- **Verify sync numerically**: find the steepest envelope rise near each event in the SFX stem and report the offset.
  Delivered: every attack within ±1 frame, music drop -4 ms, voice lines within 7 ms of their first-word time.
- **One cue per on-screen action.** Diff the cue list against the event list whenever picture events change. A critic
  caught 4 release sounds for 3 visible magnet drops; a light cascade's pan had to be reversed to match the picture's
  direction.

## Peaks that stack

One clank peaked 1.5x above its siblings. Turning it down (twice) didn't help. A debug switch that lists every cue
sounding at a given instant showed the cause: the *previous* clank's sample was a "clank series" whose next hit, after
pitching down stretched it, landed on the same moment. Fix: trim earlier samples (0.9 s with a 0.3 s fade instead of
1.6 s) and restore the emphasis. Build an "active cues at time t" view into the SFX builder and check the peak layout
after every rebuild.

## Mix targets that worked for social video

- Stems by BS.1770 loudness: voice -16 LUFS (high-pass 90 Hz, light presence, 3:1 on the loudest 20%), music -18,
  one-shots -23.5, room tones -37.
- Ducking under voice with lookahead (0.1 s), 80 ms attack, 400 ms release: music -9 dB plus a -4 dB dip in 1-4 kHz.
- Master: static gain to **-14 LUFS integrated**, lookahead limiter, re-trim until within 0.2 LU, **true peak
  ≤ -1 dBTP**. 48 kHz stereo 24-bit, sample-exact film length.
- Write stems at final levels whose sum equals the pre-limiter mix, so any stem can be swapped without remixing by ear.
- The whole audio rebuild (SFX, mix, sync check) took ~20 s, so sound changes never waited on renders.
