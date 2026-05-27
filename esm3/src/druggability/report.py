"""Generate per-target Markdown reports and a summary report.

Inputs:  data/scores.tsv, data/pockets/<id>/integrated.json, references/gold_standard.tsv
Outputs: output/<gene>_<uniprot>.md   (one per target)
         output/README.md             (summary, rendered automatically on GitHub)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

from druggability.paths import (
    DATA,
    GOLD_STANDARD_TSV,
    OUTPUT,
    POCKETS_DIR,
)

TOP_K_POCKETS = 5

# Plain-English explanation for each confidence band
BAND_DESCRIPTIONS = {
    "strong": "All three signals (geometry, function, fold) agree — trust the verdict.",
    "likely": "Geometry and function agree, but global fold confidence is shaky. Probably real with a caveat.",
    "geometry_only": "A strong pocket exists, but no function annotation supports it. Could be a real cryptic site, or a geometric false positive.",
    "data_limited": "ESM3 declined to produce function annotations for this protein. Geometric signal is real but cannot be cross-checked. Treat as 'unknown', not 'undruggable'.",
    "likely_undruggable": "Low pocket quality and low fold confidence. The structure-based view says no obvious pocket exists.",
    "ambiguous": "Mixed signals; manual review recommended.",
}

CAVEAT_DESCRIPTIONS = {
    "low_fold_confidence": "Global pTM < 0.4 — ESM3 is uncertain how the protein folds globally. Trust pocket-level pLDDT, not the overall structure.",
    "disordered_signature": "Mean pLDDT < 0.5 — protein is largely disordered or flexible. Any pocket call should be viewed skeptically.",
    "no_function_annotations": "ESM3 produced zero function annotations. This is a model blind spot, not evidence of no function.",
    "annotations_mislocated": "ESM3 produced annotations, but they don't overlap with high-quality pockets. The function track may be confused about this protein.",
    "multi_domain_confound": "Long protein with low global fold confidence — likely multi-domain. Per-domain analysis may be more informative than whole-protein scoring.",
}


def _fmt(x, n=3):
    if x is None:
        return "—"
    try:
        return f"{x:.{n}f}"
    except (TypeError, ValueError):
        return str(x)


def interpret(row: pd.Series, integ: dict) -> str:
    """A few sentences calling out the headline pattern for this target."""
    bullets: list[str] = []
    score, label = row["score"], row.get("label", "?")
    D, F, S = row["D"], row["F"], row["S"]

    # Headline judgment
    if score >= 0.5 and label == "positive":
        bullets.append("**True positive.** Score above 0.5 and gold standard is druggable.")
    elif score < 0.3 and label == "negative":
        bullets.append("**True negative.** Score below 0.3 and gold standard is undruggable.")
    elif score >= 0.5 and label == "negative":
        bullets.append("**False positive.** Score above 0.5 but gold standard is undruggable — a case where geometry/confidence look druggable but the biology says no.")
    elif score < 0.3 and label == "positive":
        bullets.append("**False negative.** Score below 0.3 but the target is known druggable — likely a structural or annotation failure mode.")
    else:
        bullets.append(f"**Borderline ({_fmt(score)}).** Sits between the clear-positive and clear-negative bands.")

    # Confidence
    ptm = row.get("ptm")
    if ptm is not None:
        if ptm < 0.4:
            bullets.append(f"Global pTM is low ({_fmt(ptm)}) — multi-domain or disordered. Per-pocket pLDDT (mean lining = {_fmt(row['top_mean_plddt'])}) is the more honest signal here.")
        elif ptm > 0.8:
            bullets.append(f"Strong global fold (pTM {_fmt(ptm)}); geometry is trustworthy.")

    # Component-level diagnostics
    if D > 0.7 and F < 0.1:
        bullets.append("Best pocket is geometrically strong but doesn't coincide with any narrow function annotation — could be a real cryptic site, or a fpocket false positive.")
    if F > 0.9 and D < 0.3:
        bullets.append("Function-annotation support is strong but the underlying pocket quality is weak — suggests known functional surface but no obvious small-molecule pocket.")
    if S < 0.2:
        bullets.append(f"Top pocket SASA is small ({_fmt(row['top_sasa'], 0)} Å²) — pocket is shallow or partially buried.")

    return "\n".join(f"- {b}" for b in bullets)


def write_target_report(row: pd.Series, integ: dict) -> Path:
    pockets = sorted(integ["pockets"], key=lambda p: p["druggability"] * p["mean_plddt"], reverse=True)
    top_pockets = pockets[:TOP_K_POCKETS]

    md: list[str] = []
    md.append(f"# {row['gene']}  ({row['uniprot_id']})")
    md.append("")
    md.append(f"**Gold label:** `{row.get('label', '?')}`  •  **Modality:** {row.get('modality', '—')}")
    md.append(f"**Rank:** {row['rank']} / {row.get('n_total', '?')}  •  **Score:** {_fmt(row['score'])}  •  **Confidence:** `{row.get('confidence', '—')}`")
    md.append("")
    md.append(f"> {row.get('rationale', '')}")
    md.append("")

    band = row.get("confidence")
    if band in BAND_DESCRIPTIONS:
        md.append(f"**What `{band}` means:** {BAND_DESCRIPTIONS[band]}")
        md.append("")

    cav = row.get("caveats", "")
    caveats = [c for c in str(cav).split(";") if c and c != "nan"] if isinstance(cav, str) else []
    if caveats:
        md.append("**Caveats:**")
        for c in caveats:
            md.append(f"- `{c}` — {CAVEAT_DESCRIPTIONS.get(c, '')}")
        md.append("")

    md.append("## Score breakdown")
    md.append("")
    md.append("| Component | Weight | Value | Contribution |")
    md.append("|---|---|---|---|")
    md.append(f"| D — best confidence-weighted druggability | 0.5 | {_fmt(row['D'])} | {_fmt(0.5*row['D'])} |")
    md.append(f"| F — function-annotation support | 0.3 | {_fmt(row['F'])} | {_fmt(0.3*row['F'])} |")
    md.append(f"| S — top-pocket surface openness | 0.2 | {_fmt(row['S'])} | {_fmt(0.2*row['S'])} |")
    md.append(f"| **Total** | | | **{_fmt(row['score'])}** |")
    md.append("")

    md.append("## Structure quality")
    md.append("")
    md.append(f"- Length: {row['length']} aa")
    md.append(f"- pTM: {_fmt(row['ptm'])}")
    md.append(f"- Global mean pLDDT: {_fmt(row['mean_plddt_global'])}")
    md.append(f"- Pockets detected (fpocket): {row['n_pockets']}")
    md.append(f"- Pockets with ≥1 narrow function-annotation overlap: {row['n_annotated_pockets']}")
    md.append("")

    md.append(f"## Top {len(top_pockets)} pockets")
    md.append("")
    md.append("| # | Drugg. | Mean pLDDT | q = D·pLDDT | SASA (Å²) | n_residues | n_narrow_overlap |")
    md.append("|---|---|---|---|---|---|---|")
    for p in top_pockets:
        q = p["druggability"] * p["mean_plddt"]
        md.append(
            f"| {p['pocket_id']} | {_fmt(p['druggability'])} | {_fmt(p['mean_plddt'])} | "
            f"{_fmt(q)} | {_fmt(p.get('sasa_total', 0), 0)} | {p['n_lining_residues']} | "
            f"{len(p['narrow_annotation_overlaps'])} |"
        )
    md.append("")

    if top_pockets and top_pockets[0]["narrow_annotation_overlaps"]:
        md.append(f"### Narrow function annotations overlapping pocket {top_pockets[0]['pocket_id']}")
        md.append("")
        md.append("| Label | Span | Overlap |")
        md.append("|---|---|---|")
        for hit in top_pockets[0]["narrow_annotation_overlaps"][:10]:
            md.append(f"| {hit['label']} | {hit['start']}–{hit['end']} ({hit['span']} aa) | {hit['n_overlap']} |")
        md.append("")

    md.append("## Interpretation")
    md.append("")
    md.append(interpret(row, integ))
    md.append("")

    out = OUTPUT / f"{row['gene']}_{row['uniprot_id']}.md"
    out.write_text("\n".join(md))
    return out


def write_summary(df: pd.DataFrame) -> Path:
    md: list[str] = []
    md.append("# Druggability scoring — summary")
    md.append("")
    md.append(f"_{len(df)} proteins scored on a continuous 0–1 scale_")
    md.append("")
    md.append("Score = 0.5·D + 0.3·F + 0.2·S, where D is the best confidence-weighted pocket "
              "druggability, F is the fraction of that quality captured by annotation-supported "
              "pockets, and S is the top pocket's surface area normalized to 1000 Å².")
    md.append("")

    md.append("## Ranked results")
    md.append("")
    md.append("| Rank | Gene | Gold | D | F | S | Score | Confidence | Caveats | Outcome |")
    md.append("|---|---|---|---|---|---|---|---|---|---|")
    for _, r in df.iterrows():
        outcome = classify_outcome(r["score"], r.get("label"))
        cav = r.get("caveats", "")
        caveats = cav if isinstance(cav, str) and cav else "—"
        md.append(
            f"| {r['rank']} | {r['gene']} | {r.get('label', '?')} | "
            f"{_fmt(r['D'])} | {_fmt(r['F'])} | {_fmt(r['S'])} | "
            f"{_fmt(r['score'])} | `{r.get('confidence', '—')}` | {caveats} | {outcome} |"
        )
    md.append("")

    # Group by confidence band
    md.append("## Calls by confidence band")
    md.append("")
    for band in ["strong", "likely", "geometry_only", "data_limited", "ambiguous", "likely_undruggable"]:
        sub = df[df["confidence"] == band]
        if sub.empty:
            continue
        md.append(f"### `{band}` (n={len(sub)})")
        md.append("")
        md.append(f"_{BAND_DESCRIPTIONS.get(band, '')}_")
        md.append("")
        for _, r in sub.iterrows():
            outcome = classify_outcome(r["score"], r.get("label"))
            md.append(f"- **{r['gene']}** ({r.get('label', '?')}, score {_fmt(r['score'])}, {outcome})")
        md.append("")

    pos = df[df["label"] == "positive"]
    neg = df[df["label"] == "negative"]
    md.append("## Aggregate")
    md.append("")
    md.append(f"- Positive set mean score: **{_fmt(pos['score'].mean())}** (n={len(pos)})")
    md.append(f"- Negative set mean score: **{_fmt(neg['score'].mean())}** (n={len(neg)})")
    md.append(f"- Separation (Δ): **{_fmt(pos['score'].mean() - neg['score'].mean())}**")
    md.append("")

    # Confusion matrix at score=0.5
    threshold = 0.5
    tp = len(df[(df["label"] == "positive") & (df["score"] >= threshold)])
    fn = len(df[(df["label"] == "positive") & (df["score"] < threshold)])
    fp = len(df[(df["label"] == "negative") & (df["score"] >= threshold)])
    tn = len(df[(df["label"] == "negative") & (df["score"] < threshold)])
    md.append(f"## Confusion matrix at threshold = {threshold}")
    md.append("")
    md.append("|  | predicted + | predicted − |")
    md.append("|---|---|---|")
    md.append(f"| actual + | {tp} (TP) | {fn} (FN) |")
    md.append(f"| actual − | {fp} (FP) | {tn} (TN) |")
    md.append("")
    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    md.append(f"- Precision: {_fmt(precision)}  •  Recall: {_fmt(recall)}")
    md.append("")

    # ROC-AUC
    try:
        from sklearn.metrics import roc_auc_score
        y = (df["label"] == "positive").astype(int)
        auc = roc_auc_score(y, df["score"])
        md.append(f"- **ROC-AUC (all calls): {_fmt(auc)}**")
        # Restricted AUC: drop the calls we don't trust (data_limited, ambiguous)
        trusted = df[~df["confidence"].isin(["data_limited", "ambiguous"])]
        if len(trusted) > 2 and trusted["label"].nunique() > 1:
            yt = (trusted["label"] == "positive").astype(int)
            auc_t = roc_auc_score(yt, trusted["score"])
            md.append(f"- **ROC-AUC (trusted calls only, n={len(trusted)}): {_fmt(auc_t)}**")
        md.append("")
    except Exception:
        pass

    md.append("## Notable cases")
    md.append("")
    fps = df[(df["label"] == "negative") & (df["score"] >= threshold)].sort_values("score", ascending=False)
    fns = df[(df["label"] == "positive") & (df["score"] < threshold)].sort_values("score")
    if not fps.empty:
        md.append("**False positives (predicted druggable, gold says undruggable):**")
        for _, r in fps.iterrows():
            md.append(f"- {r['gene']} (score {_fmt(r['score'])}) — {r.get('rationale', '')}")
        md.append("")
    if not fns.empty:
        md.append("**False negatives (predicted undruggable, gold says druggable):**")
        for _, r in fns.iterrows():
            md.append(f"- {r['gene']} (score {_fmt(r['score'])}) — {r.get('rationale', '')}")
        md.append("")

    md.append("## Per-target reports")
    md.append("")
    for _, r in df.iterrows():
        md.append(f"- [{r['gene']} ({r['uniprot_id']})]({r['gene']}_{r['uniprot_id']}.md) — score {_fmt(r['score'])}")
    md.append("")

    out = OUTPUT / "README.md"
    out.write_text("\n".join(md))
    return out


def classify_outcome(score: float, label) -> str:
    if pd.isna(label):
        return "—"
    pred_pos = score >= 0.5
    actual_pos = label == "positive"
    if pred_pos and actual_pos: return "TP"
    if (not pred_pos) and (not actual_pos): return "TN"
    if pred_pos and (not actual_pos): return "FP"
    return "FN"


def main() -> int:
    scores_path = DATA / "scores.tsv"
    if not scores_path.exists():
        print(f"ERROR: {scores_path} not found — run `make score` first", file=sys.stderr)
        return 1

    df = pd.read_csv(scores_path, sep="\t")
    df["n_total"] = len(df)

    # The gold standard rationale isn't on the validate set; merge it in.
    gold = pd.read_csv(GOLD_STANDARD_TSV, sep="\t")[["uniprot_id", "label", "modality", "rationale"]]
    df = df.drop(columns=[c for c in ("label", "modality", "rationale") if c in df.columns], errors="ignore")
    df = df.merge(gold, on="uniprot_id", how="left")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    for _, row in df.iterrows():
        integ_path = POCKETS_DIR / row["uniprot_id"] / "integrated.json"
        if not integ_path.exists():
            continue
        write_target_report(row, json.loads(integ_path.read_text()))

    summary_path = write_summary(df)
    print(f"Wrote {len(df)} per-target reports to {OUTPUT}")
    print(f"Wrote summary to {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
