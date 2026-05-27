.PHONY: help install fetch-sequences run-esm3 run-pockets clean

VENV := $(HOME)/venv
PYTHON := $(VENV)/bin/python

help:
	@echo "Targets:"
	@echo "  install           install fpocket, P2Rank, Java, and Python deps into ~/venv"
	@echo "  fetch-sequences   download canonical FASTA for proteins in validate.tsv"
	@echo "  run-esm3          fold + function-annotate each sequence via Forge API"
	@echo "  run-pockets       run fpocket + P2Rank on each predicted structure"
	@echo "  clean             remove generated data/ and __pycache__"

install:
	bash install.sh

fetch-sequences:
	$(PYTHON) -m druggability.fetch_sequences

run-esm3:
	$(PYTHON) -m druggability.run_esm3

run-pockets:
	$(PYTHON) -m druggability.run_pockets

clean:
	rm -rf data/ __pycache__ .pytest_cache *.egg-info
