# Creating druggability scores at scale for any protein variant and isoform with ESM3

Druggability scores help filter drug discovery target lists. But most pipelines are "rules-based" — deterministic and sparse, especially for isoforms and variants.

Generative Large Biological Models might be able to fill this gap, so I tried ESM3 from Evolutionary Scale (now Biohub).  ESM3 is a multimodal LLM trained on three tracks (sequence, structure, function) that predicts:

* All-atom 3D structures with per-residue confidence (pLDDT) 
* Per-residue functional annotations for any protein sequence (natural or engineered)

I built a simple pipeline on top of ESM3 and fpocket to assess targets for small molecule druggability.  Given any set of protein identifiers or sequences:

1. Predict structure, residue-level functional annotations, and per-residue confidence (pLDDT)
2. Detect pockets in each predicted structure with fpocket
3. Cross-reference pocket-lining residues with ESM3's pLDDT and function annotations
4. Score each protein: 50% confidence-weighted pocket druggability + 30% function-residue overlap + 20% surface accessibility (ESM3)
5. Tag every call with a confidence band so the reader knows how much to trust the score.

I tested against a 40-protein gold standard (25 druggable, 15 undruggable) using a 20-protein held-out validation set.

Results: ROC-AUC 0.79. The top six were five known druggable targets (BTK, ADRB2, NR3C1, BRD4, EGFR) and one known undruggable (TP53). Two cases worth a closer look:

* False positive: TP53 (rank 6) — known undruggable but called druggable.
* False negative: BCL2 (rank 16) — a drug exists but marked undruggable.

TP53 is a false positive, but the pipeline is right about every individual claim: ESM3 folds the DNA-binding domain confidently, fpocket finds a 0.99-druggability cavity there, and ESM3's annotations correctly identify it as a DNA-binding surface — all three signals agree.

The issue: the cavity is part of a protein-DNA interface — flat, polar, and shaped for extended macromolecular contact, not the deep hydrophobic pockets small molecules need. The pipeline reasons on geometry; this is a chemistry problem.

For BCL2, ESM3 wasn't emitting the data the pipeline needed:

* fpocket found a respectable cavity (top pocket: 0.79 druggability, mean pLDDT 0.69).
* The fold holds up locally even though global pTM is low (0.34).
* But ESM3 produced zero function annotations across the protein — sampling sweeps confirmed a real model blind spot.

With no function signal to cross-check, the pipeline tagged BCL2 "data limited" rather than "undruggable." That distinction matters: BCL2 was considered undruggable for 15 years before venetoclax got FDA approval in 2016.

The full 20-protein run took ~17 minutes on a 1-core machine. At scale, this is tractable across the entire druggable proteome and every isoform ever sequenced.

Code, instructions, and per-target reports in the comments.

-------------------------

Code:  https://github.com/dorkosaurus/zero_to_one/blob/main/esm3

Instructions: https://github.com/dorkosaurus/zero_to_one/blob/main/esm3/INSTRUCTIONS.md

Summary report: https://github.com/dorkosaurus/zero_to_one/blob/main/esm3/output/README.md  

The summary report links to every target analyzed.

