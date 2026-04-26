"""
Train genomes from random seeds until they beat all 4 baselines (78+/80).
Each survivor is automatically saved to genomes.json.

Usage:
  - Set NUM_TO_FIND to stop after N padawans are found.
  - Tune NUM_ROUNDS, NUM_VARIANTS, NUM_MUTATIONS, PASS_SCORE.
  - Run: python padawans.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import json
from datetime import datetime
from utils import random_genome, mutate_genome, genome_to_str, total_score_vs

PADAWANS_FILE = os.path.join(os.path.dirname(__file__), 'padawans.json')

def save_to_padawans(name, genome, score):
    data = []
    if os.path.exists(PADAWANS_FILE):
        with open(PADAWANS_FILE) as f:
            data = json.load(f)
    data.append({'name': name, 'genome': genome_to_str(genome), 'baseline_score': score})
    with open(PADAWANS_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"  Saved '{name}' to padawans.json")

# -- Parameters ----------------------------------------------------------------

NUM_TO_FIND   = 3      # stop after finding this many
PASS_SCORE    = 78     # min score out of 80 to count
NUM_ROUNDS    = 100
NUM_VARIANTS  = 30
NUM_MUTATIONS = 3

BASELINES = [[0]*50, [1]*50, [2]*50, [3]*50]

# -- Main ----------------------------------------------------------------------

def train():
    padawans = []
    attempt  = 0

    print("=" * 60)
    print("PADAWAN TRAINING")
    print(f"Goal   : {NUM_TO_FIND} genomes scoring >= {PASS_SCORE}/80")
    print(f"Rounds : {NUM_ROUNDS}   Variants: {NUM_VARIANTS}   Mutations: {NUM_MUTATIONS}")
    print("=" * 60)

    while len(padawans) < NUM_TO_FIND:
        attempt += 1
        print(f"\n--- Attempt {attempt} ---")

        current    = random_genome()
        best       = current[:]
        best_score = 0

        for rnd in range(NUM_ROUNDS):
            variants = [mutate_genome(current, NUM_MUTATIONS) for _ in range(NUM_VARIANTS)]
            variants.append(current)

            top_genome, top_score = max(
                ((v, total_score_vs(v, BASELINES)) for v in variants),
                key=lambda x: x[1]
            )

            if top_score > best_score:
                best, best_score = top_genome[:], top_score
                print(f"  Round {rnd+1:3d}: {best_score}/80")

            current = top_genome[:]

            if best_score == 80:
                break  # perfect, no need to keep going

        if best_score >= PASS_SCORE:
            padawans.append(best)
            name = f"padawan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            print(f"\nPADAWAN FOUND ({len(padawans)}/{NUM_TO_FIND})  [{best_score}/80]")
            print(f"  {genome_to_str(best)}")
            save_to_padawans(name, best, best_score)
        else:
            print(f"  Failed: {best_score}/80")

    print()
    print("=" * 60)
    print(f"All {NUM_TO_FIND} padawans found:")
    for i, g in enumerate(padawans, 1):
        print(f"  {i}. {genome_to_str(g)}")
    return padawans


if __name__ == "__main__":
    train()
