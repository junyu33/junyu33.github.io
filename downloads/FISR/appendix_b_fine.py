#!/usr/bin/env python3
"""Fine-grained FISR minimax search and plots.

Reuses EXACT input generation/semantics from appendix_a_coarse.py:
10_000 uniform-by-bit-pattern positive *normal* float32 values, seed 0xC0FFEE.
Enumerate EVERY magic number from 0x5f375000 through 0x5f377fff.
Compute max absolute relative error before and after one float32 Newton step.

Usage:
    python appendix_b_fine.py
"""

from pathlib import Path
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

START = 0x5F375000
END = 0x5F377FFF  # inclusive
SEED = 0xC0FFEE
N = 10_000


def evaluate():
    rng = np.random.default_rng(SEED)
    exponents = rng.integers(1, 255, size=N, dtype=np.uint32)
    fractions = rng.integers(0, 1 << 23, size=N, dtype=np.uint32)
    input_bits = (exponents << np.uint32(23)) | fractions
    inputs = input_bits.view(np.float32)
    reference = 1.0 / np.sqrt(inputs.astype(np.float64))
    shifted_bits = input_bits >> np.uint32(1)
    half_inputs = np.float32(inputs * np.float32(0.5))

    magics = np.arange(START, END + 1, dtype=np.uint32)
    err0 = np.empty(magics.size, dtype=np.float64)
    err1 = np.empty(magics.size, dtype=np.float64)
    worst0 = np.empty(magics.size, dtype=np.uint32)
    worst1 = np.empty(magics.size, dtype=np.uint32)

    for j, magic in enumerate(magics):
        y0 = np.uint32(magic - shifted_bits).view(np.float32)
        re0 = np.abs(y0.astype(np.float64) / reference - 1.0)
        wi0 = int(np.argmax(re0))
        worst0[j] = input_bits[wi0]
        err0[j] = re0[wi0] * 100

        # Match the source C evaluation order, rounding each operation to float32:
        # x2 = x * 0.5f
        # y1 = y0 * (1.5f - ((x2 * y0) * y0))
        t = np.float32(np.float32(half_inputs * y0) * y0)
        y1 = np.float32(y0 * np.float32(np.float32(1.5) - t))
        re1 = np.abs(y1.astype(np.float64) / reference - 1.0)
        wi1 = int(np.argmax(re1))
        worst1[j] = input_bits[wi1]
        err1[j] = re1[wi1] * 100

    return magics, err0, err1, worst0, worst1


def plot(magics, e0, e1, output: Path, which: int):
    fig, ax = plt.subplots(figsize=(11.5, 6))
    y = [e0, e1][which]
    best = int(np.argmin(y))
    ax.plot(magics, y, linewidth=1.1)
    ax.scatter([magics[best]], [y[best]], s=55, zorder=4)
    ax.annotate(f"0x{int(magics[best]):08x}\n{y[best]:.9f}%",
                (magics[best], y[best]), xytext=(18, 30),
                textcoords="offset points",
                arrowprops=dict(arrowstyle="->", lw=1.0),
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.86))
    ax.set_title(f"FISR fine search: {which} Newton iteration{'s' if which != 1 else ''}\n"
                 f"10,000 positive normal binary32 | seed 0xC0FFEE | stride = 1")
    ax.set_xlabel("Magic number")
    ax.set_ylabel("Sample maximum absolute relative error (%)")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"0x{int(v):08x}"))
    ax.tick_params(axis="x", rotation=30)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_both(magics, e0, e1, output: Path):
    fig, ax = plt.subplots(figsize=(11.5, 6))
    ax.plot(magics, e0, lw=1.3, label="0 Newton iterations")
    ax.plot(magics, e1, lw=1.3, label="1 Newton iteration")
    for k, y in [(0, e0), (1, e1)]:
        idx = int(np.argmin(y))
        ax.scatter([magics[idx]], [y[idx]], s=45, zorder=4)
        ax.annotate(f"0x{int(magics[idx]):08x}: {y[idx]:.6f}%",
                    (magics[idx], y[idx]), xytext=(8, 16 if k == 0 else -25),
                    textcoords="offset points", fontsize=9)
    ax.set_yscale("log")
    ax.set_title("FISR fine search: minimax error vs. magic number\n"
                 "10,000 positive normal binary32 | seed 0xC0FFEE | stride = 1")
    ax.set_xlabel("Magic number")
    ax.set_ylabel("Sample maximum absolute relative error (%) [log scale]")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"0x{int(v):08x}"))
    ax.tick_params(axis="x", rotation=30)
    ax.grid(alpha=0.3, which="both")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("."))
    args = parser.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    magics, e0, e1, worst0, worst1 = evaluate()
    idx0 = int(np.argmin(e0))
    idx1 = int(np.argmin(e1))
    print(f"Search: 0x{START:08x} .. 0x{END:08x} (inclusive), {len(magics)} values")
    for n, e, wi, worst in [(0, e0, idx0, worst0), (1, e1, idx1, worst1)]:
        tie_count = int(np.count_nonzero(e == e[wi]))
        print(f"{n} Newton: winner 0x{int(magics[wi]):08x}, "
              f"sample minimax = {e[wi]:.12f}%, "
              f"worst sampled input bits = 0x{int(worst[wi]):08x}, "
              f"ties = {tie_count}")
    csv = out / "fisr_minimax_fine.csv"
    with csv.open("w") as fp:
        fp.write("magic,error0_max_pct,error1_max_pct,worst_input0_bits,worst_input1_bits\n")
        for m, v0, v1, w0, w1 in zip(magics, e0, e1, worst0, worst1):
            fp.write(f"0x{int(m):08x},{v0:.12f},{v1:.12f},0x{int(w0):08x},0x{int(w1):08x}\n")
    plot(magics, e0, e1, out / "fisr_minimax_fine_0_newton.png", 0)
    plot(magics, e0, e1, out / "fisr_minimax_fine_1_newton.png", 1)
    plot_both(magics, e0, e1, out / "fisr_minimax_fine_comparison.png")
    print("Saved plots and CSV to", out)

if __name__ == "__main__":
    main()
