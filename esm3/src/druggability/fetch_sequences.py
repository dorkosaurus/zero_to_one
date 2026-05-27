"""Fetch canonical UniProt FASTA for each protein in validate.tsv.

Outputs:
  data/sequences/<uniprot_id>.fasta  — one FASTA per protein
  data/sequences.tsv                 — manifest: uniprot_id, gene, length, sequence
"""

from __future__ import annotations

import sys
import time
from io import StringIO
from pathlib import Path

import pandas as pd
import requests
from Bio import SeqIO
from tqdm import tqdm

from druggability.paths import SEQUENCES_DIR, SEQUENCES_TSV, VALIDATE_TSV

OUT_DIR = SEQUENCES_DIR
MANIFEST = SEQUENCES_TSV

UNIPROT_FASTA_URL = "https://rest.uniprot.org/uniprotkb/{acc}.fasta"
TIMEOUT_S = 30
THROTTLE_S = 0.2


def fetch_fasta(accession: str) -> str:
    r = requests.get(UNIPROT_FASTA_URL.format(acc=accession), timeout=TIMEOUT_S)
    r.raise_for_status()
    if not r.text.startswith(">"):
        raise ValueError(f"no FASTA returned for {accession}")
    return r.text


def parse_sequence(fasta_text: str) -> str:
    rec = next(SeqIO.parse(StringIO(fasta_text), "fasta"))
    return str(rec.seq)


def main() -> int:
    if not VALIDATE_TSV.exists():
        print(f"ERROR: {VALIDATE_TSV} not found", file=sys.stderr)
        return 1

    targets = pd.read_csv(VALIDATE_TSV, sep="\t")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    failures: list[str] = []
    for _, row in tqdm(targets.iterrows(), total=len(targets), desc="UniProt"):
        acc, gene = row["uniprot_id"], row["gene"]
        fasta_path = OUT_DIR / f"{acc}.fasta"

        if fasta_path.exists():
            fasta_text = fasta_path.read_text()
        else:
            try:
                fasta_text = fetch_fasta(acc)
            except Exception as e:
                print(f"  FAIL {acc} ({gene}): {e}", file=sys.stderr)
                failures.append(acc)
                continue
            fasta_path.write_text(fasta_text)
            time.sleep(THROTTLE_S)

        seq = parse_sequence(fasta_text)
        rows.append({"uniprot_id": acc, "gene": gene, "length": len(seq), "sequence": seq})

    pd.DataFrame(rows).to_csv(MANIFEST, sep="\t", index=False)
    print(f"\nFetched {len(rows)}/{len(targets)} sequences -> {OUT_DIR}")
    print(f"Manifest: {MANIFEST}")
    if failures:
        print(f"Failed: {', '.join(failures)}", file=sys.stderr)
    return 0 if not failures else 2


if __name__ == "__main__":
    sys.exit(main())
