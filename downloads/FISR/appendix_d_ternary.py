#!/usr/bin/env python3
"""FISR binary64 minimax magic-number search by heuristic integer ternary search.

Run:
    python appendix_d_ternary.py
    python appendix_d_ternary.py --samples 10000 --seed 0xC0FFEE --bracket-width 512

- IEEE 754 binary64: bias 1023, 52 fraction bits; fixed magic exponent 1534.
- Search all *possible magic mantissas* [0, 2**52 - 1] using integer ternary search,
  then exhaustively check the surviving bracket (no extra margin).
- For each candidate, minimax is tested against the SAME fixed set of randomly
  sampled positive NORMAL binary64 bit patterns (not all 2**63 normal inputs).
- Separately minimize max(abs(relative error)) for 0 and 1 Newton iteration.
- Newton operations use float64; error measurement uses NumPy longdouble
  to distinguish nearby magic constants more accurately. On some platforms
  longdouble may have the same precision as float64; check the printed eps.

This is an empirical *heuristic* optimization. It does not prove global
optimality across all magic values or all positive normal double inputs.
"""

import argparse
import csv
from functools import lru_cache
from pathlib import Path
import time

import numpy as np

MAGIC_BASE = 0x5FE0000000000000
TAIL_MAX = (1 << 52) - 1


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--samples", type=int, default=10_000)
    ap.add_argument("--seed", type=lambda s: int(s, 0), default=0xC0FFEE)
    ap.add_argument("--bracket-width", type=int, default=512,
                    help="stop integer ternary when bracket width <= this many values")
    ap.add_argument("--output", type=Path, default=Path("fisr_binary64_ternary_results.csv"))
    args = ap.parse_args()
    if args.samples < 1 or args.bracket_width < 3:
        ap.error("samples must be positive; bracket-width >= 3")

    rng = np.random.default_rng(args.seed)
    exp = rng.integers(1, 2047, size=args.samples, dtype=np.uint64)  # 1 ... 2046
    frac = rng.integers(0, 1 << 52, size=args.samples, dtype=np.uint64)
    xbits = (exp << np.uint64(52)) | frac
    x = xbits.view(np.float64)
    xhalf = np.float64(0.5) * x
    half_bits = xbits >> np.uint64(1)

    # Compute the reference just once. float64 accuracy is insufficient to
    # evaluate errors at 1e-16 sensitivity for neighboring candidate magics.
    sqrt_x = np.sqrt(x.astype(np.longdouble))
    one = np.longdouble(1.0)

    @lru_cache(maxsize=None)
    def evaluate(tail: int) -> tuple[np.longdouble, np.longdouble]:
        if not 0 <= tail <= TAIL_MAX:
            raise ValueError(f"magic mantissa out of range: {tail}")
        magic = np.uint64(MAGIC_BASE | tail)
        y0 = (magic - half_bits).view(np.float64)
        err0 = np.max(np.abs(y0.astype(np.longdouble) * sqrt_x - one))

        # Exact evaluation order of Quake III's double-adapted Newton step:
        # y1 = y0 * (1.5 - ((xhalf * y0) * y0))
        correction = np.float64(1.5) - ((xhalf * y0) * y0)
        y1 = y0 * correction
        err1 = np.max(np.abs(y1.astype(np.longdouble) * sqrt_x - one))
        return err0, err1

    def ternary(which: int) -> tuple[int, int, int]:
        left, right = 0, TAIL_MAX
        steps = 0
        while right - left > args.bracket_width:
            third = (right - left) // 3
            m1 = left + third
            m2 = right - third
            e1 = evaluate(m1)[which]
            e2 = evaluate(m2)[which]
            if e1 <= e2:
                right = m2
            else:
                left = m1
            steps += 1
        return left, right, steps

    start = time.perf_counter()
    outcomes = []
    print(f"Samples: {args.samples}; seed: {args.seed:#x}")
    print(f"Input: positive normal binary64; max mantissa: 0x{TAIL_MAX:013x}")
    print(f"Reference precision np.longdouble eps={np.finfo(np.longdouble).eps:.4g}")
    for which in (0, 1):
        left, right, steps = ternary(which)
        low, high = left, right
        best_e = np.longdouble(np.inf)
        best_tail = low
        n_ties = 0
        # Exhaustively check ONLY the surviving ternary bracket, step 1.
        for tail in range(low, high + 1):
            e = evaluate(tail)[which]
            if e < best_e:
                best_e = e
                best_tail = tail
                n_ties = 1
            elif e == best_e:
                n_ties += 1
        best_magic = MAGIC_BASE | best_tail
        other_error = evaluate(best_tail)[1 - which]
        outcomes.append((which, best_magic, best_tail, best_e,
                         other_error, n_ties, steps, low, high))
        print(f"{which} Newton: steps={steps}, local=[0x{low:013x}, 0x{high:013x}], "
              f"tested={high - low + 1}")
        print(f"    best magic=0x{best_magic:016x}, minimax={float(100*best_e):.12f}% "
              f"({n_ties} tied in local interval)")

    with args.output.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["iterations", "magic_hex", "mantissa_hex", "minimax_pct",
                         "other_iterations_minimax_pct", "local_tie_count",
                         "ternary_steps", "local_low_hex", "local_high_hex",
                         "sample_count", "seed_hex"])
        for n, m, t, e, eother, ties, steps, lo, hi in outcomes:
            writer.writerow([n, f"0x{m:016x}", f"0x{t:013x}",
                             np.format_float_positional(100*e, precision=17),
                             np.format_float_positional(100*eother, precision=17),
                             ties, steps, f"0x{lo:013x}", f"0x{hi:013x}",
                             args.samples, hex(args.seed)])
    print(f"Saved: {args.output}")
    print(f"Total candidate evaluations (shared cache): {evaluate.cache_info().misses}")
    print(f"Elapsed: {time.perf_counter() - start:.2f} s")


if __name__ == "__main__":
    main()
