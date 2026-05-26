# Computing over 11M scientific publications with Paperclip

Literature mining in drug discovery remains an unsolved problem. Paperclip by GXL doesn't fully solve it, but it's a step in the right direction.

Under the hood: Paperclip uses Elasticsearch BM25 + vector similarity search over the free scientific publication corpus, with LLM capabilities layered on top. 

Docs here: https://lnkd.in/gtYT96wh

Installation of Paperclip was a single curl command. It also exposes MCP endpoints if you'd rather skip the local install.

I ran two use cases that come up in drug discovery:

Gathering cell types associated with a target (LRRK2, a Parkinson's target). This kind of literature query is bread-and-butter for target discovery teams.

Mapping phenotypic consequences of upregulating a target (YAP). This one's harder but is especially useful to toxicologists. The key challenge is that most evidence of perturbation is focused on knocking out a target or downregulating in some way. But often times, we seek to therapeutically intervene by upregulating a target. Toxicologists want to know what has been observed in humans when that happens.

Both use cases were easy to execute with Claude's help but one limitation I hit: it doesn't reliably execute multi-step pipelines in bash. There's an async-write race between map and the .gxl read that surfaces often enough to rule this out for embedded algorithmic workflows. Fine for interactive use, not for automation.

Paperclip allows you to return up to 1000 publications but for the purpose of trying it out, I limited my results to just 15 publications to compute over.

LRRK2 TSV output: https://lnkd.in/gUYThVsB

YAP TSV output: https://lnkd.in/gBRvwHbd

Source code: https://lnkd.in/gykMbu5C

Running the code should you choose to check it out:

```
make clean
make lrrk2
make yap
```

Loom demo: https://lnkd.in/gCZyYrPy

Shout out to Julia Gross for introducing me to Paperclip!

#drugdiscovery  #AIxBiology
