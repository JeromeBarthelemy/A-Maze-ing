"""Pytest unit tests for maze generation and pathfinding."""

from collections import deque

import pytest

from mazegen import MazeGenerator, WallBits


def test_shortest_path_raises_before_generation() -> None:
    """Raise when asking shortest path before maze generation."""
    generator = MazeGenerator(width=3, height=3, seed=42, perfect=True)
    with pytest.raises(ValueError):
        generator.shortest_path()


def test_generate_and_shortest_path_validity() -> None:
    """Generate maze and validate the returned path step-by-step."""
    width, height = 8, 6
    entry = (0, 0)
    exit_ = (7, 5)
    generator = MazeGenerator(width=width, height=height, seed=42,
                              perfect=True)
    generator.generate(entry=entry, exit_=exit_)

    path = generator.shortest_path()
    assert all(step in "NESW" for step in path)

    maze = generator.get_structure()
    x, y = entry
    direction_delta = {
        "N": (0, -1, WallBits.NORTH),
        "E": (1, 0, WallBits.EAST),
        "S": (0, 1, WallBits.SOUTH),
        "W": (-1, 0, WallBits.WEST),
    }

    for step in path:
        dx, dy, direction = direction_delta[step]
        cell = maze[y][x]
        assert not cell.has_wall(direction)
        x += dx
        y += dy
        assert 0 <= x < width
        assert 0 <= y < height

    assert (x, y) == exit_


def test_all_cells_reachable_in_perfect_maze() -> None:
    """Ensure perfect-maze generation produces one connected component."""
    width, height = 10, 7
    generator = MazeGenerator(width=width, height=height, seed=123,
                              perfect=True)
    generator.generate(entry=(0, 0), exit_=(9, 6))

    maze = generator.get_structure()
    visited = {(0, 0)}
    queue = deque([maze[0][0]])

    while queue:
        current = queue.popleft()
        for neighbor, _ in generator.get_reachable_neighbors(current):
            key = (neighbor.col, neighbor.row)
            if key not in visited:
                visited.add(key)
                queue.append(neighbor)

    assert len(visited) == width * height


def test_single_cell_maze_path() -> None:
    """Handle single-cell maze edge case for direct API usage."""
    generator = MazeGenerator(width=1, height=1, seed=42, perfect=True)
    generator.generate(entry=(0, 0), exit_=(0, 0))

    path = generator.shortest_path()
    assert path == ""
    cell = generator.get_structure()[0][0]
    assert cell.is_on_path
