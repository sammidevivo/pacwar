import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import _PyPacwar
import random

def random_genome():
    """Generate a random genome of 50 genes (each 0-3)"""
    return [random.randint(0, 3) for _ in range(50)]

def battle_winner(g1, g2):
    """
    Battle two genomes and return the result.
    Returns: 1 if g1 wins, -1 if g2 wins, 0 for tie
    """
    rounds, c1, c2 = _PyPacwar.battle(g1, g2)
    if c1 > c2:
        return 1
    elif c2 > c1:
        return -1
    return 0

def round_robin_tournament(genomes):
    """
    Run a round-robin tournament where every genome battles every other genome.
    Returns list of (genome, wins, losses, ties) sorted by performance.
    """
    num_genomes = len(genomes)
    records = [[genome, 0, 0, 0] for genome in genomes]  # [genome, wins, losses, ties]
    
    print(f"Running round-robin tournament with {num_genomes} genomes...")
    print(f"Total battles: {num_genomes * (num_genomes - 1) // 2}")
    print()
    
    battle_count = 0
    total_battles = num_genomes * (num_genomes - 1) // 2
    
    for i in range(num_genomes):
        for j in range(i + 1, num_genomes):
            result = battle_winner(genomes[i], genomes[j])
            
            if result == 1:  # genome i wins
                records[i][1] += 1  # win
                records[j][2] += 1  # loss
            elif result == -1:  # genome j wins
                records[i][2] += 1  # loss
                records[j][1] += 1  # win
            else:  # tie
                records[i][3] += 1
                records[j][3] += 1
            
            battle_count += 1
            if battle_count % 100 == 0:
                print(f"Battles completed: {battle_count}/{total_battles}")
    
    # Sort by wins (descending), then by losses (ascending)
    records.sort(key=lambda x: (x[1], -x[2]), reverse=True)
    
    return records

def main():
    """Generate random genomes and find the best through tournament"""
    
    NUM_RANDOM_GENOMES = 100  # Adjust this number
    
    print("=" * 60)
    print("RANDOM GENOME TOURNAMENT")
    print("=" * 60)
    print()
    
    # Generate random genomes
    print(f"Generating {NUM_RANDOM_GENOMES} random genomes...")
    genomes = [random_genome() for _ in range(NUM_RANDOM_GENOMES)]
    
    # Add some baseline strategies for comparison

    winner = "31030312111111223210033233023123121023230333210213"
    genomes.append(list(map(int, winner)))
    # genomes.append([0] * 50)  # all 0s
    # genomes.append([1] * 50)  # all 1s
    # genomes.append([2] * 50)  # all 2s
    # genomes.append([3] * 50)  # all 3s
    

    
    print(f"Total genomes (including 4 baselines): {len(genomes)}")
    print()
    
    # Run tournament
    results = round_robin_tournament(genomes)
    
    # Display results
    print()
    print("=" * 60)
    print("TOURNAMENT RESULTS (Top 10)")
    print("=" * 60)
    print()
    
    for rank, (genome, wins, losses, ties) in enumerate(results[:10], 1):
        total = wins + losses + ties
        win_rate = wins / total * 100 if total > 0 else 0
        print(f"Rank {rank:2d}: W={wins:3d} L={losses:3d} T={ties:3d} "
              f"(Win Rate: {win_rate:.1f}%)")
        print(f"          Genome: {genome}")
        print()
    
    # Get the best genome
    best_genome = results[0][0]
    
    print("=" * 60)
    print("BEST GENOME:")
    print(best_genome)
    print("=" * 60)
    print()
    
    # Test best genome against baselines
    baselines = {
        "All 0s": [0] * 50,
        "All 1s": [1] * 50,
        "All 2s": [2] * 50,
        "All 3s": [3] * 50,
    }
    
    print("Testing best genome against baselines:")
    print("-" * 60)
    for name, baseline in baselines.items():
        rounds, c1, c2 = _PyPacwar.battle(best_genome, baseline)
        result = "WIN" if c1 > c2 else ("LOSS" if c2 > c1 else "TIE")
        print(f"{name:10s}: Your={c1:3d}, Theirs={c2:3d}, Rounds={rounds:3d} [{result}]")
    
    print()
    print("Best genome as string:")
    print(''.join(str(g) for g in best_genome))
    
    return best_genome

if __name__ == "__main__":
    best = main()