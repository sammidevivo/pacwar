"""
Stage 3 — Known Genomes (test_genome.py pool)
==============================================
Loads Stage 2 survivors and hill-climbs each one against the full set of
known genomes from test_genome.py (padawans, evolved variants, randos, etc.)
plus the last-year genomes and the baselines, so nothing is lost between stages.

Saves final ranked results to stage3_results.json.

Usage:
    python stage3_known.py
"""

import time
from utils import (
    hill_climb, score_battle, genome_to_str,
    save_results, load_results, total_score_vs
)

# -- Parameters --------------------------------------------------------------
HILL_CLIMB_ROUNDS  = 120
VARIANTS_PER_ROUND = 30
NUM_MUTATIONS      = 3
TOP_N_TO_SAVE      = 20
# ----------------------------------------------------------------------------

# -- All known genomes from test_genome.py -----------------------------------
KNOWN_GENOMES = {
    # Padawans (original)
    "Padawan_I":   "32123003100022221333222332331322331223230133013310",
    "Padawan_M":   "10330330111120223333312331212111212212333130101331",
    "Padawan_R":   "00100010301322233023111111111112132113133331033331",
    "Padawan_P":   "03133300101101203333323121131111122123133131203131",
    "Padawan_Q":   "30300100133122203303333333333333333333132203323130",
    "Padawan_V":   "30330000113020303303323333333333223323310313130310",
    "Padawan_E":   "10113000101121013301111111111221121113301311301311",
    "Padawan_K":   "10110000011122211310111111111112311111331330231301",
    "Padawan_W":   "30331130100323330303333333333332323323213333133333",
    "Padawan_A":   "10110100011122010011111111111121212112311111131111",

    # Evolved
    "Evolved_I":   "33320300131022223333213232232331232222030133100131",
    "Evolved_M":   "10330030130122233033312331212112112212233131201331",
    "Evolved_R":   "00100000331022233033111111111111122112130333333311",
    "Evolved_P":   "03133300101123203300323121131121122122133131212131",
    "Evolved_Q":   "00300000133122003303331333333333333333130101111131",
    "Evolved_V":   "30300000113020003303323333333333323323113313110111",
    "Evolved_E":   "00100000101021023001111111111221111112301133301331",
    "Evolved_K":   "10100000011122203000111111111112121111321330002301",
    "Evolved_W":   "00300100111322303300333333333333233222310313312313",
    "Evolved_A":   "00110100011022003311111111111121212111311331230303",

    # New Randos
    "North":       "00020000110122223033213131311112232311132130330131",
    "South":       "03100001011022203303321121121012222023100110302300",
    "East":        "00300000100322223330333333333232133233110110331313",
    "West":        "00331000300122230300333333333333331332113133120131",

    # Good ones
    "Brian":       "00110000111022213001311111111122111322121331131331",
    "Claude":      "00002222222222222222111111113333333333333333333333",
    "Fran":        "33322003110122223033233232233232231232000210102103",
    "Goldie":      "00100103111022220330121111313333333333333313200331",
    "Jessica":     "13322001312212201133110232233131231222010220310123",
    "Leslie":      "00110000111022213001111111111113122122120331113331",
    "Party":       "00020010101122223033311321321121321121103101103100",
    "Pop":         "00300000011110223333333333333333321333103103020111",
    "Priya":       "00020000101022203332321321323321321321333101102131",
    "PriyaII":     "00020010101022033033321321323121321121331101103100",
    "PriyaIII":    "00020010101022033033321321323121321121331101303100",
    "Rando":       "31030312111111223210033233023123121023230333210213",
    "Ron":         "03000003131022010130232212312232213223033210322313",
    "Tack":        "31120100111122223233123221323323123223233311300311",
    "Woah":        "00020030131022230313321321321121321321132131110131",
    "WoahII":      "00020000131020200310321321321121321321130131101131",
    "WoahIII":     "00120000131020200010321321321321321322130131101131",
    "Random_ref":  "01312101113132301032311323212331200111312102112321",
}

# Last year's checkpoint genomes (carried forward so Stage-2 gains hold)
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
    "RNG4TheWin":     "00000000111122223333111000111122233300001112223330",  # trimmed to 50
    "DLPT":           "10113012131111111011111111111120111112102111323101",
    "PAC_MIGHT":      "00020000101120220030121123121113123323202303101310",
    "JT":             "10111111111111111111123111111111111111111111111111",
    "garen":          "03100200113122303003322121033122112212111110113321",
    "GeneWildest":    "33020000111122203330212232211232232232130130032331",
    "MiteOfMight":    "30333320101123233333112111311112111301333330313311",
    "geneureka":      "30333333133333333333333333333333333313333333333303",
    "PixelPredator":  "00330300131322233333333133333333333333113113111110",
    "DarkHorse":      "01000000010300000103133323223213223233313313323313",
    "pizzapizza":     "33331111111111111111333111333333333333111111111111",  # trimmed to 50
    "fmh":            "33333333333333333333230333333333333333333333000000",
    "cybergene":      "33333333333333333333333333222222222222222333333333",
    "EuGene":         "10111111111113111111111111111111111111111111311111",
    "GeneSimmons":    "13021100131122313300222221121220131111123100031331",
    "PacWarrior":     "33113313011021113313113223323123310123311223020300",
    "simpleGene":     "30333333333333333333333333333333333333333333333333",
    "Krispy":         "11112222111122221111333111111222111333222111333111",
    "coolgeen":       "31321203032321230023222202333221321210301131121211",
}

