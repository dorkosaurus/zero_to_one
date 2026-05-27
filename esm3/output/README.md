# Druggability scoring — summary

_20 proteins scored on a continuous 0–1 scale_

Score = 0.5·D + 0.3·F + 0.2·S, where D is the best confidence-weighted pocket druggability, F is the fraction of that quality captured by annotation-supported pockets, and S is the top pocket's surface area normalized to 1000 Å².

## Ranked results

| Rank | Gene | Gold | D | F | S | Score | Confidence | Caveats | Outcome |
|---|---|---|---|---|---|---|---|---|---|
| 1 | [BTK](BTK_Q06187.md) | positive | 0.877 | 1.000 | 0.415 | 0.821 | `likely` | multi_domain_confound | TP |
| 2 | [ADRB2](ADRB2_P07550.md) | positive | 0.855 | 1.000 | 0.204 | 0.768 | `strong` | — | TP |
| 3 | [TP53](TP53_P04637.md) | negative | 0.708 | 1.000 | 0.471 | 0.748 | `likely` | — | FP |
| 4 | [NR3C1](NR3C1_P04150.md) | positive | 0.817 | 1.000 | 0.184 | 0.746 | `likely` | low_fold_confidence;multi_domain_confound | TP |
| 5 | [BRD4](BRD4_O60885.md) | positive | 0.797 | 1.000 | 0.229 | 0.745 | `likely` | low_fold_confidence;multi_domain_confound | TP |
| 6 | [EGFR](EGFR_P00533.md) | positive | 0.702 | 1.000 | 0.304 | 0.712 | `likely` | low_fold_confidence;multi_domain_confound | TP |
| 7 | [NRAS](NRAS_P01111.md) | negative | 0.630 | 1.000 | 0.418 | 0.699 | `strong` | — | FP |
| 8 | [PARP1](PARP1_P09874.md) | positive | 0.587 | 1.000 | 0.279 | 0.650 | `strong` | — | TP |
| 9 | [HMGCR](HMGCR_P04035.md) | positive | 0.582 | 1.000 | 0.279 | 0.647 | `strong` | — | TP |
| 10 | [FOS](FOS_P01100.md) | negative | 0.509 | 1.000 | 0.242 | 0.603 | `likely` | low_fold_confidence | FP |
| 11 | [STAT3](STAT3_P40763.md) | negative | 0.508 | 1.000 | 0.142 | 0.582 | `strong` | — | FP |
| 12 | [CCR5](CCR5_P51681.md) | positive | 0.343 | 1.000 | 0.320 | 0.535 | `ambiguous` | — | TP |
| 13 | [ESR1](ESR1_P03372.md) | positive | 0.785 | 0.009 | 0.163 | 0.428 | `geometry_only` | annotations_mislocated;multi_domain_confound | FN |
| 14 | [CTNNB1](CTNNB1_P35222.md) | negative | 0.131 | 1.000 | 0.147 | 0.395 | `ambiguous` | — | TN |
| 15 | [KRAS](KRAS_P01116.md) | negative | 0.466 | 0.239 | 0.127 | 0.330 | `ambiguous` | — | TN |
| 16 | [BCL2](BCL2_P10415.md) | positive | 0.544 | 0.000 | 0.207 | 0.313 | `data_limited` | low_fold_confidence;no_function_annotations | FN |
| 17 | [FOXP3](FOXP3_Q9BZS1.md) | negative | 0.445 | 0.034 | 0.346 | 0.302 | `ambiguous` | low_fold_confidence;annotations_mislocated | TN |
| 18 | [NFE2L2](NFE2L2_Q16236.md) | negative | 0.469 | 0.011 | 0.139 | 0.266 | `ambiguous` | low_fold_confidence;annotations_mislocated;multi_domain_confound | TN |
| 19 | [MYC](MYC_P01106.md) | negative | 0.217 | 0.004 | 0.339 | 0.177 | `ambiguous` | low_fold_confidence;annotations_mislocated | TN |
| 20 | [RUNX1](RUNX1_Q01196.md) | negative | 0.182 | 0.000 | 0.103 | 0.112 | `ambiguous` | low_fold_confidence;no_function_annotations | TN |

## Calls by confidence band

### `strong` (n=5)

_All three signals (geometry, function, fold) agree — trust the verdict._

- [**ADRB2**](ADRB2_P07550.md) (positive, score 0.768, TP)
- [**NRAS**](NRAS_P01111.md) (negative, score 0.699, FP)
- [**PARP1**](PARP1_P09874.md) (positive, score 0.650, TP)
- [**HMGCR**](HMGCR_P04035.md) (positive, score 0.647, TP)
- [**STAT3**](STAT3_P40763.md) (negative, score 0.582, FP)

