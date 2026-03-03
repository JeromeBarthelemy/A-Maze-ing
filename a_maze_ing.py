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
from pydantic import ValidationError

from mazegen import MazeGenerator
from config_model import MazeConfig


def parse_config(config_path: Path) -> dict[str, int | str | bool]:
    """Parse config file (`KEY=VALUE`) into a dictionary.

    Args:
        config_path: Path to the config file.

    Returns:
        Dictionary with parsed config values.

    Raises:
        FileNotFoundError: If config file does not exist.
        ValueError: If config format or values are invalid.
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    load_dotenv(dotenv_path=config_path)

    try:
        config_data: dict[str, str | None] = {
            key: os.getenv(key) for key in MazeConfig.model_fields
        }
        config = MazeConfig(**config_data)  # type: ignore
        return config.model_dump()
    except ValidationError as e:
        raise ValueError(f"Invalid config file format: {e}") from e


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
            width=int(config["WIDTH"]),
            height=int(config["HEIGHT"]),
            seed=int(config["SEED"]),
            perfect=bool(config["PERFECT"]),
        )
        print(f"Maze initialized: {config['WIDTH']}x{config['HEIGHT']}")
        print("Maze generation not yet implemented.")
        return 0
    except ValueError as e:
        print(f"Error initializing maze generator: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
