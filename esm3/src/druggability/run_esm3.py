"""Run ESM3 fold + function annotation for each sequence in data/sequences.tsv.

For each protein, makes two Forge API calls:
  1. generate(track="structure") -> coordinates, pLDDT, pTM
  2. generate(track="function")  -> InterPro function annotations as (label, start, end)

Outputs:
  data/structures/<uniprot_id>.pdb  — predicted all-atom structure
  data/functions/<uniprot_id>.json  — plddt, ptm, function_annotations, sequence
"""

from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from esm.sdk import client as make_client
from esm.sdk.api import ESMProtein, GenerationConfig
from tqdm import tqdm

from druggability.paths import (
    FUNCTIONS_DIR,
    REPO,
    SEQUENCES_TSV,
    STRUCTURES_DIR,
)

MODEL = "esm3-open-2024-03"


def _to_list(x) -> list | None:
    if x is None:
        return None
    if hasattr(x, "detach"):
        x = x.detach().cpu().numpy()
    if isinstance(x, np.ndarray):
        return x.tolist()
    return list(x)


def run_one(client, sequence: str) -> tuple[str, dict]:
    folded = client.generate(ESMProtein(sequence=sequence), GenerationConfig(track="structure"))
    if hasattr(folded, "error_code"):
        raise RuntimeError(f"fold error {folded.error_code}: {folded.error_msg}")
    # Function annotation: pass sequence only — including coordinates blows the 1MB body
    # limit for proteins >~1000 aa and adds no useful conditioning for InterPro labels.
    annotated = client.generate(
        ESMProtein(sequence=sequence), GenerationConfig(track="function")
    )
    if hasattr(annotated, "error_code"):
        raise RuntimeError(f"function error {annotated.error_code}: {annotated.error_msg}")

    pdb = folded.to_pdb_string()
    meta = {
        "sequence": sequence,
        "plddt": _to_list(folded.plddt),
        "ptm": float(folded.ptm) if folded.ptm is not None else None,
        "function_annotations": [
            {"label": fa.label, "start": fa.start, "end": fa.end}
            for fa in (annotated.function_annotations or [])
        ],
    }
    return pdb, meta


def main() -> int:
    load_dotenv(REPO / ".env")
    token = os.environ.get("ESM3_API_KEY") or os.environ.get("ESM_API_KEY")
    if not token:
        print("ERROR: ESM3_API_KEY not set (looked in .env)", file=sys.stderr)
        return 1

    seqs = pd.read_csv(SEQUENCES_TSV, sep="\t")
    STRUCTURES_DIR.mkdir(parents=True, exist_ok=True)
    FUNCTIONS_DIR.mkdir(parents=True, exist_ok=True)

    cli = make_client(model=MODEL, token=token)

    failures: list[str] = []
    for _, row in tqdm(seqs.iterrows(), total=len(seqs), desc="ESM3"):
        acc = row["uniprot_id"]
        pdb_path = STRUCTURES_DIR / f"{acc}.pdb"
        fn_path = FUNCTIONS_DIR / f"{acc}.json"
        if pdb_path.exists() and fn_path.exists():
            continue
        try:
            pdb, meta = run_one(cli, row["sequence"])
        except Exception as e:
            print(f"  FAIL {acc} ({row['gene']}): {e}", file=sys.stderr)
            failures.append(acc)
            continue
        pdb_path.write_text(pdb)
        fn_path.write_text(json.dumps(meta))

    print(f"\nDone. PDBs -> {STRUCTURES_DIR}, function JSONs -> {FUNCTIONS_DIR}")
    if failures:
        print(f"Failed ({len(failures)}): {', '.join(failures)}", file=sys.stderr)
    return 0 if not failures else 2


if __name__ == "__main__":
    sys.exit(main())
