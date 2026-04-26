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

def calculate_comprehensive_score(genome, test_suite):
    """
    Calculate a comprehensive fitness score by testing against multiple categories.
    Uses the professor's scoring system to reward fast kills.
    
    Scoring per duel (out of 20 points):
    - 20 pts: Destroy opponent in <100 rounds
    - 19 pts: Destroy opponent in 100-199 rounds
    - 18 pts: Destroy opponent in 200-299 rounds
    - 17 pts: Destroy opponent in 300-500 rounds
    - 13 pts: Outnumber 10:1+ after 500 rounds
    - 12 pts: Outnumber 3:1 to 10:1 after 500 rounds
    - 11 pts: Outnumber 1.5:1 to 3:1 after 500 rounds
    - 10 pts: Neither outnumbers by more than 1.5:1
    
    test_suite is a dict with keys:
    - 'variants': other mutations of the base genome
    - 'randoms': random genomes
    - 'strategies': known good strategies
    - 'baselines': all 0s, 1s, 2s, 3s
    
    Returns: (total_score, category_scores_dict)
    """
    
    def score_battle(genome1, genome2):
        """Score a single battle using the professor's system"""
        rounds, c1, c2 = _PyPacwar.battle(genome1, genome2)
        
        # genome1 destroyed genome2
        if c2 == 0 and c1 > 0:
            if rounds < 100:
                return 20
            elif rounds < 200:
                return 19
            elif rounds < 300:
                return 18
            else:  # 300-500
                return 17
        
        # genome2 destroyed genome1
        elif c1 == 0 and c2 > 0:
            if rounds < 100:
                return 0
            elif rounds < 200:
                return 1
            elif rounds < 300:
                return 2
            else:  # 300-500
                return 3
        
        # Neither destroyed after 500 rounds - use population ratio
        else:
            if c1 == 0 and c2 == 0:
                return 10  # Both dead somehow
            elif c1 == 0:
                return 0  # We lost all our mites
            elif c2 == 0:
                return 20  # We won (shouldn't happen here but just in case)
            else:
                ratio = c1 / c2
                if ratio >= 10:
                    return 13
                elif ratio >= 3:
                    return 12
                elif ratio >= 1.5:
                    return 11
                elif ratio <= 1/10:
                    return 7
                elif ratio <= 1/3:
                    return 8
                elif ratio <= 1/1.5:
                    return 9
                else:
                    return 10
    
    category_scores = {}
    
    # Test against variants (similar genomes) - use simple wins for diversity
    if 'variants' in test_suite and test_suite['variants']:
        score = sum(score_battle(genome, opp) for opp in test_suite['variants'])
        category_scores['variants'] = score / len(test_suite['variants'])  # Average score per battle
    else:
        category_scores['variants'] = 0
    
    # Test against random genomes - use simple wins for diversity
    if 'randoms' in test_suite and test_suite['randoms']:
        score = sum(score_battle(genome, opp) for opp in test_suite['randoms'])
        category_scores['randoms'] = score / len(test_suite['randoms'])  # Average score per battle
    else:
        category_scores['randoms'] = 0
    
    # Test against known strategies - FULL SCORING (important!)
    if 'strategies' in test_suite and test_suite['strategies']:
        score = sum(score_battle(genome, opp) for opp in test_suite['strategies'])
        category_scores['strategies'] = score  # Total points (don't average - these are critical)
    else:
        category_scores['strategies'] = 0
    
    # Test against baselines - FULL SCORING WITH 2X WEIGHT (most important!)
    if 'baselines' in test_suite and test_suite['baselines']:
        score = sum(score_battle(genome, opp) for opp in test_suite['baselines'])
        category_scores['baselines'] = score * 2  # 2x weight - critical to beat these fast
    else:
        category_scores['baselines'] = 0
    
    total_score = sum(category_scores.values())
    
    return total_score, category_scores

def score_battle(genome1, genome2):
    """Score a single battle using the professor's system"""
    rounds, c1, c2 = _PyPacwar.battle(genome1, genome2)
    
    # genome1 destroyed genome2
    if c2 == 0 and c1 > 0:
        if rounds < 100:
            return 20
        elif rounds < 200:
            return 19
        elif rounds < 300:
            return 18
        else:  # 300-500
            return 17
    
    # genome2 destroyed genome1
    elif c1 == 0 and c2 > 0:
        if rounds < 100:
            return 0
        elif rounds < 200:
            return 1
        elif rounds < 300:
            return 2
        else:  # 300-500
            return 3
    
    # Neither destroyed after 500 rounds - use population ratio
    else:
        if c1 == 0 and c2 == 0:
            return 10
        elif c1 == 0:
            return 0
        elif c2 == 0:
            return 20
        else:
            ratio = c1 / c2
            if ratio >= 10:
                return 13
            elif ratio >= 3:
                return 12
            elif ratio >= 1.5:
                return 11
            elif ratio <= 1/10:
                return 7
            elif ratio <= 1/3:
                return 8
            elif ratio <= 1/1.5:
                return 9
            else:
                return 10

