"""
Test a genome against every entry in genomes.json plus N random opponents.

Usage:
  - Set TEST_GENOME to the genome string you want to evaluate.
  - Set NUM_RANDOM_TESTS (default 10000).
  - Run: python test.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from utils import (
    random_genome, genome_to_str, str_to_genome,
    score_battle, load_genome_bank
)

# -- Config --------------------------------------------------------------------

TEST_GENOME      = "01000000010100000033123323223213223233313313323311"
NUM_RANDOM_TESTS = 10000

# -- Main ----------------------------------------------------------------------

def test(genome, num_random=10000):
    bank = load_genome_bank()

    print("=" * 70)
    print("GENOME TESTER")
    print("=" * 70)
    print(f"Genome : {genome_to_str(genome)}")
    print(f"Bank   : {len(bank)} known opponents")
    print(f"Randoms: {num_random}")
    print()

    wins, losses, ties = [], [], []
    total_pts = 0

    for name, opp in bank:
        score, rounds, c1, c2 = score_battle(genome, opp)
        total_pts += score
        rec = dict(name=name, score=score, rounds=rounds, c1=c1, c2=c2)
        if   c1 > c2: wins.append(rec)
        elif c2 > c1: losses.append(rec)
        else:         ties.append(rec)

    n   = len(bank)
    wr  = len(wins) / n * 100 if n else 0
    avg = total_pts / n if n else 0
    print(f"KNOWN  ({n:4d}):  {len(wins)}W  {len(losses)}L  {len(ties)}T  "
          f"({wr:.1f}% win rate)   {total_pts}/{n*20} pts  avg {avg:.2f}/20")

    rw = rl = rt = rpts = 0
    random_losses = []

    for i in range(num_random):
        opp = random_genome()
        score, rounds, c1, c2 = score_battle(genome, opp)
        rpts += score
        if   c1 > c2: rw += 1
        elif c2 > c1: rl += 1; random_losses.append(dict(genome=opp, score=score, rounds=rounds, c1=c1, c2=c2))
        else:         rt += 1
        if (i + 1) % 2500 == 0:
            print(f"  random progress: {i+1}/{num_random}...")

    rn   = num_random
    rwr  = rw / rn * 100 if rn else 0
    ravg = rpts / rn if rn else 0
    print(f"RANDOM ({rn:4d}):  {rw}W  {rl}L  {rt}T  "
          f"({rwr:.1f}% win rate)   {rpts}/{rn*20} pts  avg {ravg:.2f}/20")

    if losses:
        print(f"\n{'='*70}")
        print(f"LOSSES VS KNOWN  ({len(losses)})")
        print(f"{'='*70}")
        for r in sorted(losses, key=lambda x: x['score']):
            print(f"  {r['name']:22s}  score={r['score']:2d}/20  "
                  f"rounds={r['rounds']:3d}  you={r['c1']:3d}  them={r['c2']:3d}")

    if wins:
        print(f"\n{'='*70}")
        print(f"WINS VS KNOWN  ({len(wins)})")
        print(f"{'='*70}")
        for r in sorted(wins, key=lambda x: -x['score']):
            print(f"  {r['name']:22s}  score={r['score']:2d}/20  "
                  f"rounds={r['rounds']:3d}  you={r['c1']:3d}  them={r['c2']:3d}")

    if random_losses:
        print(f"\n{'='*70}")
        print(f"RANDOM GENOMES THAT BEAT YOU  ({len(random_losses)})  — showing worst 20")
        print(f"{'='*70}")
        for r in sorted(random_losses, key=lambda x: x['score'])[:20]:
            print(f"  {genome_to_str(r['genome'])}  score={r['score']:2d}/20  "
                  f"rounds={r['rounds']:3d}  you={r['c1']:3d}  them={r['c2']:3d}")

    print()
    return dict(wins=wins, losses=losses, ties=ties, total_pts=total_pts,
                rw=rw, rl=rl, rt=rt, rpts=rpts, random_losses=random_losses)


if __name__ == "__main__":
    g = str_to_genome(TEST_GENOME)
    test(g, num_random=NUM_RANDOM_TESTS)
