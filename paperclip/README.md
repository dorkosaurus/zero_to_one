# Computing over 11M scientific publications with Paperclip

Literature mining in drug discovery remains an unsolved problem. Paperclip by @GXL doesn't solve it, but it's a step in the right direction.   

Under the hood: Paperclip uses Elasticsearch BM25 + vector similarity search over the free scientific publication corpus, with LLM capabilities layered on top. Docs here: https://paperclip.gxl.ai/docs

Installation of Paperclip was a single curl command.  It also exposes MCP endpoints if you'd rather skip the local install.

I ran two use cases that come up in drug discovery:

Gathering cell types associated with LRRK2 (a Parkinson's target). This kind of structured extraction from literature is bread-and-butter for target discovery teams and it just seemed to work.

Mapping phenotypic consequences of upregulating YAP. This one's harder but is especially useful to toxicologists.  The key challenge is that most evidence of perturbation is focused on knocking out a target or downregulating in some way.  But often times, we seek to therapeutically intervene by upregulating a target.  Toxicologists want to know what has been observed in humans when that happens.

Both use cases were easy to execute with Claude's help but one limitation I hit: it doesn't reliably execute multi-step pipelines in bash. There's an async-write race between map and the .gxl read that surfaces often enough to rule this out for embedded algorithmic workflows. Fine for interactive use, not for automation.


LRRK2 TSV output: https://github.com/dorkosaurus/zero_to_one/blob/main/paperclip/lrrk2/output_full.tsv

YAP TSV output: https://github.com/dorkosaurus/zero_to_one/blob/main/paperclip/yap/output_full.tsv

Source code: https://github.com/dorkosaurus/zero_to_one/tree/main/paperclip

Running the code should you choose to check it out:

```
make lrrk2
make yap
make clean
```

Loom demo: https://www.loom.com/share/fb444dd55c4f4398a757e928dc35ca88

Shout out to @Julia Gross for introducing me to Paperclip!
