PYTHON ?= python3
PIP ?= $(PYTHON) -m pip

MAIN ?= a_maze_ing.py
CONFIG ?= config.txt

.PHONY: install run debug clean lint lint-strict package

install:
	@if [ -f requirements.txt ]; then \
		$(PIP) install -r requirements.txt; \
	fi
	$(PIP) install flake8 mypy

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete
	rm -rf .mypy_cache .pytest_cache

lint:
	flake8 . --exclude .venv
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		. .venv/bin/activate && mypy . --exclude .venv --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs; \
	else \
		mypy . --exclude .venv --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs; \
	fi

lint-strict:
	flake8 . --exclude .venv
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		. .venv/bin/activate && mypy . --strict; \
	else \
		mypy . --strict; \
	fi

package:
	@if [ ! -d .venv ]; then \
		$(PYTHON) -m venv .venv; \
	fi
	@. .venv/bin/activate && \
		python -m pip install --upgrade pip build && \
		python -m build
	cp -f dist/mazegen-*.whl . || true
	cp -f dist/mazegen-*.tar.gz . || true
