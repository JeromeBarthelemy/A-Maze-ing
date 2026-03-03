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
import random
from typing import Optional


class WallBits(IntFlag):
    """Bit flags for walls in a maze cell (4 directions)."""

    NORTH = 0b0001  # 1
    EAST = 0b0010  # 2
    SOUTH = 0b0100  # 4
    WEST = 0b1000  # 8

    def opposite(self) -> WallBits:
        """Get the opposite wall direction."""
        return {
            WallBits.NORTH: WallBits.SOUTH,
            WallBits.EAST: WallBits.WEST,
            WallBits.SOUTH: WallBits.NORTH,
            WallBits.WEST: WallBits.EAST,
        }[self]


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
    col: int = 0
    row: int = 0
    is_entry: bool = False
    is_exit: bool = False
    is_pattern: bool = False
    visited: bool = False
    distance: int = -1  # -1 = not computed yet
    cluster_id: int = -1  # For maze generation algorithms

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

    def to_binary(self) -> str:
        """Convert walls to 4-bit binary string (N/E/S/W).

        Returns:
            4-character string of '0' and '1' representing walls.
        """
        return f"{self.walls:04b}"


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
        """
        self.params = GeneratorParams(
            width=width,
            height=height,
            seed=seed,
            perfect=perfect,
        )
        random.seed(self.params.seed)
        self._maze: MazeGrid = []
        self._entry: Optional[Coordinate] = None
        self._exit: Optional[Coordinate] = None
        self._solution: Optional[str] = None
        self._openable_cells_numbers: list[int] = []
        self._clusters: dict[int, list[Cell]] = {}

    def _create_empty_grid(self) -> MazeGrid:
        """Create an empty maze grid with default cells.

        Returns:
            A 2D grid of Cell objects.
        """
        return [
            [
                Cell(cluster_id=j * self.params.width + i, col=i, row=j)
                for i in range(self.params.width)
            ]
            for j in range(self.params.height)
        ]

    def generate(self, entry: Coordinate, exit_: Coordinate) -> None:
        """Generate a maze from entry to exit.

        Args:
            entry: Entry cell coordinates.
            exit_: Exit cell coordinates.

        Returns:
            Generated maze structure.

        Raises:
            NotImplementedError: Skeleton placeholder.
        """
        self._entry = entry
        self._exit = exit_
        self.initialize_maze_grid()
        i = 1
        while i < self.params.height * self.params.width:
            random_cell = self.get_random_cell()
            if self.carve_passage(random_cell):
                i += 1

    def carve_passage(self, cell: Cell) -> bool:
        """Carve a passage from the given cell to a random neighbor.

        Args:
            cell: The current cell to carve from."""
        neighbors = self.get_neighbors(cell)
        random.shuffle(neighbors)
        for neighbor, direction in neighbors:
            if neighbor.cluster_id != cell.cluster_id:
                # Merge clusters
                old_cluster_id = max(cell.cluster_id, neighbor.cluster_id)
                new_cluster_id = min(cell.cluster_id, neighbor.cluster_id)
                for c in self._clusters[old_cluster_id]:
                    c.cluster_id = new_cluster_id
                    self._clusters[new_cluster_id].append(c)
                self._clusters.pop(old_cluster_id)
                # Carve passage between cell and neighbor
                cell.remove_wall(direction)
                neighbor.remove_wall(direction.opposite())
                return True
        return False

    def get_neighbors(self, cell: Cell) -> list[tuple[Cell, WallBits]]:
        """Get neighboring cells and their wall directions.

        Args:
            cell: The current cell to find neighbors for.

        Returns:
            List of neighboring cells and their wall directions.
        """
        neighbors = []
        if cell.row > 0:
            neighbors.append(
                (self._maze[cell.row - 1][cell.col], WallBits.NORTH)
            )
        if cell.col < self.params.width - 1:
            neighbors.append(
                (self._maze[cell.row][cell.col + 1], WallBits.EAST)
            )
        if cell.row < self.params.height - 1:
            neighbors.append(
                (self._maze[cell.row + 1][cell.col], WallBits.SOUTH)
            )
        if cell.col > 0:
            neighbors.append(
                (self._maze[cell.row][cell.col - 1], WallBits.WEST)
            )
        return neighbors

    def initialize_maze_grid(self) -> None:
        """Initialize the maze grid for generation."""
        self._maze = self._create_empty_grid()
        k = 0
        for j in range(self.params.height):
            for i in range(self.params.width):
                self._maze[j][i].cluster_id = k
                self._clusters[k] = [self._maze[j][i]]
                k += 1
        if self._entry:
            self._maze[self._entry[1]][self._entry[0]].is_entry = True
        if self._exit:
            self._maze[self._exit[1]][self._exit[0]].is_exit = True
        self.openable_cells_numbers = range(
            self.params.width * self.params.height
        )

    def get_random_cell(self) -> Cell:
        """Get a random cell from the maze grid.
        Returns:
            A random Cell object from the maze grid.
        """
        cell_nb = random.choice(self.openable_cells_numbers)
        row = cell_nb // self.params.width
        col = cell_nb % self.params.width
        return self._maze[row][col]

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

    def get_hex_grid(self) -> list[list[str]]:
        """Get the maze  as a grid of hexadecimal wall representations.

        Returns:
            A 2D list of strings, where each string is a hexadecimal
            character representing the walls of the corresponding cell.
        """
        return [[cell.to_hex() for cell in row] for row in self._maze]

    def get_binary_grid(self) -> list[list[str]]:
        """Get the maze as a grid of binary wall representations.

        Returns:
            A 2D list of strings, where each string is a 4-character
            binary representation of the walls (N/E/S/W) for the
            corresponding cell.
        """
        return [[cell.to_binary() for cell in row] for row in self._maze]
