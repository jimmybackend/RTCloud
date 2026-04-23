PYTHON ?= python

.PHONY: install dev test lint demo clean

install:
	$(PYTHON) -m pip install -e .

dev:
	$(PYTHON) -m pip install -e .[dev]

test:
	pytest -q

demo:
	$(PYTHON) examples/ingest_file.py
	$(PYTHON) examples/verify_repo.py
	$(PYTHON) examples/partial_restore.py

clean:
	rm -rf .pytest_cache .venv demo_repo tmp_restore.bin
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
