*This project has been created as part of the 42 curriculum by jbarthel, oguizol.*

# A-Maze-ing

## Description
- **Goal:** Generate a valid maze from a config file, export it in the expected hexadecimal format, and provide a visual representation.
- **Project overview:**
  - Input: a config file (`KEY=VALUE`)
  - Processing: maze generation + validation + shortest path
  - Output: maze file + visual rendering (Textual TUI)
- **Scope (mandatory):**
  - Random generation with reproducibility via seed
  - `PERFECT=True` support (single path entry → exit)
  - Visible `42` pattern when maze size allows it

## Instructions

### Prerequisites
- Python >= 3.10
- Make
- **uv** (recommended) - Fast Python package manager
  ```bash
  # Install uv (if not already installed)
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # Restart your shell or run:
  source ~/.bashrc
  ```
- Textual (installed via project dependencies)

### Quick Start
```bash
# 1. Install uv (if needed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install dependencies (creates .venv automatically)
make install

# 3. Run the program
make run
```

> **Note:** `uv` automatically creates and manages the virtual environment.
> No need to manually activate it - `uv run` handles everything!

### Virtual environment (advanced)
```bash
# uv creates .venv automatically during install
make install

# Direct usage (without make)
uv sync --all-extras
uv run python a_maze_ing.py config.txt
```

### Install
```bash
make install
```

> **Note:** The current visual mode relies on Textual TUI and is installed
> with project dependencies.

### Build reusable package
```bash
make package
```

### Run
```bash
make run
# or with uv directly
uv run python a_maze_ing.py config.txt
# or if .venv is activated
python3 a_maze_ing.py config.txt
```

### Debug
```bash
make debug
```

### Lint / typing
```bash
make lint
# optional strict mode
make lint-strict
```

### Tests
```bash
# quick test run
make test

# verbose output
make test-verbose

# direct usage
uv run pytest -q
```

### Clean
```bash
# Remove cache files, build artifacts, dist folders, and packages
make clean

# Remove everything including .venv and uv.lock (fresh start)
make clean-all
```

## Usage

### Command
```bash
# Recommended (with uv)
uv run python a_maze_ing.py config.txt

# Or with make
make run

# Or if .venv is activated
python3 a_maze_ing.py config.txt
```

### Error handling expectations
- Invalid/missing config
- Syntax errors in config
- Impossible parameters (out-of-bounds entry/exit, etc.)
- Missing files / invalid permissions

## Configuration File Format
One `KEY=VALUE` per line. Lines starting with `#` are comments.

### Mandatory keys
| Key | Description | Example |
|---|---|---|
| `WIDTH` | Maze width (cells) | `WIDTH=20` |
| `HEIGHT` | Maze height (cells) | `HEIGHT=15` |
| `ENTRY` | Entry coordinates `(x,y)` | `ENTRY=0,0` |
| `EXIT` | Exit coordinates `(x,y)` | `EXIT=19,14` |
| `OUTPUT_FILE` | Output filename | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Perfect maze mode | `PERFECT=True` |

### Optional keys (team choices)
- `SEED=<int>`
- `ALGORITHM=<name>`
- `DISPLAY_MODE=<textual>`
- `WALL_COLOR=<name|hex>`

### Example config
```ini
# Default config example
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
```

## Output File Format
- One hexadecimal digit per cell
- Bit mapping:
  - bit 0: North
  - bit 1: East
  - bit 2: South
  - bit 3: West
- Rows written line by line
- Then one empty line
- Then 3 lines (all terminated by `\n`):
  1. entry coordinates (`x,y`)
  2. exit coordinates (`x,y`)
  3. shortest valid path (`N`, `E`, `S`, `W`)

### Output example
```text
9D9D1D
AC9C26
E368A6
...

0,0
19,14
EESSENNW...
```

## Maze Generation Algorithm
- **Chosen algorithm:** randomized Kruskal on cell-adjacency graph
- **Disjoint set structure:** Union-Find (path compression + union by size)
- **Seed/reproducibility strategy:** Python `random.seed(SEED)`
- **Perfect maze behavior:** exactly `W*H - 1` passages opened, no cycles,
  all cells connected (single unique path between two cells)
- **42 logo behavior:** logo placement is always enabled; when maze size is
  at least `7x5`, closed cells forming the `42` pattern are injected.

## Visual Representation
- **Mode implemented:** Textual TUI (`graphic_visualizer.py`)
- Must show:
  - walls
  - entry / exit
  - shortest path (highlighted)
  - optional dedicated color for the `42` pattern (`is_pattern`)
- **Controls:**
  - `q`: quit
  - `p`: toggle shortest path visibility
  - `c`: cycle Textual themes
  - `w`: cycle wall color
  - `f`: cycle `42` pattern color
  - `r`: regenerate maze

## Reusability (Mandatory)

### Reusable module
- **Class name:** `MazeGenerator`
- **Package name:** `mazegen-*`
- **Source module file:** `mazegen.py`
- **Built artifact(s):** `.whl` and/or `.tar.gz`
- **Location:** repository root

### Build the package
```bash
make package
```

Or manually with uv:
```bash
uv sync
uv run --with setuptools --with wheel python -m build --no-isolation
```

Generated files will be available in `dist/` with names like:
- `mazegen-0.2.0-py3-none-any.whl`
- `mazegen-0.2.0.tar.gz`

For final submission, copy at least one generated artifact to repository root
to match the project requirement.

### How to use (short doc)
```python
from mazegen import MazeGenerator

generator = MazeGenerator(width=20, height=15, seed=42, perfect=True)
generator.generate(entry=(0, 0), exit_=(19, 14))
maze = generator.get_structure()
path = generator.shortest_path()
```

