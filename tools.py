def print_grid(grid: list[list[str]]) -> None:
    """Print a 2D grid of strings to the console.

    Args:
        grid: A 2D list of strings to print.
    """
    if not grid or not grid[0]:
        print("(empty grid)")
        return

    print("=" * len(grid[0]) * 2)
    for row in grid:
        print(" ".join(row))
