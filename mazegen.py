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

from collections import deque
from dataclasses import dataclass
from enum import IntFlag
import random
import sys
from typing import Optional

# Logo "42" pattern (5 rows x 7 columns)
# 1 = logo cell (closed), 0 = normal maze cell
LOGO_42_PATTERN = [
    [1, 0, 0, 0, 1, 1, 1],  # row 0
    [1, 0, 0, 0, 0, 0, 1],  # row 1
    [1, 1, 1, 0, 1, 1, 1],  # row 2
    [0, 0, 1, 0, 1, 0, 0],  # row 3
    [0, 0, 1, 0, 1, 1, 1],  # row 4
]
LOGO_HEIGHT = 5
LOGO_WIDTH = 7


class WallBits(IntFlag):
    """Bit flags for walls in a maze cell (4 directions)."""

    NORTH = 0b0001  # 1
    EAST = 0b0010  # 2
    SOUTH = 0b0100  # 4
    WEST = 0b1000  # 8

    def opposite(self) -> WallBits:
        """Return the opposite wall direction.

        Returns:
            Opposite direction for the current wall bit.
        """
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

    walls: WallBits = (
        WallBits.NORTH | WallBits.EAST | WallBits.SOUTH | WallBits.WEST
    )
    col: int = 0
    row: int = 0
    is_entry: bool = False
    is_exit: bool = False
    is_pattern: bool = False
    is_on_path: bool = False
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
        return f"{int(self.walls):X}"

    def to_binary(self) -> str:
        """Convert walls to 4-bit binary string (N/E/S/W).

        Returns:
            4-character string of '0' and '1' representing walls.
        """
        return f"{int(self.walls):04b}"


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
    """Reusable maze generator based on Kruskal + Union-Find.

    Responsibilities:
        - build a perfect maze with deterministic seeding support,
        - expose the generated structure,
        - compute one shortest path between entry and exit.
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

        Initializes:
            Internal maze storage, entry/exit coordinates, solution cache,
            and Union-Find arrays used during generation.
        """
        self.params = GeneratorParams(
            width=width,
            height=height,
            seed=seed,
            perfect=perfect,
        )
        self._show_logo = True
        random.seed(self.params.seed)
        self._maze: MazeGrid = []
        self._entry: Optional[Coordinate] = None
        self._exit: Optional[Coordinate] = None
        self._solution: Optional[str] = None
        self._parent: list[int] = []
        self._size: list[int] = []
        self._logo_placed: bool = False
        self._logo_cell_count: int = 0

    def _cell_index(self, row: int, col: int) -> int:
        """Convert grid coordinates into a Union-Find index.

        Args:
            row: Cell row index.
            col: Cell column index.

        Returns:
            Flattened index in ``[0, width * height)``.
        """
        return row * self.params.width + col

    def _find(self, index: int) -> int:
        """Find the representative of a set with path compression.

        Args:
            index: Union-Find element index.

        Returns:
            Root index of the connected component.
        """
        if self._parent[index] != index:
            self._parent[index] = self._find(self._parent[index])
        return self._parent[index]

    def _union(self, index_a: int, index_b: int) -> bool:
        """Union two sets by size.

        Args:
            index_a: First Union-Find element index.
            index_b: Second Union-Find element index.

        Returns:
            True if a merge happened, False if already in same set.
        """
        root_a = self._find(index_a)
        root_b = self._find(index_b)

        if root_a == root_b:
            return False

        if self._size[root_a] < self._size[root_b]:
            root_a, root_b = root_b, root_a

        self._parent[root_b] = root_a
        self._size[root_a] += self._size[root_b]
        return True

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

    def _build_candidate_edges(
        self,
    ) -> list[tuple[Cell, Cell, WallBits]]:
        """Build all unique neighbor edges for Kruskal generation.

        Excludes edges that touch logo pattern cells to keep them closed.

        Returns:
            List of (cell, neighbor, direction_from_cell_to_neighbor).
        """
        edges: list[tuple[Cell, Cell, WallBits]] = []

        for row in range(self.params.height):
            for col in range(self.params.width):
                cell = self._maze[row][col]

                # Skip edges involving logo pattern cells
                if cell.is_pattern:
                    continue

                if col < self.params.width - 1:
                    east = self._maze[row][col + 1]
                    if not east.is_pattern:
                        edges.append((cell, east, WallBits.EAST))

                if row < self.params.height - 1:
                    south = self._maze[row + 1][col]
                    if not south.is_pattern:
                        edges.append((cell, south, WallBits.SOUTH))

        return edges

    def _can_fit_logo(self) -> bool:
        """Check if the maze is large enough to contain the 42 logo.

        Returns:
            True if the maze can fit the logo, False otherwise.
        """
        return (
            self.params.width > LOGO_WIDTH
            and self.params.height > LOGO_HEIGHT
        )

    def _is_in_logo(self, x: int, y: int) -> bool:
        """Check if a coordinate falls on a logo cell.

        Args:
            x: Column coordinate.
            y: Row coordinate.

        Returns:
            True if the cell is part of the logo pattern.
        """
        if not self._can_fit_logo():
            return False

        logo_start_col = (self.params.width - LOGO_WIDTH) // 2
        logo_start_row = (self.params.height - LOGO_HEIGHT) // 2

        rel_col = x - logo_start_col
        rel_row = y - logo_start_row

        if 0 <= rel_col < LOGO_WIDTH and 0 <= rel_row < LOGO_HEIGHT:
            return LOGO_42_PATTERN[rel_row][rel_col] == 1
        return False

    def random_entry_exit(self) -> tuple[Coordinate, Coordinate]:
        """Generate random valid entry and exit positions.

        Positions are guaranteed to be different and not inside the logo.

        Returns:
            Tuple of (entry, exit) coordinates.
        """

        valid_positions: list[Coordinate] = [
            (x, y)
            for x in range(self.params.width)
            for y in range(self.params.height)
            if not self._is_in_logo(x, y)
        ]

        if len(valid_positions) < 2:
            raise ValueError("Not enough valid positions for entry and exit")

        entry, exit_ = random.sample(valid_positions, 2)
        return entry, exit_

    def _place_logo_42(self) -> bool:
        """Place the 42 logo in the center of the maze.

        Marks logo cells as pattern cells with all walls closed and
        unifies them in the Union-Find structure.

        Returns:
            True if the logo was placed, False if maze is too small.
        """
        if not self._can_fit_logo():
            print(
                f"Error: Maze too small for 42 logo "
                f"(minimum size: {LOGO_WIDTH}x{LOGO_HEIGHT}, "
                f"current: {self.params.width}x{self.params.height})",
                file=sys.stderr,
            )
            return False

        # Calculate center position for the logo
        start_col = (self.params.width - LOGO_WIDTH) // 2
        start_row = (self.params.height - LOGO_HEIGHT) // 2

        # Collect all pattern cells
        pattern_cells: list[Cell] = []

        for row_offset, pattern_row in enumerate(LOGO_42_PATTERN):
            for col_offset, is_logo in enumerate(pattern_row):
                if is_logo:
                    cell = self._maze[start_row + row_offset][
                        start_col + col_offset
                    ]
                    cell.is_pattern = True
                    # Keep all walls (cell stays closed)
                    cell.walls = (
                        WallBits.NORTH
                        | WallBits.EAST
                        | WallBits.SOUTH
                        | WallBits.WEST
                    )
                    pattern_cells.append(cell)

        self._logo_placed = True
        self._logo_cell_count = len(pattern_cells)
        return True

    def generate(self, entry: Coordinate, exit_: Coordinate) -> None:
        """Generate a maze from entry to exit.

        Uses randomized Kruskal on the grid graph and Union-Find to avoid
        cycles, producing a perfect maze.

        Args:
            entry: Entry cell coordinates.
            exit_: Exit cell coordinates.
        """
        self._entry = entry
        self._exit = exit_
        self.initialize_maze_grid()

        # Place 42 logo if requested
        if self._show_logo:
            self._place_logo_42()

        edges = self._build_candidate_edges()
        random.shuffle(edges)

        opened_passages = 0
        # Exclude logo cells from the target count (they form isolated blocks)
        active_cells = (
            self.params.width * self.params.height - self._logo_cell_count
        )
        target_passages = active_cells - 1

        for cell, neighbor, direction in edges:
            cell_index = self._cell_index(cell.row, cell.col)
            neighbor_index = self._cell_index(neighbor.row, neighbor.col)

            if self._union(cell_index, neighbor_index):
                cell.remove_wall(direction)
                neighbor.remove_wall(direction.opposite())
                opened_passages += 1

                if opened_passages == target_passages:
                    break

        for row in self._maze:
            for cell in row:
                cell.cluster_id = self._find(
                    self._cell_index(cell.row, cell.col)
                )
        # If not perfect, remove extra walls to create cycles
        if not self.params.perfect:
            self._remove_extra_walls()

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

    def get_reachable_neighbors(
        self,
        cell: Cell,
    ) -> list[tuple[Cell, WallBits]]:
        """Get neighboring cells reachable from ``cell``.

        A reachable neighbor is adjacent and separated by no wall in the
        corresponding direction.

        Args:
            cell: The source cell.

        Returns:
            List of (neighbor, direction) that can be traversed.
        """
        reachable_neighbors: list[tuple[Cell, WallBits]] = []

        for neighbor, direction in self.get_neighbors(cell):
            if not cell.has_wall(direction):
                reachable_neighbors.append((neighbor, direction))

        return reachable_neighbors

    def initialize_maze_grid(self) -> None:
        """Initialize maze cells and Union-Find state before generation."""
        self._maze = self._create_empty_grid()

        total_cells = self.params.width * self.params.height
        self._parent = list(range(total_cells))
        self._size = [1] * total_cells

        for j in range(self.params.height):
            for i in range(self.params.width):
                self._maze[j][i].cluster_id = self._cell_index(j, i)

        if self._entry:
            self._maze[self._entry[1]][self._entry[0]].is_entry = True
        if self._exit:
            self._maze[self._exit[1]][self._exit[0]].is_exit = True

    def _reset_search_state(self) -> None:
        """Reset pathfinding and rendering flags on every cell."""
        for row in self._maze:
            for cell in row:
                cell.visited = False
                cell.distance = -1
                cell.is_on_path = False

    def shortest_path(self) -> str:
        """Compute and return the shortest path from entry to exit.

        Returns:
            Path encoded as a string of directions (``N/E/S/W``).

        Raises:
            ValueError: If maze or endpoints are not initialized, or if no
                path exists.
        """
        start, goal, came_from = self._run_lee_search()
        directions = self._reconstruct_directions(start, goal, came_from)
        return self._store_solution(directions)

    def _run_lee_search(
        self,
    ) -> tuple[Cell, Cell, dict[Coordinate, tuple[Coordinate, WallBits]]]:
        """Run Lee's algorithm (BFS) and return traversal data.

        Returns:
            Tuple ``(start, goal, came_from)`` where ``came_from`` maps a
            cell coordinate to ``(previous_coordinate, direction_used)``.

        Uses Lee's algorithm (BFS on unit-weight edges).

        Raises:
            ValueError: If maze or endpoints are not initialized, or if no
                path exists.
        """
        if not self._maze:
            raise ValueError("Maze is not generated yet.")
        if self._entry is None or self._exit is None:
            raise ValueError("Entry/exit coordinates are not defined.")

        entry_col, entry_row = self._entry
        exit_col, exit_row = self._exit

        start = self._maze[entry_row][entry_col]
        goal = self._maze[exit_row][exit_col]

        self._reset_search_state()

        queue = deque([start])
        start.visited = True
        start.distance = 0

        came_from: dict[Coordinate, tuple[Coordinate, WallBits]] = {}

        while queue:
            current = queue.popleft()
            if current is goal:
                break

            for neighbor, direction in self.get_reachable_neighbors(current):
                if not neighbor.visited:
                    neighbor.visited = True
                    neighbor.distance = current.distance + 1
                    queue.append(neighbor)
                    came_from[(neighbor.col, neighbor.row)] = (
                        (current.col, current.row),
                        direction,
                    )

        if not goal.visited:
            raise ValueError("No path found from entry to exit.")

        return start, goal, came_from

    def _reconstruct_directions(
        self,
        start: Cell,
        goal: Cell,
        came_from: dict[Coordinate, tuple[Coordinate, WallBits]],
    ) -> list[WallBits]:
        """Reconstruct path directions from the BFS provenance map.

        Args:
            start: Entry cell.
            goal: Exit cell.
            came_from: Mapping produced by BFS from child coordinate to
                ``(parent coordinate, direction used from parent)``.

        Returns:
            Ordered list of directions from entry to exit.
        """
        path_directions: list[WallBits] = []
        cursor = (goal.col, goal.row)
        origin = (start.col, start.row)

        while cursor != origin:
            previous, direction = came_from[cursor]
            path_directions.append(direction)
            cursor = previous

        path_directions.reverse()
        return path_directions

    def _store_solution(self, directions: list[WallBits]) -> str:
        """Serialize and persist the current solution path.

        Marks cells on the solution path through ``is_on_path`` and stores
        the serialized direction string in ``_solution``.

        Args:
            directions: Ordered list of directions from entry to exit.

        Returns:
            Solution encoded as a string of directions (``N/E/S/W``).
        """
        direction_to_char = {
            WallBits.NORTH: "N",
            WallBits.EAST: "E",
            WallBits.SOUTH: "S",
            WallBits.WEST: "W",
        }

        if self._entry is not None:
            entry_col, entry_row = self._entry
            current = self._maze[entry_row][entry_col]
            current.is_on_path = True

            offsets = {
                WallBits.NORTH: (0, -1),
                WallBits.EAST: (1, 0),
                WallBits.SOUTH: (0, 1),
                WallBits.WEST: (-1, 0),
            }

            for direction in directions:
                col_delta, row_delta = offsets[direction]
                next_col = current.col + col_delta
                next_row = current.row + row_delta
                current = self._maze[next_row][next_col]
                current.is_on_path = True

        self._solution = "".join(
            direction_to_char[direction] for direction in directions
        )
        return self._solution

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


    def _remove_extra_walls(self, ratio: float = 0.10) -> None:
        """Remove extra walls to make the maze imperfect (add cycles).

        Args:
            ratio: Fraction of eligible walls to remove (default: 10%).
        """
        width, height = self.params.width, self.params.height
        candidates = []
        for y in range(height):
            for x in range(width):
                cell = self._maze[y][x]
                # Skip logo cells
                if cell.is_pattern:
                    continue
                # Try to remove east wall
                if x < width - 1:
                    neighbor = self._maze[y][x + 1]
                    if not neighbor.is_pattern and cell.has_wall(WallBits.EAST):
                        # Only consider if wall exists (should be open in perfect maze, but may be closed in logo)
                        if not cell.has_wall(WallBits.EAST) and not neighbor.has_wall(WallBits.WEST):
                            continue
                        # Only add if not on border
                        candidates.append((cell, neighbor, WallBits.EAST))
                # Try to remove south wall
                if y < height - 1:
                    neighbor = self._maze[y + 1][x]
                    if not neighbor.is_pattern and cell.has_wall(WallBits.SOUTH):
                        if not cell.has_wall(WallBits.SOUTH) and not neighbor.has_wall(WallBits.NORTH):
                            continue
                        candidates.append((cell, neighbor, WallBits.SOUTH))
        n_remove = max(1, int(len(candidates) * ratio))
        random.shuffle(candidates)
        for cell, neighbor, direction in candidates[:n_remove]:
            # Remove wall in both cells
            cell.remove_wall(direction)
            neighbor.remove_wall(direction.opposite())
