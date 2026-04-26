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

def fitness(genome, opponents):
    """
    Calculate fitness by battling against a set of opponents.
    Returns win rate (wins + 0.5*ties).
    """
    score = 0
    for opp in opponents:
        result = battle_winner(genome, opp)
        if result == 1:
            score += 1
        elif result == 0:
            score += 0.5
    return score

def crossover(parent1, parent2):
    """Single-point crossover"""
    point = random.randint(1, 49)
    return parent1[:point] + parent2[point:]

def mutate(genome, mutation_rate=0.02):
    """Mutate each gene with given probability"""
    return [random.randint(0, 3) if random.random() < mutation_rate else gene 
            for gene in genome]

def evolve():
    """Main genetic algorithm"""
    # Parameters
    POPULATION_SIZE = 80
    GENERATIONS = 100
    ELITE_SIZE = 8
    MUTATION_RATE = 0.1
    TOURNAMENT_SIZE = 10  # How many opponents to test against
    
    # Initialize population
    population = [random_genome() for _ in range(POPULATION_SIZE)]
    
    # Add some known baselines to the initial population
    # best_so_far = "21002101131022310110222013202331213120133210323323"
    # second_best = "00011210101322202031221131202023232312321100132232"
    # population[0] = list(map(int, best_so_far))
    # population[1] = list(map(int, second_best))
    
    best_ever_genome = None
    best_ever_score = -1
    
    print(f"evolving: pop={POPULATION_SIZE} gen={GENERATIONS} elite={ELITE_SIZE} mut={MUTATION_RATE}")

    for gen in range(GENERATIONS):
        scores = []
        for i, genome in enumerate(population):
            # Select random opponents (excluding self)
            other_indices = list(range(i)) + list(range(i+1, POPULATION_SIZE))
            opponent_indices = random.sample(other_indices, min(TOURNAMENT_SIZE, len(other_indices)))
            opponents = [population[j] for j in opponent_indices]
            
            score = fitness(genome, opponents)
            scores.append(score)
        
        ranked = sorted(zip(population, scores), key=lambda x: x[1], reverse=True)
        population_sorted = [genome for genome, score in ranked]
        scores_sorted = [score for genome, score in ranked]
        
        if scores_sorted[0] > best_ever_score:
            best_ever_score = scores_sorted[0]
            print("new best!")
            best_ever_genome = population_sorted[0][:]
        
        avg_score = sum(scores) / len(scores)
        print(f"Gen {gen:3d}: Best={scores_sorted[0]:.2f}/{TOURNAMENT_SIZE}, "
              f"Avg={avg_score:.2f}, "
              f"Worst={scores_sorted[-1]:.2f}")
        
        elite = population_sorted[:ELITE_SIZE]

        children = []
        while len(children) < POPULATION_SIZE - ELITE_SIZE:
            # Select two parents from elite (could also do tournament selection)
            parent1, parent2 = random.sample(elite, 2)
            child = crossover(parent1, parent2)
            child = mutate(child, MUTATION_RATE)
            children.append(child)
        
        population = elite + children
    
    print("-" * 60)
    print("Evolution complete!")
    print()
    
    best_genome = best_ever_genome
    
    print("=" * 60)
    print("BEST GENOME FOUND:")
    print(best_genome)
    print("=" * 60)
    print()
    
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
    return best_genome

if __name__ == "__main__":
    best = evolve()
    
    print()
    print("Copy this genome for submission:")
    print(''.join(str(g) for g in best))