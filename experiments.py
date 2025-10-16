
"""Matplotlib experiments for Range–CoMine + baselines with profiling overlays.

- Supports synthetic or CSV datasets
- Side-by-side series for Range–CoMine, Naïve, RangeInc-Mining
- Optional SVG export
- Records average runtime (ms) and peak memory (KB) per algorithm and overlays in legend

Examples:
  python experiments.py --mode min_prev --mins 0.2,0.4,0.6 --d1 10 --d2 35 --features 4 --instances 8 --seed 13 --algos range,naive,range_inc --export_svg
  python experiments.py --mode range --min_prev 0.5 --d1s 5,10 --d2s 20,30 --csv examples/toy.csv --export_svg
"""
import os, csv, argparse, time, tracemalloc, statistics as stats
from pathlib import Path
import matplotlib.pyplot as plt

from range_comine.synthetic import generate_synthetic
from range_comine.data import load_objects_csv
from range_comine.mining import range_comine
from range_comine.baselines import naive_range, range_inc_mining

PLOTS = Path("plots"); PLOTS.mkdir(exist_ok=True, parents=True)

ALGOS = {
    "range": ("Range–CoMine", range_comine),
    "naive": ("Naïve", naive_range),
    "range_inc": ("RangeInc-Mining", range_inc_mining),
}

def _count_patterns(col):
    s = set()
    for d, pats in col.items():
        for p in pats:
            s.add(tuple(p))
    return len(s)

def _ensure_list_str(csvish):
    if isinstance(csvish, (list, tuple)):
        return list(csvish)
    if isinstance(csvish, str) and csvish.strip():
        return [x.strip() for x in csvish.split(",")]
    return []

def _get_objects(args):
    if args.csv:
        return load_objects_csv(args.csv)
    return generate_synthetic(n_features=args.features, instances_per_feat=args.instances, seed=args.seed)

def _savefig(basepath, export_svg=False):
    png_path = basepath.with_suffix(".png")
    plt.savefig(png_path, dpi=160)
    if export_svg:
        svg_path = basepath.with_suffix(".svg")
        plt.savefig(svg_path)
    plt.close()

def _run_profiled(fn, objs, d1, d2, min_prev):
    # measure wall time ms and peak kb using tracemalloc
    tracemalloc.start()
    t0 = time.perf_counter()
    col = fn(objs, d1=float(d1), d2=float(d2), min_prev=float(min_prev))
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    peak_kb = peak / 1024.0
    return col, elapsed_ms, peak_kb

def sweep_min_prev(args, mins, d1=10.0, d2=35.0, algos=("range","naive","range_inc")):
    objs = _get_objects(args)
    xs = [float(x) for x in mins]
    series = {}
    overlay = {}
    for a in algos:
        name, fn = ALGOS[a]
        rows, ys, times, mems = [], [], [], []
        for m in xs:
            col, t_ms, pk_kb = _run_profiled(fn, objs, d1, d2, m)
            cnt = _count_patterns(col)
            rows.append({"min_prev": m, "num_patterns": cnt, "time_ms": round(t_ms,3), "peak_kb": round(pk_kb,1)})
            ys.append(cnt); times.append(t_ms); mems.append(pk_kb)
        # CSV + single
        csv_path = PLOTS / f"sweep_min_prev_{a}.csv"
        with open(csv_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["min_prev","num_patterns","time_ms","peak_kb"])
            w.writeheader(); w.writerows(rows)
        # Plot
        plt.figure()
        plt.plot(xs, ys, marker="o", label=f"{name} (avg {stats.mean(times):.0f} ms, {stats.mean(mems):.0f} KB)")
        plt.xlabel("min_prev"); plt.ylabel("Number of prevalent patterns")
        plt.title(f"Effect of min_prev — {name}")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.6); plt.tight_layout()
        _savefig(PLOTS / f"sweep_min_prev_{a}", export_svg=args.export_svg)
        series[a] = (name, ys)
        overlay[a] = (stats.mean(times), stats.mean(mems))

    # combined
    plt.figure()
    for a, (name, ys) in series.items():
        avg_t, avg_m = overlay[a]
        plt.plot(xs, ys, marker="o", label=f"{name} (avg {avg_t:.0f} ms, {avg_m:.0f} KB)")
    plt.xlabel("min_prev"); plt.ylabel("Number of prevalent patterns")
    plt.title("Effect of min_prev — comparison"); plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6); plt.tight_layout()
    _savefig(PLOTS / "sweep_min_prev_all", export_svg=args.export_svg)

