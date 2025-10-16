
import argparse, json
from .data import load_objects_csv
from .synthetic import generate_synthetic
from .mining import range_comine
from .baselines import naive_range, range_inc_mining

def main():
    ap = argparse.ArgumentParser(description="Range–CoMine demo (with baselines)")
    ap.add_argument('--csv', type=str, default='', help='CSV file with id,feature,x,y')
    ap.add_argument('--synthetic', action='store_true', help='Use synthetic data')
    ap.add_argument('--features', type=int, default=4)
    ap.add_argument('--instances', type=int, default=8)
    ap.add_argument('--d1', type=float, default=10.0)
    ap.add_argument('--d2', type=float, default=30.0)
    ap.add_argument('--min_prev', type=float, default=0.5)
    ap.add_argument('--algo', type=str, default='range_comine', choices=['range_comine','naive','range_inc'])
    args = ap.parse_args()

    if args.synthetic:
        objects = generate_synthetic(n_features=args.features, instances_per_feat=args.instances)
    else:
        if not args.csv:
            ap.error('Provide --csv or use --synthetic')
        objects = load_objects_csv(args.csv)

    if args.algo == 'range_comine':
        result = range_comine(objects, args.d1, args.d2, args.min_prev)
    elif args.algo == 'naive':
        result = naive_range(objects, args.d1, args.d2, args.min_prev)
    else:
        result = range_inc_mining(objects, args.d1, args.d2, args.min_prev)

    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
