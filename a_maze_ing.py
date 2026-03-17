"""A-Maze-ing command-line entry point.

This script remains intentionally minimal at this stage:
- it is the required executable entry (`python3 a_maze_ing.py config.txt`)
- reusable generation logic lives in `mazegen.py` (Chapter VI)
"""

from __future__ import annotations

import sys
from pathlib import Path
import os
from typing import TypedDict


def _missing_dependency_message(error: ImportError) -> str:
    """Build a clear user-facing message for missing Python dependencies.

    Args:
        error: Import error raised while loading project dependencies.

    Returns:
        Human-readable instruction to install dependencies.
    """
    return (
        f"Missing dependency: {error}. " "Run `make install`, then `make run`."
    )


class ParsedConfig(TypedDict):
    """Typed structure for validated maze configuration values."""

    WIDTH: int
    HEIGHT: int
    ENTRY: tuple[int, int]
    EXIT: tuple[int, int]
    OUTPUT_FILE: str
    PERFECT: bool
    ENABLE_TUI: bool
    SEED: int
    RATIO: float
    GENERATION_ALGO: str
    ASCII_VISUALIZER: bool


def parse_config(config_path: Path) -> ParsedConfig:
    """Parse config file (`KEY=VALUE`) into a dictionary.

    Args:
        config_path: Path to the config file.

    Returns:
        Dictionary with parsed config values.

    Raises:
        FileNotFoundError: If config file does not exist.
        ValueError: If config format or values are invalid.
    """
    try:
        from dotenv import load_dotenv
        from pydantic import ValidationError
        from config_model import MazeConfig
    except ImportError as e:
        raise ValueError(_missing_dependency_message(e)) from e

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    # Ensure config file values override ambient environment variables.
    load_dotenv(dotenv_path=config_path, override=True)

    try:
        config_data: dict[str, str | None] = {
            key: os.getenv(key) for key in MazeConfig.model_fields
        }
        config = MazeConfig(**config_data)  # type: ignore
        return {
            "WIDTH": config.WIDTH,
            "HEIGHT": config.HEIGHT,
            "ENTRY": config.ENTRY,
            "EXIT": config.EXIT,
            "OUTPUT_FILE": config.OUTPUT_FILE,
            "PERFECT": config.PERFECT,
            "ENABLE_TUI": config.ENABLE_TUI,
            "SEED": config.SEED,
            "RATIO": config.RATIO,
            "GENERATION_ALGO": config.GENERATION_ALGO,
            "ASCII_VISUALIZER": config.ASCII_VISUALIZER,
        }
    except ValidationError as e:
        raise ValueError(f"Invalid config file format: {e}") from e
    except Exception as e:
        raise ValueError(f"Failed to parse config file: {e}") from e


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
        from mazegen import MazeGenerator
    except ImportError as e:
        print(_missing_dependency_message(e), file=sys.stderr)
        return 1

    try:
        config = parse_config(config_path)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected configuration error: {e}", file=sys.stderr)
        return 1

    try:
        maze_generator = MazeGenerator(
            width=config["WIDTH"],
            height=config["HEIGHT"],
            seed=config["SEED"],
            perfect=config["PERFECT"],
            ratio=config["RATIO"],
            algo=config["GENERATION_ALGO"],
        )
        print(f"Maze ready: {config['WIDTH']}x{config['HEIGHT']}")
        entry = config["ENTRY"]
        exit_ = config["EXIT"]
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
        print("Maze:")
        print(shortest_path)
        if config["ENABLE_TUI"]:
            if not config["ASCII_VISUALIZER"]:
                try:
                    from graphic_visualizer import MazeApp
                except ImportError as e:
                    print(_missing_dependency_message(e), file=sys.stderr)
                    return 1
                MazeApp(maze_generator).run()
            else:
                try:
                    from ascii_visualizer import display_ascii_labyrinthe
                except ImportError as e:
                    print(_missing_dependency_message(e), file=sys.stderr)
                    return 1
                display_ascii_labyrinthe(maze_generator.get_structure())

        return 0
    except (ValueError, TypeError, KeyError, OSError) as e:
        print(f"Error during maze generation: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected runtime error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
