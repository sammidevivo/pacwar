import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import _PyPacwar

def score_battle(genome1, genome2):
    """Score a single battle using the professor's system"""
    rounds, c1, c2 = _PyPacwar.battle(genome1, genome2)
    
    # genome1 destroyed genome2
    if c2 == 0 and c1 > 0:
        if rounds < 100:
            return 20, rounds, c1, c2
        elif rounds < 200:
            return 19, rounds, c1, c2
        elif rounds < 300:
            return 18, rounds, c1, c2
        else:  # 300-500
            return 17, rounds, c1, c2
    
    # genome2 destroyed genome1
    elif c1 == 0 and c2 > 0:
        if rounds < 100:
            return 0, rounds, c1, c2
        elif rounds < 200:
            return 1, rounds, c1, c2
        elif rounds < 300:
            return 2, rounds, c1, c2
        else:  # 300-500
            return 3, rounds, c1, c2
    
    # Neither destroyed after 500 rounds - use population ratio
    else:
        if c1 == 0 and c2 == 0:
            return 10, rounds, c1, c2
        elif c1 == 0:
            return 0, rounds, c1, c2
        elif c2 == 0:
            return 20, rounds, c1, c2
        else:
            ratio = c1 / c2
            if ratio >= 10:
                return 13, rounds, c1, c2
            elif ratio >= 3:
                return 12, rounds, c1, c2
            elif ratio >= 1.5:
                return 11, rounds, c1, c2
            elif ratio <= 1/10:
                return 7, rounds, c1, c2
            elif ratio <= 1/3:
                return 8, rounds, c1, c2
            elif ratio <= 1/1.5:
                return 9, rounds, c1, c2
            else:
                return 10, rounds, c1, c2

def round_robin_tournament(padawans):
    """
    Run a complete round-robin tournament.
    Each padawan battles every other padawan once.
    
    padawans: dict mapping name -> genome (as list of ints)
    
    Returns: list of (name, total_points, wins, losses, ties, details)
    """
    
    names = list(padawans.keys())
    num_padawans = len(names)
    
    print(f"round-robin: {num_padawans} competitors, {num_padawans * (num_padawans - 1) // 2} battles")

    
    # Initialize records
    records = {name: {
        'total_points': 0,
        'wins': 0,
        'losses': 0,
        'ties': 0,
        'battles': []  # (opponent, result, score, rounds, c1, c2)
    } for name in names}
    
    # Run all battles
    battle_count = 0
    total_battles = num_padawans * (num_padawans - 1) // 2
    
    for i in range(num_padawans):
        for j in range(i + 1, num_padawans):
            name1 = names[i]
            name2 = names[j]
            genome1 = padawans[name1]
            genome2 = padawans[name2]
            
            score1, rounds, c1, c2 = score_battle(genome1, genome2)
            score2 = 20 - score1  # Opponent gets remainder of 20 points
            
            # Determine result
            if c1 > c2:
                result1, result2 = 'WIN', 'LOSS'
                records[name1]['wins'] += 1
                records[name2]['losses'] += 1
            elif c2 > c1:
                result1, result2 = 'LOSS', 'WIN'
                records[name1]['losses'] += 1
                records[name2]['wins'] += 1
            else:
                result1, result2 = 'TIE', 'TIE'
                records[name1]['ties'] += 1
                records[name2]['ties'] += 1
            
            # Update points
            records[name1]['total_points'] += score1
            records[name2]['total_points'] += score2
            
            # Store battle details
            records[name1]['battles'].append((name2, result1, score1, rounds, c1, c2))
            records[name2]['battles'].append((name1, result2, score2, rounds, c2, c1))
            
            battle_count += 1
            if battle_count % 50 == 0:
                print(f"Progress: {battle_count}/{total_battles} battles complete...")
    
    print(f"All {total_battles} battles complete!")
    print()
    
    # Create rankings
    rankings = []
    for name in names:
        rec = records[name]
        rankings.append((
            name,
            rec['total_points'],
            rec['wins'],
            rec['losses'],
            rec['ties'],
            rec['battles']
        ))
    
    # Sort by total points (descending), then by wins (descending)
    rankings.sort(key=lambda x: (x[1], x[2]), reverse=True)
    
    return rankings

