#!/usr/bin/env python3
"""Exhaustively validate seven FISR magic constants on all binary32 x in [1,4).

Python + NumPy equivalent of fisr_full_range_verify.c (0 or 1 Newton step).
The 2**24 input bit patterns span [0x3f800000, 0x407fffff].
Float32 intermediate rounding follows the C expression
    y1 = y0 * (1.5f - (x2 * y0 * y0))
with x2 = x * 0.5f. Floating-point contraction/reassociation is not used.
The real-number relative error is approximated to float64 precision as
    abs(y * sqrt(float64(x)) - 1).

To run:
    python -m pip install numpy
    python appendix_c_verify.py
Or:
    python appendix_c_verify.py --chunk-size 262144 --output results.csv
"""

import argparse
import csv
from pathlib import Path

import numpy as np

MAGICS = (
    0x5F3759DF,  # Quake III original
    0x5F375A71,  # 10,000-sample 1-Newton winner
    0x5F375A73,  # 10,000-sample 1-Newton tied winner
    0x5F375A86,  # Lomont 1-Newton candidate
    0x5F375A87,  # neighboring candidate
    0x5F37642E,  # 10,000-sample 0-Newton winner
    0x5F37642F,  # Lomont 0-Newton candidate
)

FIRST = 0x3F800000  # 1.0f
STOP = 0x40800000   # 4.0f, exclusive


def search(chunk_size: int):
    # For each candidate: worst error for 0/1 iterations, and input bit pattern.
    results = {
        magic: {0: (0.0, 0), 1: (0.0, 0)}
        for magic in MAGICS
    }
    for begin in range(FIRST, STOP, chunk_size):
        end = min(begin + chunk_size, STOP)
        bits = np.arange(begin, end, dtype=np.uint32)
        x = bits.view(np.float32)
        x2 = np.float32(x * np.float32(0.5))
        sqrt_x = np.sqrt(x.astype(np.float64))
        shifted = bits >> np.uint32(1)

        for magic in MAGICS:
            y0bits = np.uint32(magic) - shifted
            y0 = y0bits.view(np.float32)

            error0 = np.abs(y0.astype(np.float64) * sqrt_x - 1.0)
            i0 = int(np.argmax(error0))
            if float(error0[i0]) > results[magic][0][0]:
                results[magic][0] = (float(error0[i0]), int(bits[i0]))

            # Match C: y0 * (1.5f - ((x2 * y0) * y0)).
            product = np.float32(x2 * y0)
            product = np.float32(product * y0)
            correction = np.float32(np.float32(1.5) - product)
            y1 = np.float32(y0 * correction)

            error1 = np.abs(y1.astype(np.float64) * sqrt_x - 1.0)
            i1 = int(np.argmax(error1))
            if float(error1[i1]) > results[magic][1][0]:
                results[magic][1] = (float(error1[i1]), int(bits[i1]))

    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunk-size", type=int, default=1 << 18)
    parser.add_argument("--output", type=Path,
                        default=Path("fisr_full_range_results_python.csv"))
    args = parser.parse_args()
    if args.chunk_size <= 0:
        parser.error("--chunk-size must be positive")

    results = search(args.chunk_size)
    rows = []
    for magic in MAGICS:
        error0, bits0 = results[magic][0]
        error1, bits1 = results[magic][1]
        rows.append({
            "magic": f"0x{magic:08x}",
            "zero_newton_max_pct": f"{100 * error0:.12f}",
            "zero_newton_worst_bits": f"0x{bits0:08x}",
            "one_newton_max_pct": f"{100 * error1:.12f}",
            "one_newton_worst_bits": f"0x{bits1:08x}",
        })

    with args.output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Exhausted {STOP - FIRST:,} binary32 inputs in [1,4)")
    for row in rows:
        print("{magic}: 0-step = {zero_newton_max_pct}% at "
              "{zero_newton_worst_bits}; 1-step = {one_newton_max_pct}% at "
              "{one_newton_worst_bits}".format(**row))
    print(f"Saved CSV: {args.output}")


if __name__ == "__main__":
    main()
