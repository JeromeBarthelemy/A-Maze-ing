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

# from tools import print_grid
from graphic_visualizer import MazeApp


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


def save_output_file(
    output_file: str,
    hex_grid: list[list[str]],
    entry: tuple[int, int],
    exit_: tuple[int, int],
    shortest_path: str,
) -> None:
    """Write maze output file in subject format.

    Args:
        output_file: Output file path.
        hex_grid: Maze grid encoded as hexadecimal characters.
        entry: Entry coordinates as ``(x, y)``.
        exit_: Exit coordinates as ``(x, y)``.
        shortest_path: Shortest path encoded with ``N/E/S/W``.
    """
    with open(output_file, "w") as output_stream:
        for row in hex_grid:
            output_stream.write("".join(row) + "\n")
        output_stream.write("\n")
        output_stream.write(f"{entry[0]},{entry[1]}\n")
        output_stream.write(f"{exit_[0]},{exit_[1]}\n")
        output_stream.write(f"{shortest_path}\n")


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
        maze_generator = MazeGenerator(
            width=int(config["WIDTH"]),
            height=int(config["HEIGHT"]),
            seed=int(config["SEED"]),
            perfect=bool(config["PERFECT"]),
        )
        print(f"Maze ready: {config['WIDTH']}x{config['HEIGHT']}")
        entry: tuple[int, int] = config["ENTRY"]  # type: ignore
        exit_: tuple[int, int] = config["EXIT"]  # type: ignore
        maze_generator.generate(entry=entry, exit_=exit_)
        shortest_path = maze_generator.shortest_path()
        print("Maze generation complete.")
        hex_grid = maze_generator.get_hex_grid()
        try:
            save_output_file(
                output_file=str(config["OUTPUT_FILE"]),
                hex_grid=hex_grid,
                entry=entry,
                exit_=exit_,
                shortest_path=shortest_path,
            )
        except OSError as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            return 1
        print(f"Maze saved to {config['OUTPUT_FILE']}")
        # binary_grid = maze_generator.get_binary_grid()
        # maze = maze_generator.get_structure()
        print("Maze:")
        # print_grid(hex_grid)
        # print_grid(binary_grid)
        print(shortest_path)
        MazeApp(maze_generator).run()

        return 0
    except ValueError as e:
        print(f"Error initializing maze generator: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
