# Computing over 11M scientific publications with PaperClip

We still haven't cracked mining publication data within Drug Discovery but I think Paperclip by @GXL is a step in the right direction.  I don't think this is a production-grade tool but do think it's amazing for ad-hoc manually-run workflows for computationally savvy personnel.

In a nutshell, it's a toolkit that provides traditional search-engine like search (Elasticsearch BM25 + vector similarity) with LLM capabilities to allow you to compute over the free corpus of scientific publications.  https://paperclip.gxl.ai/docs

The sweet spot for drug discovery given my experience:  extracting structured content after searching the corpus of publicly available scientific publications for sets of key words.

It was pleasantly easy to install:

```
curl -fsSL https://paperclip.gxl.ai/install.sh | bash
```

If you don't want to install it locally it also exposes MCP end points you can connect to as well.

I focused on 2 use cases:

* Gathering cell types about a target (commonly needed for discovery biology and target discvory).  In this case, I used LRRK2 (linked to Parkinson's Disease).  
* Understanding the phenotypic consequences of upregulating a target (I used YAP) - this has broad applications but is especially useful to toxicologists.  The key challenge is that most evidence of perturbation is focused on knocking out a target or downregulating in some way.  But often times, we seek to therapeutically intervene by upregulating a target. Toxicologists need to mine the literature to achieve this and so I sought to find out if Paperclip could make a dent here.

I found both use cases remarkably easy to execute (with Claude's help). Paperclip can return up to 1000 results via search but for the purpose of my testing, I kept it to 15.  

The key hiccup:  it doesn't reliably work across steps when executed in bash.  There seems to be some kind of race condition between the `map` and `grep` step that creeps up often enough to not make me want to embed this in an algorithmic workflow.  

Example outputs:

* LRK22 cell types:
* Phenotypic consequences of upregulating YAP:  

Source code here:  https://github.com/dorkosaurus/zero_to_one/tree/main/paperclip

Run the code with make:

* make lrrk2
* make yap
* make clean

Loom video here demoing usage: 
