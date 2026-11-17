# <cut_vN> brief: shared context for every agent this round

<One paragraph: what the film is, tool versions, project root.> Read `SPEC.md` (the last "cut_vN changes" sections
win) and `timing.json` (shots, events in seconds, `vo[*].words`; frame = round(t*fps)+1).

## Film facts
- Length / frames / fps. Shot ranges and which module owns each shot.
- Last delivered cut: `<renders/cut_vN-1/frames>`, `<out/cut_vN-1/...>`. Reference only, never write there.
- Timing changes already made this round (do NOT edit timing.json; report new event times instead).
- Voice-over status (e.g. LOCKED) and a word -> frame table for the words picture must land on.

## Feedback driving this round (verbatim, numbered)
1. ...
2. ...

## Rules (binding)
- All renders go through `<render wrapper>`; never run the local binary.
- Anything that takes minutes: `job submit --name <n> --expect N -- <cmd>`, then `job wait <id>` repeatedly.
  No sleep loops, no long foreground runs.
- Only edit the files you own (listed in your prompt). Need a change elsewhere? Put it in your report.
- Test output only under `renders/dev/<round>_<you>/`.
- Never `rm` broad globs; delete only files you created.
- At most 2 fix rounds of your own. Report honestly what is and isn't verified.
- Keep shot boundary poses and velocities identical to the last cut unless told otherwise.
- Start with proxies behind one swap function if an asset scout is running; don't wait for it.

## Commands
- Build + stills: `<...>`
- Clip test of a range: `<...>`
- Contact sheet: `contact-sheet DIR -o out.jpg`
- Clip/interpenetration check: `<...>`

## Assets
Allowed sources and licences. Never buy, never create accounts, never sign in.

## Final report (your last message, <= 25 lines)
- Files changed and what
- **Exact frame ranges that change on screen** (the lead re-renders only these)
- Event times to add to timing.json (seconds)
- Deviations from the plan, each with its re-render cost
- Paths of verification stills, sheets, clips
- What you could not verify
