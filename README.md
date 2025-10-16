# Range–CoMine (demo implementation)

This repository contains a **reference implementation** of *Range–CoMine* (single‑pass colocation mining for a **distance range**) and two baselines (Naive and RangeInc‑Mining). It is designed for clarity and correctness on small–medium datasets.

## Quick start

```bash
# (In this folder)
python -m range_comine.cli --synthetic --features 4 --instances 6 --d1 10 --d2 35 --min_prev 0.5 --algo range_comine
```

Use the baselines:
```bash
python -m range_comine.cli --synthetic --features 4 --instances 6 --d1 10 --d2 35 --min_prev 0.5 --algo naive
python -m range_comine.cli --synthetic --features 4 --instances 6 --d1 10 --d2 35 --min_prev 0.5 --algo range_inc
```

## Data format

If using real data, prepare a CSV with header:
```
id,feature,x,y
A.1,A,12.3,45.6
...
```

## Notes

- This demo uses an O(n^2) star‑neighborhood build and a naive clique enumeration for k≥3. It is faithful to the paper’s logic but not tuned for very large datasets.
- For production scale, replace the neighbor construction with an **R‑tree/IR‑tree** and use a **join‑less** clique enumeration with star instances as in the paper.
- The **critical distance** computation follows the 3‑step procedure (map → cumulative union → PI sweep) and **CDMP** pruning.

## Citation

Please cite the original paper when using this code.


## Credits

This reference implementation follows the ideas presented in:

> **Srikanth Baride, Anuj S. Saxena, Vikram Goyal.** *Efficiently Mining Colocation Patterns for Range Query.* **Big Data Research**, 31:100369, 2023.

If you use this repository in academic work, please cite the above paper. (BibTeX sketch)

```bibtex
@article{Baride2023RangeCoMine,
  title   = {Efficiently Mining Colocation Patterns for Range Query},
  author  = {Baride, Srikanth and Saxena, Anuj S. and Goyal, Vikram},
  journal = {Big Data Research},
  volume  = {31},
  pages   = {100369},
  year    = {2023},
  issn    = {2214-5796}
}
```


## Experiments (CLI + SVG export)

Synthetic:
```bash
python experiments.py --mode min_prev --mins 0.2,0.4,0.6 --d1 10 --d2 35 --features 4 --instances 8 --seed 13 --algos range,naive,range_inc --export_svg
```

CSV dataset:
```bash
python experiments.py --mode range --min_prev 0.5 --d1s 5,10 --d2s 20,30 --csv examples/toy.csv --algos range,naive --export_svg
```

## Lattice export (PDF/SVG)
```bash
python lattice_export.py --outfile lattice_demo --d1 8 --d2 30 --min_prev 0.5 --features 4 --instances 5 --seed 7
# outputs plots/lattice_demo.pdf and plots/lattice_demo.svg
```

## Tests
```bash
pytest -q
```


## Makefile shortcuts
```bash
make install   # deps
make test      # run pytest
make plots     # quick sweeps + SVG
make lattice   # lattice export (PDF/SVG/PNG, cross-level edges)
make all       # install + test + plots + lattice
```

## CI (GitHub Actions)
A workflow at `.github/workflows/ci.yml` runs:
- `pytest`
- sample experiments (min_prev/range) with SVG export
- lattice export with cross-level edges and PNG
- uploads `plots/` as build artifacts


## Packaging
Install in editable/development mode:
```bash
./dev_install.sh
# or
pip install -e .
```


## Console scripts
After `pip install -e .`, you can run:
```bash
range-comine-cli --synthetic --features 4 --instances 6 --d1 10 --d2 35 --min_prev 0.5 --algo range_comine
range-comine-exp --mode min_prev --mins 0.2,0.4,0.6 --d1 10 --d2 35 --features 4 --instances 8 --seed 13 --algos range,naive,range_inc --export_svg
range-comine-lattice --outfile lattice_demo --d1 8 --d2 30 --min_prev 0.5 --features 4 --instances 5 --seed 7 --cross_level --png
```

## Lockfiles
- Classic pip:
  ```bash
  make lock        # creates requirements.lock via pip freeze
  ```
- Using **uv**:
  ```bash
  uv venv && uv pip install -e .
  uv lock          # creates uv.lock
  ```

## Docker
```bash
make docker-build      # build image
make docker-test       # run tests in container
make docker-minprev    # min_prev sweep (plots mounted to ./plots)
make docker-range      # range sweep (plots mounted to ./plots)
make docker-lattice    # lattice export (PDF/SVG/PNG)
```
