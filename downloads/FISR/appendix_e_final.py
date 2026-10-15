#!/usr/bin/env python3
"""Appendix E: FISR binary64 minimax with three 2**24-input datasets.

One self-contained reproducible workflow (requires numpy, matplotlib):
    python appendix_e_final.py --stage all --out-dir .

To regenerate the COMPLETE six-column magic summary and the two 4x3 figures
from the previously computed 24-row cross-evaluation CSV, use:
    python appendix_e_final.py --stage plot --out-dir .

The full stage uses integer ternary search on an active subset, exhaustively
checks the final bracket (width <=512), and repeatedly inserts worst-case
inputs from the entire fixed dataset. It then evaluates every selected magic
and each literature magic on all 3 datasets, with no omitted diagonal cells.

Datasets, each with exactly N=2**24 numbers in [1,4):
  linear:      x[k] = 1 + 3*k/N for k = 0,...,N-1, float64
  random:      x = 1 + 3*default_rng(0xC0FFEE).random(N), float64
  float32grid: float32 bit patterns 0x3F800000,...,0x407FFFFF,
               converted exactly to float64.

Newton uses float64 arithmetic, with evaluation order
  y1 = y0 * (1.5 - ((0.5*x * y0) * y0)).
The error |y*sqrt(x)-1| is computed with np.longdouble for comparison.
For best comparability, use a platform where longdouble offers >53 bits.

The method is HEURISTIC: ternary's empirical shape is not proved globally
unimodal; equality of active and full max for the chosen magic is a statement
about a fixed sample, not a mathematical global-optimality proof.
"""

import argparse
import csv
from decimal import Decimal
from functools import lru_cache
from pathlib import Path
import time

import numpy as np

N = 1 << 24
SEED = 0xC0FFEE
BASE = 0x5FE0000000000000
TAIL_MAX = (1 << 52) - 1
MODES = ("linear", "random", "float32grid")
LABELS = {"linear": "Equispaced", "random": "Random", "float32grid": "float32 grid", "paper": "Paper (2021)"}
PAPER = {0: 0x5FE6EC85E7DE30DA, 1: 0x5FE6EB50C7B537A9}
# Reference results from the 2**24 experiments, for plot/evaluate-only mode.
# The all stage recomputes all six values instead of trusting these defaults.
REFERENCE_WINNERS = {
    0: {"linear": 0x5FE6EC85E7C18A4C, "random": 0x5FE6EC85E7B577A0, "float32grid": 0x5FE6EC85E7A5CE2A},
    1: {"linear": 0x5FE6EB50C7B33619, "random": 0x5FE6EB50C736BCE6, "float32grid": 0x5FE6EB50C77C4635},
}


def get_data(mode):
    if mode == "linear":
        x = 1.0 + (3.0 / N) * np.arange(N, dtype=np.float64)
    elif mode == "random":
        x = 1.0 + 3.0 * np.random.default_rng(SEED).random(N)
    elif mode == "float32grid":
        bits = np.arange(0x3F800000, 0x40800000, dtype=np.uint32)
        x = bits.view(np.float32).astype(np.float64)
    else:
        raise ValueError(mode)
    return x, x * np.float64(0.5), np.sqrt(x.astype(np.longdouble))


def error_vectors(xbits, xhalf, sqrtx, magic):
    y0 = (np.uint64(magic) - (xbits >> np.uint64(1))).view(np.float64)
    e0 = np.abs(y0.astype(np.longdouble) * sqrtx - np.longdouble(1.0))
    y1 = y0 * (np.float64(1.5) - ((xhalf * y0) * y0))
    e1 = np.abs(y1.astype(np.longdouble) * sqrtx - np.longdouble(1.0))
    return e0, e1


