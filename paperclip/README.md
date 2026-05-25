# Paperclip 

URL: https://gxl.ai/blog/paperclip#conclusion

# Overview

*Today we're releasing Paperclip, the agent-native counterpart to Sy. Whereas humans use a chat-based UI, agents work best within the rich text environment of a command-line interface. Paperclip gives your agent direct CLI access to 8M+ papers—standard search and retrieval functions, plus several powerful tools that, when used together, let agents actually explore, deep-dive, and synthesize.*

# Operations

## Search

*As a starting point, we've implemented hybrid search, combining BM25 and embedding-based retrieval. The agent can also select a specific ranking mechanism more suited for its queries. For token efficiency, rather than return the entire abstract of each search result, we return a 1–2 sentence TL;DR summary.*

BM25:  https://en.wikipedia.org/wiki/Okapi_BM25

*BM25 is a bag-of-words retrieval function that ranks a set of documents based on the query terms appearing in each document, regardless of their proximity within the document.*


```
paperclip search "KRAS G12C resistance mechanisms" -n 5

Found 5 papers  [s_74db6679]

1. M1C is a druggable target for NSCLC KRAS G12C mutant tumors resistant to KRAS inhibitors
     bio_5c6e4b117ab6 · bioRxiv · 2025-12-02
     “M1C protein expression drives resistance to sotorasib by promoting EMT, and targeting M1C reverses it.”

2. Modeling response to AZD4625 in KRAS G12C NSCLC patient-derived xenografts
     PMC12765001 · British Journal of Cancer · 2025-10-11
     “mTOR signaling was identified as a potential mechanism of primary resistance to the drug.”

3. Genetic mechanisms of resistance to targeted KRAS inhibition
     bio_d7a242096fc0 · bioRxiv · 2025-08-04
     “CRISPR screens identified resistance mutations, with CIC mutations being a notable example.”

4. Combining EGFR and KRAS G12C Inhibitors for Advanced Colorectal Cancer
     PMC11340593 · J Cancer Immunol · 2024-08-07
     “EGFR + KRAS G12C inhibitor combinations show improved efficacy vs monotherapy.”

5. Inhibition of ULK1/2 and KRAS G12C controls tumor growth in lung cancer
     bio_f7c3187b7275 · bioRxiv · 2024-02-06
     “Combining KRAS G12C and ULK1/2 inhibition synergistically reduces tumor growth.”

```

## Grep

## Map

## Ask-image

## sql

## from