BASELINE_OPPONENTS = {
    "All 0s": [0] * 50,
    "All 1s": [1] * 50,
    "All 2s": [2] * 50,
    "All 3s": [3] * 50,
}


def build_opponent_list():
    combined = {}
    combined.update(KNOWN_GENOMES)
    combined.update(LAST_YEAR_GENOMES)
    opps = [list(map(int, s[:50])) for s in combined.values()]
    names = list(combined.keys())
    for bname, bg in BASELINE_OPPONENTS.items():
        opps.append(bg)
        names.append(bname)
    return opps, names


def detailed_report(genome, opponents, names):
    max_score = len(opponents) * 20
    wins, losses, ties = [], [], []
    total = 0
    rows = []

    for name, opp in zip(names, opponents):
        s, rounds, c1, c2 = score_battle(genome, opp)
        result = "WIN" if c1 > c2 else ("LOSS" if c2 > c1 else "TIE")
        total += s
        rows.append((name, s, result, rounds, c1, c2))
        if c1 > c2:   wins.append(name)
        elif c2 > c1: losses.append(name)
        else:         ties.append(name)

    print(f"\n  {'Opponent':<18}  {'Sc':>4}  {'Res':<5}  Rnd   You  Them")
    print(f"  {'-'*18}  {'-'*4}  {'-'*5}  {'-'*3}  {'-'*3}  {'-'*3}")
    for name, s, result, rounds, c1, c2 in rows:
        print(f"  {name:<18}  {s:2d}/20  {result:<5}  {rounds:3d}  {c1:3d}  {c2:3d}")
    print(f"  {'-'*50}")
    print(f"  {'TOTAL':<18}  {total}/{max_score}")
    print(f"  W-L-T: {len(wins)}-{len(losses)}-{len(ties)}")
    if losses:
        print(f"  Losses: {', '.join(losses)}")
    return total, len(wins), len(losses), len(ties)


def main():
    print("=" * 65)
    print("STAGE 3 — FULL KNOWN-GENOME GAUNTLET")
    print("=" * 65)

    try:
        stage2 = load_results("stage2_results.json")
    except FileNotFoundError:
        print("ERROR: stage2_results.json not found. Run stage2_last_year.py first.")
        return

    opponents, opp_names = build_opponent_list()
    max_score = len(opponents) * 20

    print(f"Loaded {len(stage2)} Stage-2 survivors")
    print(f"Total opponents: {len(opponents)}")
    print(f"  Known (test_genome.py): {len(KNOWN_GENOMES)}")
    print(f"  Last year checkpoint  : {len(LAST_YEAR_GENOMES)}")
    print(f"  Baselines             : {len(BASELINE_OPPONENTS)}")
    print(f"Max possible score : {max_score}")
    print(f"Hill-climb         : {HILL_CLIMB_ROUNDS} rounds × {VARIANTS_PER_ROUND} variants")
    print("=" * 65)

    results = []
    t0 = time.time()

    for idx, entry in enumerate(stage2):
        genome = entry['genome']
        s2_score = entry.get('score_stage2', '?')
        s1_score = entry.get('score_stage1', '?')

        print(f"\n{'='*65}")
        print(f"Genome {idx+1}/{len(stage2)}  "
              f"(S1={s1_score}/40, S2={s2_score})")
        print(f"Starting: {genome_to_str(genome)}")

        init_score = total_score_vs(genome, opponents)
        print(f"Initial Stage-3 score: {init_score}/{max_score}")

        best, best_score = hill_climb(
            genome,
            opponents,
            num_rounds=HILL_CLIMB_ROUNDS,
            num_variants=VARIANTS_PER_ROUND,
            num_mutations=NUM_MUTATIONS,
            verbose=True,
            label=f"g{idx+1}",
        )

        final_total, wins, losses, ties = detailed_report(best, opponents, opp_names)

        results.append({
            'genome': best,
            'score_stage3': final_total,
            'score_stage2': s2_score,
            'score_stage1': s1_score,
            'wins': wins,
            'losses': losses,
            'ties': ties,
        })
        print(f"\n  Final genome: {genome_to_str(best)}")

    elapsed = time.time() - t0

    results.sort(key=lambda x: x['score_stage3'], reverse=True)

    print(f"\n{'='*65}")
    print(f"STAGE 3 COMPLETE  ({elapsed:.1f}s)")
    print("=" * 65)
    print(f"\n{'Rank':>4}  {'S3 Score':>12}  {'W-L-T':<9}  Genome")
    print(f"{'-'*4}  {'-'*12}  {'-'*9}  {'-'*50}")
    for i, r in enumerate(results[:TOP_N_TO_SAVE], 1):
        wlt = f"{r['wins']}-{r['losses']}-{r['ties']}"
        print(f"{i:4d}  {r['score_stage3']:6d}/{max_score}  "
              f"{wlt:<9}  {genome_to_str(r['genome'])}")

    save_results("stage3_results.json", results[:TOP_N_TO_SAVE])

    print(f"\nBest genome:")
    print(f"    {genome_to_str(results[0]['genome'])}")
    print(f"    Score: {results[0]['score_stage3']}/{max_score}  "
          f"W-L-T: {results[0]['wins']}-{results[0]['losses']}-{results[0]['ties']}")


if __name__ == "__main__":
    main()
