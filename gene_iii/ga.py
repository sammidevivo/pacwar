"""
Genetic Algorithm — use this to discover new strong species from scratch.
Hill climbing (evolve.py) is better for polishing; GA is better for exploring.

Each generation:
  1. Score every genome against the known bank + fresh random opponents
  2. Keep the top ELITE_SIZE unchanged (elitism)
  3. Fill the rest via tournament selection + crossover + mutation
  4. Auto-save anything with >90% win rate to genomes.json

Run: py -3.11 ga.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import random
from datetime import datetime
from utils import (
    random_genome, mutate_genome, genome_to_str, str_to_genome,
    score_battle, total_score_vs, load_genome_bank, save_new_genome
)

# -- Parameters ----------------------------------------------------------------

POPULATION_SIZE      = 80
GENERATIONS          = 100
ELITE_SIZE           = 8    # top N carried unchanged into next generation
TOURNAMENT_SIZE      = 5    # candidates per parent selection draw
NUM_MUTATIONS        = 2    # genes mutated per child (after crossover)
NUM_RANDOM_OPPONENTS = 20   # fresh randoms added to opponent pool each generation

SAVE_PREFIX = "ga"

# -- GA operators --------------------------------------------------------------

def tournament_select(population, scores):
    """Pick the best genome from a random sample of TOURNAMENT_SIZE."""
    candidates = random.sample(range(len(population)), TOURNAMENT_SIZE)
    best = max(candidates, key=lambda i: scores[i])
    return population[best][:]

def crossover(parent1, parent2):
    """Single-point crossover."""
    point = random.randint(1, 48)
    return parent1[:point] + parent2[point:]

# -- Main ----------------------------------------------------------------------

def run_ga():
    bank  = load_genome_bank()
    known = [g for _, g in bank]

    print(f"Population      : {POPULATION_SIZE}")
    print(f"Generations     : {GENERATIONS}")
    print(f"Elite size      : {ELITE_SIZE}")
    print(f"Tournament size : {TOURNAMENT_SIZE}")
    print(f"Mutations/child : {NUM_MUTATIONS}")
    print(f"Known opponents : {len(known)}")
    print(f"Randoms/gen     : {NUM_RANDOM_OPPONENTS}")
    print()

    # seed population
    population = [random_genome() for _ in range(POPULATION_SIZE)]

    all_time_best       = None
    all_time_best_score = -1
    saved_genomes       = set()

    for gen in range(GENERATIONS):
        randoms   = [random_genome() for _ in range(NUM_RANDOM_OPPONENTS)]
        opponents = known + randoms

        # score everyone
        scores = [total_score_vs(g, opponents) for g in population]

        # rank
        ranked = sorted(zip(scores, population), key=lambda x: x[0], reverse=True)
        top_score, top_genome = ranked[0]

        # track all-time best
        if top_score > all_time_best_score:
            all_time_best_score = top_score
            all_time_best       = top_genome[:]

        # win rate of current best against known bank only
        wins     = sum(1 for _, g in bank if score_battle(top_genome, g)[2] > score_battle(top_genome, g)[3])
        win_rate = wins / len(bank) * 100
        avg      = sum(scores) / len(scores)

        print(f"Gen {gen+1:4d}: best={top_score}/{len(opponents)*20}  avg={avg:.0f}  win={win_rate:.1f}%", end="")

        # auto-save if strong and not seen before
        genome_str = genome_to_str(top_genome)
        if win_rate > 90 and genome_str not in saved_genomes:
            name = f"{SAVE_PREFIX}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            print(f"  -> saving as '{name}'", end="")
            save_new_genome(name, top_genome, tags=["ga"])
            saved_genomes.add(genome_str)

        print()

        # build next generation
        elite    = [g for _, g in ranked[:ELITE_SIZE]]
        children = []

        while len(children) < POPULATION_SIZE - ELITE_SIZE:
            p1 = tournament_select(population, scores)
            p2 = tournament_select(population, scores)
            child = crossover(p1, p2)
            child = mutate_genome(child, NUM_MUTATIONS)
            children.append(child)

        population = elite + children

    print()
    print("Best genome found:")
    print(genome_to_str(all_time_best))

    name = f"{SAVE_PREFIX}_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    save_new_genome(name, all_time_best, tags=["ga", "converged"])

    return all_time_best


if __name__ == "__main__":
    run_ga()
