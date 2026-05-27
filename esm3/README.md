# Scaling druggability assessments with ESM3

Having a target list is not enough - we need to know if targets are actually druggable. But the more data we have, the bigger our target lists get, and this can make druggability assessments a daunting task.

So I was interested in exploring whether we could use ESM3 to scale our ability to perform such assessments.  To limit scope for this zero-to-one project, I'm just focused on small molecule druggability.  Specifically, can I identify targets where ESM3-annotated functional residues sit in detected binding pockets, and does the resulting ranking recover known druggable targets?

Here's what I did:

First, I created a validation set comprised of a) known positives small molecules from ChEMBL b) known negatives (e.g. hard targetse like MYC and p53) c) and a set-aside validation comprised of randomly mixed positives and negatives.  

Next, I ran ESM3 open weights model (esm3-large-2024-03) on the set-aside validation set.  This generated:

* Predicted structure with per-residue confidence
* Annotated functional residues (catalytic, binding-site)
* Sequence and structure embeddings

I then ran fpocket and P2Rank on every predicted structure which generated the following per pocket:

* Pocket ID, lining residues, volume, druggability score
* Hydrophobic/polar character
* Burial depth

I then checked whether an functional residues were found in pocket lining residues.  This produced:

* Number of pockets containing ≥1 functional residue
* Best druggability score among function-overlapping pockets
* Fraction of functional residues that are pocket-accessible
* Best pocket's volume, hydrophobicity, and lining identity

I then created a score per protein that took into account pocket-level druggability (50%), functional residue overlap (30%), surface accessibility (20%).  

Finally, I compared against the positive and negative validation set.  




