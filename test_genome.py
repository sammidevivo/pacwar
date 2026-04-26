import _PyPacwar
import random

def score_battle(genome1, genome2):
    """Score a single battle using the professor's system. Returns (score, rounds, c1, c2)"""
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

def random_genome():
    """Generate a random genome of 50 genes (each 0-3)"""
    return [random.randint(0, 3) for _ in range(50)]

def test_genome(test_genome, genome_bank, num_random_tests=100):
    """
    Test a genome against a bank of genomes and random genomes.
    
    Parameters:
    - test_genome: The genome to test (list of 50 ints)
    - genome_bank: List of genomes (each is a list of 50 ints)
    - num_random_tests: How many random genomes to test against
    
    Returns: dict with all battle statistics
    """
    
    print("=" * 70)
    print("GENOME TESTING SUITE")
    print("=" * 70)
    print(f"Test Genome: {''.join(str(g) for g in test_genome)}")
    print(f"Testing against {len(genome_bank)} known genomes")
    print(f"Testing against {num_random_tests} random genomes")
    print("=" * 70)
    print()
    
    print("Testing against known genomes...")
    
    bank_results = []
    wins = []
    losses = []
    ties = []
    total_points = 0
    max_possible_points = len(genome_bank) * 20
    
    for idx, genome in enumerate(genome_bank, 1):
        score, rounds, c1, c2 = score_battle(test_genome, genome)
        
        result = {
            'index': idx,
            'score': score,
            'rounds': rounds,
            'your_count': c1,
            'their_count': c2,
            'genome': genome
        }
        
        total_points += score
        
        if c1 > c2:
            result['outcome'] = 'WIN'
            wins.append(result)
        elif c2 > c1:
            result['outcome'] = 'LOSS'
            losses.append(result)
        else:
            result['outcome'] = 'TIE'
            ties.append(result)
        
        bank_results.append(result)
        
        if idx % 10 == 0:
            print(f"  Progress: {idx}/{len(genome_bank)} battles complete...")
    
    print(f"Testing against {num_random_tests} random genomes...")
    
    random_wins = 0
    random_losses = 0
    random_ties = 0
    random_total_points = 0
    random_max_points = num_random_tests * 20
    random_killer_genomes = []
    
    for i in range(num_random_tests):
        random_opp = random_genome()
        score, rounds, c1, c2 = score_battle(test_genome, random_opp)
        
        random_total_points += score
        
        if c1 > c2:
            random_wins += 1
        elif c2 > c1:
            random_losses += 1
            random_killer_genomes.append({
                'genome': random_opp,
                'score': score,
                'rounds': rounds,
                'your_count': c1,
                'their_count': c2
            })
        else:
            random_ties += 1
        
        if (i + 1) % 25 == 0:
            print(f"  Progress: {i + 1}/{num_random_tests} random battles complete...")
    
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    
    total_battles = len(wins) + len(losses) + len(ties)
    win_rate = (len(wins) / total_battles * 100) if total_battles > 0 else 0
    avg_points = total_points / total_battles if total_battles > 0 else 0
    
    print(f"\nKNOWN GENOMES ({len(genome_bank)} opponents):")
    print(f"  Record: {len(wins)}-{len(losses)}-{len(ties)} (Win Rate: {win_rate:.1f}%)")
    print(f"  Total Points: {total_points}/{max_possible_points} (Avg: {avg_points:.2f}/20)")
    
    random_total = random_wins + random_losses + random_ties
    random_win_rate = (random_wins / random_total * 100) if random_total > 0 else 0
    random_avg_points = random_total_points / random_total if random_total > 0 else 0
    
    print(f"\nRANDOM GENOMES ({num_random_tests} opponents):")
    print(f"  Record: {random_wins}-{random_losses}-{random_ties} (Win Rate: {random_win_rate:.1f}%)")
    print(f"  Total Points: {random_total_points}/{random_max_points} (Avg: {random_avg_points:.2f}/20)")
    
    if wins:
        print(f"\n{'='*70}")
        print(f"VICTORIES ({len(wins)}) - Sorted by Score")
        print(f"{'='*70}")
        wins.sort(key=lambda x: (-x['score'], x['rounds']))  # Best scores first, fastest first
        
        for result in wins:
            print(f"Opponent #{result['index']:3d}: Score={result['score']:2d}/20, "
                  f"Rounds={result['rounds']:3d}, "
                  f"Your={result['your_count']:3d}, Theirs={result['their_count']:3d}")
    
    if losses:
        print(f"\n{'='*70}")
        print(f"LOSSES ({len(losses)})")
        print(f"{'='*70}")
        losses.sort(key=lambda x: (x['score'], -x['rounds']))
        
        for result in losses:
            print(f"Opponent #{result['index']:3d}: Score={result['score']:2d}/20, "
                  f"Rounds={result['rounds']:3d}, "
                  f"Your={result['your_count']:3d}, Theirs={result['their_count']:3d}")
            print(f"  Genome: {''.join(str(g) for g in result['genome'])}")
    
    if ties:
        print(f"\n{'='*70}")
        print(f"= TIES ({len(ties)})")
        print(f"{'='*70}")
        
        for result in ties:
            print(f"Opponent #{result['index']:3d}: Score={result['score']:2d}/20, "
                  f"Rounds={result['rounds']:3d}, "
                  f"Your={result['your_count']:3d}, Theirs={result['their_count']:3d}")
    
    if random_killer_genomes:
        print(f"\n{'='*70}")
        print(f"RANDOM LOSSES ({len(random_killer_genomes)})")
        print(f"{'='*70}")
        random_killer_genomes.sort(key=lambda x: (x['score'], -x['rounds']))
        
        for idx, result in enumerate(random_killer_genomes, 1):
            print(f"Random #{idx}: Score={result['score']:2d}/20, "
                  f"Rounds={result['rounds']:3d}, "
                  f"Your={result['your_count']:3d}, Theirs={result['their_count']:3d}")
            print(f"  Genome: {''.join(str(g) for g in result['genome'])}")
    
    print(f"\n{'='*70}")
    print("SCORE BREAKDOWN (Known Genomes)")
    print(f"{'='*70}")
    
    score_bins = {
        '20 (Destroyed <100)': 0,
        '19 (Destroyed 100-199)': 0,
        '18 (Destroyed 200-299)': 0,
        '17 (Destroyed 300-500)': 0,
        '13 (Outnumber 10:1+)': 0,
        '12 (Outnumber 3:1-10:1)': 0,
        '11 (Outnumber 1.5:1-3:1)': 0,
        '10 (Close/Tie)': 0,
        '9 (Outnumbered 1.5:1-3:1)': 0,
        '8 (Outnumbered 3:1-10:1)': 0,
        '7 (Outnumbered 10:1+)': 0,
        '3 (Destroyed 300-500)': 0,
        '2 (Destroyed 200-299)': 0,
        '1 (Destroyed 100-199)': 0,
        '0 (Destroyed <100)': 0,
    }
    
    score_map = {
        20: '20 (Destroyed <100)',
        19: '19 (Destroyed 100-199)',
        18: '18 (Destroyed 200-299)',
        17: '17 (Destroyed 300-500)',
        13: '13 (Outnumber 10:1+)',
        12: '12 (Outnumber 3:1-10:1)',
        11: '11 (Outnumber 1.5:1-3:1)',
        10: '10 (Close/Tie)',
        9: '9 (Outnumbered 1.5:1-3:1)',
        8: '8 (Outnumbered 3:1-10:1)',
        7: '7 (Outnumbered 10:1+)',
        3: '3 (Destroyed 300-500)',
        2: '2 (Destroyed 200-299)',
        1: '1 (Destroyed 100-199)',
        0: '0 (Destroyed <100)',
    }
    
    for result in bank_results:
        score_key = score_map.get(result['score'], '10 (Close/Tie)')
        score_bins[score_key] += 1
    
    for category, count in score_bins.items():
        if count > 0:
            pct = count / len(genome_bank) * 100
            print(f"  {category:30s}: {count:3d} ({pct:5.1f}%)")
    
    print("\n" + "=" * 70)
    
    return {
        'test_genome': test_genome,
        'bank_results': bank_results,
        'wins': wins,
        'losses': losses,
        'ties': ties,
        'win_rate': win_rate,
        'total_points': total_points,
        'avg_points': avg_points,
        'random_win_rate': random_win_rate,
        'random_wins': random_wins,
        'random_losses': random_losses,
        'random_ties': random_ties,
        'random_killer_genomes': random_killer_genomes,
    }

