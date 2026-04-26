"""
run_pipeline.py — Full Three-Stage Pipeline
============================================
Runs Stage 1 -> Stage 2 -> Stage 3 in sequence.

You can also run each stage independently:
    python stage1_baseline.py
    python stage2_last_year.py
    python stage3_known.py

Or run this file to do the whole thing end-to-end:
    python run_pipeline.py

Results at each stage are saved to JSON so you can resume from any point.
"""

import subprocess
import sys
import os
import time

STAGES = [
    ("Stage 1 — Baseline Filter",          "stage1_baseline.py"),
    ("Stage 2 — Last Year's Checkpoints",   "stage2_last_year.py"),
    ("Stage 3 — Full Known-Genome Gauntlet","stage3_known.py"),
]


def run_stage(label, script):
    print("\n" + "+" + "=" * 63 + "+")
    print(f"|  {label:<61}|")
    print("+" + "=" * 63 + "+\n")

    t0 = time.time()
    result = subprocess.run(
        [sys.executable, script],
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )
    elapsed = time.time() - t0

    if result.returncode != 0:
        print(f"\nFAIL  {script} exited with code {result.returncode}. Aborting pipeline.")
        sys.exit(result.returncode)

    print(f"\nOK  {label} complete ({elapsed:.1f}s)")


def main():
    print("+" + "=" * 63 + "+")
    print("|  PACWAR CHECKPOINT 2 — FULL PIPELINE                       |")
    print("+" + "=" * 63 + "+")
    print()
    print("This will run three hill-climbing stages in sequence:")
    print("  Stage 1 -> beat All-1s and All-3s (threshold 36/40)")
    print("  Stage 2 -> fine-tune vs 29 last-year checkpoint genomes")
    print("  Stage 3 -> fine-tune vs full known-genome pool (~70 opponents)")
    print()
    print("Results saved after each stage (stage1/2/3_results.json).")
    print("You can Ctrl-C and resume from any stage file independently.")
    print()

    pipeline_start = time.time()

    for label, script in STAGES:
        run_stage(label, script)

    total_elapsed = time.time() - pipeline_start
    print("\n" + "+" + "=" * 63 + "+")
    print(f"|  ALL STAGES COMPLETE  ({total_elapsed/60:.1f} min total){'':>28}|")
    print("+" + "=" * 63 + "+")
    print()
    print("Final best genome is printed at the end of Stage 3 above.")
    print("See stage3_results.json for the full ranked list.")


if __name__ == "__main__":
    main()