def hill_climb_with_diversity():
    """
    Start with a good genome and make mutations to try to improve it.
    Test against a diverse set of opponents including variants, randoms, and baselines.
    Track random genomes that perform well as potential "killer genes".
    """
    
    # ========== PARAMETERS ==========
    # BASE_GENOME = [1,1,1,1] + [2]*16 + [1]*4 + [1]*4 + [3]*16 + [3]*6
    BASE_GENOME = list(map(int, "00000000011022223333332133133233233233103103333103"))

    
    NUM_VARIANTS_PER_ROUND = 30      # How many mutations to test each round
    NUM_MUTATIONS = 3                 # How many genes to mutate at once
    NUM_RANDOM_OPPONENTS = 20         # Random genomes to test against
    NUM_ROUNDS = 50                   # How many rounds of hill climbing
    
    # Known good strategies
    KNOWN_STRATEGIES = [
        # PADAWANS
        list(map(int, "32123003100022221333222332331322331223230133013310")), # I
        list(map(int, "10330330111120223333312331212111212212333130101331")), # M
        list(map(int, "00100010301322233023111111111112132113133331033331")), # R
        list(map(int, "03133300101101203333323121131111122123133131203131")), # P
        list(map(int, "30300100133122203303333333333333333333132203323130")), # Q
        list(map(int, "30330000113020303303323333333333223323310313130310")), # V
        list(map(int, "10113000101121013301111111111221121113301311301311")), # E
        list(map(int, "10110000011122211310111111111112311111331330231301")), # K
        list(map(int, "30331130100323330303333333333332323323213333133333")), # W
        list(map(int, "10110100011122010011111111111121212112311111131111")), # A


        # EVOLVED
        list(map(int, "33320300131022223333213232232331232222030133100131")), # I
        list(map(int, "10330030130122233033312331212112112212233131201331")), # M
        list(map(int, "00100000331022233033111111111111122112130333333311")), # R
        list(map(int, "03133300101123203300323121131121122122133131212131")), # P
        list(map(int, "00300000133122003303331333333333333333130101111131")), # Q
        list(map(int, "30300000113020003303323333333333323323113313110111")), # V
        list(map(int, "00100000101021023001111111111221111112301133301331")), # E
        list(map(int, "10100000011122203000111111111112121111321330002301")), # K
        list(map(int, "00300100111322303300333333333333233222310313312313")), # W
        list(map(int, "00110100011022003311111111111121212111311331230303")), # A

        # NEW RANDOS
        list(map(int, "00020000110122223033213131311112232311132130330131")), # North
        list(map(int, "03100001011022203303321121121012222023100110302300")), # South
        list(map(int, "00300000100322223330333333333232133233110110331313")), # East
        list(map(int, "00331000300122230300333333333333331332113133120131")), # West

        # GOOD ONES
        list(map(int, "00110000111022213001311111111122111322121331131331")), # Brian
        list(map(int, "00002222222222222222111111113333333333333333333333")), # Claude
        list(map(int, "33322003110122223033233232233232231232000210102103")), # Fran
        list(map(int, "00100103111022220330121111313333333333333313200331")), # Goldie
        list(map(int, "13322001312212201133110232233131231222010220310123")), # Jessica
        list(map(int, "00110000111022213001111111111113122122120331113331")), # Leslie
        list(map(int, "00020010101122223033311321321121321121103101103100")), # Party
        list(map(int, "00300000011110223333333333333333321333103103020111")), # Pop
        list(map(int, "00020000101022203332321321323321321321333101102131")), # Priya
        list(map(int, "00020010101022033033321321323121321121331101103100")), # Priya II
        list(map(int, "00020010101022033033321321323121321121331101303100")), # Priya III
        list(map(int, "31030312111111223210033233023123121023230333210213")), # Rando
        list(map(int, "03000003131022010130232212312232213223033210322313")), # Ron
        list(map(int, "31120100111122223233123221323323123223233311300311")), # Tack
        list(map(int, "00020030131022230313321321321121321321132131110131")), # Woah
        list(map(int, "00020000131020200310321321321121321321130131101131")), # Woah II
        list(map(int, "00120000131020200010321321321321321322130131101131")), # Woah III


        list(map(int, "01312101113132301032311323212331200111312102112321")), # Random


        # ROUND 2 RESULTS
        list(map(int, "03100000101002033333311121122112121022121133131131")), # S2-1
        list(map(int, "03100000100122203330311121121112212222111121130311")), # S2-2
        list(map(int, "03100000130122203333331121110122112312110100301101")), # S2-3
        list(map(int, "01300000110121203333113323323123323323310313301310")), # S2-4
        list(map(int, "01300100111121301033113323323321322312310313313313")), # S2-5
        list(map(int, "03103000131120203030311121130121121121230101033100")), # S2-6
        list(map(int, "01300000011022323031131323323322132333310323133210")), # S2-7
        list(map(int, "01300100101321000303223323023023222023311021300313")), # S2-8
        list(map(int, "30000000131022223333331133233233233333103113221100")), # S2-9
        list(map(int, "01300100101132010333123323322321323312323310030330")), # S2-10
        list(map(int, "00020000111020203003323331313121121221101133103300")), # S2-11
        list(map(int, "01300000130121213303121323311112323021310310103312")), # S2-12
        list(map(int, "03100230103122003300321121121011012031120221100230")), # S2-13
        list(map(int, "33100300111120203330331123123123123123311113021211")), # S2-14
        list(map(int, "33020003131122203333211232221232221211101133013101")), # S2-15
        list(map(int, "03133000310021232333223121101121122132133131022131")), # S2-16
        list(map(int, "03133333131020300323112122120123022123120120213313")), # S2-17
        list(map(int, "10020000111020203333232213213112213332103310002313")), # S2-18
        list(map(int, "31020000111100201302223213323213313232313013023313")), # S2-19


        # LAST YEAR
        # LAST YEAR'S CHECKPOINT
        list(map(int, "03133000111120113033313121022122121313331131101131")), # HappyGene
        list(map(int, "11121111111111313111031113111111113211113303131313")), # 3L1M0N4T0R
        list(map(int, "10111111111111111111110111111111111111111111111111")), # Infecto
        list(map(int, "30100000111122203333210132112202332202111132331301")), # Darwin
        list(map(int, "30333333333333333333333333333333333333333333333333")), # Geneus
        list(map(int, "33333333333333333333333333333333333333100100100100")), # NewJeans
        list(map(int, "00000000000000003333333333111111222333111000000333")), # Juju
        list(map(int, "10112310231121101111101111111222232111212220232111")), # Paccident
        list(map(int, "01303320323303122003303323023131022332211230203113")), # Zacho
        list(map(int, "03103120003232202033331121112113212203131131312330")), # philip
        list(map(int, "00000000111122223333111000111122233300001112223330")), # RNG4TheWin (trimmed to 50)
        list(map(int, "10113012131111111011111111111120111112102111323101")), # DLPT
        list(map(int, "00020000101120220030121123121113123323202303101310")), # PAC_MIGHT
        list(map(int, "10111111111111111111123111111111111111111111111111")), # JT
        list(map(int, "03100200113122303003322121033122112212111110113321")), # garen
        list(map(int, "33020000111122203330212232211232232232130130032331")), # GeneWildest
        list(map(int, "30333320101123233333112111311112111301333330313311")), # MiteOfMight
        list(map(int, "30333333133333333333333333333333333313333333333303")), # geneureka
        list(map(int, "00330300131322233333333133333333333333113113111110")), # PixelPredator
        list(map(int, "01000000010300000103133323223213223233313313323313")), # DarkHorse
        list(map(int, "33331111111111111111333111333333333333111111111111")), # pizzapizza (trimmed to 50)
        list(map(int, "33333333333333333333230333333333333333333333000000")), # fmh
        list(map(int, "33333333333333333333333333222222222222222333333333")), # cybergene
        list(map(int, "10111111111113111111111111111111111111111111311111")), # EuGene
        list(map(int, "13021100131122313300222221121220131111123100031331")), # GeneSimmons
        list(map(int, "33113313011021113313113223323123310123311223020300")), # PacWarrior
        list(map(int, "30333333333333333333333333333333333333333333333333")), # simpleGene
        list(map(int, "11112222111122221111333111111222111333222111333111")), # Krispy
        list(map(int, "31321203032321230023222202333221321210301131121211")), # coolgeen

         # STAGE 3 RESULTS
        list(map(int, "01300000101020000031133323323322232333313310313310")), # S3-1
        list(map(int, "03100000031120003330321121133121021121131131123121")), # S3-2
        list(map(int, "03100000100120003333321121121111122122131130300131")), # S3-3
        list(map(int, "03100000011120233333321121121111111222131131011130")), # S3-4
        list(map(int, "03100000101013003303311121121112320122131130130131")), # S3-5
        list(map(int, "01300000110320000333133323323320323323310300310313")), # S3-6
        list(map(int, "03100000101121103330321121121111212022111121132131")), # S3-7
        list(map(int, "03100000001123203330321121121211212122120100331131")), # S3-8
        list(map(int, "01300000011121003000123323313013223033310310330310")), # S3-9
        list(map(int, "01300030111120300330123323023323322023313313232323")), # S3-10
        list(map(int, "01300101111120301030113323323321322332300313310313")), # S3-11
        list(map(int, "01300000011110310303113323323223323333323310120310")), # S3-12
        list(map(int, "00020000111022003003323321321121321321303133102301")), # S3-13
        list(map(int, "00000000011022223333332133133233233233103103333103")), # S3-14
        list(map(int, "11020000111122203103233212212222212212310310010311")), # S3-15
        list(map(int, "33130303111120003330123123123123123123313110121313")), # S3-16
        list(map(int, "03131333131023000333112122123121022123120120313123")), # S3-17
        list(map(int, "31000000111122203333231232212232231212231130000331")), # S3-18
        list(map(int, "10020000111120200003232212113112212312313310200311")), # S3-19

        # STAGE 4 RESULTS
        list(map(int, "01300000101000000031133323323323223323313310312313")), # S4-1
        list(map(int, "03100000031120003330321121133121021121131130121121")), # S4-2
        list(map(int, "03100000100130203333321121121111121122131131311131")), # S4-3
        list(map(int, "03100000011100233333321121121111111122131131031130")), # S4-4
        list(map(int, "03100000030000003333312121121122121112131131131130")), # S4-5
        list(map(int, "01300000110100000330133323323323223323310310100310")), # S4-6
        list(map(int, "03100000001103000333321121121111012022121121110131")), # S4-7
        list(map(int, "03100000001303203330321121121111211322101131330131")), # S4-8
        list(map(int, "01300000011121003000123323313013223033313310300310")), # S4-9
        list(map(int, "01300020101120300030123323023023322023313323020333")), # S4-10
        list(map(int, "01300101111120000030113323323323322332300313300313")), # S4-11



        # RON 2.0
        list(map(int, "01000100010001000103123323233213223333313313313313"))


    ]


    BASELINES = [
        # Uniform strategies
        [0] * 50,
        [1] * 50,
        [2] * 50,
        [3] * 50,

        # # === Birth-focused (U genes 0-3) ===
        # # Babies always turn once from mother (spread out)
        # [1,1,1,1] + [0]*46,
        # # Babies face opposite of mother
        # [2,2,2,2] + [0]*46,

        # [3,3,3,3] + [0]*46,

        # # === Aggressive replacement (V genes 4-19) ===
        # # All V=2: conquered enemies face opposite of attacker (face back toward attacker's territory)
        # [0]*4 + [2]*16 + [0]*30,
        # # All V=1: conquered enemies turn left from attacker
        # [0]*4 + [1]*16 + [0]*30,
        # [0]*4 + [3]*16 + [0]*30,

        # # === Wall bouncer (W genes 20-23) ===
        # # Always reverse at walls (W=2)
        # [0]*20 + [2,2,2,2] + [0]*26,
        # # Always turn left at walls
        # [0]*20 + [1,1,1,1] + [0]*26,

        # # Always turn left at walls
        # [0]*20 + [3,3,3,3] + [0]*26,

        # # === Blob behavior / expansion (X genes 24-27) ===
        # # Always go straight into empty space (X=0) - aggressive expansion
        # # Turn left when facing empty - spiral pattern
        # [0]*24 + [1,1,1,1] + [0]*22,
        # # Turn right when facing empty - opposite spiral
        # [0]*24 + [3,3,3,3] + [0]*22,
        # # Reverse when facing empty - defensive/clumping
        # [0]*24 + [2,2,2,2] + [0]*22,

        # # === Friendly interaction (Y genes 28-43) ===
        # # Turn away from friendlies (spread out) - Y all 2
        # [0]*28 + [2]*16 + [0]*6,
        # # Turn right from friendly (flock/align) - Y all 0
        # [0]*28 + [3]*16 + [0]*6,
        # # Turn left from friendlies (swirl formation)
        # [0]*28 + [1]*16 + [0]*6,

        # # === Enemy interaction (Z genes 44-49) ===
        # # Always face enemy head-on (Z=0) - aggressive
        # [0]*44 + [3,3,3,3,3,3],
        # # Turn away from enemies (Z=2) - defensive/evasive
        # [0]*44 + [2,2,2,2,2,2],
        # # Turn left from enemies - flanking
        # [0]*44 + [1,1,1,1,1,1],

        # # === Combined archetypes ===
        # # "Berserker": aggressive births, aggressive conquest, charge enemies
        # [1,1,1,1] + [1]*16 + [1,1,1,1] + [0,0,0,0] + [1]*16 + [0,0,0,0,0,0],

        # # "Age-dependent": young go straight, old turn - uses 0,1,2,3 pattern
        # [0,1,2,3] + [0,1,2,3]*4 + [0,1,2,3] + [0,1,2,3] + [0,1,2,3]*4 + [0,1,2,3,0,1],
        # # "Random-looking but structured": alternating
        # [0,2]*25,
        # [1,3]*25,
    ]
    
    # ========== INITIALIZATION ==========
    print(f"Base genome: {BASE_GENOME}")
    print(f"Variants per round: {NUM_VARIANTS_PER_ROUND}")
    print(f"Mutations per variant: {NUM_MUTATIONS}")
    print(f"Random opponents: {NUM_RANDOM_OPPONENTS}")
    print(f"Rounds: {NUM_ROUNDS}")
    print("=" * 70)
    print()
    
    current_best = BASE_GENOME[:]
    all_time_best = BASE_GENOME[:]
    all_time_best_score = 0
    
    # Track killer random genomes
    killer_randoms = []
   
    for round_num in range(NUM_ROUNDS):
        print(f"\n{'='*70}")
        print(f"ROUND {round_num + 1}/{NUM_ROUNDS}")
        print(f"{'='*70}")
        
        # Generate variants by mutating current best
        variants = [mutate_genome(current_best, NUM_MUTATIONS) 
                   for _ in range(NUM_VARIANTS_PER_ROUND)]
        variants.append(current_best)  # Include current best
        
        # Generate random opponents
        random_opponents = [random_genome() for _ in range(NUM_RANDOM_OPPONENTS)]
        
        # Build test suite
        # Variants test against each other, randoms, strategies, and baselines
        print(f"Testing {len(variants)} variants...")
        
        results = []
        
        # Test each variant
        for i, variant in enumerate(variants):
            # Create test suite (exclude self from variants)
            other_variants = variants[:i] + variants[i+1:]
            
            test_suite = {
                'variants': other_variants,
                'randoms': random_opponents,
                'strategies': KNOWN_STRATEGIES,
                'baselines': BASELINES
            }
            
            score, category_scores = calculate_comprehensive_score(variant, test_suite)
            results.append((variant, score, category_scores))
            
            if (i + 1) % 10 == 0:
                print(f"  Tested {i + 1}/{len(variants)} variants...")
        
        # Also test random opponents to see if any are killer genes
        print(f"Testing random opponents for killer genes...")
        for i, random_opp in enumerate(random_opponents):
            test_suite = {
                'variants': variants,
                'randoms': [],  # Don't test against other randoms
                'strategies': KNOWN_STRATEGIES,
                'baselines': BASELINES
            }
            
            score, category_scores = calculate_comprehensive_score(random_opp, test_suite)
            
            # If random genome beats most variants, it might be a killer
            variant_wins = category_scores.get('variants', 0)
            if variant_wins > len(variants) * 0.7:  # Beats 70%+ of variants
                print(f"      KILLER RANDOM FOUND! Score: {score:.2f}")
                killer_randoms.append((random_opp, score, category_scores))
        
        # Sort results by score
        results.sort(key=lambda x: x[1], reverse=True)
        
        # # Display top 5
        # print(f"\nTop 5 variants this round:")
        # print("-" * 70)
        # for rank, (genome, score, cat_scores) in enumerate(results[:5], 1):
        #     is_current = "← CURRENT" if genome == current_best else ""
        #     print(f"Rank {rank}: Score={score:.2f} {is_current}")
        #     print(f"  vs Variants: {cat_scores.get('variants', 0):.1f}/{len(variants)-1}")
        #     print(f"  vs Randoms:  {cat_scores.get('randoms', 0):.1f}/{NUM_RANDOM_OPPONENTS}")
        #     print(f"  vs Strats:   {cat_scores.get('strategies', 0):.1f}/{len(KNOWN_STRATEGIES)}")
        #     print(f"  vs Baselines:{cat_scores.get('baselines', 0):.1f}/{len(BASELINES)*2} (2x weight)")
        #     print()
        
        # Update current best for next round
        round_best = results[0][0]
        round_best_score = results[0][1]
        
        if round_best_score > all_time_best_score:
            all_time_best = round_best[:]
            all_time_best_score = round_best_score
            print(f"    NEW ALL-TIME BEST! Score: {all_time_best_score:.2f}")
        
        current_best = round_best
        print(f"Current best score: {round_best_score:.2f}")
    
    # ========== FINAL RESULTS ==========
    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    print()
    print("ALL-TIME BEST GENOME:")
    print(all_time_best)
    print(f"Score: {all_time_best_score:.2f}")
    print()

    known_genomes = {
        "Priya": [0,0,0,2,0,0,0,0,1,0,1,0,2,2,2,0,3,3,3,2,3,2,1,3,2,1,3,2,3,3,2,1,3,2,1,3,2,1,3,3,3,1,0,1,1,0,2,1,3,1],
        "Priya II": [0,0,0,2,0,0,1,0,1,0,1,0,2,2,0,3,3,0,3,3,3,2,1,3,2,1,3,2,3,1,2,1,3,2,1,1,2,1,3,3,1,1,0,1,1,0,3,1,0,0],
        "Claude": [0,0,0,0,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,1,1,1,1,1,1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3],
        "Pop": [0,0,3,0,0,0,0,0,0,1,1,1,1,0,2,2,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,1,3,3,3,1,0,3,1,0,3,0,2,0,1,1,1],
        "Priya III": [0,0,0,2,0,0,1,0,1,0,1,0,2,2,0,3,3,0,3,3,3,2,1,3,2,1,3,2,3,1,2,1,3,2,1,1,2,1,3,3,1,1,0,1,3,0,3,1,0,0],
        "Rando": [3,1,0,3,0,3,1,2,1,1,1,1,1,1,2,2,3,2,1,0,0,3,3,2,3,3,0,2,3,1,2,3,1,2,1,0,2,3,2,3,0,3,3,3,2,1,0,2,1,3],
        "Tack": [3,1,1,2,0,1,0,0,1,1,1,1,2,2,2,2,3,2,3,3,1,2,3,2,2,1,3,2,3,3,2,3,1,2,3,2,2,3,2,3,3,3,1,1,3,0,0,3,1,1],
        "Woah": [0,0,0,2,0,0,3,0,1,3,1,0,2,2,2,3,0,3,1,3,3,2,1,3,2,1,3,2,1,1,2,1,3,2,1,3,2,1,1,3,2,1,3,1,1,1,0,1,3,1],
        "Brian": [0,0,1,1,0,0,0,0,1,1,1,0,2,2,2,1,3,0,0,1,3,1,1,1,1,1,1,1,1,1,2,2,1,1,1,3,2,2,1,2,1,3,3,1,1,3,1,3,3,1],
        "Leslie": [0,0,1,1,0,0,0,0,1,1,1,0,2,2,2,1,3,0,0,1,1,1,1,1,1,1,1,1,1,1,1,3,1,2,2,1,2,2,1,2,0,3,3,1,1,1,3,3,3,1],
        "Jessica": [1,3,3,2,2,0,0,1,3,1,2,2,1,2,2,0,1,1,3,3,1,1,0,2,3,2,2,3,3,1,3,1,2,3,1,2,2,2,0,1,0,2,2,0,3,1,0,1,2,3],
        "Fran": [3,3,3,2,2,0,0,3,1,1,0,1,2,2,2,2,3,0,3,3,2,3,3,2,3,2,2,3,3,2,3,2,2,3,1,2,3,2,0,0,0,2,1,0,1,0,2,1,0,3],
        "Woah II": list(map(int, "00020000131020200310321321321121321321130131101131")),
        "Woah III": list(map(int, "00120000131020200010321321321321321322130131101131")),

        # EVOLVED
        "I": list(map(int, "33320300131022223333213232232331232222030133100131")),
        "M": list(map(int, "10330030130122233033312331212112112212233131201331")),
        "R": list(map(int, "00100000331022233033111111111111122112130333333311")),
        "P": list(map(int, "03133300101123203300323121131121122122133131212131")),
        "Q": list(map(int, "00300000133122003303331333333333333333130101111131")),
        "V": list(map(int, "30300000113020003303323333333333323323113313110111")),
        "E": list(map(int, "00100000101021023001111111111221111112301133301331")),
        "K": list(map(int, "10100000011122203000111111111112121111321330002301")),
        "W": list(map(int, "00300100111322303300333333333333233222310313312313")),
        "A": list(map(int, "00110100011022003311111111111121212111311331230303")),

        # New Randos
        "NORTH": list(map(int, "00020000110122223033213131311112232311132130330131")),
        "SOUTH": list(map(int, "03100001011022203303321121121012222023100110302300")),
        "EAST": list(map(int, "00300000100322223330333333333232133233110110331313")),
        "WEST": list(map(int, "00331000300122230300333333333333331332113133120131")),

        # ROUND 2 RESULTS
        "S2-2":  list(map(int, "03100000100122203330311121121112212222111121130311")),
        "S2-3":  list(map(int, "03100000130122203333331121110122112312110100301101")),
        "S2-4":  list(map(int, "01300000110121203333113323323123323323310313301310")),
        "S2-5":  list(map(int, "01300100111121301033113323323321322312310313313313")),
        "S2-6":  list(map(int, "03103000131120203030311121130121121121230101033100")),
        "S2-7":  list(map(int, "01300000011022323031131323323322132333310323133210")),
        "S2-8":  list(map(int, "01300100101321000303223323023023222023311021300313")),
        "S2-9":  list(map(int, "30000000131022223333331133233233233333103113221100")),
        "S2-10": list(map(int, "01300100101132010333123323322321323312323310030330")),
        "S2-11": list(map(int, "00020000111020203003323331313121121221101133103300")),
        "S2-12": list(map(int, "01300000130121213303121323311112323021310310103312")),
        "S2-13": list(map(int, "03100230103122003300321121121011012031120221100230")),
        "S2-14": list(map(int, "33100300111120203330331123123123123123311113021211")),
        "S2-15": list(map(int, "33020003131122203333211232221232221211101133013101")),
        "S2-16": list(map(int, "03133000310021232333223121101121122132133131022131")),
        "S2-17": list(map(int, "03133333131020300323112122120123022123120120213313")),
        "S2-18": list(map(int, "10020000111020203333232213213112213332103310002313")),
        "S2-19": list(map(int, "31020000111100201302223213323213313232313013023313")),

        # LAST YEAR'S CHECKPOINT
        "HappyGene":     list(map(int, "03133000111120113033313121022122121313331131101131")),
        "3L1M0N4T0R":    list(map(int, "11121111111111313111031113111111113211113303131313")),
        "Infecto":       list(map(int, "10111111111111111111110111111111111111111111111111")),
        "Darwin":        list(map(int, "30100000111122203333210132112202332202111132331301")),
        "Geneus":        list(map(int, "30333333333333333333333333333333333333333333333333")),
        "NewJeans":      list(map(int, "33333333333333333333333333333333333333100100100100")),
        "Juju":          list(map(int, "00000000000000003333333333111111222333111000000333")),
        "Paccident":     list(map(int, "10112310231121101111101111111222232111212220232111")),
        "Zacho":         list(map(int, "01303320323303122003303323023131022332211230203113")),
        "philip":        list(map(int, "03103120003232202033331121112113212203131131312330")),
        "RNG4TheWin":    list(map(int, "00000000111122223333111000111122233300001112223330")),
        "DLPT":          list(map(int, "10113012131111111011111111111120111112102111323101")),
        "PAC_MIGHT":     list(map(int, "00020000101120220030121123121113123323202303101310")),
        "JT":            list(map(int, "10111111111111111111123111111111111111111111111111")),
        "garen":         list(map(int, "03100200113122303003322121033122112212111110113321")),
        "GeneWildest":   list(map(int, "33020000111122203330212232211232232232130130032331")),
        "MiteOfMight":   list(map(int, "30333320101123233333112111311112111301333330313311")),
        "geneureka":     list(map(int, "30333333133333333333333333333333333313333333333303")),
        "PixelPredator": list(map(int, "00330300131322233333333133333333333333113113111110")),
        "DarkHorse":     list(map(int, "01000000010300000103133323223213223233313313323313")),
        "pizzapizza":    list(map(int, "33331111111111111111333111333333333333111111111111")),
        "fmh":           list(map(int, "33333333333333333333230333333333333333333333000000")),
        "cybergene":     list(map(int, "33333333333333333333333333222222222222222333333333")),
        "EuGene":        list(map(int, "10111111111113111111111111111111111111111111311111")),
        "GeneSimmons":   list(map(int, "13021100131122313300222221121220131111123100031331")),
        "PacWarrior":    list(map(int, "33113313011021113313113223323123310123311223020300")),
        "simpleGene":    list(map(int, "30333333333333333333333333333333333333333333333333")),
        "Krispy":        list(map(int, "11112222111122221111333111111222111333222111333111")),
        "coolgeen":      list(map(int, "31321203032321230023222202333221321210301131121211")),

        # STAGE 3 RESULTS
        "S3-1":  list(map(int, "01300000101020000031133323323322232333313310313310")),
        "S3-2":  list(map(int, "03100000031120003330321121133121021121131131123121")),
        "S3-3":  list(map(int, "03100000100120003333321121121111122122131130300131")),
        "S3-4":  list(map(int, "03100000011120233333321121121111111222131131011130")),
        "S3-5":  list(map(int, "03100000101013003303311121121112320122131130130131")),
        "S3-6":  list(map(int, "01300000110320000333133323323320323323310300310313")),
        "S3-7":  list(map(int, "03100000101121103330321121121111212022111121132131")),
        "S3-8":  list(map(int, "03100000001123203330321121121211212122120100331131")),
        "S3-9":  list(map(int, "01300000011121003000123323313013223033310310330310")),
        "S3-10": list(map(int, "01300030111120300330123323023323322023313313232323")),
        "S3-11": list(map(int, "01300101111120301030113323323321322332300313310313")),
        "S3-12": list(map(int, "01300000011110310303113323323223323333323310120310")),
        "S3-13": list(map(int, "00020000111022003003323321321121321321303133102301")),
        "S3-14": list(map(int, "00000000011022223333332133133233233233103103333103")),
        "S3-15": list(map(int, "11020000111122203103233212212222212212310310010311")),
        "S3-16": list(map(int, "33130303111120003330123123123123123123313110121313")),
        "S3-17": list(map(int, "03131333131023000333112122123121022123120120313123")),
        "S3-18": list(map(int, "31000000111122203333231232212232231212231130000331")),
        "S3-19": list(map(int, "10020000111120200003232212113112212312313310200311")),

        # STAGE 4 RESULTS
        "S4-1":  list(map(int, "01300000101000000031133323323323223323313310312313")),
        "S4-2":  list(map(int, "03100000031120003330321121133121021121131130121121")),
        "S4-3":  list(map(int, "03100000100130203333321121121111121122131131311131")),
        "S4-4":  list(map(int, "03100000011100233333321121121111111122131131031130")),
        "S4-5":  list(map(int, "03100000030000003333312121121122121112131131131130")),
        "S4-6":  list(map(int, "01300000110100000330133323323323223323310310100310")),
        "S4-7":  list(map(int, "03100000001103000333321121121111012022121121110131")),
        "S4-8":  list(map(int, "03100000001303203330321121121111211322101131330131")),
        "S4-9":  list(map(int, "01300000011121003000123323313013223033313310300310")),
        "S4-10": list(map(int, "01300020101120300030123323023023322023313323020333")),
        "S4-11": list(map(int, "01300101111120000030113323323323322332300313300313")),


        "Ron 2.0": list(map(int, "01000100010001000103123323233213223333313313313313")),
    }
    
    # Test final best against baselines
    print("Final testing against baselines:")
    print("-" * 70)
    baseline_names = ["All 0s", "All 1s", "All 2s", "All 3s"]
    for name, baseline in zip(baseline_names, BASELINES):
        rounds, c1, c2 = _PyPacwar.battle(all_time_best, baseline)
        result = "WIN" if c1 > c2 else ("LOSS" if c2 > c1 else "TIE")
        print(f"{name:10s}: Your={c1:3d}, Theirs={c2:3d}, Rounds={rounds:3d} [{result}]")
    
    # Test against all known genomes
    print("\n" + "=" * 70)
    print("MATCHUPS AGAINST KNOWN GENOMES")
    print("=" * 70)
    
    wins = []
    losses = []
    ties = []
    
    for name, genome in known_genomes.items():
        rounds, c1, c2 = _PyPacwar.battle(all_time_best, genome)
        score = score_battle(all_time_best, genome)
        
        if c1 > c2:
            result = "WIN"
            wins.append((name, c1, c2, rounds, score))
        elif c2 > c1:
            result = "LOSS"
            losses.append((name, c1, c2, rounds, score))
        else:
            result = "TIE"
            ties.append((name, c1, c2, rounds, score))
    
    # Display wins
    if wins:
        print(f"\n✓ VICTORIES ({len(wins)}):")
        print("-" * 70)
        wins.sort(key=lambda x: x[4], reverse=True)  # Sort by score
        for name, c1, c2, rounds, score in wins:
            print(f"  {name:12s}: Your={c1:3d}, Theirs={c2:3d}, Rounds={rounds:3d}, Score={score:2d}/20")
    
    # Display losses
    if losses:
        print(f"\n✗ DEFEATS ({len(losses)}):")
        print("-" * 70)
        losses.sort(key=lambda x: x[4])  # Sort by score (lowest first = worst losses)
        for name, c1, c2, rounds, score in losses:
            print(f"  {name:12s}: Your={c1:3d}, Theirs={c2:3d}, Rounds={rounds:3d}, Score={score:2d}/20")
    
    # Display ties
    if ties:
        print(f"\n= TIES ({len(ties)}):")
        print("-" * 70)
        for name, c1, c2, rounds, score in ties:
            print(f"  {name:12s}: Your={c1:3d}, Theirs={c2:3d}, Rounds={rounds:3d}, Score={score:2d}/20")
    
    # Summary
    total = len(wins) + len(losses) + len(ties)
    print(f"\nRecord: {len(wins)}-{len(losses)}-{len(ties)} ({len(wins)}/{total} wins)")
    
    # Show killer randoms if any
    if killer_randoms:
        print("\n" + "=" * 70)
        print(f"KILLER RANDOM GENOMES DISCOVERED: {len(killer_randoms)}")
        print("=" * 70)
        killer_randoms.sort(key=lambda x: x[1], reverse=True)
        for i, (genome, score, cat_scores) in enumerate(killer_randoms[:5], 1):
            print(f"\nKiller Random #{i}: Score={score:.2f}")
            print(f"  Genome: {genome}")
            print(f"  Beat {cat_scores.get('variants', 0):.1f} variants")
    
    print("\n" + "=" * 70)
    print("Best genome as string:")
    print(''.join(str(g) for g in all_time_best))
    print("=" * 70)
    
    return all_time_best, killer_randoms

if __name__ == "__main__":
    best, killers = hill_climb_with_diversity()