def main():
    """Test a genome against a comprehensive bank"""
    
    TEST_GENOME = list(map(int, "01000000010100000033123323223213223233313313323311"))

    GENOME_BANK = [
        [0] * 50,
        [1] * 50,
        [2] * 50,
        [3] * 50,

        list(map(int, "00020000101022203332321321323321321321333101102131")), # Priya
        list(map(int, "00020010101022033033321321323121321121331101103100")), # Priya II
        list(map(int, "00020010101022033033321321323121321121331101303100")), # Priya III
        list(map(int, "00002222222222222222111111113333333333333333333333")), # Claude
        list(map(int, "00300000011110223333333333333333321333103103020111")), # Pop
        list(map(int, "31030312111111223210033233023123121023230333210213")), # Rando
        list(map(int, "31120100111122223233123221323323123223233311300311")), # Tack
        list(map(int, "00020030131022230313321321321121321321132131110131")), # Woah
        list(map(int, "00020000131020200310321321321121321321130131101131")), # Woah II
        list(map(int, "00120000131020200010321321321321321322130131101131")), # Woah III
        list(map(int, "00110000111022213001311111111122111322121331131331")), # Brian
        list(map(int, "00110000111022213001111111111113122122120331113331")), # Leslie
        list(map(int, "13322001312212201133110232233131231222010220310123")), # Jessica
        list(map(int, "33322003110122223033233232233232231232000210102103")), # Fran
        list(map(int, "10111311011111111111111111111111213111121111121111")),
        list(map(int, "30333301333330333303303333333333233020330333333000")),
        list(map(int, "11111130111110111111300111111011131233213111211111")),
        list(map(int, "33333333333323033333233333333330303333333333303333")),
        list(map(int, "33332021333300333333301333333313303333103333303323")),
        list(map(int, "21111310111100101111132111111112023021023102331111")),
        list(map(int, "33332210333320333333322333333320300323210333203323")),
        list(map(int, "11210210111111112111111111111111101001211111310111")),
        list(map(int, "32123003100022221333222332331322331223230133013310")),
        list(map(int, "11111312101010111111111111111201111311110111100111")),
        list(map(int, "10111111111112111111101111111112111111121311311101")),
        list(map(int, "30333312333330332333333333333332033333333333013333")),
        list(map(int, "10301300011123023333312131112131111210330133100330")),
        list(map(int, "11113110111121021111120111111112113113031111311111")),
        list(map(int, "33332330333333003333100333333333332333312333003333")),
        list(map(int, "03101100122110323103221121130101322213122211111330")),
        list(map(int, "30333200133333333300333333333333333323133233303133")),
        list(map(int, "10111000301022233023111111111113332111123312313111")),
        list(map(int, "11112330011102011111301111111121111111100111101111")),
        list(map(int, "11111121111113001111312111111111011111011111332111")),
        list(map(int, "33332231333303323333333330333333111333333333021333")),
        list(map(int, "30330023033320303313323333333333333323323313303333")),
        list(map(int, "30333133333303333333333333333333303333333333330333")),
        list(map(int, "11110201111111011111300111111111330101111121121111")),
        list(map(int, "30333233233332333233330333333333313323023333303333")),
        list(map(int, "10112212132111211011111111111131111111111011011111")),
        list(map(int, "10113111131120111211121111111121120112310311332111")),
        list(map(int, "33133330100301121333323122021132123123321122100220")),
        list(map(int, "30333320033330133033333333333333320010233333221130")),
        list(map(int, "10111330131110111311131111111110201111311111003111")),
        list(map(int, "10112200101111311101111111111122111110131111101311")),

        list(map(int, "30021300131121223031213131311312132311333130003330")),
        list(map(int, "03103200120113003100312121323022022323020310013212")),
        list(map(int, "10321310130102223100332312133332113302303110130313")),
        list(map(int, "30333310300102032103233333333333321322223133103233")),

        # EVOLVED 1
        list(map(int, "32123003100022221333222332331322331223230133013310")),
        list(map(int, "10330330111120223333312331212111212212333130101331")),
        list(map(int, "00100010301322233023111111111112132113133331033331")),
        list(map(int, "03133300101101203333323121131111122123133131203131")),
        list(map(int, "30300100133122203303333333333333333333132203323130")),
        list(map(int, "30330000113020303303323333333333223323310313130310")),
        list(map(int, "10113000101121013301111111111221121113301311301311")),
        list(map(int, "10110000011122211310111111111112311111331330231301")),
        list(map(int, "30331130100323330303333333333332323323213333133333")),
        list(map(int, "10110100011122010011111111111121212112311111131111")),
        list(map(int, "00020000110122223033213131311112232311132130330131")),
        list(map(int, "03100001011022203303321121121012222023100110302300")),
        list(map(int, "00300000100322223330333333333232133233110110331313")),
        list(map(int, "00331000300122230300333333333333331332113133120131")),


        # EVOLVED 2
        list(map(int, "33320300131022223333213232232331232222030133100131")),
        list(map(int, "10330030130122233033312331212112112212233131201331")),
        list(map(int, "00100000331022233033111111111111122112130333333311")),
        list(map(int, "03133300101123203300323121131121122122133131212131")),
        list(map(int, "00300000133122003303331333333333333333130101111131")),

        list(map(int, "30300000113020003303323333333333323323113313110111")),
        list(map(int, "00100000101021023001111111111221111112301133301331")),
        list(map(int, "10100000011122203000111111111112121111321330002301")),
        list(map(int, "00300100111322303300333333333333233222310313312313")),
        list(map(int, "00110100011022003311111111111121212111311331230303")),

        list(map(int, "00020000100122223033213131211112232311131130330131")),
        list(map(int, "03100000010000133333321121121121222023120131331120")),
        list(map(int, "00300000100120203330333333333332223233110110131313")),
        list(map(int, "00301000100122213333333333333333221332113113100131")),

        # Random genome that keeps beating mine
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
    
    results = test_genome(TEST_GENOME, GENOME_BANK, num_random_tests=0)
    
    return results

if __name__ == "__main__":
    results = main()