### Exposed API checklist
- Instantiate with custom parameters (size, seed, perfect mode)
- Generate maze
- Access internal structure
- Access at least one solution path

## Team & Project Management

### Roles
- `jbarthel`: 
  - Maze generation algorithm: randomized Kruskal + Union-Find
  - Config parsing using `python-dotenv`
  - Shortest path algorithm: BFS (Lee algorithm)
  - Visual representation: Textual TUI
- `oguizol`: 
  - Validation and tooling support
  - Documentation and workflow support

### Initial planning

**Week 1 - Foundation (Days 1-7):**
- **Day 1-2:** Infrastructure & Setup
  - Git branches setup + workflow agreement
  - Virtual env + dependencies installation
  - Project structure validation
  - Documentation skeleton completion
  
- **Day 3-4:** Config & Data Structures
  - jbarthel: Config parser with python-dotenv
  - oguizol: Maze data structure + validation helpers
  - Both: Unit tests for parsing/validation
  
- **Day 5-7:** Core Generation Algorithms
  - jbarthel: Randomized Kruskal + Union-Find implementation
  - oguizol: Alternative generation strategy exploration
  - Both: "42" pattern integration + perfect maze mode

**Week 2 - Completion (Days 8-14):**
- **Day 8-9:** Pathfinding & Output
  - jbarthel: BFS/Lee shortest path implementation
  - oguizol: Hex output file writer + format validation
  - Both: Integration tests (generate → solve → write)
  
- **Day 10-11:** Visual Representation
  - jbarthel: Textual TUI display + interactions
  - oguizol: Textual TUI support and UX tests
  - Both: Color management + path toggle feature
  
- **Day 12-13:** Testing & Polish
  - Edge cases testing (invalid configs, impossible mazes)
  - Error handling verification (try-except, context managers)
  - Code quality: flake8 + mypy strict mode
  - Package build validation (make package)
  
- **Day 14:** Final Review
  - Cross-review code between team members
  - README completion (AI disclosure, retrospective)
  - Dry-run evaluation simulation
  - Submission preparation

### Evolution during project
- TODO: what changed and why.

### Retrospective
- **What worked well:** TODO
- **What could be improved:** TODO

### Tools used
- TODO (e.g., GitHub Projects, Issues, Discord, Excalidraw, etc.)

## Git Workflow (Binôme)

### Branch strategy
- Stable branch: `main` (no direct development on it)
- Personal long-lived branches:
  - `jbarthel`
  - `oguizol`
- Optional temporary sub-branches for risky changes:
  - `jbarthel/<feature-name>`
  - `oguizol/<feature-name>`

### Regular sync rule
Each member rebases regularly their personal branch on `main`:

```bash
git checkout <your-branch>
git fetch origin
git rebase origin/main
```

### Integration rule
- Open a Pull Request from personal branch to `main`
- Mandatory review by the other teammate before merge
- Merge only when checks are green (run, lint, typing, and project-specific validations)

### Safety rules
- No force push on `main`
- Force push allowed only on personal branches after rebase, using:

```bash
git push --force-with-lease
```

### Commit convention
- `feat: ...`
- `fix: ...`
- `refactor: ...`
- `test: ...`

## Project Structure
```text
.
├── .flake8                   # Flake8 configuration
├── a_maze_ing.py              # CLI entry point
├── config_model.py            # Pydantic config validation model
├── graphic_visualizer.py      # Textual TUI maze visualizer
├── graphic_visualizer/        # Visualizer resources/cache directory
├── mazegen.py                 # Reusable generator module
├── tools.py                   # Utility helpers
├── tests/                     # Pytest unit tests
├── pyproject.toml             # Project config & dependencies
├── uv.lock                    # Locked dependency versions
├── config.txt                 # Default config file
├── Makefile                   # Build automation
├── .gitignore                 # Git exclusions
├── README.md                  # This file
├── output_validator.py        # Provided validation script
├── en.subject.pdf             # Project subject
├── .venv/                     # Virtual environment (auto-created by uv)
└── .git/                      # Git repository metadata
```

## Resources

### Technical references
- Python docs: https://docs.python.org/3/
- `flake8`: https://flake8.pycqa.org/
- `mypy`: https://mypy.readthedocs.io/
- Graph/maze algorithms:
  - https://en.wikipedia.org/wiki/Maze_generation_algorithm
  - https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap

### AI usage disclosure (required)
- **Tools used:** GitHub Copilot (GPT-5.3-Codex)
- **Used for:** refactoring, docstring normalization, robustness checks,
  and README updates.
- **Not used for:** blind integration without manual review.
- **Validation process:** `flake8`, `mypy --strict`, runtime checks via
  CLI and TUI execution.

## Bonus (if implemented)
- Multiple generation algorithms
- Multiple Textual display modes/themes
- Additional interactions/options

## Current Project Status

**Implemented:**
- ✅ Config parsing/validation with Pydantic
- ✅ Maze generation with randomized Kruskal + Union-Find
- ✅ Shortest path with Lee/BFS
- ✅ Hex output file generation from CLI
- ✅ Textual visualizer with entry/exit/pattern/path highlighting
- ✅ Packaging (`make package`) for reusable `mazegen` module
- ✅ Linting/typing workflow (`make lint`, `make lint-strict`)

**Open items:**
- ⬜ Expand automated test coverage
- ⬜ Final evaluator-oriented polishing/documentation

## Submission Notes
- Ensure `README.md` is complete and up to date
- Ensure default config file is present in repository ✅
- Ensure package build inputs are present (`mazegen-*` buildable) ✅
- Ensure mandatory checks pass before evaluation (`make lint`, `make run`)
