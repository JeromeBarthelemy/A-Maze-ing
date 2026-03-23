from mazegen import MazeGenerator, MazeGrid, Cell


def generate_ascii_cell(
    width: int,
    height: int,
    cell: int,
    is_entry: bool,
    is_exit: bool,
    is_on_path: bool,
    is_pattern: bool,
    show_path: bool = False,
) -> list[list[str]]:
    """
    Create an ASCII representation of a single maze cell.

    Args:
        width (int): Width of the cell.
        height (int): Height of the cell.
        cell (int): Bitmask representing the cell's walls.
        is_entry (bool): True if the cell is the maze entry.
        is_exit (bool): True if the cell is the maze exit.
        is_on_path (bool): True if the cell is part of the solution path.
        is_pattern (bool): True if the cell is part of the logo/pattern.
        show_path (bool, optional): Whether to display the solution path.
        Defaults to False.

    Returns:
        list[list[str]]: 2D list of strings representing the cell.
    """
    ascii_cell: list[list[str]] = [
        [" " for _ in range(width)] for _ in range(height)
    ]

    north: int = cell & 1
    east: int = cell & 2
    south: int = cell & 4
    west: int = cell & 8
    for i in range(height):
        for j in range(width):
            if (
                ((i == 0 and j == 0) and (north > 0 or west > 0))
                or (
                    (i == height - 1 and j == width - 1)
                    and (south > 0 or east > 0)
                )
                or ((i == 0 and j == width - 1) and (north > 0 or east > 0))
                or ((i == height - 1 and j == 0) and (south > 0 or west > 0))
            ):
                ascii_cell[i][j] = "+"
            elif ((i == 0) and (north > 0)) or (
                (i == height - 1) and (south > 0)
            ):
                ascii_cell[i][j] = "-"
            elif ((j == 0) and (west > 0)) or (
                (j == width - 1) and (east > 0)
            ):
                ascii_cell[i][j] = "|"
            else:
                if i == width // 2 - 1 and j == height // 2 + 1:
                    if is_entry:
                        ascii_cell[i][j] = "E"
                    elif is_exit:
                        ascii_cell[i][j] = "X"
                    elif is_on_path and show_path:
                        ascii_cell[i][j] = "@"
                    elif is_pattern:
                        ascii_cell[i][j] = "#"
                    else:
                        ascii_cell[i][j] = " "
                else:
                    if is_pattern:
                        ascii_cell[i][j] = "#"
                    elif is_on_path and show_path:
                        ascii_cell[i][j] = "@"
                    else:
                        ascii_cell[i][j] = " "
    return ascii_cell


def generate_ascii_line(line: list[Cell], show_path: bool) -> list[list[str]]:
    """
    Create a single ASCII line from a list of maze cells.

    Args:
        line (list[Cell]): List of maze cells in a row.
        show_path (bool): Whether to display the solution path.

    Returns:
        list[list[str]]: 2D list of strings representing the row of cells.
    """
    ascii_line: list[list[str]] = generate_ascii_cell(
        7,
        5,
        line[0].walls,
        line[0].is_entry,
        line[0].is_exit,
        line[0].is_on_path,
        line[0].is_pattern,
        show_path=show_path,
    )
    ascii_cell: list[list[str]]
    for i in range(1, (len(line))):
        ascii_cell = generate_ascii_cell(
            7,
            5,
            line[i].walls,
            line[i].is_entry,
            line[i].is_exit,
            line[i].is_on_path,
            line[i].is_pattern,
            show_path=show_path,
        )
        for j in range(len(ascii_cell)):
            if ascii_cell[j][0] == "+":
                ascii_line[j][len(ascii_line[j]) - 1] = "+"
            for k in range(1, len(ascii_cell[0])):
                ascii_line[j].append(ascii_cell[j][k])
    return ascii_line


