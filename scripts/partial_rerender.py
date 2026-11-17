#!/usr/bin/env python3
"""Seed a new cut's frame folder from the previous cut, so only changed frames need rendering.

Frames are named f0001.png, f0002.png, ... (global frame numbers). Unchanged frames are hardlinked (no extra disk
space, the old cut is never modified). Frames after an inserted span are renumbered by an offset. Changed ranges are
simply left out, so a resumable renderer that skips existing frames renders exactly those.

  python3 partial_rerender.py OLD_DIR NEW_DIR --last OLD_LAST_FRAME \
      [--rerender 1-152 --rerender 481-708] [--shift-from 1037 --shift 43] [--pattern f{:04d}.png] [--dry-run]

Example: a shot ending at 1036 grows by 43 frames, so old 1037-1146 become new 1080-1189 and new 1037-1079 are left
for rendering together with the --rerender ranges. Pad ranges by ~1 frame for vector motion blur and a few frames
for temporal denoise. Run it once per frame folder (raw, denoised, upscaled caches).
"""
import argparse, os, sys


def parse_range(s):
    a, _, b = s.partition("-")
    a = int(a); b = int(b or a)
    if b < a:
        raise argparse.ArgumentTypeError(f"bad range {s}")
    return a, b


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("old_dir"); ap.add_argument("new_dir")
    ap.add_argument("--last", type=int, required=True, help="last frame number of the old cut")
    ap.add_argument("--first", type=int, default=1)
    ap.add_argument("--rerender", type=parse_range, action="append", default=[],
                    help="NEW-cut frame range to leave out (repeatable), e.g. 481-708")
    ap.add_argument("--shift-from", type=int, help="first OLD frame that moves")
    ap.add_argument("--shift", type=int, default=0, help="frames to add to every old frame >= --shift-from")
    ap.add_argument("--pattern", default="f{:04d}.png")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)

    def skip(f):
        return any(lo <= f <= hi for lo, hi in a.rerender)

    os.makedirs(a.new_dir, exist_ok=True)
    linked = skipped = missing = exists = 0
    for old in range(a.first, a.last + 1):
        new = old + a.shift if a.shift_from is not None and old >= a.shift_from else old
        if skip(new):
            skipped += 1; continue
        src = os.path.join(a.old_dir, a.pattern.format(old))
        dst = os.path.join(a.new_dir, a.pattern.format(new))
        if not os.path.exists(src):
            missing += 1; continue
        if os.path.exists(dst):
            exists += 1; continue
        if not a.dry_run:
            os.link(src, dst)
        linked += 1
    gap = f"{a.shift_from}-{a.shift_from + a.shift - 1}" if a.shift_from is not None and a.shift > 0 else "none"
    print(f"linked {linked}, left for rendering {skipped} (+ inserted span {gap}), "
          f"already present {exists}, missing in old {missing}{' [dry run]' if a.dry_run else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
