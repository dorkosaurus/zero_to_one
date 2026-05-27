# FOXP3  (Q9BZS1)

**Gold label:** `negative`  •  **Modality:** transcription_factor
**Rank:** 17 / 20  •  **Score:** 0.302  •  **Confidence:** `ambiguous`

> Treg lineage TF

**What `ambiguous` means:** Mixed signals; manual review recommended.

**Caveats:**
- `low_fold_confidence` — Global pTM < 0.4 — ESM3 is uncertain how the protein folds globally. Trust pocket-level pLDDT, not the overall structure.
- `annotations_mislocated` — ESM3 produced annotations, but they don't overlap with high-quality pockets. The function track may be confused about this protein.

## Score breakdown

| Component | Weight | Value | Contribution |
|---|---|---|---|
| D — best confidence-weighted druggability | 0.5 | 0.445 | 0.223 |
| F — function-annotation support | 0.3 | 0.034 | 0.010 |
| S — top-pocket surface openness | 0.2 | 0.346 | 0.069 |
| **Total** | | | **0.302** |

## Structure quality

- Length: 431 aa
- pTM: 0.292
- Global mean pLDDT: 0.695
- Pockets detected (fpocket): 25
- Pockets with ≥1 narrow function-annotation overlap: 5

## Top 5 pockets

| # | Drugg. | Mean pLDDT | q = D·pLDDT | SASA (Å²) | n_residues | n_narrow_overlap |
|---|---|---|---|---|---|---|
| 25 | 0.625 | 0.712 | 0.445 | 347 | 18 | 0 |
| 24 | 0.069 | 0.727 | 0.050 | 82 | 5 | 0 |
| 7 | 0.016 | 0.949 | 0.015 | 28 | 8 | 12 |
| 11 | 0.011 | 0.778 | 0.009 | 110 | 8 | 0 |
| 5 | 0.007 | 0.960 | 0.007 | 116 | 9 | 11 |

## Interpretation

- **Borderline (0.302).** Sits between the clear-positive and clear-negative bands.
- Global pTM is low (0.292) — multi-domain or disordered. Per-pocket pLDDT (mean lining = 0.712) is the more honest signal here.