def sweep_range(args, min_prev=0.5, d1s=(5,10,15), d2s=(20,25,30,35), algos=("range","naive","range_inc")):
    objs = _get_objects(args)
    pairs = [(float(d1), float(d2)) for d1 in d1s for d2 in d2s if float(d1) < float(d2)]
    xlabels = [f"{int(d1)}-{int(d2)}" if (float(d1).is_integer() and float(d2).is_integer()) else f"{d1}-{d2}" for d1,d2 in pairs]
    xs = list(range(len(pairs)))
    series = {}
    overlay = {}
    for a in algos:
        name, fn = ALGOS[a]
        rows, ys, times, mems = [], [], [], []
        for (d1, d2) in pairs:
            col, t_ms, pk_kb = _run_profiled(fn, objs, d1, d2, min_prev)
            cnt = _count_patterns(col)
            rows.append({"d1": d1, "d2": d2, "num_patterns": cnt, "time_ms": round(t_ms,3), "peak_kb": round(pk_kb,1)})
            ys.append(cnt); times.append(t_ms); mems.append(pk_kb)
        # CSV + single
        csv_path = PLOTS / f"sweep_range_{a}.csv"
        with open(csv_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["d1","d2","num_patterns","time_ms","peak_kb"])
            w.writeheader(); w.writerows(rows)
        # Plot
        plt.figure()
        plt.plot(xs, ys, marker="o", label=f"{name} (avg {stats.mean(times):.0f} ms, {stats.mean(mems):.0f} KB)")
        plt.xticks(xs, xlabels, rotation=45, ha="right")
        plt.xlabel("Distance range [d1–d2]"); plt.ylabel("Number of prevalent patterns")
        plt.title(f"Effect of distance range — {name}"); plt.legend()
        plt.grid(True, linestyle="--", alpha=0.6); plt.tight_layout()
        _savefig(PLOTS / f"sweep_range_{a}", export_svg=args.export_svg)
        series[a] = (name, ys)
        overlay[a] = (stats.mean(times), stats.mean(mems))

    # combined
    plt.figure()
    for a, (name, ys) in series.items():
        avg_t, avg_m = overlay[a]
        plt.plot(xs, ys, marker="o", label=f"{name} (avg {avg_t:.0f} ms, {avg_m:.0f} KB)")
    plt.xticks(xs, xlabels, rotation=45, ha="right")
    plt.xlabel("Distance range [d1–d2]"); plt.ylabel("Number of prevalent patterns")
    plt.title("Effect of distance range — comparison"); plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6); plt.tight_layout()
    _savefig(PLOTS / "sweep_range_all", export_svg=args.export_svg)

def parse_args():
    ap = argparse.ArgumentParser(description="Experiments for Range–CoMine and baselines (with profiling overlays)")
    ap.add_argument("--mode", choices=["min_prev","range"], required=True, help="Sweep mode")
    ap.add_argument("--mins", type=str, default="0.2,0.3,0.4,0.5,0.6,0.7", help="CSV of min_prev values (mode=min_prev)")
    ap.add_argument("--d1", type=float, default=10.0, help="Lower distance bound (mode=min_prev)")
    ap.add_argument("--d2", type=float, default=35.0, help="Upper distance bound (mode=min_prev)")
    ap.add_argument("--min_prev", type=float, default=0.5, help="min_prev (mode=range)")
    ap.add_argument("--d1s", type=str, default="5,10,15", help="CSV of d1 values (mode=range)")
    ap.add_argument("--d2s", type=str, default="20,25,30,35", help="CSV of d2 values (mode=range)")
    ap.add_argument("--features", type=int, default=4, help="Number of features for synthetic data")
    ap.add_argument("--instances", type=int, default=8, help="Instances per feature for synthetic data")
    ap.add_argument("--seed", type=int, default=13, help="Random seed for synthetic data")
    ap.add_argument("--csv", type=str, default="", help="Path to CSV dataset (overrides synthetic)")
    ap.add_argument("--algos", type=str, default="range,naive,range_inc", help="CSV of algos to include (range,naive,range_inc)")
    ap.add_argument("--export_svg", action="store_true", help="Also export SVG versions of plots")
    return ap.parse_args()

def main():
    args = parse_args()
    algos = _ensure_list_str(args.algos)
    if args.mode == "min_prev":
        mins = _ensure_list_str(args.mins)
        sweep_min_prev(args, mins, d1=float(args.d1), d2=float(args.d2), algos=algos)
    else:
        d1s = [float(x) for x in _ensure_list_str(args.d1s)]
        d2s = [float(x) for x in _ensure_list_str(args.d2s)]
        sweep_range(args, min_prev=float(args.min_prev), d1s=d1s, d2s=d2s, algos=algos)

if __name__ == "__main__":
    main()
