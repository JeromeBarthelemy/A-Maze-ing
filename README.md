*This project has been created as part of the 42 curriculum by jbarthel, oguizol.*

# A-Maze-ing

## Description
- **Goal:** Generate a valid maze from a config file, export it in the expected hexadecimal format, and provide a visual representation.
- **Project overview:**
  - Input: a config file (`KEY=VALUE`)
  - Processing: maze generation + validation + shortest path
  - Output: maze file + visual rendering (terminal or MLX)
- **Scope (mandatory):**
  - Random generation with reproducibility via seed
  - `PERFECT=True` support (single path entry → exit)
  - Visible `42` pattern when maze size allows it

## Instructions

### Prerequisites
- Python >= 3.10
- Make
- Virtual environment (`virtualenv`) recommended
- MLX (optional, for graphical rendering only - see [INSTALL_MLX.md](INSTALL_MLX.md))

### Virtual environment (recommended)
```bash
python3 -m virtualenv .venv
source .venv/bin/activate
make install
# leave the virtual environment
deactivate
```

### Install
```bash
make install
```

> **Note:** MLX (graphical rendering) is optional and documented separately in [INSTALL_MLX.md](INSTALL_MLX.md).
> The wheels provided may be incompatible with Python 3.12+. Install it manually when needed for visual development.

### Build reusable package
```bash
make package
```

### Run
```bash
make run
# or
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

### Clean
```bash
make clean
```

## Usage

### Command
```bash
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
- `DISPLAY_MODE=<ascii|mlx>`
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
- Then an empty line, then 3 lines:
  1. entry coordinates
  2. exit coordinates
  3. shortest valid path (`N`, `E`, `S`, `W`)

### Output example
> TODO: Add a real output example produced by the project.

## Maze Generation Algorithm
- **Chosen algorithm:** TODO (e.g., recursive backtracker / Prim / Kruskal)
- **Why this algorithm:** TODO (complexity, quality of mazes, implementation simplicity)
- **Seed/reproducibility strategy:** TODO
- **Perfect maze behavior:** TODO

## Visual Representation
- **Mode implemented:** TODO (`ASCII`, `MLX`, or both)
- Must show:
  - walls
  - entry / exit
  - shortest path (toggle)
  - wall colors (change interaction)
  - optional dedicated colors for the `42` pattern
- **Controls:** TODO (keys/buttons and behavior)

## Reusability (Mandatory)

### Reusable module
- **Class name:** `MazeGenerator`
- **Package name:** `mazegen-*`
- **Source module file:** `mazegen.py`
- **Built artifact(s):** `.whl` and/or `.tar.gz`
- **Location:** repository root

### Build the package
```bash
python3 -m pip install build
python3 -m build
```

Or use:

```bash
make package
```

Generated files will be available in `dist/` with names like:
- `mazegen-0.1.0-py3-none-any.whl`
- `mazegen-0.1.0.tar.gz`

For final submission, copy at least one generated artifact to repository root
to match the project requirement.

### How to use (short doc)
```python
from mazegen import MazeGenerator

generator = MazeGenerator(width=20, height=15, seed=42, perfect=True)
maze = generator.generate(entry=(0, 0), exit=(19, 14))
path = generator.shortest_path()
```

### Exposed API checklist
- Instantiate with custom parameters (size, seed, mode)
- Generate maze
- Access internal structure
- Access at least one solution path

## Team & Project Management

### Roles
- `jbarthel`: 
  - Maze generation algorithm: random path fusion
  - Config parsing using `python-dotenv`
  - Shortest path algorithm: BFS (Lee algorithm)
  - Visual representation: MiniLibX (graphical)
- `oguizol`: 
  - Maze generation algorithm: exhaustive exploration
  - Visual representation: ASCII terminal rendering

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
  - jbarthel: Random path fusion algorithm implementation
  - oguizol: Exhaustive exploration algorithm implementation
  - Both: "42" pattern integration + perfect maze mode

**Week 2 - Completion (Days 8-14):**
- **Day 8-9:** Pathfinding & Output
  - jbarthel: BFS/Lee shortest path implementation
  - oguizol: Hex output file writer + format validation
  - Both: Integration tests (generate → solve → write)
  
- **Day 10-11:** Visual Representation
  - jbarthel: MiniLibX graphical display + interactions
  - oguizol: ASCII terminal rendering + interactions
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
├── a_maze_ing.py              # CLI entry point
├── mazegen.py                 # Reusable generator module
├── pyproject.toml             # Package build configuration
├── config.txt                 # Default config file
├── requirements.txt           # Python dependencies
├── Makefile                   # Build automation
├── .gitignore                 # Git exclusions
├── README.md                  # This file
├── INSTALL_MLX.md             # MLX installation guide (optional)
├── output_validator.py        # Provided validation script
├── en.subject.pdf             # Project subject
├── mlx-2.2-py3-ubuntu-any.whl # MLX library (Ubuntu)
├── mlx-2.2-py3-fedora-any.whl # MLX library (Fedora)
├── mlx_CLXV-2.2.tgz           # MLX source archive
└── dist/                      # Generated package artifacts (after make package)
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
- **Tools used:** TODO (e.g., ChatGPT, Copilot)
- **Used for:** TODO (brainstorming, test ideas, README drafting, refactor suggestions)
- **Not used for:** TODO (critical algorithm implementation without understanding)
- **Validation process:** TODO (peer review, tests, manual checks)

## Bonus (if implemented)
- Multiple generation algorithms
- Multiple display modes
- Additional interactions/options

## Current Project Status

**Setup phase completed:**
- ✅ Git workflow defined (branches, PR rules)
- ✅ Python environment structure (virtualenv, requirements.txt)
- ✅ Makefile automation (install, run, debug, lint, package, clean)
- ✅ Module skeleton (mazegen.py + a_maze_ing.py)
- ✅ Package build infrastructure (pyproject.toml)
- ✅ Default config file (config.txt)
- ✅ Documentation (README.md)

**Next implementation steps:**
- ⬜ Config parser (parse_config function)
- ⬜ Maze generation algorithm
- ⬜ Output file writer (hex format)
- ⬜ Shortest path computation (BFS/Lee algorithm)
- ⬜ Visual representation (ASCII/MLX)
- ⬜ "42" pattern integration
- ⬜ Tests and validation

## Submission Notes
- Ensure `README.md` is complete and up to date
- Ensure default config file is present in repository ✅
- Ensure package build inputs are present (`mazegen-*` buildable) ✅
- Ensure mandatory checks pass before evaluation (`make lint`, `make run`)
