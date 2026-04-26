"""
Adaptive GA- exploration search with stagnation recovery
=========================================================
Runs a genetic algorithm against opponents loaded from opponents.txt.
Uses a diversity bonus, 3-point crossover, and automatic stagnation
recovery (mutation ramp, fresh injection, hard restart).

Best for discovering new strong genomes from scratch

Usage:
    python explore.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import random
from utils import (
    random_genome, mutate_genome, genome_to_str, score_battle, total_score_vs
)

# ── Hyperparameters ────────────────────────────────────────────────────────────
POP_SIZE        = 40
GENERATIONS     = 500
ELITE_FRAC      = 0.15
MUTATION_RATE   = 0.15
TRIALS_FAST     = 3
TRIALS_FINAL    = 30
SAMPLE_OPPS     = 15    # opponents sampled per fitness call
DIVERSITY_W     = 25    # reward for hamming distance from elites
TOURNAMENT_K    = 4     # contestants per tournament selection

# ── Load opponents ─────────────────────────────────────────────────────────────
def load_opponents(filepath="opponents.txt"):
    opponents = {}
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            name, gene = line.split(":", 1)
            opponents[name.strip()] = gene.strip()
    return opponents

OPPONENTS      = load_opponents()
OPPONENT_GENES = [[int(c) for c in g] for g in OPPONENTS.values()]

# ── Gene ops ───────────────────────────────────────────────────────────────────
def random_gene():
    return [random.randint(0, 3) for _ in range(50)]

def crossover(a, b):
    """3-point crossover for more varied recombination."""
    points = sorted(random.sample(range(1, 49), 3))
    result = []
    use_a  = True
    prev   = 0
    for p in points + [50]:
        result += (a if use_a else b)[prev:p]
        use_a   = not use_a
        prev    = p
    return result

def mutate(gene, rate=MUTATION_RATE):
    return [
        random.randint(0, 3) if random.random() < rate else g
        for g in gene
    ]

def hamming(a, b):
    return sum(x != y for x, y in zip(a, b))

# ── Fitness ────────────────────────────────────────────────────────────────────
def score_duel(rounds, mine, opp):
    if opp == 0:
        return 10000 - rounds * 10
    elif mine == 0:
        return -5000
    else:
        return (mine - opp) * 5 - 2000

def fitness(gene, elites=None, trials=TRIALS_FAST):
    """
    Battle a random sample of opponents.
    Optionally adds a diversity bonus based on hamming distance from elites.
    """
    sampled = random.sample(OPPONENT_GENES, min(SAMPLE_OPPS, len(OPPONENT_GENES)))

    total   = 0
    wins    = 0
    battles = 0

    for opp in sampled:
        for _ in range(trials):
            r, m, o = _PyPacwar.battle(gene, opp)
            total  += score_duel(r, m, o)
            if o == 0:
                wins += 1
            battles += 1

    win_rate  = wins / battles
    avg_score = total / battles
    base      = win_rate * 10000 + avg_score

    # diversity bonus — reward genes far from current elites
    if elites:
        min_dist = min(hamming(gene, e) for e in elites)
        base    += min_dist * DIVERSITY_W

    return base

# ── Selection ──────────────────────────────────────────────────────────────────
def tournament_select(scored, k=TOURNAMENT_K):
    """Pick the best gene out of k random contestants."""
    contestants = random.sample(scored, k)
    return max(contestants, key=lambda x: x[0])[1]

# ── Main loop ──────────────────────────────────────────────────────────────────
def evolve():
    seed       = [int(c) for c in "01000000011101000103123323223213223233313313213311"]
    population = [seed] + [random_gene() for _ in range(POP_SIZE - 1)]

    best_gene     = None
    best_fit      = float('-inf')
    stagnant      = 0
    mutation_rate = MUTATION_RATE

    for gen in range(GENERATIONS):
        # score with no diversity bonus first pass to get elites
        scored = [(fitness(g), g) for g in population]
        scored.sort(reverse=True, key=lambda x: x[0])

        n_elites = max(2, int(POP_SIZE * ELITE_FRAC))
        elites   = [g for _, g in scored[:n_elites]]

        # re-score full population with diversity bonus
        scored = [(fitness(g, elites=elites), g) for g in population]
        scored.sort(reverse=True, key=lambda x: x[0])

        gen_best_fit, gen_best_gene = scored[0]

        if gen_best_fit > best_fit:
            best_fit      = gen_best_fit
            best_gene     = gen_best_gene
            stagnant      = 0
            mutation_rate = MUTATION_RATE
            print(f"Gen {gen:>4} | ✓ New best: {best_fit:.1f} | {''.join(map(str, best_gene))}")
        else:
            stagnant += 1
            print(f"Gen {gen:>4} | Best: {best_fit:.1f} | Stagnant: {stagnant}")

        # ramp up mutation when stuck
        if stagnant > 15:
            mutation_rate = min(0.35, mutation_rate * 1.1)

        # inject fresh random genes when stuck
        if stagnant > 25:
            print(f"  >> Injecting fresh genes (mutation={mutation_rate:.2f})")
            scored = scored[:POP_SIZE // 2]
            for _ in range(POP_SIZE // 2):
                scored.append((float('-inf'), random_gene()))

        # hard restart around best gene when very stuck
        if stagnant > 45:
            print(f"  >> Hard restart around best gene")
            population    = [best_gene] + [mutate(best_gene, rate=0.25) for _ in range(POP_SIZE - 1)]
            stagnant      = 0
            mutation_rate = MUTATION_RATE
            continue

        # ── Build next generation ──────────────────────────────────────────────
        next_gen = elites[:]  # elites carry over unchanged

        # fill remaining slots via tournament selection + crossover + mutation
        while len(next_gen) < POP_SIZE:
            a     = tournament_select(scored)
            b     = tournament_select(scored)
            child = mutate(crossover(a, b), rate=mutation_rate)
            next_gen.append(child)

        population = next_gen

    return best_gene, best_fit

# ── Final eval ─────────────────────────────────────────────────────────────────
def main():
    best_gene, approx_fit = evolve()

    print("\n--- Final Evaluation (all opponents, 30 trials each) ---")
    true_fit = fitness(best_gene, trials=TRIALS_FINAL)
    print(f"Fitness: {true_fit:.2f}")
    print(f"Gene:    {''.join(map(str, best_gene))}")

    print("\nBattle results:")
    for name, g_str in OPPONENTS.items():
        opp    = [int(c) for c in g_str]
        r, m, o = _PyPacwar.battle(best_gene, opp)
        result  = "WIN " if o == 0 else "LOSS" if m == 0 else "DRAW"
        print(f"  {result} vs {name:<15} | rounds={r} mine={m} opp={o}")

if __name__ == "__main__":
    main()