"""Shared filesystem paths for the pipeline."""

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

VALIDATE_TSV = REPO / "validate.tsv"
GOLD_STANDARD_TSV = REPO / "gold_standard.tsv"

DATA = REPO / "data"
SEQUENCES_DIR = DATA / "sequences"
SEQUENCES_TSV = DATA / "sequences.tsv"
STRUCTURES_DIR = DATA / "structures"
FUNCTIONS_DIR = DATA / "functions"
POCKETS_DIR = DATA / "pockets"
