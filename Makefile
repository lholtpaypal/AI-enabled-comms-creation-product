.PHONY: install run test lint format check

PYTHON ?= .venv/bin/python

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[dev]"

run:
	PYTHONPATH=src $(PYTHON) -m oslo_comms_studio

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

format:
	$(PYTHON) -m ruff format .

check:
	$(PYTHON) -m pytest
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .
