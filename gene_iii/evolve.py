"""
Hill-climbing evolution against the full genome bank + fresh random opponents.
New bests are automatically saved to genomes.json.

Usage:
  - Set BASE_GENOME to a genome string to start from, or None to start random.
  - Tune NUM_ROUNDS, NUM_VARIANTS, NUM_MUTATIONS, NUM_RANDOM_OPPONENTS.
  - Run: python evolve.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime
from utils import (
    random_genome, mutate_genome, genome_to_str, str_to_genome,
    score_battle, total_score_vs, load_genome_bank, save_new_genome
)

# -- Parameters ----------------------------------------------------------------

BASE_GENOME          = "01000100010001000103123323233213223333313313313313"   # genome string to start from, or None for random
NUM_ROUNDS           = 1000
NUM_VARIANTS         = 40
NUM_MUTATIONS        = 3
NUM_RANDOM_OPPONENTS = 20     # fresh random genomes added each round

SAVE_PREFIX = "evolved"       # saved names will be e.g. "evolved_20250325_143021"

# -- Main ----------------------------------------------------------------------

def evolve():
    bank = load_genome_bank()
    known = [g for _, g in bank]

    start = str_to_genome(BASE_GENOME) if BASE_GENOME else random_genome()
    print(f"Starting genome : {genome_to_str(start)}")
    print(f"Known opponents : {len(known)}")
    print(f"Rounds          : {NUM_ROUNDS}")
    print(f"Variants/round  : {NUM_VARIANTS}")
    print(f"Mutations       : {NUM_MUTATIONS}")
    print(f"Randoms/round   : {NUM_RANDOM_OPPONENTS}")
    print()

    current = start[:]
    all_time_best = start[:]
    all_time_best_score = -1
    rounds_since_improvement = 0

    for rnd in range(NUM_ROUNDS):
        # escalate mutation size and variant count when stuck
        if rounds_since_improvement < 15:
            mutations = NUM_MUTATIONS        # phase 1: fine tuning
            variants_count = NUM_VARIANTS
        elif rounds_since_improvement < 25:
            mutations = NUM_MUTATIONS * 2    # phase 2: medium jump
            variants_count = NUM_VARIANTS * 2
        else:
            mutations = NUM_MUTATIONS * 3    # phase 3: big jump
            variants_count = NUM_VARIANTS * 3

        randoms   = [random_genome() for _ in range(NUM_RANDOM_OPPONENTS)]
        opponents = known + randoms

        variants = [mutate_genome(current, mutations) for _ in range(variants_count)]
        variants.append(current)

        top_genome, top_score = max(
            ((v, total_score_vs(v, opponents)) for v in variants),
            key=lambda x: x[1]
        )
        current = top_genome[:]

        if top_score > all_time_best_score:
            all_time_best           = top_genome[:]
            all_time_best_score     = top_score
            rounds_since_improvement = 0

            # check win rate against known bank only (no randoms)
            wins = sum(1 for _, g in bank if score_battle(top_genome, g)[2] > score_battle(top_genome, g)[3])
            win_rate = wins / len(bank) * 100

            if win_rate > 90:
                name = f"{SAVE_PREFIX}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                print(f"Round {rnd+1:3d}: NEW BEST  {top_score}/{len(opponents)*20}  win={win_rate:.1f}%  mut={mutations}  -> saving as '{name}'")
                save_new_genome(name, all_time_best, tags=["evolved"])
            else:
                print(f"Round {rnd+1:3d}: NEW BEST  {top_score}/{len(opponents)*20}  win={win_rate:.1f}%  mut={mutations}  (below 90%, not saved)")
        else:
            rounds_since_improvement += 1
            phase = 1 if rounds_since_improvement < 15 else (2 if rounds_since_improvement < 25 else 3)
            print(f"Round {rnd+1:3d}: {top_score}/{len(opponents)*20}  mut={mutations}  stale={rounds_since_improvement}  phase={phase}")

            if rounds_since_improvement >= 50:
                print(f"\nStale for 50 rounds — stopping early.")
                break

    print()
    print("Best genome found:")
    print(genome_to_str(all_time_best))

    name = f"{SAVE_PREFIX}_converged_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    save_new_genome(name, all_time_best, tags=["evolved", "converged"])

    return all_time_best


if __name__ == "__main__":
    evolve()
