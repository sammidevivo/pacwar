import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import _PyPacwar
import random
import json

GENOMES_FILE = os.path.join(os.path.dirname(__file__), 'genomes.json')

# ── Genome helpers ────────────────────────────────────────────────────────────

def random_genome():
    return [random.randint(0, 3) for _ in range(50)]

def mutate_genome(genome, num_mutations=3):
    mutated = genome[:]
    for pos in random.sample(range(50), num_mutations):
        mutated[pos] = random.randint(0, 3)
    return mutated

def genome_to_str(genome):
    return ''.join(str(g) for g in genome)

def str_to_genome(s):
    return list(map(int, s))

# ── Scoring ───────────────────────────────────────────────────────────────────

def score_battle(genome1, genome2):
    """Returns (score, rounds, c1, c2). Score is 0-20 per professor's system."""
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
        if   ratio >= 10:    return 13, rounds, c1, c2
        elif ratio >= 3:     return 12, rounds, c1, c2
        elif ratio >= 1.5:   return 11, rounds, c1, c2
        elif ratio <= 1/10:  return  7, rounds, c1, c2
        elif ratio <= 1/3:   return  8, rounds, c1, c2
        elif ratio <= 1/1.5: return  9, rounds, c1, c2
        else:                return 10, rounds, c1, c2

def total_score_vs(genome, opponents):
    return sum(score_battle(genome, opp)[0] for opp in opponents)

# ── Hill climber ──────────────────────────────────────────────────────────────

def hill_climb(start_genome, opponents, num_rounds=60, num_variants=30,
               num_mutations=3, verbose=True, label=""):
    current = start_genome[:]
    best = current[:]
    best_score = total_score_vs(current, opponents)

    for rnd in range(num_rounds):
        variants = [mutate_genome(current, num_mutations) for _ in range(num_variants)]
        variants.append(current)
        top_genome, top_score = max(
            ((v, total_score_vs(v, opponents)) for v in variants),
            key=lambda x: x[1]
        )
        if top_score > best_score:
            best, best_score = top_genome[:], top_score
            if verbose:
                print(f"  [{label}] Round {rnd+1:3d}: NEW BEST {best_score}/{len(opponents)*20}")
        current = top_genome[:]

    return best, best_score

# ── Genome registry ───────────────────────────────────────────────────────────

def load_genome_bank():
    """Returns list of (name, genome_list) from genomes.json."""
    if not os.path.exists(GENOMES_FILE):
        print(f"Warning: {GENOMES_FILE} not found. Using empty bank.")
        return []
    with open(GENOMES_FILE) as f:
        data = json.load(f)
    return [(entry['name'], str_to_genome(entry['genome'])) for entry in data]

def save_new_genome(name, genome, tags=None):
    """Append a genome to genomes.json. Skips if the genome string already exists."""
    genome_str = genome_to_str(genome)
    if os.path.exists(GENOMES_FILE):
        with open(GENOMES_FILE) as f:
            data = json.load(f)
    else:
        data = []

    for entry in data:
        if entry['genome'] == genome_str:
            print(f"  (already in registry as '{entry['name']}')")
            return False

    entry = {'name': name, 'genome': genome_str}
    if tags:
        entry['tags'] = tags
    data.append(entry)

    with open(GENOMES_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"  Saved '{name}' to genomes.json  [{genome_str}]")
    return True