def display_rankings(rankings):
    """Display the tournament rankings"""
    
    print("FINAL RANKINGS")
    print()
    
    max_points = (len(rankings) - 1) * 20  # Maximum possible points
    
    for rank, (name, points, wins, losses, ties, battles) in enumerate(rankings, 1):
        total_battles = wins + losses + ties
        win_pct = (wins / total_battles * 100) if total_battles > 0 else 0
        
        print(f"Rank {rank:2d}: {name}")
        print(f"  Points: {points:4d}/{max_points} | "
              f"Record: {wins:2d}-{losses:2d}-{ties:2d} | "
              f"Win%: {win_pct:5.1f}%")
        print()

def display_detailed_results(rankings, top_n=5):
    """Display detailed matchup results for top N padawans"""
    
    print("=" * 70)
    print(f"DETAILED RESULTS - TOP {top_n} PADAWANS")
    print("=" * 70)
    
    for rank, (name, points, wins, losses, ties, battles) in enumerate(rankings[:top_n], 1):
        print(f"\n{'='*70}")
        print(f"RANK #{rank}: {name}")
        print(f"Total Points: {points} | Record: {wins}-{losses}-{ties}")
        print(f"{'='*70}")
        
        # Sort battles by score (highest first for wins, lowest first for losses)
        battles_sorted = sorted(battles, key=lambda x: (x[1] != 'WIN', -x[2], x[3]))
        
        # Show best wins
        best_wins = [b for b in battles_sorted if b[1] == 'WIN'][:5]
        if best_wins:
            print(f"\n  Best Victories:")
            for opp, result, score, rounds, c1, c2 in best_wins:
                print(f"    vs {opp:8s}: Score={score:2d}/20, "
                      f"Rounds={rounds:3d}, Your={c1:3d}, Theirs={c2:3d}")
        
        # Show worst losses
        worst_losses = [b for b in battles if b[1] == 'LOSS']
        worst_losses.sort(key=lambda x: x[2])  # Sort by score (lowest = worst)
        worst_losses = worst_losses[:5]
        
        if worst_losses:
            print(f"\n  Worst Defeats:")
            for opp, result, score, rounds, c1, c2 in worst_losses:
                print(f"    vs {opp:8s}: Score={score:2d}/20, "
                      f"Rounds={rounds:3d}, Your={c1:3d}, Theirs={c2:3d}")

