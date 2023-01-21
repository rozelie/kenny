SHELL := /usr/bin/env bash
VENV_BIN := venv/bin
PYTHON := $(VENV_BIN)/python
PIP := $(PYTHON) -m pip
PYTHONPATH := `pwd`
PYTHON_DIRS := kenny tests

.PHONY: install
install:
	python3 -m venv venv
	$(PIP) install -e .[dev]

.PHONY: format
format:
	$(VENV_BIN)/ruff --config pyproject.toml --fix $(PYTHON_DIRS)
	$(VENV_BIN)/black --config pyproject.toml $(PYTHON_DIRS)

.PHONY: verify
verify:
	$(VENV_BIN)/black --diff --check --config pyproject.toml $(PYTHON_DIRS)
	$(VENV_BIN)/ruff --config pyproject.toml $(PYTHON_DIRS)
	$(VENV_BIN)/mypy --config-file pyproject.toml $(PYTHON_DIRS)

.PHONY: test
test:
	PYTHONPATH=$(PYTHONPATH) $(VENV_BIN)/pytest -c pyproject.toml --cov-report=html --cov=kenny tests/
	$(VENV_BIN)/coverage-badge -o assets/images/coverage.svg -f

.PHONY: clean
clean:
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf
	find . | grep -E ".DS_Store" | xargs rm -rf
	rm -rf build/
