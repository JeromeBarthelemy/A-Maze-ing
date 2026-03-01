"""Reusable maze generator module for A-Maze-ing.

This standalone module is designed to be packaged and installed via pip
(as distribution `mazegen-*`).

Example:
    from mazegen import MazeGenerator

    generator = MazeGenerator(width=20, height=15, seed=42, perfect=True)
    maze = generator.generate(entry=(0, 0), exit_=(19, 14))
    path = generator.shortest_path()
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntFlag
from typing import Optional


class WallBits(IntFlag):
    """Bit flags for walls in a maze cell (4 directions)."""

    NORTH = 0b0001  # 1
    EAST = 0b0010  # 2
    SOUTH = 0b0100  # 4
    WEST = 0b1000  # 8


@dataclass
class Cell:
    """A single cell in the maze grid.

    Attributes:
        walls: Bitmask of walls (use WallBits flags).
        is_entry: True if this is the entry cell.
        is_exit: True if this is the exit cell.
        is_pattern: True if part of the "42" pattern.
        visited: Temporary flag for generation/pathfinding algorithms.
        distance: Distance from entry (for BFS/shortest path).
    """

    walls: int = 0xF  # All walls by default (15)
    is_entry: bool = False
    is_exit: bool = False
    is_pattern: bool = False
    visited: bool = False
    distance: int = -1  # -1 = not computed yet

    def has_wall(self, direction: WallBits) -> bool:
        """Check if a wall exists in the given direction.

        Args:
            direction: Wall direction to check (NORTH/EAST/SOUTH/WEST).

        Returns:
            True if the wall exists, False otherwise.
        """
        return bool(self.walls & direction)

    def add_wall(self, direction: WallBits) -> None:
        """Add a wall in the given direction.

        Args:
            direction: Wall direction to add (NORTH/EAST/SOUTH/WEST).
        """
        self.walls |= direction

    def remove_wall(self, direction: WallBits) -> None:
        """Remove a wall in the given direction.

        Args:
            direction: Wall direction to remove (NORTH/EAST/SOUTH/WEST).
        """
        self.walls &= ~direction

    def to_hex(self) -> str:
        """Convert walls to hexadecimal character (0-F).

        Returns:
            Single hexadecimal character representing the wall bitmask.
        """
        return f"{self.walls:X}"


Coordinate = tuple[int, int]
MazeGrid = list[list[Cell]]


@dataclass(frozen=True, slots=True)
class GeneratorParams:
    """Input parameters for maze generation."""

    width: int
    height: int
    seed: Optional[int] = None
    perfect: bool = True


class MazeGenerator:
    """Reusable maze generator API skeleton.

    This class is intentionally a structural placeholder:
    - instantiate with custom parameters
    - generate a maze
    - access generated structure
    - access at least one solution path
    """

    def __init__(
        self,
        width: int,
        height: int,
        seed: Optional[int] = None,
        perfect: bool = True,
    ) -> None:
        """Initialize generator parameters and internal placeholders.

        Args:
            width: Maze width (number of columns).
            height: Maze height (number of rows).
            seed: Random seed for generation (None for random).
            perfect: True for perfect maze, False for imperfect.

        Raises:
            ValueError: If width or height are not positive.
        """
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be positive")

        self.params = GeneratorParams(
            width=width,
            height=height,
            seed=seed,
            perfect=perfect,
        )
        self._maze: MazeGrid = []
        self._entry: Optional[Coordinate] = None
        self._exit: Optional[Coordinate] = None
        self._solution: Optional[str] = None

    def generate(self, entry: Coordinate, exit_: Coordinate) -> MazeGrid:
        """Generate a maze from entry to exit.

        Args:
            entry: Entry cell coordinates.
            exit_: Exit cell coordinates.

        Returns:
            Generated maze structure.

        Raises:
            ValueError: If entry and exit are the same cell, or coordinates
                are out of bounds.
            NotImplementedError: Skeleton placeholder.
        """
        # Validate coordinates are within bounds
        if not (
            0 <= entry[0] < self.params.width
            and 0 <= entry[1] < self.params.height
        ):
            raise ValueError(f"Entry {entry} is out of bounds")
        if not (
            0 <= exit_[0] < self.params.width
            and 0 <= exit_[1] < self.params.height
        ):
            raise ValueError(f"Exit {exit_} is out of bounds")

        # Validate entry and exit are different cells
        if entry == exit_:
            raise ValueError("Entry and exit must be different cells")

        self._entry = entry
        self._exit = exit_
        raise NotImplementedError("Maze generation is not implemented yet.")

    def shortest_path(self) -> str:
        """Return the shortest valid path from entry to exit (N/E/S/W).

        Raises:
            NotImplementedError: Skeleton placeholder.
        """
        raise NotImplementedError("Path computation is not implemented yet.")

    def get_structure(self) -> MazeGrid:
        """Access the generated maze structure.

        Returns:
            The 2D grid of Cell objects representing the maze.
        """
        return self._maze

    def get_solution(self) -> Optional[str]:
        """Access one computed solution path when available.

        Returns:
            Solution path as a string of directions (N/E/S/W), or None
            if not yet computed.
        """
        return self._solution
