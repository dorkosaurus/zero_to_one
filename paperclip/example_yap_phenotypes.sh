#!/bin/bash
set -e

OUT=./yap
mkdir -p "$OUT"

# 0. Paperclip search — YAP/TAZ gain of function across species
paperclip search "YAP TAZ WWTR1 gain of function phenotype" -n 15 -s papers > "$OUT/search.txt"

# 1. Search session from previous search output
SEARCH_SESSION=$(tail -n 1 "$OUT/search.txt" | grep -oE 's_[a-f0-9]+')
echo "Search session: $SEARCH_SESSION"

# 2. Run map → local truncated output to map.txt
paperclip map --from "$SEARCH_SESSION" --output_schema '{"findings":[{"species":"string","yap_alteration":"string","alteration_category":"string","tissue_or_organ":"string","phenotype":"string","evidence_quote":"string"}]}' "For each DISTINCT YAP or TAZ (WWTR1) gain-of-function finding reported in the paper, extract one row with: (1) species — the organism studied (e.g., human, mouse, zebrafish, Drosophila, rat, Xenopus, or organoid system). (2) yap_alteration — the specific genetic or experimental alteration (e.g., YAP-S127A, YAP-5SA, YAP1 amplification, YAP overexpression, LATS1/2 KO, MST1/2 KO, TAZ-S89A, TAZ overexpression). (3) alteration_category — must be one of: 'activating_mutation', 'overexpression', 'upstream_pathway_loss', or 'amplification'. (4) tissue_or_organ — the tissue, organ, or cell context (e.g., liver, intestinal crypt, cardiomyocyte, mammary epithelium, hepatocellular carcinoma). (5) phenotype — the observed phenotypic consequence (e.g., hepatomegaly, tumor formation, organ overgrowth, increased proliferation, dedifferentiation, regeneration). (6) evidence_quote — a verbatim ≤200 chars quote from the paper showing the finding. Dedupe within the paper. Skip if paper isn't about YAP or TAZ gain of function." > "$OUT/map.txt"

# 3. Map session ID from map.txt
MAP_SESSION=$(grep -oE 'm_[a-f0-9]+' "$OUT/map.txt" | tail -n 1)
echo "Map session: $MAP_SESSION"

# 4. Fetch full (un-truncated) results from paperclip's virtual fs → output.txt
#    /.gxl/ writes are async — retry briefly until the file is readable.
for i in 1 2 3 4 5; do
  paperclip grep "" "/.gxl/map_${MAP_SESSION}.txt" > "$OUT/output.txt" 2>/dev/null
  grep -qE '^[[:space:]]*\{' "$OUT/output.txt" && break
  sleep 1
done

# 5. Extract JSON blobs and inject paperclip's authoritative paper_id from doc_id metadata
#    - sed strips markdown ```json fences
#    - awk pairs the doc_id (above each JSON) with the JSON line and injects it
sed -E 's/^\s*```json\s*//; s/```\s*$//' "$OUT/output.txt" \
  | awk '/^[[:space:]]*doc_id:/{id=$2; next} /^[[:space:]]*\{/{sub(/\{/, "{\"paper_id\":\""id"\","); print}' \
  > "$OUT/output.jsonl"

# 6. Flatten schema → TSV (one row per (paper_id, finding))
{
  printf 'paper_id\tspecies\tyap_alteration\talteration_category\ttissue_or_organ\tphenotype\tevidence_quote\n'
  jq -r '.paper_id as $pid | .findings[]? | [$pid, .species, .yap_alteration, .alteration_category, .tissue_or_organ, .phenotype, .evidence_quote] | @tsv' "$OUT/output.jsonl"
} > "$OUT/output.tsv"

# 7. Look up publication metadata for each unique paper_id
#    paperclip cat appends a `[NNms]` timing footer on stdout; `jq -n 'first(inputs)'`
#    consumes only the first JSON value and ignores any trailing noise.
jq -r '.paper_id' "$OUT/output.jsonl" | sort -u > "$OUT/paper_ids.txt"
: > "$OUT/papers.jsonl"
while IFS= read -r pid; do
  [ -z "$pid" ] || [ "$pid" = "null" ] && continue
  paperclip cat "/papers/$pid/meta.json" 2>/dev/null \
    | jq -c -n 'first(inputs) | {paper_id: "'"$pid"'", title, authors, doi, journal_or_source: (.journal // .source // ""), pub_year: (.pub_year // ""), pub_date}' \
    >> "$OUT/papers.jsonl" || echo "warning: meta.json lookup failed for $pid" >&2
done < "$OUT/paper_ids.txt"

# 8. Publications table (TSV) — lookup by paper_id
{
  printf 'paper_id\ttitle\tauthors\tjournal_or_source\tpub_year\tpub_date\tdoi\n'
  jq -r '[.paper_id, .title, .authors, .journal_or_source, (.pub_year|tostring), .pub_date, .doi] | @tsv' "$OUT/papers.jsonl"
} > "$OUT/papers.tsv"

# 9. Denormalized table: findings × publication metadata (joined on paper_id)
awk -F'\t' 'NR==FNR{if(FNR>1){t[$1]=$2"\t"$3"\t"$4"\t"$5"\t"$7}; next} \
            FNR==1{print $0"\ttitle\tauthors\tjournal_or_source\tpub_year\tdoi"; next} \
            {print $0"\t"(($1 in t)?t[$1]:"\t\t\t\t")}' \
  "$OUT/papers.tsv" "$OUT/output.tsv" > "$OUT/output_full.tsv"
