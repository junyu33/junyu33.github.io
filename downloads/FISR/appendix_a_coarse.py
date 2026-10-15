#!/usr/bin/env python3
"""FISR coarse search plot on a LINEAR y-axis (same dataset as logarithmic plot).

2048 magic constants: 0x5f000000 to 0x5f7ff000 inclusive, step 0x1000.
10,000 random positive normal binary32 inputs, seed 0xC0FFEE.
Minimax is the largest absolute relative error in the sampled inputs.
"""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

SEED = 0xC0FFEE
N = 10_000
STEP = 0x1000
BASE = 0x5F000000

rng = np.random.default_rng(SEED)
exp = rng.integers(1, 255, size=N, dtype=np.uint32)
frac = rng.integers(0, 1 << 23, size=N, dtype=np.uint32)
xbits = (exp << np.uint32(23)) | frac
x = xbits.view(np.float32)
truth = 1.0 / np.sqrt(x.astype(np.float64))
shifted = xbits >> np.uint32(1)
xhalf = np.float32(x * np.float32(0.5))

mantissas = np.arange(0, 1 << 23, STEP, dtype=np.uint32)
err0 = np.empty(len(mantissas), dtype=np.float64)
err1 = np.empty(len(mantissas), dtype=np.float64)

for j, m in enumerate(mantissas):
    magic = np.uint32(BASE) + m
    y0 = np.uint32(magic - shifted).view(np.float32)
    err0[j] = 100.0 * np.max(np.abs(y0.astype(np.float64) / truth - 1.0))
    t = np.float32(np.float32(xhalf * y0) * y0)
    y1 = np.float32(y0 * np.float32(np.float32(1.5) - t))
    err1[j] = 100.0 * np.max(np.abs(y1.astype(np.float64) / truth - 1.0))

best0 = int(np.argmin(err0))
best1 = int(np.argmin(err1))
fig, ax = plt.subplots(figsize=(11.5, 6.5))
ax.plot(mantissas, err0, label="0 Newton iterations", lw=2)
ax.plot(mantissas, err1, label="1 Newton iteration", lw=2)
ax.set_xlabel("Magic number mantissa M  (magic = 0x5f000000 + M)")
ax.set_ylabel("Sample maximum absolute relative error (%)")
ax.set_title("FISR: coarse minimax search (linear scale)\n"
             "10,000 positive normal binary32 | step 0x1000 | seed 0xC0FFEE")
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"0x{int(v):06x}"))
ax.tick_params(axis="x", rotation=30)
ax.grid(alpha=0.25)
ax.legend()
fig.tight_layout()

out = Path(__file__).with_suffix(".png")
fig.savefig(out, dpi=180, bbox_inches="tight")
plt.close(fig)

for n, idx, values in [(0, best0, err0), (1, best1, err1)]:
    print(f"{n} Newton: magic=0x{BASE + int(mantissas[idx]):08x}, error={values[idx]:.6f}%")
print(f"Image saved to {out}")
