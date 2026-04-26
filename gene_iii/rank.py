"""
Runs every genome in genomes.json against every other genome (round-robin).
Ranks by total points scored. Good for spotting which genomes have the most
potential to be evolved further.

Run: py -3.11 rank.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from utils import load_genome_bank, score_battle, genome_to_str

def rank():
    bank = load_genome_bank()
    n = len(bank)
    total_battles = n * (n - 1) // 2

    print(f"Round-robin: {n} genomes, {total_battles} battles")
    print()

    # track points, wins, losses, ties per genome
    records = {name: dict(pts=0, w=0, l=0, t=0) for name, _ in bank}

    done = 0
    for i in range(n):
        name_i, g_i = bank[i]
        for j in range(i + 1, n):
            name_j, g_j = bank[j]
            score_i, _, c1, c2 = score_battle(g_i, g_j)
            score_j = 20 - score_i  # symmetric

            records[name_i]['pts'] += score_i
            records[name_j]['pts'] += score_j

            if c1 > c2:
                records[name_i]['w'] += 1
                records[name_j]['l'] += 1
            elif c2 > c1:
                records[name_j]['w'] += 1
                records[name_i]['l'] += 1
            else:
                records[name_i]['t'] += 1
                records[name_j]['t'] += 1

            done += 1
            if done % 200 == 0:
                print(f"  {done}/{total_battles} battles done...")

    # sort by total points
    ranked = sorted(records.items(), key=lambda x: x[1]['pts'], reverse=True)
    max_pts = (n - 1) * 20

    print()
    print(f"{'Rank':<5} {'Name':<25} {'Pts':>6} {'Max':>6} {'Pct':>6}  {'W':>4} {'L':>4} {'T':>4}  Genome")
    print("-" * 100)

    for rank, (name, rec) in enumerate(ranked, 1):
        genome_str = genome_to_str(dict(bank)[name])
        pct = rec['pts'] / max_pts * 100
        print(f"{rank:<5} {name:<25} {rec['pts']:>6} {max_pts:>6} {pct:>5.1f}%  "
              f"{rec['w']:>4} {rec['l']:>4} {rec['t']:>4}  {genome_str}")

    print()
    print(f"Max possible points per genome: {max_pts}")
    return ranked


if __name__ == "__main__":
    rank()
