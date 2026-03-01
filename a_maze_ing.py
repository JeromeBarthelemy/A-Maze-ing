"""A-Maze-ing command-line entry point.

This script remains intentionally minimal at this stage:
- it is the required executable entry (`python3 a_maze_ing.py config.txt`)
- reusable generation logic lives in `mazegen.py` (Chapter VI)
"""

from __future__ import annotations

import sys
from pathlib import Path
import os
from dotenv import load_dotenv

from mazegen import MazeGenerator


def parse_config(config_path: Path
                 ) -> dict[str, int | tuple[int, int] | str | bool]:
    """Parse config file (`KEY=VALUE`) into a dictionary.

    Args:
        config_path: Path to the config file.

    Returns:
        Dictionary with parsed config values (WIDTH, HEIGHT, ENTRY, EXIT,
        OUTPUT_FILE, PERFECT, SEED).

    Raises:
        FileNotFoundError: If config file does not exist.
        ValueError: If config format or values are invalid.
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    load_dotenv(dotenv_path=config_path)
    result: dict[str, int | tuple[int, int] | str | bool] = {}

    try:
        # Parse WIDTH
        width_str = os.getenv("WIDTH")
        if width_str is None:
            raise ValueError("Missing required key: WIDTH")
        width = int(width_str)
        if width <= 0:
            raise ValueError("WIDTH must be positive")
        result["WIDTH"] = width

        # Parse HEIGHT
        height_str = os.getenv("HEIGHT")
        if height_str is None:
            raise ValueError("Missing required key: HEIGHT")
        height = int(height_str)
        if height <= 0:
            raise ValueError("HEIGHT must be positive")
        result["HEIGHT"] = height

        # Parse ENTRY
        entry_str = os.getenv("ENTRY")
        if entry_str is None:
            raise ValueError("Missing required key: ENTRY")
        entry_coords = tuple(int(x.strip()) for x in entry_str.split(","))
        if len(entry_coords) != 2:
            raise ValueError("ENTRY must be comma-separated integers (x,y)")
        result["ENTRY"] = entry_coords

        # Parse EXIT
        exit_str = os.getenv("EXIT")
        if exit_str is None:
            raise ValueError("Missing required key: EXIT")
        exit_coords = tuple(int(x.strip()) for x in exit_str.split(","))
        if len(exit_coords) != 2:
            raise ValueError("EXIT must be comma-separated integers (x,y)")
        result["EXIT"] = exit_coords

        # Parse OUTPUT_FILE
        output_file = os.getenv("OUTPUT_FILE")
        if output_file is None:
            raise ValueError("Missing required key: OUTPUT_FILE")
        result["OUTPUT_FILE"] = output_file

        # Parse PERFECT
        perfect_str = os.getenv("PERFECT")
        if perfect_str is None:
            raise ValueError("Missing required key: PERFECT")
        result["PERFECT"] = perfect_str.lower() == "true"

        # Parse optional SEED
        seed_str = os.getenv("SEED", "42")
        result["SEED"] = int(seed_str)

    except (ValueError, TypeError, AttributeError) as e:
        raise ValueError(f"Invalid config file format: {e}") from e

    return result


def main() -> int:
    """CLI entry point for `python3 a_maze_ing.py config.txt`.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return 1

    config_path = Path(sys.argv[1])

    try:
        config = parse_config(config_path)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    try:
        _ = MazeGenerator(
            width=config["WIDTH"],  # type: ignore
            height=config["HEIGHT"],  # type: ignore
            seed=config["SEED"],  # type: ignore
            perfect=config["PERFECT"],  # type: ignore
        )
        print(f"Maze initialized: {config['WIDTH']}x{config['HEIGHT']}")
        print("Maze generation not yet implemented.")
        return 0
    except ValueError as e:
        print(f"Error initializing maze generator: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
