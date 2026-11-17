# Review loops

## Open-ended scoring loops plateau

The first build ran builder -> critic -> fixer loops aiming for 90/100 on realism and storyboard match. After 2-4
rounds every part sat at 64-80 and some went down (68 -> 64). The causes, found afterwards:

- a fresh critic each round who "judges a bit differently", so scores were noise plus drift
- nothing checked whether last round's issues were fixed
- each fixer got ~15 issues at once
- composition and camera problems (worth the most points) were never owned by anyone
- shared modules were judged in their own test scenes, not in film frames

Cost by fix round: $311, $223, $66, $17. Fixers (40%) and builders (31%) were the cost centres; critics were 7%.

## The ledger design that fixed the structure

If you do score, keep these parts:

- **Fixed eval frames** rendered every round, plus side-by-sides against the reference panel with numeric deltas
  (layout correlation of a coarse luma grid, Lab colour distance, clipped and crushed percentages).
- **A rubric with hard caps:** any open critical issue caps the axis at 75, any open major at 88. "90" then means
  every critical and major issue is fixed and verified.
- **A persistent issue ledger:** critics first mark each open issue fixed / partial / not fixed / regressed (citing a
  frame), then add at most 10 new ones, each tagged with the module that must change.
- **Fixers get at most 6 issues**, composition first, with before/after renders as proof. An issue that survives two
  attempts must be solved a different way. A set that barely moves over two rounds gets a director re-plan.
- **Passing needs two independent critics**, ideally on different models.

The side-by-side tool immediately exposed a framing error two critic rounds had missed.

## What actually caught defects

1. **Deterministic scripts:** interpenetration check (115 pairs), luma and clipping stats across a cut, magenta scan
   for missing textures, build smoke tests, camera speed and text legibility, degrees per frame, ffprobe frame counts,
   seam steps, sound sync offsets, peak layout.
2. **Structured visual comparison:** side-by-side with the reference, 50% overlays at match cuts, contact sheets.
3. **Targeted reviews with a narrow question** ("does the cut read as a match?", "is the stamp readable?").
4. **The human, for story and taste:** the hard cut, "sterile", the black box, synthetic-sounding SFX, too short,
   anticlimactic payoff, implausible physics.

## The fresh critic that earned its cost

Late rounds used one critic per round: fresh context, images and test outputs only, barred from editing, ~30 minutes,
$1.4-2. The brief: the stakeholder's goals, exact paths of test outputs, "BLOCKERS (must fix, with frame numbers and a
concrete fix) vs NITS", and "don't invent problems".

What it found that builders' self-checks missed:

- **Stale artifacts, not scene bugs.** An end-card test was composited over the *old* frames; a test clip was rendered
  *before* the patch it was meant to verify. Ask critics to compare output timestamps against patch timestamps.
- **A correct fix that didn't read.** Arms landed exactly on the beat with clean physics, but no magnet carrying an
  arm and letting go was ever in frame. "You never see the drop" is a viewer's note no metric produces. A builder
  reviewing its own render "sees what it intended rather than what's there".

One fix round, then render. Remaining nits go into the delivery message for the human to prioritise.

## Iteration budget (write it into the spec)

The director found an agent's render folder numbered to v17: "you don't need to review them 17 times, I do want to
get the renders soon". Budget that worked:

- plan the change from code first; 1 before + 1 after render per issue; a second attempt only if the after clearly
  failed; about 4 render calls per issue and 12 per agent
- batch all stills into one Blender call at 25-50%
- one overwritten output folder per task, never a numbered series
- stop when it meets the brief; stop if the score gains < 3 points; same failure twice = stop and report

## Report contract for builders

Every agent ends with ≤ 25 lines: files changed and what; **exact frame ranges that change on screen**; event times
it needs added to the timing file; paths of stills, sheets and clips; **deviations from the plan with their
re-render cost**; what it could not verify. The frame ranges are what make partial re-renders possible. The deviation
section turned "the kiosk can't fit under the gate, so it comes out of a machine instead" into an honest line in the
delivery note instead of a surprise.

## Delivery checklist

1. Render log scanned for errors, with known-harmless warnings filtered.
2. Frame count and duration match the timing file (ffprobe).
3. Seam steps measured wherever new frames meet reused ones.
4. Key-frame contact sheet of the final MP4, looked at.
5. Loudness and true peak of the mix.
6. A full master plus a copy under the chat upload limit.
7. A plain list of what was **not** verified ("I haven't watched it end to end", "nobody has listened to the new
   voice lines next to the old ones").

Delete or rename superseded test outputs and backups. A backup compositor still holding an old tagline and stale test
frames were both flagged as traps.
