# Checkpoint 2 — Three-Stage Evolution Pipeline

Evolves PacWar genomes through three increasingly demanding gauntlets.

---

## Files

| File | Purpose |
|---|---|
| `utils.py` | Shared helpers: `random_genome`, `mutate_genome`, `score_battle`, `hill_climb`, JSON save/load |
| `stage1_baseline.py` | Random seeds → hill-climb until good vs All-1s & All-3s |
| `stage2_last_year.py` | Fine-tune survivors vs 29 last-year checkpoint genomes |
| `stage3_known.py` | Fine-tune vs full known pool (~70 opponents total) |
| `run_pipeline.py` | Runs all three stages end-to-end |

---

## Quick Start

```bash
# Run the full pipeline (all three stages back to back):
python run_pipeline.py

# Or run each stage individually:
python stage1_baseline.py    # → stage1_results.json
python stage2_last_year.py   # → stage2_results.json  (needs stage1)
python stage3_known.py       # → stage3_results.json  (needs stage2)
```

All three files are also runnable independently — each stage reads the
previous stage's JSON output, so you can resume from any point after a crash
or tweak parameters between stages.

---

## Scoring System (professor's system, 0–20 per duel)

| Outcome | Points |
|---|---|
| Destroy opponent in < 100 rounds | 20 |
| Destroy opponent in 100–199 rounds | 19 |
| Destroy opponent in 200–299 rounds | 18 |
| Destroy opponent in 300–500 rounds | 17 |
| Survive 500 rounds, outnumber ≥ 10:1 | 13 |
| Survive 500 rounds, outnumber ≥ 3:1 | 12 |
| Survive 500 rounds, outnumber ≥ 1.5:1 | 11 |
| Neither outnumbers by 1.5× | 10 |
| Survive 500 rounds, outnumbered ≤ 1/1.5 | 9 |
| Survive 500 rounds, outnumbered ≤ 1/3 | 8 |
| Survive 500 rounds, outnumbered ≤ 1/10 | 7 |
| Destroyed in 300–500 rounds | 3 |
| Destroyed in 200–299 rounds | 2 |
| Destroyed in 100–199 rounds | 1 |
| Destroyed in < 100 rounds | 0 |

---

## Key Parameters (tune in each stage file)

### Stage 1
| Parameter | Default | Meaning |
|---|---|---|
| `TARGET_SURVIVORS` | 20 | Genomes to pass forward |
| `PASS_THRESHOLD` | 36 | Min score vs All-1s+All-3s (out of 40) |
| `HILL_CLIMB_ROUNDS` | 80 | Rounds per candidate |
| `VARIANTS_PER_ROUND` | 30 | Mutations tested each round |
| `NUM_MUTATIONS` | 3 | Genes changed per mutation |

### Stage 2 & 3
Same shape — adjust `HILL_CLIMB_ROUNDS` for more/less refinement.
Stage 3 defaults to 120 rounds since the opponent pool is much larger.

---

## Stage Opponent Counts

| Stage | Opponents | Max Score |
|---|---|---|
| Stage 1 | 2 (All-1s, All-3s) | 40 |
| Stage 2 | 31 (29 last-year + 2 baselines) | 620 |
| Stage 3 | ~72 (known + last-year + 4 baselines) | ~1440 |
