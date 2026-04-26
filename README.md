# PacWar — Running the Code

## Requirements

- Python 3.11 (Windows)
- The `_PyPacwar.cp311-win_amd64.pyd` file must be in the root `python/` directory

Activate the virtual environment before running anything:
```
.venv\Scripts\activate
```

All scripts are run from inside their folder (e.g. `cd gene_ii` before running stage scripts).

---

## gene_i — Simple Hill Climbing

Early hill climbing and fine-tuning experiments.

```
cd gene_i
py -3.11 padawans.py          # hill-climb random genomes until they beat all baselines
py -3.11 evolution.py         # early GA experiment
py -3.11 fine_tuning.py       # weighted hill climber against full known genome pool
py -3.11 test_genome.py       # test a genome against the genome bank
py -3.11 tournament.py        # round-robin among a set of known genomes
py -3.11 random_tournament.py # round-robin among random genomes
```

---

## gene_ii — Three-Stage Pipeline

Runs hill climbing through three progressively harder opponent pools. Run stages in order, or use `run_pipeline.py` to do all three at once.

```
cd gene_ii
py -3.11 run_pipeline.py      # runs all three stages end-to-end
```

Or run each stage individually:
```
py -3.11 stage1_baseline.py   # finds 20 survivors that beat all-1s and all-3s (38/40)
py -3.11 stage2_last_year.py  # hill-climbs survivors vs 31 opponents (needs stage1_results.json)
py -3.11 stage3_known.py      # hill-climbs survivors vs 75 opponents (needs stage2_results.json)
```

Results are saved to `stage1_results.json`, `stage2_results.json`, `stage3_results.json` inside `gene_ii/`. Stage 1 saves after every survivor so it is safe to Ctrl-C and resume.

---

## gene_iii — Genetic Algorithm + Fine-Tuning

The final stage. Genomes discovered here are saved to `genomes.json`.

```
cd gene_iii
py -3.11 padawans.py   # find genomes that beat all 4 baselines (78/80), saves to padawans.json
py -3.11 ga.py         # run the genetic algorithm, saves strong genomes to genomes.json
py -3.11 evolve.py     # adaptive hill climbing from a single starting genome
py -3.11 test.py       # test a genome against genomes.json + random opponents
py -3.11 rank.py       # round-robin all genomes in genomes.json, ranked by score
```

To change which genome `evolve.py` or `test.py` operates on, edit `BASE_GENOME` or `TEST_GENOME` at the top of the file.