def find_on_active(active_idx, x, xhalf, sqrtx, iteration, bracket_width):
    idx = np.array(sorted(active_idx), dtype=np.int64)
    xb = x[idx].view(np.uint64)
    half = xhalf[idx]
    sq = sqrtx[idx]

    @lru_cache(None)
    def f(tail):
        return np.max(error_vectors(xb, half, sq, BASE | int(tail))[iteration])

    left, right = 0, TAIL_MAX
    while right - left > bracket_width:
        third = (right-left)//3
        p, q = left+third, right-third
        if f(p) <= f(q):
            right = q
        else:
            left = p
    winner_tail = min(range(left, right+1), key=f)
    return BASE | winner_tail, f(winner_tail)


def scan_magic(x, xhalf, sq, magic, chunk):
    emax = [np.longdouble(-1), np.longdouble(-1)]
    imax = [-1, -1]
    for a in range(0, N, chunk):
        b = min(a+chunk, N)
        errors = error_vectors(x[a:b].view(np.uint64), xhalf[a:b], sq[a:b], magic)
        for k in (0, 1):
            at = int(np.argmax(errors[k]))
            if errors[k][at] > emax[k]:
                emax[k], imax[k] = errors[k][at], a+at
    return tuple(emax), tuple(imax)


def optimize_data(mode, x, xhalf, sq, opts):
    active = set(range(0, N, opts.active_stride))
    active.add(N-1)
    breakpoints = (0, N//3, 2*N//3, N-1) if mode == "linear" else (0, 1 << 23, N-1) if mode == "float32grid" else ()
    for k in breakpoints:
        active.update(range(max(0,k-4), min(N,k+5)))
    full_cache = {}
    winners = {}
    for iteration in (0, 1):
        for rnd in range(1, opts.max_rounds+1):
            magic, active_max = find_on_active(active, x, xhalf, sq, iteration, opts.bracket_width)
            if magic not in full_cache:
                full_cache[magic] = scan_magic(x, xhalf, sq, magic, opts.chunk_size)
            full_err, worst_idx = full_cache[magic]
            print(f'  [{mode}] {iteration} Newton round={rnd}, active={len(active):,}, '
                  f'magic=0x{magic:016x}, active={float(active_max*100):.12f}%, '
                  f'full={float(full_err[iteration]*100):.12f}%', flush=True)
            if full_err[iteration] <= active_max:
                winners[iteration] = magic
                break
            witness = worst_idx[iteration]
            if witness in active:
                raise RuntimeError('Active-set discrepancy: witness already active')
            active.update(range(max(0,witness-3), min(N,witness+4)))
        else:
            raise RuntimeError(f'{mode}: no active/full agreement in {opts.max_rounds} rounds')
    return winners


def save_magic_table(winners, cross_rows, out_dir):
    """Write the paper-versus-winners SIX-column table, using actual train errors.

    Each winner's error is from ITS OWN 2**24-input search/evaluation dataset.
    Its delta is calculated against the paper constant evaluated on that SAME
    dataset (not against a paper baseline from another dataset).
    The paper row uses the equispaced dataset; the 12-decimal display value
    is identical for the paper constant on all three datasets.
    """
    keyed = {}
    for row in cross_rows:
        key = (int(row['newton_iterations']), row['source'], row['test_dataset'])
        if key in keyed:
            raise ValueError(f'Duplicate cross-evaluation entry: {key}')
        keyed[key] = row

    output = out_dir / 'appendix_e_magic_table.csv'
    with output.open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['newton_iterations', 'method', 'magic_number',
                         'dist_over_2pow52', 'max_relative_error_pct',
                         'delta_vs_paper_pp'])
        for k in (0, 1):
            paper_row = keyed[(k, 'paper', 'linear')]
            if int(paper_row['magic_hex'], 16) != PAPER[k]:
                raise ValueError('Unexpected paper magic number')
            paper_e = Decimal(paper_row['max_relative_error_pct'])
            writer.writerow([k, 'paper', f'0x{PAPER[k]:016x}', '',
                             f'{paper_e:.12f}', ''])
            for mode in MODES:
                magic = winners[k][mode]
                row = keyed[(k, mode, mode)]
                baseline = keyed[(k, 'paper', mode)]
                if int(row['magic_hex'], 16) != magic:
                    raise ValueError(f'Winner mismatch in cross CSV: {k}, {mode}')
                e = Decimal(row['max_relative_error_pct'])
                paper_same_set = Decimal(baseline['max_relative_error_pct'])
                difference = e - paper_same_set
                dist = Decimal(abs(magic - PAPER[k])) / Decimal(1 << 52)
                writer.writerow([k, mode, f'0x{magic:016x}', f'{dist:.3e}',
                                 f'{e:.12f}', f'{difference:.3e}'])
    print('Wrote', output, '(complete six-column summary)', flush=True)


