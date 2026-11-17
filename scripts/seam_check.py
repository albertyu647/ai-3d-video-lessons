#!/usr/bin/env python3
"""Measure the frame-to-frame change at seams (where re-rendered frames meet reused ones, or at cuts that should
match) and compare it with the neighbouring steps. A seam step far above its neighbours is a visible jump.

  python3 seam_check.py FRAME_DIR 152 708 1079 [--pattern f{:04d}.png] [--window 4] [--ratio 2.5] [--crop x,y,w,h]

For each seam S it reports step(S -> S+1) = mean |luma difference| (0-1) and the median of the steps in the
`window` frames on each side. Exit code 1 if any seam step exceeds ratio x the neighbour median (and 0.004 absolute).
Real scene cuts are expected to jump; use this on seams that should be continuous.
"""
import argparse, os, sys
import numpy as np
from PIL import Image


def load(d, pat, f, crop):
    im = Image.open(os.path.join(d, pat.format(f))).convert("L")
    if crop:
        x, y, w, h = crop
        im = im.crop((x, y, x + w, y + h))
    return np.asarray(im, dtype=np.float32) / 255.0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("dir"); ap.add_argument("seams", type=int, nargs="+", help="last frame before each seam")
    ap.add_argument("--pattern", default="f{:04d}.png")
    ap.add_argument("--window", type=int, default=4)
    ap.add_argument("--ratio", type=float, default=2.5)
    ap.add_argument("--crop", type=lambda s: tuple(int(v) for v in s.split(",")))
    a = ap.parse_args(argv)

    cache = {}
    def fr(f):
        if f not in cache:
            p = os.path.join(a.dir, a.pattern.format(f))
            cache[f] = load(a.dir, a.pattern, f, a.crop) if os.path.exists(p) else None
        return cache[f]

    def step(f):
        x, y = fr(f), fr(f + 1)
        return None if x is None or y is None else float(np.mean(np.abs(y - x)))

    bad = 0
    for s in a.seams:
        st = step(s)
        nb = [v for k in range(1, a.window + 1) for v in (step(s - k), step(s + k)) if v is not None]
        if st is None or not nb:
            print(f"seam {s}->{s + 1}: frames missing"); bad += 1; continue
        med = float(np.median(nb))
        flag = st > a.ratio * med and st > 0.004
        bad += flag
        print(f"seam {s}->{s + 1}: step {st:.4f}  neighbours median {med:.4f}  x{st / max(med, 1e-6):.1f}"
              f"{'  <-- JUMP' if flag else ''}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
