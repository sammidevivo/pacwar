"""
Stage 1 — Baseline Filter
=========================
Generate random genomes and hill-climb them until they score >= PASS_THRESHOLD
(out of 40) against All-1s and All-3s combined.

Keeps running batches until TARGET_SURVIVORS qualifying genomes are found.
Saves to stage1_results.json immediately every time a survivor is found,
so Ctrl+C at any point leaves a valid file ready for Stage 2.

If a candidate scores >= RETRY_THRESHOLD after the initial hill climb,
it keeps getting extra hill-climb passes until it hits PASS_THRESHOLD
or stops improving.

Usage:
    python stage1_baseline.py
"""

import time
from utils import (
    random_genome, hill_climb, score_battle,
    genome_to_str, save_results, total_score_vs
)

# ── Parameters ──────────────────────────────────────────────────────────────
TARGET_SURVIVORS   = 20      # how many passing genomes we want
PASS_THRESHOLD     = 38      # out of 40  — must reach this to be a survivor
RETRY_THRESHOLD    = 30      # if score >= this, keep trying extra passes
HILL_CLIMB_ROUNDS  = 80      # rounds per hill-climb pass
VARIANTS_PER_ROUND = 30      # mutations tested each round
NUM_MUTATIONS      = 3       # genes changed per mutation
MAX_ATTEMPTS       = 500     # safety cap on total candidates tried
MAX_RETRY_PASSES   = 10      # max extra passes before giving up on a candidate
# ────────────────────────────────────────────────────────────────────────────

OPPONENTS = [
    [1] * 50,   # All 1s
    [3] * 50,   # All 3s
]

OPPONENT_NAMES = ["All 1s", "All 3s"]


def evaluate(genome):
    """Return (total_score, per-opponent breakdown)."""
    breakdown = {}
    total = 0
    for name, opp in zip(OPPONENT_NAMES, OPPONENTS):
        s, rounds, c1, c2 = score_battle(genome, opp)
        breakdown[name] = {'score': s, 'rounds': rounds, 'c1': c1, 'c2': c2}
        total += s
    return total, breakdown


def print_breakdown(total, breakdown):
    print(f"  Total: {total}/40")
    for name, info in breakdown.items():
        result = "WIN" if info['c1'] > info['c2'] else ("LOSS" if info['c2'] > info['c1'] else "TIE")
        print(f"    vs {name}: {info['score']:2d}/20  "
              f"Rounds={info['rounds']:3d}  "
              f"You={info['c1']:3d} Them={info['c2']:3d}  [{result}]")


def main():
    print("=" * 65)
    print("STAGE 1 — BASELINE FILTER (All 1s & All 3s)")
    print("=" * 65)
    print(f"Target survivors : {TARGET_SURVIVORS}")
    print(f"Pass threshold   : {PASS_THRESHOLD}/40")
    print(f"Retry threshold  : {RETRY_THRESHOLD}/40  (keep trying if score >= this)")
    print(f"Max retry passes : {MAX_RETRY_PASSES}")
    print(f"Hill-climb rounds: {HILL_CLIMB_ROUNDS} per pass")
    print(f"Variants/round   : {VARIANTS_PER_ROUND}")
    print(f"Saves after each survivor — Ctrl+C safe!")
    print("=" * 65)

    survivors = []
    attempt = 0
    t0 = time.time()

    while len(survivors) < TARGET_SURVIVORS and attempt < MAX_ATTEMPTS:
        attempt += 1
        print(f"\n── Candidate #{attempt}  "
              f"(survivors so far: {len(survivors)}/{TARGET_SURVIVORS}) ──")

        seed = random_genome()
        seed_score = total_score_vs(seed, OPPONENTS)
        print(f"  Seed score: {seed_score}/40")

        # Initial hill-climb pass
        best, best_score = hill_climb(
            seed,
            OPPONENTS,
            num_rounds=HILL_CLIMB_ROUNDS,
            num_variants=VARIANTS_PER_ROUND,
            num_mutations=NUM_MUTATIONS,
            verbose=True,
            label=f"cand#{attempt} pass 1",
        )

        # If promising but not there yet, keep giving it extra passes
        if RETRY_THRESHOLD <= best_score < PASS_THRESHOLD:
            print(f"  Score {best_score}/40 >= retry threshold {RETRY_THRESHOLD} — running extra passes...")

            for retry in range(2, MAX_RETRY_PASSES + 2):
                prev_score = best_score
                best, best_score = hill_climb(
                    best,
                    OPPONENTS,
                    num_rounds=HILL_CLIMB_ROUNDS,
                    num_variants=VARIANTS_PER_ROUND,
                    num_mutations=NUM_MUTATIONS,
                    verbose=True,
                    label=f"cand#{attempt} pass {retry}",
                )

                print(f"  Pass {retry} finished: {best_score}/40")

                if best_score >= PASS_THRESHOLD:
                    break  # Made it!

                if best_score <= prev_score:
                    print(f"  No improvement (still {best_score}/40) — giving up on this candidate")
                    break

        total, breakdown = evaluate(best)
        print(f"\n  Final result for candidate #{attempt}:")
        print_breakdown(total, breakdown)
        print(f"  Genome: {genome_to_str(best)}")

        if total >= PASS_THRESHOLD:
            print(f"  PASSES ({total}/40 >= {PASS_THRESHOLD}) — survivor #{len(survivors)+1}")
            survivors.append({
                'genome': best,
                'score_stage1': total,
                'breakdown_stage1': breakdown,
                'candidate_num': attempt,
            })
            # Save immediately after every survivor
            save_results("stage1_results.json", survivors)
            print(f"  Saved {len(survivors)} survivor(s) to stage1_results.json")
        else:
            print(f"  Does not pass ({total}/40 < {PASS_THRESHOLD})")

    elapsed = time.time() - t0
    print(f"\n{'='*65}")
    print(f"STAGE 1 COMPLETE — {len(survivors)} survivors found "
          f"in {attempt} attempts ({elapsed:.1f}s)")
    print("=" * 65)

    print("\nSurvivor Summary:")
    print(f"  {'#':>3}  {'Score':>7}  Genome")
    print(f"  {'─'*3}  {'─'*7}  {'─'*50}")
    for i, s in enumerate(survivors, 1):
        print(f"  {i:3d}  {s['score_stage1']:4d}/40  {genome_to_str(s['genome'])}")

    print("\nRun stage2_last_year.py next.")


if __name__ == "__main__":
    main()