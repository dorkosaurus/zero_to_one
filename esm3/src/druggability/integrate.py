"""Integrate fpocket results with ESM3 confidence (pLDDT) and function annotations.

For each protein we produce one summary JSON listing every fpocket pocket,
enriched with:
  - druggability, volume, total/polar/apolar SASA, n_alpha_spheres (from fpocket)
  - lining residues (extracted from pocket<N>_atm.pdb)
  - mean pLDDT over lining residues (the confidence mask)
  - overlapping narrow function annotations (motif-sized spans intersecting the pocket)

We treat function annotations as "narrow" when they span fewer than NARROW_ANNOT_MAX
residues. Whole-protein labels (e.g. "acid anhydrides" 1→L on KRAS) carry almost no
positional information and are dropped from the overlap signal.

Output:
  data/pockets/<id>/integrated.json
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from druggability.paths import FUNCTIONS_DIR, POCKETS_DIR, SEQUENCES_TSV

NARROW_ANNOT_MAX = 50  # residues; annotations longer than this are dropped from overlap

POCKET_HEADER_RE = re.compile(r"^Pocket (\d+) :")
SCORE_FIELDS = {
    "Score": "score",
    "Druggability Score": "druggability",
    "Number of Alpha Spheres": "n_alpha_spheres",
    "Total SASA": "sasa_total",
    "Polar SASA": "sasa_polar",
    "Apolar SASA": "sasa_apolar",
    "Volume": "volume",
    "Hydrophobicity score": "hydrophobicity",
    "Polarity score": "polarity",
    "Flexibility": "flexibility",
}


def parse_info(info_path: Path) -> dict[int, dict]:
    """fpocket info.txt -> {pocket_id: {field: value}}"""
    pockets: dict[int, dict] = {}
    current: int | None = None
    for raw in info_path.read_text().splitlines():
        m = POCKET_HEADER_RE.match(raw)
        if m:
            current = int(m.group(1))
            pockets[current] = {}
            continue
        if current is None:
            continue
        if ":" not in raw:
            continue
        key, _, val = raw.strip().partition(":")
        key = key.strip()
        if key in SCORE_FIELDS:
            try:
                pockets[current][SCORE_FIELDS[key]] = float(val.strip())
            except ValueError:
                pass
    return pockets


def parse_lining_residues(pdb_path: Path) -> list[int]:
    """Unique residue numbers (preserving first-seen order) from a fpocket atm PDB."""
    seen: dict[int, None] = {}
    for line in pdb_path.read_text().splitlines():
        if not line.startswith("ATOM"):
            continue
        try:
            resnum = int(line[22:26])
        except ValueError:
            continue
        seen.setdefault(resnum, None)
    return list(seen.keys())


def overlap_narrow(residues: list[int], annotations: list[dict], seq_len: int) -> list[dict]:
    """Return annotations that (a) are narrow and (b) overlap with the residue set."""
    if not residues:
        return []
    rset = set(residues)
    hits = []
    for ann in annotations:
        start, end = ann["start"], ann["end"]
        span = end - start + 1
        if span >= NARROW_ANNOT_MAX or span >= seq_len:
            continue
        ann_set = set(range(start, end + 1))
        n_overlap = len(rset & ann_set)
        if n_overlap == 0:
            continue
        hits.append({
            "label": ann["label"],
            "start": start,
            "end": end,
            "span": span,
            "n_overlap": n_overlap,
        })
    return hits


def integrate_one(acc: str) -> dict | None:
    fn_path = FUNCTIONS_DIR / f"{acc}.json"
    info_path = POCKETS_DIR / acc / "fpocket" / f"{acc}_out" / f"{acc}_info.txt"
    pockets_dir = POCKETS_DIR / acc / "fpocket" / f"{acc}_out" / "pockets"
    if not (fn_path.exists() and info_path.exists() and pockets_dir.exists()):
        return None

    fn = json.loads(fn_path.read_text())
    plddt = fn["plddt"]
    seq_len = len(plddt)
    annotations = fn.get("function_annotations", [])

    pocket_meta = parse_info(info_path)
    pockets = []
    for pid in sorted(pocket_meta.keys()):
        atm_path = pockets_dir / f"pocket{pid}_atm.pdb"
        if not atm_path.exists():
            continue
        residues = parse_lining_residues(atm_path)
        lining_plddt = [plddt[r - 1] for r in residues if 1 <= r <= seq_len]
        mean_plddt = sum(lining_plddt) / len(lining_plddt) if lining_plddt else 0.0
        pockets.append({
            "pocket_id": pid,
            **pocket_meta[pid],
            "n_lining_residues": len(residues),
            "lining_residues": residues,
            "mean_plddt": mean_plddt,
            "narrow_annotation_overlaps": overlap_narrow(residues, annotations, seq_len),
        })

    return {
        "uniprot_id": acc,
        "seq_len": seq_len,
        "ptm": fn.get("ptm"),
        "mean_plddt_global": sum(plddt) / len(plddt),
        "n_annotations_total": len(annotations),
        "n_annotations_narrow": sum(
            1 for a in annotations if a["end"] - a["start"] + 1 < NARROW_ANNOT_MAX
        ),
        "n_pockets": len(pockets),
        "pockets": pockets,
    }


def main() -> int:
    seqs = pd.read_csv(SEQUENCES_TSV, sep="\t")
    missing: list[str] = []
    for _, row in tqdm(seqs.iterrows(), total=len(seqs), desc="integrate"):
        acc = row["uniprot_id"]
        result = integrate_one(acc)
        if result is None:
            missing.append(acc)
            continue
        out = POCKETS_DIR / acc / "integrated.json"
        out.write_text(json.dumps(result, indent=2))
    print(f"\nWrote integrated.json for {len(seqs) - len(missing)}/{len(seqs)} proteins")
    if missing:
        print(f"Missing inputs: {', '.join(missing)}", file=sys.stderr)
    return 0 if not missing else 2


if __name__ == "__main__":
    sys.exit(main())
