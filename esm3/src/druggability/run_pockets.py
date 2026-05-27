"""Run fpocket on each predicted structure in data/structures/.

Geometry-based pocket detection (alpha-sphere theory). P2Rank was originally in
the design as a second, ML-based detector for cross-tool agreement, but the
JVM's memory footprint is incompatible with this host (1 core, 1.9 GB RAM).

Outputs:
  data/pockets/<id>/fpocket/<id>_out/...   — full fpocket output tree
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from tqdm import tqdm

from druggability.paths import POCKETS_DIR, STRUCTURES_DIR

FPOCKET_BIN = shutil.which("fpocket") or "/usr/local/bin/fpocket"


def run_fpocket(pdb: Path, out_root: Path) -> Path:
    """fpocket writes <stem>_out/ next to its input. Stage the PDB then run."""
    work = out_root / "fpocket"
    work.mkdir(parents=True, exist_ok=True)
    staged = work / pdb.name
    if not staged.exists():
        shutil.copy(pdb, staged)
    result_dir = work / f"{pdb.stem}_out"
    if result_dir.exists():
        return result_dir
    subprocess.run(
        [FPOCKET_BIN, "-f", staged.name],
        cwd=work,
        check=True,
        capture_output=True,
    )
    return result_dir


def main() -> int:
    pdbs = sorted(STRUCTURES_DIR.glob("*.pdb"))
    if not pdbs:
        print(f"ERROR: no PDBs in {STRUCTURES_DIR}", file=sys.stderr)
        return 1
    if not Path(FPOCKET_BIN).exists():
        print(f"ERROR: fpocket not found at {FPOCKET_BIN}", file=sys.stderr)
        return 1

    POCKETS_DIR.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []
    for pdb in tqdm(pdbs, desc="fpocket"):
        acc = pdb.stem
        try:
            run_fpocket(pdb, POCKETS_DIR / acc)
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode("utf-8", errors="replace")[-500:] if e.stderr else ""
            print(f"  FAIL {acc}: fpocket returned {e.returncode}\n{stderr}", file=sys.stderr)
            failures.append(acc)

    print(f"\nDone. Pocket outputs -> {POCKETS_DIR}")
    if failures:
        print(f"Failed ({len(failures)}): {', '.join(failures)}", file=sys.stderr)
    return 0 if not failures else 2


if __name__ == "__main__":
    sys.exit(main())
