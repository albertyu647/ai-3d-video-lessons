# Voice-over

## Engines tried

| Engine | Use | Notes |
|---|---|---|
| A local TTS CLI with word timestamps | Cuts 1-4 | Deterministic (same seed = same audio), returned word times that drove timing and subtitles |
| Qwen3-TTS 1.7B VoiceDesign (MLX) | Auditions | Cleanest audio, but invents a new voice on every call, so the whole script must be one call (13.6 GB peak on a 16 GB Mac). Misread brand names in 1 of 6 probes |
| OmniVoice | Auditions | Clones a voice from a reference clip, so one voice across lines by construction |
| Ming TTS 0.5B | Auditions | Whole-script and cloning modes failed on Apple MPS; usable one line per call, takes picked by speaker-embedding agreement |
| ElevenLabs (library voice) | Final, cuts 5-8 | The director generated takes himself (account-gated); whole-script take, then pickups |
| parakeet-tdt-0.6b (ASR) | Checking takes | Word error vs the script, word times |
| Qwen3-ForcedAligner 0.6B (mlx-audio) | Alignment | Word-level times for imported takes; these drive subtitles, placement and camera moves |
| CAM++ speaker embeddings | Take selection | Keep takes whose voice matches |

## The agent can't hear

Nine auditions (3 models x 3 voices) were ranked from transcripts and audio metrics; the agent never listened, and
said so. The sound agent's report later said "I did not listen to it, only measured it". Treat audio rankings from a
model as a shortlist. Deliver auditions **as short films over the current picture through the real mixer** with an
index page, so the human judges in context.

## Lock the speaker, then vary emotion

Per-line emotion prompts make a prompt-designed narrator drift. Either generate the whole script in one call under
one description, clone from a reference clip, or generate several takes per line and keep those whose speaker
embedding matches. Keep emotion tags restrained (1-2 per line; heavy ones "tip into infomercial").

## Fitting voice to picture

**Don't speed up the voice.** The first placement of a pro take used pitch-preserving tempo changes of 4-7% on four
stretches. The director heard it immediately. The method that stuck:

1. Import the whole take, force-align it against the script, cut each line at the quietest point between lines,
   loudness-match (-20 LUFS), trim to 50 ms before the first word and 150 ms after the last.
2. Anchor each **sentence** to a picture event: `ANCHORS = {(line, sentence): film_time}`.
3. If a run of sentences would overrun the next anchor, first cap the gaps between sentences (0.22-0.55 s), then the
   pauses **inside** sentences, with caps by punctuation (ellipsis 0.4-0.6 s, full stop 0.3-0.5, comma 0.15-0.3,
   other 0.08-0.2). If it still overruns, the next anchor moves later.
4. Report drift per line as a dry run before writing anything.

Result: zero tempo change, max drift 0.42 s, every line on or just after its cue. At natural speed with no fitting
the voice would have slid 2.8 s behind the picture by mid-film.

Options, best first: re-generate with the TTS speed setting slightly up (~1.06), trim pauses (free), retime the
picture (a re-render, rarely worth it).

**Write to the slot.** Before changing a line, count words against its slot (18 words in a 6.1 s slot; 26 words
in 9.5 s at a brisk pace) and say which phrase to cut first if a take runs long. The director's constraint was
"don't change the pacing, that would need a re-render".

## Pickups

"Can we just do the few lines that need to be replaced instead of the entire thing?" Yes:

- Generate all changed lines together in one generation so they match each other.
- Import with a `--lines` option; keep the other lines from the old take.
- Compare loudness, spectral brightness and pitch of old vs new lines; regenerate one only if it stands out.
- **Run ASR on every delivered take and diff it against the script.** The pickup take held 4 changed lines, not the
  3 agreed: the director had also rewritten the closing line. Only the diff caught it.
- ASR mishears brand names. Ask the human to listen to them rather than assuming the voice got it wrong.

## Subtitles

Generate them from the placed voice's word times, in post, never in 3D. Chunk by sentence, split chunks over ~52
characters near the middle, prefer breaking after a colon over a comma, never split a two-word term, show from first
word -0.06 s to last word end +0.12 s. When a line is both spoken and shown as on-screen text (an end card), don't
also subtitle it.

Keep one canonical script file with start times and slot lengths. The text existed in three places at one point, one
with a stale line.
