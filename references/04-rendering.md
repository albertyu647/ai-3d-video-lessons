# Rendering: tiers, flicker, remote GPU, partial re-renders

## Benchmark first, let the numbers pick the tier

Measured (Blender 5.2 Cycles, 1920x804 picture):

| Setup | s/frame |
|---|---|
| Apple M3 laptop, Metal, 64 spp, full res | ~11 |
| RTX 3060 Ti, OptiX, "final" tier, full res | ~163 (≈ 52 h for 1,146 frames, so never used) |
| RTX 3060 Ti, draft tier, 50% | 4.4-6.3 (3.8 with GPU denoise) |
| RTX 3060 Ti, film tier (64-96 spp, adaptive 0.01), 50% | 5.4-10 (a 1,146-frame cut in ~2.5-3 h) |

The PC rendered ~3.5x faster than the M3 but built scenes ~2x slower (single-threaded Python). On day 1, multiply
frames x s/frame per tier and write the totals into the plan. "Deliverable = 50% render + upscale" should be a plan
decision, not something discovered under deadline.

## Flicker and speed: test advice, don't adopt it

A benchmark agent rendered a fixed 36-frame clip and measured time, frame-to-frame flicker on locked shots, moving
residual (using Blender's own Vector pass to warp the previous frame), and error against a 1024-spp reference.
Variants were interleaved in one process (warm-up + 5 timed frames per block, alternating) because the GPU was shared.

| Advice | Result |
|---|---|
| Animate the seed per frame (manual and forums recommend it) | **Worse.** Locked shot went from 0 flicker to visible shimmer; moving residual +60% |
| OptiX temporal denoiser (`denoise_animation`) | Three workarounds to run headless, no flicker gain, lower quality. Rejected |
| Fewer bounces, 2048 texture limit | 0% faster, ~240 MB VRAM saved. Rejected |
| **GPU denoising (`denoising_use_gpu`, off by default)** | **20% faster**, output within 1/255. Two whole cuts had denoised on the CPU |
| Film tier vs draft | 16% lower error, +57% time |
| **Per-shot ffmpeg `atadenoise=s=9` in post** | **~30% less residual flicker**, no added error, 5x less edge softening than `hqdn3d` |

Defaults that held: static seed, OIDN with albedo+normal, indirect clamp 4, glossy filter 1.0, caustics off, no
volumetrics (fake light shafts with emissive cards), emission ≤ ~15 with bloom for glow, decals offset ≥ 1 mm, AgX.

Verify alarming research claims before acting: "the PC never uses OptiX" was false (a shim switched it).

## The image chain order

```
render (linear HDR) -> bloom + vector blur in the compositor (need HDR) -> 8-bit PNG
-> temporal NR per shot at render res (never across a cut) -> Lanczos upscale + light unsharp
-> chromatic aberration, vignette, grain -> letterbox + text -> x264
```

Grain before NR gets denoised away; grain before upscale becomes blobs; CA before unsharp gets sharpened fringes.
Frame-by-frame AI super-resolution adds detail that differs per frame and shimmers; plain Lanczos was better.
In ffmpeg shell loops pass `-nostdin`, or ffmpeg eats the loop's input.

## Cheap realism, and its side effects

Bloom (low strength), vector motion blur (shutter 0.2; 0.4 smeared pans), subtle camera noise (≤ 0.1 degrees), luma
grain (~2/255, new seed per frame), a 10-15% vignette and ≤ 1 px radial CA each passed A/B tests at near-zero render
cost. Then two of them caused the next round's defects:

- **Camera noise with a separate seed per camera jumped 8.5 px at a cut**, which the director saw as a "camera
  hiccup". Fix: continuity cuts reuse the previous camera's noise; match cuts fade it to exactly 0 on both frames.
- **The same drift during a locked hold slid the image under the fixed sampling pattern**, so highlights popped. With
  the drift zeroed and parts held still, the frames became pixel-identical. No sample or material change needed.

A/B global effects across every cut and every locked hold, not only on a sample clip.

## Static tails: hold one converged frame

A static end shot flickered along vent fins thinner than a pixel at 50% resolution. A darker, rougher material only
reduced it 10-30%. What worked: probe for the last frame on which anything visible changes (transforms,
constraints, light energy, keyed properties, visibility, lens), render that frame once at 1024 spp, copy it over every
remaining frame, give the lead-in frames 512 spp so the step into the hold looks normal, and keep light film grain on
top so it doesn't look frozen. Probe first: any late animation dies in a hold.

## Remote GPU

- **One entry point for every Blender call** (`bl` wrapper, same arguments as the binary). After the move to the PC,
  agents still called the laptop's Blender directly and pushed it into swap. Say it in the spec and guard it.
- **The wrapper:** push files changed since a stamp, run Blender over SSH, stream output, pull back files written
  after the start time, return Blender's exit code. Mirror the project at the same absolute path on the remote drive.
  Helper scripts must live in the synced project, not /tmp. Overhead ~5-10 s per call, so batch stills.
- **Slot queue sized to VRAM:** 4-7 jobs on an 8 GB card was too many; a 2-slot `flock` queue whose slots free
  themselves when a holder dies fixed it.
- **Blender exits 0 when the Python script throws** unless run with `--python-exit-code 1`.
- **Known-harmless warnings** (an AMD HIP init warning on an NVIDIA box) appear in every log; whitelist them in error
  scans.
- Windows remote shells: PowerShell does not accept `&&`; write remote commands for the remote shell.

## Detached and resumable

- Renders write `f####.png` with global frame numbers and **skip frames that exist**, in chunks of 40-60. An
  interrupted run resumes with the same command; this saved 326 frames after a build crash.
- When the controlling laptop had to leave the network mid-render (516 of 1,146 frames), the remaining chunks were
  restarted **as detached processes on the GPU host**, one per slot, each writing a progress log and a done-flag.
  Losses: 2 half-rendered frames. Frames were pulled back later with a missing-frame check, then post ran.
- Don't move cheap post to the GPU box: denoise ~7 s, upscale ~2 min, compose ~3 min, encode ~1 min on the laptop
  against hours of rendering. The levers are fewer frames and less time per frame.

## Partial re-renders

- Seed the new cut's frame folder with **hardlinks** to the previous cut, delete only changed ranges (this unlinks
  the new copies and leaves the old cut intact), renumber shifted shots. `scripts/partial_rerender.py` does this.
- Cut history: v5 re-rendered 0 frames (new voice and end card, 4 minutes), v6 280 of 1,146, v8 485 of 1,189.
- Every agent's report must state **exact changed frame ranges**. Pad by ±1 frame for vector motion blur and ~5 frames
  for temporal denoise; confirm with a "first frame that differs" script.
- Keep boundary poses and velocities identical to the previous cut so neighbouring shots don't need re-rendering.
- **Measure every seam** where new frames meet reused ones (`scripts/seam_check.py`). The camera-hiccup fix was
  verified this way (step at the cut 0.13 vs the earlier jump).
- **Order render queues by confidence.** Unchanged or approved shots first, shots under review last. A chain started
  with a shot the critic then blocked and had to be killed after 9 minutes. Keep both slots busy from opposite ends
  of the remaining ranges and refill an idle slot at once.
- Render untouched sets while a fixer works on another set; chain the rest automatically when the fix passes.