def evaluate_cross(winners, out_dir, chunk_size):
    rows=[]
    for mode in MODES:
        t0=time.perf_counter()
        print(f'Full cross-evaluation: {mode} ({N:,} inputs)', flush=True)
        x, half, sq = get_data(mode)
        magics = sorted(set([PAPER[0], PAPER[1]] + [winners[k][s] for k in (0,1) for s in MODES]))
        result = {m: scan_magic(x, half, sq, m, chunk_size) for m in magics}
        for k in (0,1):
            paper_pct = np.longdouble(100) * result[PAPER[k]][0][k]
            for source in (*MODES, 'paper'):
                magic = PAPER[k] if source == 'paper' else winners[k][source]
                emax, loc = result[magic]
                value = np.longdouble(100) * emax[k]
                rows.append({
                    'newton_iterations':k, 'source':source, 'test_dataset':mode,
                    'magic_hex':f'0x{magic:016x}',
                    'max_relative_error_pct':np.format_float_positional(value,precision=18),
                    'delta_vs_paper_pp':np.format_float_positional(value-paper_pct,precision=18),
                    'worst_input_bits':f'0x{int(x[loc[k]].view(np.uint64)):016x}',
                    'is_training_dataset': str(source == mode),
                })
        del x, half, sq, result
        print(f'Finished {mode}, {time.perf_counter()-t0:.1f}s', flush=True)
    path=out_dir/'appendix_e_cross_4x3.csv'
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print('Wrote',path,flush=True)
    return rows


def plot_cross(rows, out_dir):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import TwoSlopeNorm

    source_order = (*MODES, 'paper')
    for k in (0, 1):
        records = {(r['source'],r['test_dataset']):r for r in rows if int(r['newton_iterations']) == k}
        if len(records) != 12:
            raise ValueError(f'Expected 12 unique cross-evaluations for {k} Newton, got {len(records)}')
        pct = np.empty((4,3),dtype=float)
        delta = np.empty((4,3),dtype=float)
        for i, src in enumerate(source_order):
            for j, test in enumerate(MODES):
                r=records[(src,test)]
                pct[i,j]=float(r['max_relative_error_pct'])
                delta[i,j]=float(Decimal(r['delta_vs_paper_pp'])*Decimal('1e9'))
        if not np.all(np.abs(delta[3,:]) < 1e-9):
            raise ValueError('Paper baseline must be zero')
        span = max(0.5, np.max(np.abs(delta[:3,:])))
        fig,ax=plt.subplots(figsize=(13.7,7.5))
        cmap=plt.get_cmap('RdBu_r')
        im=ax.imshow(delta,cmap=cmap,norm=TwoSlopeNorm(vmin=-span*1.04,vcenter=0.,vmax=span*1.04),aspect='auto')
        ax.set_xticks(range(3),[LABELS[t] for t in MODES],fontsize=12)
        ax.set_yticks(range(4),[f'{LABELS[s]}'+(' winner' if s!='paper' else '')+'\n'+f"0x{(PAPER[k] if s=='paper' else int(records[(s,MODES[0])]['magic_hex'],16)):016x}" for s in source_order],fontsize=10.6)
        ax.xaxis.tick_top();ax.xaxis.set_label_position('top')
        ax.set_xlabel('Evaluation dataset  (2²⁴ inputs each)',fontsize=11.5,labelpad=14)
        ax.set_title(f'binary64 · {k} Newton iteration{"s" if k!=1 else ""}\n'
                     'Cross-dataset minimax, including training sets and paper baseline',
                     fontsize=15.5,pad=26)
        ax.set_xticks(np.arange(-.5,3,1),minor=True)
        ax.set_yticks(np.arange(-.5,4,1),minor=True)
        ax.grid(which='minor',color='white',linewidth=3.3)
        ax.tick_params(which='minor',bottom=False,left=False,top=False)
        for i in range(4):
            for j in range(3):
                r,g,b,_=im.cmap(im.norm(delta[i,j]))
                brightness=.2126*r+.7152*g+.0722*b
                color='#18202a' if brightness>0.55 else 'white'
                number = f'{pct[i,j]:.12f}%'
                vs = 'paper baseline' if i==3 else f'{delta[i,j]:+.3f} × 10⁻⁹ pp'
                mark = '  [train]' if i==j and i<3 else ''
                ax.text(j,i,number+'\n'+vs+mark,ha='center',va='center',fontsize=11.2,
                        linespacing=1.8,weight='bold' if i==3 else 'normal',color=color)
        bar=fig.colorbar(im,ax=ax,shrink=.82,pad=.028)
        bar.set_label('Δ max error vs paper  (10⁻⁹ percentage points)\n'
                      'negative = better',fontsize=10.3)
        fig.text(.54,.025,'Each cell: worst relative error (%), then difference vs the paper constant on the same test set.\n'
                 'The diagonal shows training-set performance. Heuristic search; not a proof of global optimality.',
                 ha='center',va='center',fontsize=9.6,color='0.3')
        fig.tight_layout(rect=[0,.076,1,1])
        path=out_dir/f'appendix_e_cross_{k}_newton.png'
        fig.savefig(path,dpi=175,bbox_inches='tight')
        plt.close(fig)
        print('Wrote',path,flush=True)


