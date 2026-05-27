.PHONY: help install fetch-sequences run-esm3 run-pockets integrate score report all clean

VENV := $(HOME)/venv
PYTHON := $(VENV)/bin/python

help:
	@echo "Targets:"
	@echo "  install           install fpocket, P2Rank, Java, and Python deps into ~/venv"
	@echo "  fetch-sequences   download canonical FASTA for proteins in validate.tsv"
	@echo "  run-esm3          fold + function-annotate each sequence via Forge API"
	@echo "  run-pockets       run fpocket on each predicted structure"
	@echo "  integrate         join pocket geometry with pLDDT + function annotations"
	@echo "  score             compute D/F/S/score per protein -> data/scores.tsv"
	@echo "  report            generate per-target reports + summary -> data/reports/, data/report.md"
	@echo "  all               run integrate -> score -> report"
	@echo "  clean             remove generated data/ and __pycache__"

install:
	bash install.sh

fetch-sequences:
	$(PYTHON) -m druggability.fetch_sequences

run-esm3:
	$(PYTHON) -m druggability.run_esm3

run-pockets:
	$(PYTHON) -m druggability.run_pockets

integrate:
	$(PYTHON) -m druggability.integrate

score:
	$(PYTHON) -m druggability.score

report:
	$(PYTHON) -m druggability.report

all: integrate score report

clean:
	rm -rf data/ __pycache__ .pytest_cache *.egg-info
