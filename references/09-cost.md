# Where the tokens went

All figures are estimates at API list prices, computed from the session transcripts. Use the percentages to rank
causes.

## The first session: $964 over 8,481 calls

| By token type | Share |
|---|---|
| Cache writes (94M tokens) | 49% |
| Cache reads (1.5B tokens) | 31% |
| Output (9.4M tokens) | 20% |

| By role | Share |
|---|---|
| Fixers | 40% |
| Builders | 31% |
| Integrators | 10% |
| Critics | 7% |
| Main thread | 5% |

- 99.2% on the strongest model.
- Median context per call ~178k tokens (p90 312k, max 569k).
- 2,987 images returned to agents cost ~$39, **4%**. Not the problem.
- By activity: reading code, specs and logs 21%; looking at renders 21%; waiting and polling 13%; measuring pixels 10%;
  launching renders 8%. Actually authoring the film (modelling, materials, animation, lighting) was ~16%.
- The three open-ended build/critic loops cost ~$650 (68%) and produced no film the director could watch.

## The biggest single waste: waiting inside the agent

**$326 (34% of the session) was cache rewrites after the agent sat idle more than 5 minutes.** Subagent prompt caches
live 5 minutes; the main thread's live 1 hour. Agents started a render and then waited in their own context:

- half the idle gaps were foreground sleep/poll loops (`for i in $(seq 1 55); do ...; sleep 10`)
- 42% were renders run in the foreground with Bash timeouts up to 10-30 minutes (in 137 of 143 cases the agent set a
  timeout over 5 minutes, so it *knew* it would wait)

Each expiry re-wrote ~180k tokens at 1.25x the input price, about $1 each.

## The fix: detached jobs, bounded waits, hooks

- **`job submit`** starts a detached supervisor with a heartbeat, retries transient SSH failures once, kills stalls,
  verifies output (frame count vs expected, zero-byte files, blank-frame outliers), adds `--python-exit-code 1` for
  Blender, and counts Blender's `Saved:` lines for progress and ETA. State lives in files, so any later agent or
  session can pick it up.
- **`job wait ID`** blocks at most 240 s and returns an exit code (0 done, 1 failed, 2 stalled, 3 lost, 4 timeout,
  5 killed, 10 still running). Agents call it again while the job runs, so the cache stays warm.
- **Main thread:** a background shell loop (`while job wait ID; [ $? -eq 10 ]; do :; done`) costs zero tokens and
  wakes the session when the job ends. This replaced an hourly cron watchdog that kept waking a huge context.
- **Hooks** block the patterns in subagents: a sleep over 240 s, unbounded polling loops, `tail -f`, foreground
  commands with timeouts over 5 minutes, more than 6 short sleeps in 10 minutes; and a lint on workflow scripts
  requires an explicit model per agent and bounded loops. Escape hatches are logged.

**Waiting math** (150k-token context, strongest-model list prices): one `job wait` every 4 min ≈ $0.03, about $0.45 per
hour; one cache rewrite ≈ $0.75. Polling under the cache lifetime beats letting it expire for waits up to ~100
minutes. Polling every 30 s is as bad as expiring. A small-model waiter with ~20k context waits for about a cent an
hour.

**Validate guards on real history.** The idle-wait hook was replayed against the commands that preceded each of the
336 real idle gaps: it would have blocked 313 (93%), an estimated ~30% saving. The 23 it missed were long model turns,
not waits.

## Before and after

| Period | Est. cost | Idle cache rewrites | Share of total |
|---|---|---|---|
| First session, before hooks | $862 | $316 | **37%** |
| Same session after hooks (two cut workflows) | $102 | $10 | 10% |
| Later session: four feedback rounds, cuts 4-8 | $98 | $10 | 10% (3% inside subagents) |

Later work was also smaller fix passes, so compare the idle share, not the dollar totals. In the later session 74% of
spend was inside subagents; each critic cost $1.4-2 and the asset scout $2.

## Other costs worth cutting

- **Per-agent fixed overhead.** Each workflow agent started at ~57-60k tokens of tool definitions, skill lists and
  system prompt against a ~1.6k-token task, re-read on ~6,800 calls (~13% of the bill). Disable tools render agents
  never use and hide irrelevant skills per project before a big fan-out.
- **Huge contexts.** Small modules, outlines, grep instead of whole-file reads, state files instead of transcripts,
  fresh agents instead of long-lived fixers.
- **Fix rounds.** Cap at 1-2; sign off a look (one approved still per set) before polishing.
- **Model choice.** Mechanical roles on a cheaper model would have cut build and fix spend an estimated 30-40%.
- **Physical-action builds** were the cost sink of the last round: the hoist/physics builder cost $24 of $98, half of
  it on a framing problem a "is the action in frame?" probe would have caught.
- **Interruptions:** restarted agents cost an extra ~16% re-orienting.

## Red herrings

- **Images.** "2,700 render images in context" looked like a top cause; measured, they were 4%. An image-cap hook was
  built and removed the same day because it also blocked the human's normal use. Price each cause before building a
  guard.
- **The app's cost counter vs a quick estimate.** A first estimate with assumed prices said ~$1,400 and blamed the
  counter; at real prices it matched the counter (~$860). State your price assumptions.
- **A global 1-hour subagent cache.** It would have saved ~24% on the render-heavy session but makes every subagent
  cache write 2x instead of 1.25x; set it per project for render-heavy work, not globally.

## What made late rounds cheap

Not a cheaper model: architecture. Text in post, voice placed by anchors, subtitles from the voice, partial
re-renders, and agents that report changed frame ranges. One round shipped in 9 minutes with no render; another
cost ~$5 of agents and 51 minutes end to end.
