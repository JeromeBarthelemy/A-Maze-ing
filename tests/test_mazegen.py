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
    width, height = 6, 6
    entry = (0, 0)
    exit_ = (5, 5)
    generator = MazeGenerator(
        width=width, height=height, seed=42, perfect=True
    )
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
    width, height = 10, 4
    generator = MazeGenerator(
        width=width, height=height, seed=123, perfect=True
    )
    generator.generate(entry=(0, 0), exit_=(9, 3))

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


def test_logo_not_placed_when_maze_too_small(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Verify error message when maze is too small for the 42 logo."""
    # Logo requires 7x5, test with smaller maze
    generator = MazeGenerator(width=5, height=4, seed=42, perfect=True)
    generator.generate(entry=(0, 0), exit_=(4, 3))

    captured = capsys.readouterr()
    assert "Error: Maze too small for 42 logo" in captured.err
    assert not generator._logo_placed


def test_logo_placed_in_large_maze() -> None:
    """Verify 42 logo is placed correctly in a sufficiently large maze."""
    width, height = 15, 11
    generator = MazeGenerator(
        width=width, height=height, seed=42, perfect=True
    )
    generator.generate(entry=(0, 0), exit_=(14, 10))

    assert generator._logo_placed
    assert generator._logo_cell_count == 18  # Number of '1's in the pattern

    maze = generator.get_structure()
    # Count pattern cells
    pattern_count = sum(1 for row in maze for cell in row if cell.is_pattern)
    assert pattern_count == 18


def test_logo_cells_are_closed() -> None:
    """Ensure all logo cells have all four walls intact."""
    from mazegen import WallBits

    width, height = 15, 11
    generator = MazeGenerator(
        width=width, height=height, seed=42, perfect=True
    )
    generator.generate(entry=(0, 0), exit_=(14, 10))

    maze = generator.get_structure()
    all_walls = WallBits.NORTH | WallBits.EAST | WallBits.SOUTH | WallBits.WEST

    for row in maze:
        for cell in row:
            if cell.is_pattern:
                assert (
                    cell.walls == all_walls
                ), f"Logo cell at ({cell.col}, {cell.row}) is not fully closed"


def test_path_exists_with_logo() -> None:
    """Verify a path from entry to exit exists even with the logo present."""
    width, height = 15, 11
    generator = MazeGenerator(
        width=width, height=height, seed=42, perfect=True
    )
    generator.generate(entry=(0, 0), exit_=(14, 10))

    # Should not raise
    path = generator.shortest_path()
    assert len(path) > 0
    assert all(step in "NESW" for step in path)


def test_logo_state_reset_between_generations_keeps_small_perfect() -> None:
    """Large maze with logo then small maze should still be fully connected."""
    generator = MazeGenerator(width=15, height=11, seed=42, perfect=True)
    generator.generate(entry=(0, 0), exit_=(14, 10))
    assert generator._logo_placed
    assert generator._logo_cell_count > 0

    generator.params = generator.params.__class__(
        width=6,
        height=4,
        seed=42,
        perfect=True,
        ratio=generator.params.ratio,
    )
    generator.generate(entry=(0, 0), exit_=(5, 3))

    assert not generator._logo_placed
    assert generator._logo_cell_count == 0

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

    assert len(visited) == 6 * 4


def test_imperfect_ratio_zero_adds_no_extra_walls() -> None:
    """Ratio 0% must not add cycles in imperfect mode."""
    width, height = 6, 4
    generator = MazeGenerator(
        width=width,
        height=height,
        seed=42,
        perfect=False,
        ratio=0.0,
    )
    generator.generate(entry=(0, 0), exit_=(5, 3))

    maze = generator.get_structure()
    passages = 0
    active_cells = 0
    for y in range(height):
        for x in range(width):
            cell = maze[y][x]
            if cell.is_pattern:
                continue
            active_cells += 1
            if x < width - 1 and not cell.has_wall(WallBits.EAST):
                passages += 1
            if y < height - 1 and not cell.has_wall(WallBits.SOUTH):
                passages += 1

    assert passages == active_cells - 1
