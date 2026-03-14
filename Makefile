SHELL := /bin/bash
export PATH := $(HOME)/.local/bin:$(PATH)

MAIN ?= a_maze_ing.py
CONFIG ?= config.txt
OUTPUT_FILE_FROM_CONFIG := $(shell awk -F= '/^[[:space:]]*OUTPUT_FILE[[:space:]]*=/{gsub(/[[:space:]]/,"",$$2); print $$2; exit}' $(CONFIG) 2>/dev/null)

# Check if uv is installed
UV := $(shell command -v uv 2>/dev/null)

.PHONY: install run debug test test-verbose clean clean-all lint lint-strict package check-uv

check-uv:
ifndef UV
	@echo "Error: uv is not installed or not in PATH."
	@echo "Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
	@echo "Then restart your shell or run: source ~/.bashrc"
	@exit 1
endif

install: check-uv
	uv sync --all-extras

run: check-uv
	uv run python $(MAIN) $(CONFIG)

debug: check-uv
	uv run python -m pdb $(MAIN) $(CONFIG)

test: check-uv
	uv run --extra dev python -m pytest -q

test-verbose: check-uv
	uv run --extra dev python -m pytest -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete
	rm -rf .mypy_cache .pytest_cache
	rm -rf dist build *.egg-info
	rm -f mazegen-*.whl mazegen-*.tar.gz
	rm -f $(OUTPUT_FILE_FROM_CONFIG)

# Clean everything including virtual environment
clean-all: clean
	rm -rf .venv uv.lock

lint: check-uv
	uv run flake8 . 
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict: check-uv
	uv run flake8 .
	uv run mypy . --strict

package: check-uv
	uv sync --all-extras
	uv run --with setuptools --with wheel python -m build --no-isolation
	cp -f dist/mazegen-*.whl . || true
	cp -f dist/mazegen-*.tar.gz . || true
