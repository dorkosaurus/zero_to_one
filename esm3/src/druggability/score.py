"""Compute per-protein druggability score from integrated pocket data.

Continuous formulation (no hard cutoffs):

  q_i = pocket_i.druggability * pocket_i.mean_plddt        # confidence-weighted quality
  D = max_i q_i                                            # best pocket [0..1]
  F = max(q over annotated pockets) / max(q over all)      # function support [0..1]
  S = min(top_pocket.sasa_total / 1000, 1)                 # surface openness [0..1]

  score = 0.5*D + 0.3*F + 0.2*S

Output:
  data/scores.tsv         — joined to gold_standard, sortable
"""

from __future__ import annotations

import json
import sys

import pandas as pd

from druggability.paths import (
    DATA,
    GOLD_STANDARD_TSV,
    POCKETS_DIR,
    SEQUENCES_TSV,
)

SASA_NORM = 1000.0  # Å² — typical druggable pocket is 200-800 Å²
W_D, W_F, W_S = 0.5, 0.3, 0.2


def score_protein(integ: dict) -> dict:
    pockets = integ["pockets"]
    if not pockets:
        return {
            "D": 0.0, "F": 0.0, "S": 0.0, "score": 0.0,
            "top_pocket_id": None, "top_druggability": 0.0,
            "top_mean_plddt": 0.0, "top_sasa": 0.0,
            "n_pockets": 0, "n_annotated_pockets": 0,
        }

    for p in pockets:
        p["q"] = p["druggability"] * p["mean_plddt"]

    top = max(pockets, key=lambda p: p["q"])
    q_best = top["q"]
    annotated = [p for p in pockets if p["narrow_annotation_overlaps"]]
    q_best_annot = max((p["q"] for p in annotated), default=0.0)

    D = q_best
    F = q_best_annot / q_best if q_best > 0 else 0.0
    S = min(top.get("sasa_total", 0.0) / SASA_NORM, 1.0)
    score = W_D * D + W_F * F + W_S * S

    return {
        "D": D, "F": F, "S": S, "score": score,
        "top_pocket_id": top["pocket_id"],
        "top_druggability": top["druggability"],
        "top_mean_plddt": top["mean_plddt"],
        "top_sasa": top.get("sasa_total", 0.0),
        "n_pockets": len(pockets),
        "n_annotated_pockets": len(annotated),
    }


def main() -> int:
    seqs = pd.read_csv(SEQUENCES_TSV, sep="\t")
    gold = pd.read_csv(GOLD_STANDARD_TSV, sep="\t")[["uniprot_id", "label", "modality", "rationale"]]

    rows = []
    for _, row in seqs.iterrows():
        acc = row["uniprot_id"]
        integ_path = POCKETS_DIR / acc / "integrated.json"
        if not integ_path.exists():
            print(f"  skip {acc}: no integrated.json", file=sys.stderr)
            continue
        integ = json.loads(integ_path.read_text())
        rows.append({
            "uniprot_id": acc,
            "gene": row["gene"],
            "length": row["length"],
            "ptm": integ.get("ptm"),
            "mean_plddt_global": integ.get("mean_plddt_global"),
            **score_protein(integ),
        })

    df = pd.DataFrame(rows).merge(gold, on="uniprot_id", how="left")
    df = df.sort_values("score", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1

    out = DATA / "scores.tsv"
    df.to_csv(out, sep="\t", index=False, float_format="%.4f")
    print(f"Wrote {out}  ({len(df)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
