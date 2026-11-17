---
name: ai-3d-video-lessons
description: Field-tested rules for using AI coding agents to make 3D scenes, animation and videos (Blender/Cycles or similar, rendered locally or on a remote GPU, with voice-over, music, sound effects and post). Covers planning and story, a single timing file, code vs downloaded assets, physics, rendering and flicker, partial re-renders, voice-over and TTS, sound, review loops, multi-agent splits and token cost. Use when an agent is asked to build, animate, render, fix or review a 3D scene, product video, promo, explainer or animation, or to plan agents and renders for one.
---

# 3D video with AI agents: lessons

Distilled from a ~50 s photoreal product promo built almost entirely by Claude Code agents over four days and eight
cuts (headless Blender + Cycles, a remote RTX 3060 Ti, Python/ffmpeg post, cloud TTS voice-over). Every rule below
cost real time or money to learn. Details and evidence: `references/`.

## The 12 rules that mattered most

1. **Show a full-length rough cut within hours, not days.** Storyboard panels + voice + music + subtitles, then a
   low-res render. Polish loops before the first human viewing cost ~68% of the first $964 session and were partly
   thrown away by story notes. Ask the human a story question ("does it land?"), not a fidelity score.
2. **One timing file drives picture, sound and text.** Shots, named events (seconds), voice-over word times, music
   grid. `frame = round(t*fps)+1`. No frame literals in scene code: write `event + offset`. Key animation to the
   spoken words. See `references/02-timing-contract.md`.
3. **Plan before acting on subjective feedback.** Reply with findings (frame numbers from a contact sheet), numbered
   changes, an agent table (agent / model / owned files), the frames that re-render with a time estimate, and your
   default for each open decision. Wait for an explicit go.
4. **Never let an agent wait on a render inside its own context.** Subagent prompt caches expire after 5 min; 34-37%
   of the first session's spend was rewriting expired caches. Submit the render detached, wait with bounded calls
   under 4 min (or a zero-token background waiter in the main thread), or hand off to a fresh agent.
5. **Pull real assets for surfaces and dressing; build hero objects and layout in code.** Scanned CC0 textures, HDRIs
   and models beat procedural materials, which plateaued. Free libraries rarely have the specific hero prop. Run an
   asset scout in parallel while builders use proxies behind one swap function. Count assets *used*, not downloaded.
6. **Bake physics, then post-process it.** Rigid bodies for anything that falls or collides, baked to keyframes with
   fixed seeds. Settled piles still jitter: hold each body's pose once it rests, release it only on real contact. Run
   an automated interpenetration check.
7. **Benchmark render advice on your own footage.** Static seed beat animated seed; temporal denoiser and bounce cuts
   gave nothing; GPU denoising (off by default in Cycles) was a free 20%; per-shot ffmpeg `atadenoise` cut residual
   flicker 30%. Render at 50% and upscale with Lanczos; frame-by-frame AI upscalers shimmer.
8. **Re-render only what changed.** Hardlink the previous cut's frames, delete only the changed ranges, renumber
   shifted shots, extend by whole music bars, keep shot boundary poses identical, then measure every seam. Put text,
   subtitles and end cards in post so copy changes cost minutes, not renders.
9. **Run long renders detached and resumable on the render box.** Chunked, skip-existing frames, a slot queue sized
   to VRAM (2 jobs on 8 GB), `--python-exit-code 1` so Blender errors fail the job, frame counts verified.
10. **Don't speed up the voice.** Anchor each sentence to its picture moment and shorten pauses inside sentences.
    Re-record only changed lines (pickups). Run ASR on every delivered take and diff it against the script. The
    agent can't hear: a person picks voices and listens to brand names.
11. **Measure, don't eyeball.** Clip checks, frame-difference at seams, luma across cuts, text legibility in
    %-of-frame-width per frame, degrees per frame before motion blur, peak layout of the sound mix, "first frame that
    differs". Scripts caught more real defects than critic scores.
12. **A fresh, image-only critic with a narrow brief, one fix round.** Ask for BLOCKERS vs NITS with frame numbers.
    It caught what builders' self-checks missed: stale test outputs and a fix that was correct but not visible in
    frame. Open-ended "score to 90" loops drifted instead of improving.

## When starting a 3D/video project, do this on turn 1

- Ask: may I download CC0 assets (Poly Haven, ambientCG)? Which audio licences are OK? Who signs in to paid or
  account-gated tools (TTS, Freesound, Sketchfab, Fab)? Write the login map (`references/11-sources-and-research.md`)
  and test each sign-in from the agent's own browser. What is the delivery length, aspect, size limit?
- Benchmark one frame per quality tier on the actual render machine; multiply by frame count; write the totals in
  the plan. Decide early whether delivery is "half res + upscale".
- Write `SPEC.md` (look, rules, module ownership, iteration budget), `timing.json`, and `RESUME.md` (append-only log
  with a standing-rules block) before any builder starts. Templates: `templates/`.
- Decide what is 2D post (titles, subtitles, end card, CTA) and what is 3D (diegetic signage only).

## Where to look

| Topic | File |
|---|---|
| Brief, rough cut, stakeholder feedback, story coherence, copy | `references/01-plan-and-story.md` |
| Timing file, events, retiming, extending shots | `references/02-timing-contract.md` |
| Code vs assets, scouts, physics, clipping, cameras, legibility | `references/03-scene-building.md` |
| Quality tiers, flicker, denoise, upscale, remote GPU, partial re-renders | `references/04-rendering.md` |
| TTS choices, alignment, fitting voice to picture, pickups, subtitles | `references/05-voice.md` |
| Music edits, foley, SFX sync, mix targets | `references/06-music-and-sfx.md` |
| Critics, deterministic checks, delivery checklist | `references/07-review-loops.md` |
| Agent splits, briefs, model per role, resume after interruptions | `references/08-multi-agent.md` |
| Where the tokens went and how to wait cheaply | `references/09-cost.md` |
| Failures and their root causes | `references/10-failures.md` |
| Asset and sound libraries, logins, online research, scouts | `references/11-sources-and-research.md` |

Helpers: `scripts/partial_rerender.py` (seed a new cut from the previous one with hardlinks, shifts and deletions),
`scripts/seam_check.py` (frame-to-frame change at seams vs neighbours).
