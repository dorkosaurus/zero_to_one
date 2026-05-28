# Druggability scores for any protein variant or isoform with ESM3

Druggability assessment filters drug discovery target lists, but most pipelines are rules-based and sparse, especially for isoforms and variants.  

Generative Large Biological Models can fill this gap, so I tried ESM3 from Evolutionary Scale (now Biohub).  ESM3 is a multimodal LLM trained on three tracks (sequence, structure, function) that predicts all-atom 3D structures with per-residue confidence (pLDDT) and functional annotations for any sequence.

The pipeline:

1. Predict structure and functional residues with ESM3
2. Detect pockets with fpocket
3. Cross-reference pocket-lining residues against ESM3's pLDDT and functional annotations
4. Score: 50% confidence-weighted pocket druggability + 30% function-residue overlap + 20% surface accessibility
5. Tag every score with confidence so you know what to trust

Results on a 20-protein validation set drawn from a 40-protein gold standard (25 druggable, 15 undruggable): ROC-AUC 0.79, top six included five known druggable targets (BTK, ADRB2, NR3C1, BRD4, EGFR) plus one false positive (TP53).

The misses teach you something:

TP53 ranks high (6/20) because the pipeline correctly finds a cavity with high druggability score in the DNA-binding domain. But the cavity is a protein-DNA interface: flat, polar, shaped for macromolecular contact, not small molecules. The pipeline reasons on geometry; this is a chemistry problem.

BCL2 ranked low (16/20) even though venetoclax exists. ESM3 produced zero function annotations (a model blind spot), so the pipeline conservatively tagged it "data-limited" rather than committing a call. That's working as intended.

20-protein run: ~17 minutes on 1 core. Tractable across the entire druggable proteome and every isoform ever sequenced. Code and per-target reports in the comments.

-------------------------

Code:  https://github.com/dorkosaurus/zero_to_one/blob/main/esm3

Instructions: https://github.com/dorkosaurus/zero_to_one/blob/main/esm3/INSTRUCTIONS.md

Summary report: https://github.com/dorkosaurus/zero_to_one/blob/main/esm3/output/README.md  

The summary report links to every target analyzed.

