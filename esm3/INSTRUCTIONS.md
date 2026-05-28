# Running the druggability pipeline

End-to-end: take a list of UniProt accessions, predict structures + function annotations with ESM3, detect pockets with fpocket, score, and write per-target reports.

## Prerequisites

- Linux (Ubuntu/Debian) — `install.sh` is apt-based
- Python 3.11+
- An ESM3 API key from [Forge](https://forge.evolutionaryscale.ai/)
- ~2 GB RAM, 1 core is enough

## One-time setup

```bash
git clone <repo-url> esm3
cd esm3

# create a venv at ~/venv (the Makefile expects this path)
python3 -m venv ~/venv

# install fpocket (built from source) + Python deps
make install

# put your Forge API key in .env
echo 'ESM3_API_KEY=<your-token>' > .env
```

## Input

Edit `references/validate.tsv` — one row per protein, tab-separated:

```
uniprot_id	gene
P00533	EGFR
Q06187	BTK
```

For benchmarking, `references/gold_standard.tsv` carries `label` (positive / negative) + `modality` + `rationale`. The scoring step joins on `uniprot_id` and the report step uses the labels for the confusion matrix + ROC-AUC. Add new entries here if you want them included in those stats.

## Running the pipeline

```bash
make fetch-sequences   # download canonical FASTA per UniProt -> data/sequences/
make run-esm3          # fold + annotate via Forge -> data/structures/, data/functions/
make run-pockets       # fpocket per structure       -> data/pockets/<id>/fpocket/
make integrate         # join geometry + pLDDT + fn  -> data/pockets/<id>/integrated.json
make score             # D/F/S/score per protein     -> data/scores.tsv
make report            # per-target reports + summary -> output/
```

Or run the last three together:

```bash
make all   # integrate -> score -> report
```

The Forge call is the slow step (~30–60s per protein); everything else is seconds.

## Outputs

- `data/scores.tsv` — ranked table: D/F/S, score, confidence band, caveats
- `output/README.md` — summary across all proteins (ROC-AUC, confusion matrix, ranked list)
- `output/<gene>_<uniprot>.md` — per-target report with score breakdown, top pockets, confidence band rationale

## Resource notes

The full 20-protein validation set runs in ~17 minutes on a 1-core / 1.9 GB host. The bottleneck is Forge API latency, not local compute. fpocket is fast (~5s per structure); ESM3 inference is remote.

If you swap in a much larger protein list, expect Forge to be the limiting factor — runtime scales roughly linearly with protein count, not protein length.

## Re-running individual steps

Each Make target is idempotent and reads from on-disk artifacts. To re-score with a different formula, edit `src/druggability/score.py` and run `make score report` — no need to re-fetch sequences or re-run ESM3.

To rebuild from scratch: `make clean` removes `data/` and caches.