def read_cross(path):
    with path.open(newline='',encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=24:
        raise ValueError(f'Expected 24 CSV rows, got {len(rows)}')
    return rows


def winners_from_cross(rows):
    winners={0:{},1:{}}
    for r in rows:
        source=r['source']
        k=int(r['newton_iterations'])
        if source in MODES:
            magic=int(r['magic_hex'],16)
            if source in winners[k] and winners[k][source]!=magic:
                raise ValueError('Inconsistent winner in evaluation CSV')
            winners[k][source]=magic
        elif source == 'paper' and int(r['magic_hex'],16)!=PAPER[k]:
            raise ValueError('Unexpected paper baseline constant')
    for k in (0,1):
        if set(winners[k])!=set(MODES):
            raise ValueError('Missing winner')
    return winners


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--stage',choices=('all','evaluate','plot'),default='all')
    p.add_argument('--out-dir',type=Path,default=Path('.'))
    p.add_argument('--bracket-width',type=int,default=512)
    p.add_argument('--active-stride',type=int,default=1024)
    p.add_argument('--chunk-size',type=int,default=1<<18)
    p.add_argument('--max-rounds',type=int,default=12)
    a=p.parse_args()
    if a.bracket_width<3 or a.active_stride<1 or a.chunk_size<1 or a.max_rounds<1:
        p.error('invalid width/stride/chunk/rounds')
    a.out_dir.mkdir(parents=True,exist_ok=True)
    print('np.longdouble eps =',np.finfo(np.longdouble).eps,flush=True)
    print('2**24 per dataset; random seed =',hex(SEED),flush=True)
    csv_path=a.out_dir/'appendix_e_cross_4x3.csv'
    if a.stage=='plot':
        rows=read_cross(csv_path)
        winners=winners_from_cross(rows)
    else:
        winners={0:{},1:{}}
        if a.stage=='all':
            for mode in MODES:
                print(f'Optimizing {mode}:',flush=True)
                x,half,sq=get_data(mode)
                found=optimize_data(mode,x,half,sq,a)
                for k in (0,1):
                    winners[k][mode]=found[k]
                del x,half,sq
        else:
            winners=REFERENCE_WINNERS
        rows=evaluate_cross(winners,a.out_dir,a.chunk_size)
    save_magic_table(winners,rows,a.out_dir)
    plot_cross(rows,a.out_dir)

if __name__=='__main__':
    main()