### `likely` (n=6)

_Geometry and function agree, but global fold confidence is shaky. Probably real with a caveat._

- [**BTK**](BTK_Q06187.md) (positive, score 0.821, TP)
- [**TP53**](TP53_P04637.md) (negative, score 0.748, FP)
- [**NR3C1**](NR3C1_P04150.md) (positive, score 0.746, TP)
- [**BRD4**](BRD4_O60885.md) (positive, score 0.745, TP)
- [**EGFR**](EGFR_P00533.md) (positive, score 0.712, TP)
- [**FOS**](FOS_P01100.md) (negative, score 0.603, FP)

### `geometry_only` (n=1)

_A strong pocket exists, but no function annotation supports it. Could be a real cryptic site, or a geometric false positive._

- [**ESR1**](ESR1_P03372.md) (positive, score 0.428, FN)

### `data_limited` (n=1)

_ESM3 declined to produce function annotations for this protein. Geometric signal is real but cannot be cross-checked. Treat as 'unknown', not 'undruggable'._

- [**BCL2**](BCL2_P10415.md) (positive, score 0.313, FN)

### `ambiguous` (n=7)

_Mixed signals; manual review recommended._

- [**CCR5**](CCR5_P51681.md) (positive, score 0.535, TP)
- [**CTNNB1**](CTNNB1_P35222.md) (negative, score 0.395, TN)
- [**KRAS**](KRAS_P01116.md) (negative, score 0.330, TN)
- [**FOXP3**](FOXP3_Q9BZS1.md) (negative, score 0.302, TN)
- [**NFE2L2**](NFE2L2_Q16236.md) (negative, score 0.266, TN)
- [**MYC**](MYC_P01106.md) (negative, score 0.177, TN)
- [**RUNX1**](RUNX1_Q01196.md) (negative, score 0.112, TN)

## Aggregate

- Positive set mean score: **0.636** (n=10)
- Negative set mean score: **0.421** (n=10)
- Separation (Δ): **0.215**

## Confusion matrix at threshold = 0.5

|  | predicted + | predicted − |
|---|---|---|
| actual + | 8 (TP) | 2 (FN) |
| actual − | 4 (FP) | 6 (TN) |

- Precision: 0.667  •  Recall: 0.800

- **ROC-AUC (all calls): 0.790**
- **ROC-AUC (trusted calls only, n=12): 0.656**

## Notable cases

**False positives (predicted druggable, gold says undruggable):**
- [TP53](TP53_P04637.md) (score 0.748) — flat DBD; tumor suppressor reactivators only
- [NRAS](NRAS_P01111.md) (score 0.699) — similar to KRAS WT
- [FOS](FOS_P01100.md) (score 0.603) — bZIP, AP-1 component; largely disordered
- [STAT3](STAT3_P40763.md) (score 0.582) — SH2 dimerization; hard to drug

**False negatives (predicted undruggable, gold says druggable):**
- [BCL2](BCL2_P10415.md) (score 0.313) — venetoclax (FDA 2016) — once considered undruggable
- [ESR1](ESR1_P03372.md) (score 0.428) — tamoxifen

## Per-target reports

- [BTK (Q06187)](BTK_Q06187.md) — score 0.821
- [ADRB2 (P07550)](ADRB2_P07550.md) — score 0.768
- [TP53 (P04637)](TP53_P04637.md) — score 0.748
- [NR3C1 (P04150)](NR3C1_P04150.md) — score 0.746
- [BRD4 (O60885)](BRD4_O60885.md) — score 0.745
- [EGFR (P00533)](EGFR_P00533.md) — score 0.712
- [NRAS (P01111)](NRAS_P01111.md) — score 0.699
- [PARP1 (P09874)](PARP1_P09874.md) — score 0.650
- [HMGCR (P04035)](HMGCR_P04035.md) — score 0.647
- [FOS (P01100)](FOS_P01100.md) — score 0.603
- [STAT3 (P40763)](STAT3_P40763.md) — score 0.582
- [CCR5 (P51681)](CCR5_P51681.md) — score 0.535
- [ESR1 (P03372)](ESR1_P03372.md) — score 0.428
- [CTNNB1 (P35222)](CTNNB1_P35222.md) — score 0.395
- [KRAS (P01116)](KRAS_P01116.md) — score 0.330
- [BCL2 (P10415)](BCL2_P10415.md) — score 0.313
- [FOXP3 (Q9BZS1)](FOXP3_Q9BZS1.md) — score 0.302
- [NFE2L2 (Q16236)](NFE2L2_Q16236.md) — score 0.266
- [MYC (P01106)](MYC_P01106.md) — score 0.177
- [RUNX1 (Q01196)](RUNX1_Q01196.md) — score 0.112
