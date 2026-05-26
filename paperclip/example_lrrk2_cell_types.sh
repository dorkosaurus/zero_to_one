#!/bin/bash
set -e

OUT=./lrrk2
mkdir -p "$OUT"

# 0. Paperclip search
paperclip search "LRRK2 cell types" -n 15 -s papers > "$OUT/search.txt"

# 1. Search session from previous search output
SEARCH_SESSION=$(tail -n 1 "$OUT/search.txt" | grep -oE 's_[a-f0-9]+')
echo "Search session: $SEARCH_SESSION"

# 2. Run map → local truncated output to map.txt
paperclip map --from "$SEARCH_SESSION" --output_schema '{"cell_types_studied":[{"ontology_name":"string","ontology_id":"string","evidence_quote":"string"}]}' "For each DISTINCT cell type the paper studies, experimentally manipulates, or characterizes (not just mentions in passing): (1) ontology_name — the Cell Ontology (CL) preferred name; for immortalized cell lines use the Cell Line Ontology (CLO) name. (2) ontology_id — the corresponding CL:XXXXXXX or CLO:XXXXXXX identifier. If you do not know a precise CL/CLO ID, return null for ontology_id but still provide the closest ontology_name. (3) evidence_quote — verbatim ≤200 chars from the paper showing the cell type was used. Dedupe within the paper. Skip if paper isn't about LRRK2." > "$OUT/map.txt"

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

# 6. Flatten schema → TSV (one row per (paper_id, cell_type))
{
  printf 'paper_id\tontology_name\tontology_id\tevidence_quote\n'
  jq -r '.paper_id as $pid | .cell_types_studied[]? | [$pid, .ontology_name, .ontology_id, .evidence_quote] | @tsv' "$OUT/output.jsonl"
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