def generate_ascii_labyrinth(
    cells_grid: MazeGrid, show_path: bool
) -> list[list[str]]:
    """
    Build an ASCII representation of a maze from a grid of cells.

    Args:
        cells_grid (MazeGrid): The grid of maze cells.
        show_path (bool): Whether to display the solution path.

    Returns:
        list[list[str]]: ASCII grid representing the maze.
    """
    ascii_labyrinth: list[list[str]] = [[]]
    new_line_cells: list[list[str]] = [[]]
    ascii_labyrinth = generate_ascii_line(cells_grid[0], show_path=show_path)
    for i in range(1, len(cells_grid)):
        new_line_cells = generate_ascii_line(
            cells_grid[i], show_path=show_path
        )
        for j in range(1, len(new_line_cells)):
            ascii_labyrinth.append([])
            for k in range(len(new_line_cells[j])):
                if new_line_cells[0][k] == "+" and j == 1:
                    ascii_labyrinth[len(ascii_labyrinth) - 2][k] = "+"
                ascii_labyrinth[len(ascii_labyrinth) - 1].append(
                    new_line_cells[j][k]
                )
    return ascii_labyrinth


def display_walls(
    ascii_grid: list[list[str]], wall_color: int, logo_color: int
) -> None:
    """
    Print the ASCII grid to the terminal with color codes.

    Args:
        ascii_grid (list[list[str]]): The ASCII grid to display.
        wall_color (int): ANSI color code for walls.
        logo_color (int): ANSI color code for the logo.
    """
    for i in range(len(ascii_grid)):
        print()
        for j in range(len(ascii_grid[i])):
            if ascii_grid[i][j] in ["+", "-", "|"]:
                ANSI_COLOR = wall_color
            elif ascii_grid[i][j] == "E":
                ANSI_COLOR = 32
            elif ascii_grid[i][j] == "X":
                ANSI_COLOR = 33
            elif ascii_grid[i][j] == "@":
                ANSI_COLOR = 34
            elif ascii_grid[i][j] == "#":
                ANSI_COLOR = logo_color
            else:
                ANSI_COLOR = 37
            print(
                f"\033[0;{ANSI_COLOR}m{ascii_grid[i][j]}\033[0m", end=""
            )


def display_ascii_labyrinth(
    cells_grid: MazeGrid,
    show_path: bool,
    wall_color: int,
    logo_color: int,
) -> None:
    """
    Print the maze as ASCII art in the terminal with color.

    Args:
        cells_grid (MazeGrid): The grid of maze cells.
        show_path (bool): Whether to display the solution path.
        wall_color (int): ANSI color code for walls.
        logo_color (int): ANSI color code for the logo.
    """
    ascii_grid: list[list[str]]
    ascii_grid = generate_ascii_labyrinth(cells_grid, show_path)
    display_walls(ascii_grid, wall_color=wall_color, logo_color=logo_color)


def ascii_visualizer(generator: MazeGenerator) -> None:
    """
    Launch an interactive ASCII interface to visualize and manipulate the maze.

    Args:
        generator (MazeGenerator): The maze generator to visualize.
    """
    exit = False
    show_path = False
    wall_color = 37
    logo_color = 37
    while not exit:
        display_ascii_labyrinth(
            generator.get_structure(),
            show_path=show_path,
            wall_color=wall_color,
            logo_color=logo_color,
        )
        print("\n=== A-Maze-ing ASCII Visualizer ===\n")
        choice = input(
            "Press 'q' to quit,"
            "'r' to re-generate,"
            "'t' to toggle path display,"
            "'w' to cycle wall color,"
            "'l' to cycle logo color: "
        )
        if choice.lower() == "q":
            exit = True
        elif choice.lower() == "r":
            if generator.params.entry and generator.params.exit_:
                generator.generate(
                    generator.params.entry, generator.params.exit_
                )
                generator.shortest_path()
        elif choice.lower() == "t":
            show_path = not show_path
        elif choice.lower() == "w":
            wall_color += 1
            wall_color = (wall_color - 31) % 7 + 31
        elif choice.lower() == "l":
            logo_color += 1
            logo_color = (logo_color - 31) % 7 + 31
    return
