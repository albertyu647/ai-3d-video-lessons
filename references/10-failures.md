# Failures and root causes

| Symptom | Root cause | Fix / prevention |
|---|---|---|
| Laptop swapping after renders moved to a GPU PC | Agents called the local Blender binary directly; helper scripts lived outside the synced folder | One wrapper for every Blender call; helper scripts only in the project's `tools/`; say it in the spec |
| 4-7 Blender jobs fighting over an 8 GB GPU | No queue | Slot queue sized to VRAM (2), self-freeing locks |
| Script errors reported as success | Blender exits 0 when the Python script throws | `--python-exit-code 1`; also verify frame counts and blank frames |
| Full-cut build crashed (undefined material) | A fixer was stopped mid-edit | Build smoke test after any interrupted agent; atomic edits |
| Renders kept spawning after a pause | A background helper outlived its workflow | Kill by parent process on every machine; job supervisor; "no background render loops" in prompts |
| Workflow could not resume | Journal not on disk after an account switch | State on disk; continuation scripts for the missing phases |
| An hour of finished work almost redone | RESUME note written when the stop was requested, not when it happened | Check file timestamps; write the note after the stop |
| 64 assets downloaded, 2 used | Gather and integrate were separate; integrators were interrupted | Couple them; report usage counts |
| Two cuts denoised on the CPU | GPU denoising is off by default in Cycles | Benchmark agent; `denoising_use_gpu = True` (-20%) |
| Bloom "assumed" but never applied | Spec and code comments assumed a compositor step that didn't exist | Audit "will be handled later" claims against rendered frames |
| Arm became a ghost after adding motion blur | 16 degrees per frame | Speed ceiling ~10 deg/frame; spread the move |
| ~60 keys left on the old clock after a retime | Frame literals in scene code | `event + offset` everywhere |
| Table parts flickered and wobbled | Rigid bodies never fully settle | Post-bake rest hold, released on real contact |
| Camera "hiccup" at a cut | Per-camera noise with separate seeds jumped 8.5 px | Share noise across continuity cuts, fade to 0 at match cuts |
| Highlights popping in a locked shot | Camera noise drift slid the image under a static sample pattern | Zero drift on holds |
| Static end shot shimmered | Detail thinner than a pixel at 50% res | Render one converged frame and hold it |
| "Random pan" | Two leftover camera keys | Remove; preserve the boundary tangent so later frames stay identical |
| Burned-in title on top of a subtitle | No overlay collision check | Lint the overlay timeline |
| End-card line drawn over a moving object | Text timed to the voice, not to the picture | Compute the first clear frame from pixels; disclose the lag; no drop-shadow patch |
| One clank 1.5x louder than the rest | Previous sample's tail contained another hit | "Active cues at time t" debug view; trim samples |
| Pickup take held an extra changed line | The human edited another line too | ASR + diff every delivered take |
| A critic's blockers were stale test outputs | Test comp built over old frames; test clip rendered before the patch | Compare output vs patch timestamps; delete superseded tests |
| A correct fix that viewers couldn't see | The action happened at the frame edge and off-screen | Visibility probe; fresh image-only critic |
| Render chain killed after 9 min | Started with a shot still under review | Queue by confidence: unchanged/approved shots first |
| `ffmpeg` in a shell loop produced garbage start frames | ffmpeg ate the loop's stdin | `-nostdin` |
| Error scans tripped on every log | A harmless GPU-vendor init warning | Whitelist known-harmless warnings |
| Remote command failed on Windows | PowerShell doesn't accept `&&` | Write commands for the remote shell |
| Research agent's alarming claim ("never uses the fast GPU path") | It read the code but not the runtime shim | One-command verification before acting |