def main():
    """Main tournament function"""
    
    # Define all 32 padawans
    padawans = {
        # STAGE 3 RESULTS
        "S3-1":  [0,1,3,0,0,0,0,0,1,0,1,0,2,0,0,0,0,0,3,1,1,3,3,3,2,3,3,2,3,3,2,2,2,3,2,3,3,3,3,1,3,3,1,0,3,1,3,3,1,0],
        "S3-2":  [0,3,1,0,0,0,0,0,0,3,1,1,2,0,0,0,3,3,3,0,3,2,1,1,2,1,1,3,3,1,2,1,0,2,1,1,2,1,1,3,1,1,3,1,1,2,3,1,2,1],
        "S3-3":  [0,3,1,0,0,0,0,0,1,0,0,1,2,0,0,0,3,3,3,3,3,2,1,1,2,1,1,2,1,1,1,1,1,2,2,1,2,2,1,3,1,1,3,0,3,0,0,1,3,1],
        "S3-4":  [0,3,1,0,0,0,0,0,0,1,1,1,2,0,2,3,3,3,3,3,3,2,1,1,2,1,1,2,1,1,1,1,1,1,1,2,2,2,1,3,1,1,3,1,0,1,1,1,3,0],
        "S3-5":  [0,3,1,0,0,0,0,0,1,0,1,0,1,3,0,0,3,3,0,3,3,1,1,1,2,1,1,2,1,1,1,2,3,2,0,1,2,2,1,3,1,1,3,0,1,3,0,1,3,1],
        "S3-6":  [0,1,3,0,0,0,0,0,1,1,0,3,2,0,0,0,0,3,3,3,1,3,3,3,2,3,3,2,3,3,2,0,3,2,3,3,2,3,3,1,0,3,0,0,3,1,0,3,1,3],
        "S3-7":  [0,3,1,0,0,0,0,0,1,0,1,1,2,1,1,0,3,3,3,0,3,2,1,1,2,1,1,2,1,1,1,1,2,1,2,0,2,2,1,1,1,1,2,1,1,3,2,1,3,1],
        "S3-8":  [0,3,1,0,0,0,0,0,0,0,1,1,2,3,2,0,3,3,3,0,3,2,1,1,2,1,1,2,1,2,1,1,2,1,2,1,2,2,1,2,0,1,0,0,3,3,1,1,3,1],
        "S3-9":  [0,1,3,0,0,0,0,0,0,1,1,1,2,1,0,0,3,0,0,0,1,2,3,3,2,3,3,1,3,0,1,3,2,2,3,0,3,3,3,1,0,3,1,0,3,3,0,3,1,0],
        "S3-10": [0,1,3,0,0,0,3,0,1,1,1,1,2,0,3,0,0,3,3,0,1,2,3,3,2,3,0,2,3,3,2,3,3,2,2,0,2,3,3,1,3,3,1,3,2,3,2,3,2,3],
        "S3-11": [0,1,3,0,0,1,0,1,1,1,1,1,2,0,3,0,1,0,3,0,1,1,3,3,2,3,3,2,3,3,2,1,3,2,2,3,3,2,3,0,0,3,1,3,3,1,0,3,1,3],
        "S3-12": [0,1,3,0,0,0,0,0,0,1,1,1,1,0,3,1,0,3,0,3,1,1,3,3,2,3,3,2,3,2,2,3,3,2,3,3,3,3,3,2,3,3,1,0,1,2,0,3,1,0],
        "S3-13": [0,0,0,2,0,0,0,0,1,1,1,0,2,2,0,0,3,0,0,3,3,2,3,3,2,1,3,2,1,1,2,1,3,2,1,3,2,1,3,0,3,1,3,3,1,0,2,3,0,1],
        "S3-14": [0,0,0,0,0,0,0,0,0,1,1,0,2,2,2,2,3,3,3,3,3,3,2,1,3,3,1,3,3,2,3,3,2,3,3,2,3,3,1,0,3,1,0,3,3,3,3,1,0,3],
        "S3-15": [1,1,0,2,0,0,0,0,1,1,1,1,2,2,2,0,3,1,0,3,2,3,3,2,1,2,2,1,2,2,2,2,2,1,2,2,1,2,3,1,0,3,1,0,0,1,0,3,1,1],
        "S3-16": [3,3,1,3,0,3,0,3,1,1,1,1,2,0,0,0,3,3,3,0,1,2,3,1,2,3,1,2,3,1,2,3,1,2,3,1,2,3,3,1,3,1,1,0,1,2,1,3,1,3],
        "S3-17": [0,3,1,3,1,3,3,3,1,3,1,0,2,3,0,0,0,3,3,3,1,1,2,1,2,2,1,2,3,1,2,1,0,2,2,1,2,3,1,2,0,1,2,0,3,1,3,1,2,3],
        "S3-18": [3,1,0,0,0,0,0,0,1,1,1,1,2,2,2,0,3,3,3,3,2,3,1,2,3,2,2,1,2,2,3,2,2,3,1,2,1,2,2,3,1,1,3,0,0,0,0,3,3,1],
        "S3-19": [1,0,0,2,0,0,0,0,1,1,1,1,2,0,2,0,0,0,0,3,2,3,2,2,1,2,1,1,3,1,1,2,2,1,2,3,1,2,3,1,3,3,1,0,2,0,0,3,1,1],
    }
    
    # Run tournament
    rankings = round_robin_tournament(padawans)
    
    # Display results
    display_rankings(rankings)
    display_detailed_results(rankings, top_n=10)
    
    # Print top 10 genomes for easy copying
    print("\n" + "=" * 70)
    print("TOP 10 GENOMES (for easy copying)")
    print("=" * 70)
    for rank, (name, points, wins, losses, ties, battles) in enumerate(rankings[:10], 1):
        genome = padawans[name]
        print(f"{rank:2d}. {name}: {''.join(str(g) for g in genome)}")
    
    return rankings

if __name__ == "__main__":
    rankings = main()