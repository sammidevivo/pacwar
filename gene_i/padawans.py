import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import _PyPacwar
import random

def random_genome():
    """Generate a random genome of 50 genes (each 0-3)"""
    return [random.randint(0, 3) for _ in range(50)]

def mutate_genome(genome, num_mutations=1):
    """Create a mutated copy of a genome by changing num_mutations random genes"""
    mutated = genome[:]
    positions = random.sample(range(50), num_mutations)
    for pos in positions:
        mutated[pos] = random.randint(0, 3)
    return mutated

def score_battle(genome1, genome2):
    """Score a single battle using the professor's system"""
    rounds, c1, c2 = _PyPacwar.battle(genome1, genome2)
    
    # genome1 destroyed genome2
    if c2 == 0 and c1 > 0:
        if rounds < 100:
            return 20, rounds
        elif rounds < 200:
            return 19, rounds
        elif rounds < 300:
            return 18, rounds
        else:  # 300-500
            return 17, rounds
    
    # genome2 destroyed genome1
    elif c1 == 0 and c2 > 0:
        if rounds < 100:
            return 0, rounds
        elif rounds < 200:
            return 1, rounds
        elif rounds < 300:
            return 2, rounds
        else:  # 300-500
            return 3, rounds
    
    # Neither destroyed after 500 rounds - use population ratio
    else:
        if c1 == 0 and c2 == 0:
            return 10, rounds
        elif c1 == 0:
            return 0, rounds
        elif c2 == 0:
            return 20, rounds
        else:
            ratio = c1 / c2
            if ratio >= 10:
                return 13, rounds
            elif ratio >= 3:
                return 12, rounds
            elif ratio >= 1.5:
                return 11, rounds
            elif ratio <= 1/10:
                return 7, rounds
            elif ratio <= 1/3:
                return 8, rounds
            elif ratio <= 1/1.5:
                return 9, rounds
            else:
                return 10, rounds

def evolve_padawan(base_genome, base_name, num_rounds=50, num_variants=30, num_mutations=3):
    """
    Evolve a single padawan from a base genome.
    Only tests against all_0s, all_1s, all_2s, all_3s.
    Returns the best genome found and its performance stats.
    """
    BASELINES = {
        "All 0s": [0] * 50,
        "All 1s": [1] * 50,
        "All 2s": [2] * 50,
        "All 3s": [3] * 50,
    }
    
    print(f"\n{'='*70}")
    print(f"EVOLVING PADAWAN FROM: {base_name}")
    print(f"{'='*70}")
    
    current_best = base_genome[:]
    all_time_best = base_genome[:]
    all_time_best_score = 0
    
    for round_num in range(num_rounds):
        # Generate variants by mutating current best
        variants = [mutate_genome(current_best, num_mutations) 
                   for _ in range(num_variants)]
        variants.append(current_best)  # Include current best
        
        results = []
        
        # Test each variant against all baselines
        for variant in variants:
            total_score = 0
            
            for baseline_name, baseline in BASELINES.items():
                score, _ = score_battle(variant, baseline)
                total_score += score
            
            results.append((variant, total_score))
        
        # Sort by score
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Update current best
        round_best, round_best_score = results[0]
        
        if round_best_score > all_time_best_score:
            all_time_best = round_best[:]
            all_time_best_score = round_best_score
            print(f"  Round {round_num + 1:3d}: NEW BEST! Score={all_time_best_score}/80")
        
        current_best = round_best
    
    # Get detailed stats for the best genome
    stats = {}
    for baseline_name, baseline in BASELINES.items():
        score, rounds = score_battle(all_time_best, baseline)
        rounds_actual, c1, c2 = _PyPacwar.battle(all_time_best, baseline)
        stats[baseline_name] = {
            'score': score,
            'rounds': rounds,
            'your_count': c1,
            'their_count': c2,
            'result': 'WIN' if c1 > c2 else ('LOSS' if c2 > c1 else 'TIE')
        }
    
    print(f"\n  Final Score: {all_time_best_score}/80")
    print(f"  Genome: {''.join(str(g) for g in all_time_best)}")
    
    return all_time_best, all_time_best_score, stats

def train_padawans():
    """
    Train multiple padawans from different base genomes.
    Goal: Find 50 genomes that can defeat all_0s, all_1s, all_2s, all_3s.
    """
    
    NUM_ROUNDS = 100           # Rounds of evolution per base
    NUM_VARIANTS = 30         # Variants to test per round
    NUM_MUTATIONS = 3         # Mutations per variant
    NUM_PADAWANS_PER_BASE = 3 # How many times to evolve from each base

    print(f"training padawans: rounds={NUM_ROUNDS} variants={NUM_VARIANTS} mut={NUM_MUTATIONS}")

    all_padawans = []

    while len(all_padawans) < 3:
        base_genome = random_genome()

        base_name = "RANDOM"

        for padawan_num in range(NUM_PADAWANS_PER_BASE):
            padawan_name = f"{base_name} - Padawan {padawan_num + 1}"
            
            genome, score, stats = evolve_padawan(
                base_genome, 
                padawan_name,
                num_rounds=NUM_ROUNDS,
                num_variants=NUM_VARIANTS,
                num_mutations=NUM_MUTATIONS
            )

            if score >= 78:
                print("NEW PADAWAN FOUND " + str(len(all_padawans)) + "/20")
                all_padawans.append({
                    'name': padawan_name,
                    'base': base_name,
                    'genome': genome,
                    'total_score': score,
                    'stats': stats
                })       
        
    
    print("\n" + "=" * 70)
    print("ALL PADAWANS - FINAL RANKINGS")
    print("=" * 70)
    
    # Sort by total score
    all_padawans.sort(key=lambda x: x['total_score'], reverse=True)
    
    # Display all padawans
    for rank, padawan in enumerate(all_padawans, 1):
        print(f"\n{'='*70}")
        print(f"RANK #{rank}: {padawan['name']}")
        print(f"Base Genome: {padawan['base']}")
        print(f"Total Score: {padawan['total_score']}/80")
        print(f"Genome: {''.join(str(g) for g in padawan['genome'])}")
        print(f"{'-'*70}")
        
        # Show performance against each baseline
        for baseline_name in ["All 0s", "All 1s", "All 2s", "All 3s"]:
            stat = padawan['stats'][baseline_name]
            print(f"  {baseline_name:8s}: {stat['result']:4s} | "
                  f"Score={stat['score']:2d}/20 | "
                  f"Rounds={stat['rounds']:3d} | "
                  f"Your={stat['your_count']:3d}, Theirs={stat['their_count']:3d}")
    
    perfect_padawans = [p for p in all_padawans if p['total_score'] == 80]
    
    if perfect_padawans:
        print("\n" + "=" * 70)
        print(f" PERFECT PADAWANS (80/80): {len(perfect_padawans)}")
        print("=" * 70)
        for p in perfect_padawans:
            print(f"\n{p['name']} (from {p['base']})")
            print(f"  {''.join(str(g) for g in p['genome'])}")
    
    print("\n" + "=" * 70)
    print("SUMMARY BY BASE GENOME")
    print("=" * 70)
    
    for base_name in base_genomes.keys():
        base_padawans = [p for p in all_padawans if p['base'] == base_name]
        avg_score = sum(p['total_score'] for p in base_padawans) / len(base_padawans)
        best_score = max(p['total_score'] for p in base_padawans)
        
        print(f"{base_name:20s}: Avg={avg_score:.1f}/80, Best={best_score}/80")
    
    print("\n" + "=" * 70)
    
    return all_padawans

if __name__ == "__main__":
    padawans = train_padawans()