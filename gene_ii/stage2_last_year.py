"""
Stage 2 — Last Year's Checkpoint
=================================
Loads Stage 1 survivors and hill-climbs each one against the 29 known genomes
from last year's checkpoint.

The fitness function is the *total professor-score* across all 29 opponents
(max = 29 × 20 = 580).  The All-1s / All-3s opponents are also kept in the
mix so gains from Stage 1 are not lost.

Saves the top survivors (by Stage-2 score) to stage2_results.json.

Usage:
    python stage2_last_year.py
"""

import time
from utils import (
    hill_climb, score_battle, genome_to_str,
    save_results, load_results, total_score_vs, str_to_genome
)

# -- Parameters --------------------------------------------------------------
HILL_CLIMB_ROUNDS  = 100
VARIANTS_PER_ROUND = 30
NUM_MUTATIONS      = 3
TOP_N_TO_SAVE      = 20     # how many to pass to Stage 3
# ----------------------------------------------------------------------------

LAST_YEAR_GENOMES = {
    "HappyGene":      "03133000111120113033313121022122121313331131101131",
    "3L1M0N4T0R":     "11121111111111313111031113111111113211113303131313",
    "Infecto":        "10111111111111111111110111111111111111111111111111",
    "Darwin":         "30100000111122203333210132112202332202111132331301",
    "Geneus":         "30333333333333333333333333333333333333333333333333",
    "NewJeans":       "33333333333333333333333333333333333333100100100100",
    "Juju":           "00000000000000003333333333111111222333111000000333",
    "Paccident":      "10112310231121101111101111111222232111212220232111",
    "Zacho":          "01303320323303122003303323023131022332211230203113",
    "philip":         "03103120003232202033331121112113212203131131312330",
    "RNG4TheWin":     "0000000011112222333311100011112223330000111222333000",
    "DLPT":           "10113012131111111011111111111120111112102111323101",
    "PAC_MIGHT":      "00020000101120220030121123121113123323202303101310",
    "JT":             "10111111111111111111123111111111111111111111111111",
    "garen":          "03100200113122303003322121033122112212111110113321",
    "GeneWildest":    "33020000111122203330212232211232232232130130032331",
    "MiteOfMight":    "30333320101123233333112111311112111301333330313311",
    "geneureka":      "30333333133333333333333333333333333313333333333303",
    "PixelPredator":  "00330300131322233333333133333333333333113113111110",
    "DarkHorse":      "01000000010300000103133323223213223233313313323313",
    "pizzapizza":     "3333111111111111111133311133333333333311111111111",
    "fmh":            "33333333333333333333230333333333333333333333000000",
    "cybergene":      "33333333333333333333333333222222222222222333333333",
    "EuGene":         "10111111111113111111111111111111111111111111311111",
    "GeneSimmons":    "13021100131122313300222221121220131111123100031331",
    "PacWarrior":     "33113313011021113313113223323123310123311223020300",
    "simpleGene":     "30333333333333333333333333333333333333333333333333",
    "Krispy":         "11112222111122221111333111111222111333222111333111",
    "coolgeen":       "31321203032321230023222202333221321210301131121211",
}

BASELINE_OPPONENTS = [
    [1] * 50,
    [3] * 50,
]

def build_opponent_list():
    opps = []
    for name, s in LAST_YEAR_GENOMES.items():
        # RNG4TheWin has 51 chars — trim to 50
        opps.append(list(map(int, s[:50])))
    opps += BASELINE_OPPONENTS
    return opps


def detailed_report(genome, opponents, names):
    print(f"  {'Opponent':<16}  {'Score':>5}  {'Result':<5}  Rounds  You  Them")
    print(f"  {'-'*16}  {'-'*5}  {'-'*5}  {'-'*6}  {'-'*3}  {'-'*3}")
    total = 0
    for name, opp in zip(names, opponents):
        s, rounds, c1, c2 = score_battle(genome, opp)
        result = "WIN" if c1 > c2 else ("LOSS" if c2 > c1 else "TIE")
        print(f"  {name:<16}  {s:2d}/20  {result:<5}  {rounds:5d}  {c1:3d}  {c2:3d}")
        total += s
    print(f"  {'-'*55}")
    print(f"  {'TOTAL':<16}  {total}/{len(opponents)*20}")
    return total


def main():
    print("Stage 2 — Last Year's Checkpoint Genomes")

    try:
        stage1 = load_results("stage1_results.json")
    except FileNotFoundError:
        print("ERROR: stage1_results.json not found. Run stage1_baseline.py first.")
        return

    opponents = build_opponent_list()
    opp_names = list(LAST_YEAR_GENOMES.keys()) + ["All 1s", "All 3s"]
    max_score = len(opponents) * 20

    print(f"Loaded {len(stage1)} Stage-1 survivors | {len(opponents)} opponents (29 last-year + 2 baselines) | max={max_score} | {HILL_CLIMB_ROUNDS} rounds × {VARIANTS_PER_ROUND} variants")

    results = []
    t0 = time.time()

    for idx, entry in enumerate(stage1):
        genome = entry['genome']
        s1_score = entry.get('score_stage1', '?')

        print(f"\n-- Genome {idx+1}/{len(stage1)}  "
              f"(Stage-1 score: {s1_score}/40) --")
        print(f"  Starting genome: {genome_to_str(genome)}")

        # Quick initial score
        init_score = total_score_vs(genome, opponents)
        print(f"  Initial Stage-2 score: {init_score}/{max_score}")

        best, best_score = hill_climb(
            genome,
            opponents,
            num_rounds=HILL_CLIMB_ROUNDS,
            num_variants=VARIANTS_PER_ROUND,
            num_mutations=NUM_MUTATIONS,
            verbose=True,
            label=f"g{idx+1}",
        )

        print(f"\n  -- Final detailed report --")
        final_total = detailed_report(best, opponents, opp_names)

        results.append({
            'genome': best,
            'score_stage2': final_total,
            'score_stage1': s1_score,
        })
        print(f"  Genome: {genome_to_str(best)}")

    elapsed = time.time() - t0

    # Sort by Stage-2 score
    results.sort(key=lambda x: x['score_stage2'], reverse=True)

    print(f"\n{'='*65}")
    print(f"STAGE 2 COMPLETE  ({elapsed:.1f}s)")
    print("=" * 65)
    print(f"\n{'Rank':>4}  {'S2 Score':>10}  {'S1 Score':>10}  Genome")
    print(f"{'-'*4}  {'-'*10}  {'-'*10}  {'-'*50}")
    for i, r in enumerate(results[:TOP_N_TO_SAVE], 1):
        print(f"{i:4d}  {r['score_stage2']:6d}/{max_score}  "
              f"{r['score_stage1']:6}/40  {genome_to_str(r['genome'])}")

    save_results("stage2_results.json", results[:TOP_N_TO_SAVE])
    print("\nRun stage3_known.py next.")


if __name__ == "__main__":
    main()
