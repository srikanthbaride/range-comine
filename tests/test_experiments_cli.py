
import subprocess, sys, os, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_min_prev_sweep(tmp_path):
    # Run with minimal settings and a single algo to keep runtime low
    cmd = [sys.executable, str(ROOT / "experiments.py"),
           "--mode", "min_prev", "--mins", "0.3,0.6",
           "--d1", "8", "--d2", "25", "--features", "3", "--instances", "4",
           "--seed", "5", "--algos", "range", "--export_svg"]
    subprocess.run(cmd, check=True, cwd=ROOT)
    # Artifacts should exist
    assert (ROOT / "plots" / "sweep_min_prev_range.png").exists()
    assert (ROOT / "plots" / "sweep_min_prev_range.svg").exists()
    assert (ROOT / "plots" / "sweep_min_prev_range.csv").exists()
    assert (ROOT / "plots" / "sweep_min_prev_all.png").exists()
    assert (ROOT / "plots" / "sweep_min_prev_all.svg").exists()

def test_range_sweep_csv(tmp_path):
    # Use the bundled toy CSV
    cmd = [sys.executable, str(ROOT / "experiments.py"),
           "--mode", "range", "--min_prev", "0.5",
           "--d1s", "3", "--d2s", "6,8", "--csv", "examples/toy.csv",
           "--algos", "range,naive", "--export_svg"]
    subprocess.run(cmd, check=True, cwd=ROOT)
    # Artifacts should exist
    assert (ROOT / "plots" / "sweep_range_range.png").exists()
    assert (ROOT / "plots" / "sweep_range_naive.png").exists()
    assert (ROOT / "plots" / "sweep_range_all.png").exists()
    assert (ROOT / "plots" / "sweep_range_all.svg").exists()
