import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import _PyPacwar
import random
import json


# ─────────────────────────────────────────────
#  Genome helpers
# ─────────────────────────────────────────────

def random_genome():
    return [random.randint(0, 3) for _ in range(50)]


def mutate_genome(genome, num_mutations=3):
    mutated = genome[:]
    positions = random.sample(range(50), num_mutations)
    for pos in positions:
        mutated[pos] = random.randint(0, 3)
    return mutated


def genome_to_str(genome):
    return ''.join(str(g) for g in genome)


def str_to_genome(s):
    return list(map(int, s))


# ─────────────────────────────────────────────
#  Scoring (professor's system)
# ─────────────────────────────────────────────

def score_battle(genome1, genome2):
    """
    Returns (score_for_genome1, rounds, c1, c2).

    Points scale (out of 20):
      Win by destruction:
        < 100 rounds  → 20
        100–199       → 19
        200–299       → 18
        300–500       → 17
      Loss by destruction:
        < 100 rounds  →  0
        100–199       →  1
        200–299       →  2
        300–500       →  3
      Survived 500 rounds (ratio c1/c2):
        ≥ 10:1  → 13   ≤ 1:10 → 7
        ≥  3:1  → 12   ≤ 1:3  → 8
        ≥  1.5  → 11   ≤ 1/1.5→ 9
        else    → 10
    """
    rounds, c1, c2 = _PyPacwar.battle(genome1, genome2)

    if c2 == 0 and c1 > 0:
        if rounds < 100:   return 20, rounds, c1, c2
        elif rounds < 200: return 19, rounds, c1, c2
        elif rounds < 300: return 18, rounds, c1, c2
        else:              return 17, rounds, c1, c2

    elif c1 == 0 and c2 > 0:
        if rounds < 100:   return  0, rounds, c1, c2
        elif rounds < 200: return  1, rounds, c1, c2
        elif rounds < 300: return  2, rounds, c1, c2
        else:              return  3, rounds, c1, c2

    else:
        if c1 == 0 and c2 == 0: return 10, rounds, c1, c2
        if c1 == 0:              return  0, rounds, c1, c2
        if c2 == 0:              return 20, rounds, c1, c2
        ratio = c1 / c2
        if   ratio >= 10:        return 13, rounds, c1, c2
        elif ratio >= 3:         return 12, rounds, c1, c2
        elif ratio >= 1.5:       return 11, rounds, c1, c2
        elif ratio <= 1/10:      return  7, rounds, c1, c2
        elif ratio <= 1/3:       return  8, rounds, c1, c2
        elif ratio <= 1/1.5:     return  9, rounds, c1, c2
        else:                    return 10, rounds, c1, c2


def total_score_vs(genome, opponents):
    """Sum of scores against a list of opponent genomes."""
    return sum(score_battle(genome, opp)[0] for opp in opponents)


# ─────────────────────────────────────────────
#  Hill climber
# ─────────────────────────────────────────────

def hill_climb(
    start_genome,
    opponents,
    num_rounds=60,
    num_variants=30,
    num_mutations=3,
    verbose=True,
    label="",
):
    """
    Pure hill-climbing: each round generate num_variants mutations of the
    current best; keep whichever scores highest against `opponents`.

    Returns (best_genome, best_score).
    """
    current = start_genome[:]
    current_score = total_score_vs(current, opponents)
    best = current[:]
    best_score = current_score

    for rnd in range(num_rounds):
        variants = [mutate_genome(current, num_mutations) for _ in range(num_variants)]
        variants.append(current)

        scores = [(v, total_score_vs(v, opponents)) for v in variants]
        scores.sort(key=lambda x: x[1], reverse=True)

        top_genome, top_score = scores[0]

        if top_score > best_score:
            best = top_genome[:]
            best_score = top_score
            if verbose:
                print(f"  [{label}] Round {rnd+1:3d}: NEW BEST {best_score}/{len(opponents)*20}")

        current = top_genome[:]

    return best, best_score


# ─────────────────────────────────────────────
#  JSON save / load
# ─────────────────────────────────────────────

def save_results(path, data):
    """data: list of dicts with at least 'genome' (list) and 'score' (int/float)."""
    serializable = []
    for d in data:
        entry = dict(d)
        entry['genome_str'] = genome_to_str(d['genome'])
        entry['genome'] = d['genome']
        serializable.append(entry)
    with open(path, 'w') as f:
        json.dump(serializable, f, indent=2)
    print(f"  Saved {len(serializable)} genomes -> {path}")


def load_results(path):
    with open(path) as f:
        data = json.load(f)
    for d in data:
        if 'genome' not in d and 'genome_str' in d:
            d['genome'] = str_to_genome(d['genome_str'])
    return data