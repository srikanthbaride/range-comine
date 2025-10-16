
"""Export ColList lattice as PDF/SVG (and optional PNG).
Example:
  python lattice_export.py --outfile lattice --d1 8 --d2 30 --min_prev 0.5 --features 4 --instances 5 --seed 7 --cross_level --png
"""
import argparse
from pathlib import Path
import matplotlib.pyplot as plt

from range_comine.synthetic import generate_synthetic
from range_comine.mining import range_comine

PLOTS = Path("plots"); PLOTS.mkdir(exist_ok=True, parents=True)

def lattice_positions(ColList):
    def as_tuple(p): return tuple(sorted(p))
    levels = sorted([(d, [as_tuple(p) for p in pats]) for d, pats in ColList.items()], key=lambda x: x[0])
    positions = {}
    edges_same = []
    edges_cross = []
    x_spacing = 1.6

    for li, (d, pats) in enumerate(levels):
        by_k = {}
        for p in pats:
            by_k.setdefault(len(p), []).append(p)
        x_cursor = 0.0
        for k in sorted(by_k.keys()):
            group = sorted(set(by_k[k]))
            for p in group:
                positions[p] = (li, x_cursor)
                x_cursor += x_spacing

    # Build edges (subset -> superset) across all levels
    all_patterns = {p: li for li, (d, pats) in enumerate(levels) for p in pats}
    for q, li_q in all_patterns.items():
        for i in range(len(q)):
            parent = tuple(q[:i] + q[i+1:])
            if parent in all_patterns:
                li_p = all_patterns[parent]
                if li_p == li_q:
                    edges_same.append((parent, q))
                else:
                    edges_cross.append((parent, q))
    return levels, positions, edges_same, edges_cross

def draw_lattice(levels, positions, edges_same, edges_cross, title="ColList Lattice"):
    plt.figure(figsize=(11, 7))
    # nodes
    for p, (li, x) in positions.items():
        y = li
        label = "".join(p)
        plt.scatter([x], [y])
        plt.text(x, y + 0.05, label, ha="center", va="bottom", fontsize=10)
    # same-level edges
    for a, b in edges_same:
        xa, ya = positions[a][1], positions[a][0]
        xb, yb = positions[b][1], positions[b][0]
        plt.arrow(xa, ya, xb - xa, yb - ya, length_includes_head=True, head_width=0.08, head_length=0.12)
    # cross-level edges (draw as thin lines; optional activation by caller)
    for a, b in edges_cross:
        xa, ya = positions[a][1], positions[a][0]
        xb, yb = positions[b][1], positions[b][0]
        plt.plot([xa, xb], [ya, yb], linewidth=1)

    y_ticks = list(range(len(levels)))
    y_labels = [f"d={d:.2f}" for (d, _) in levels]
    plt.yticks(y_ticks, y_labels)
    plt.xlabel("Patterns laid out horizontally")
    plt.ylabel("Critical distance levels")
    plt.title(title)
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()

def main():
    ap = argparse.ArgumentParser(description="Export ColList lattice to PDF/SVG/PNG")
    ap.add_argument("--outfile", type=str, default="lattice", help="Base filename (without extension) under plots/")
    ap.add_argument("--d1", type=float, default=8.0)
    ap.add_argument("--d2", type=float, default=30.0)
    ap.add_argument("--min_prev", type=float, default=0.5)
    ap.add_argument("--features", type=int, default=4)
    ap.add_argument("--instances", type=int, default=5)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--cross_level", action="store_true", help="Draw cross-level parent→child edges")
    ap.add_argument("--png", action="store_true", help="Also save PNG")
    args = ap.parse_args()

    objs = generate_synthetic(n_features=args.features, instances_per_feat=args.instances, seed=args.seed)
    ColList = range_comine(objs, d1=args.d1, d2=args.d2, min_prev=args.min_prev)
    levels, positions, edges_same, edges_cross = lattice_positions(ColList)

    if args.cross_level:
        # draw with cross-level edges included (plot function draws both kinds)
        pass
    else:
        # remove cross-level edges
        edges_cross = []

    draw_lattice(levels, positions, edges_same, edges_cross, title="ColList Lattice (subset links)")
    pdf_path = PLOTS / f"{args.outfile}.pdf"
    svg_path = PLOTS / f"{args.outfile}.svg"
    plt.savefig(pdf_path)
    plt.savefig(svg_path)
    if args.png:
        png_path = PLOTS / f"{args.outfile}.png"
        plt.savefig(png_path, dpi=160)
    print(f"Saved: {pdf_path}, {svg_path}" + (" (and PNG)" if args.png else ""))

if __name__ == "__main__":
    main()
