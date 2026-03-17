from mazegen import MazeGenerator, MazeGrid, Cell


def one_cell_list(
    width: int,
    height: int,
    cell: int,
    is_entry: bool,
    is_exit: bool,
    is_on_path: bool,
    is_pattern: bool,
    show_path: bool = False,
) -> list[list[str]]:
    """Create a List From ont Cell"""
    one_cell_list: list[list[str]] = [
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
                one_cell_list[i][j] = "+"
            elif ((i == 0) and (north > 0)) or (
                (i == height - 1) and (south > 0)
            ):
                one_cell_list[i][j] = "-"
            elif ((j == 0) and (west > 0)) or (
                (j == width - 1) and (east > 0)
            ):
                one_cell_list[i][j] = "|"
            else:
                if i == width // 2 - 1 and j == height // 2 + 1:
                    if is_entry:
                        one_cell_list[i][j] = "E"
                    elif is_exit:
                        one_cell_list[i][j] = "S"
                    elif is_on_path and show_path:
                        one_cell_list[i][j] = "@"
                    elif is_pattern:
                        one_cell_list[i][j] = "#"
                    else:
                        one_cell_list[i][j] = " "
                else:
                    if is_pattern:
                        one_cell_list[i][j] = "#"
                    elif is_on_path and show_path:
                        one_cell_list[i][j] = "@"
                    else:
                        one_cell_list[i][j] = " "
    return one_cell_list


def one_line_cell_list(cells: list[Cell], show_path: bool) -> list[list[str]]:
    """Create a List of List of Cells on One Line"""
    line_cells: list[list[str]] = one_cell_list(
        7,
        5,
        cells[0].walls,
        cells[0].is_entry,
        cells[0].is_exit,
        cells[0].is_on_path,
        cells[0].is_pattern,
        show_path=show_path,
    )
    cell: list[list[str]]
    for i in range(1, (len(cells))):
        cell = one_cell_list(
            7,
            5,
            cells[i].walls,
            cells[i].is_entry,
            cells[i].is_exit,
            cells[i].is_on_path,
            cells[i].is_pattern,
            show_path=show_path,
        )
        for j in range(len(cell)):
            if cell[j][0] == "+":
                line_cells[j][len(line_cells[j]) - 1] = "+"
            for k in range(1, len(cell[0])):
                line_cells[j].append(cell[j][k])
    return line_cells


def labyrinthe_list(cells_grid: MazeGrid, show_path: bool) -> list[list[str]]:
    """Create a Labyrinthe's List of List"""
    labyrinthe: list[list[str]] = [[]]
    new_line_cells: list[list[str]] = [[]]
    labyrinthe = one_line_cell_list(cells_grid[0], show_path=show_path)
    for i in range(1, len(cells_grid)):
        new_line_cells = one_line_cell_list(cells_grid[i], show_path=show_path)
        for j in range(1, len(new_line_cells)):
            labyrinthe.append([])
            for k in range(len(new_line_cells[j])):
                if new_line_cells[0][k] == "+" and j == 1:
                    labyrinthe[len(labyrinthe) - 2][k] = "+"
                labyrinthe[len(labyrinthe) - 1].append(new_line_cells[j][k])
    return labyrinthe


def display_walls(
    ascii_grid: list[list[str]], wall_color: int, logo_color: int
) -> None:
    """Display One Cell"""
    for i in range(len(ascii_grid)):
        print()
        for j in range(len(ascii_grid[i])):
            if ascii_grid[i][j] in ["+", "-", "|"]:
                CODE_COULEUR_ANSI = wall_color
            elif ascii_grid[i][j] == "+":
                CODE_COULEUR_ANSI = 31
            elif ascii_grid[i][j] == "E":
                CODE_COULEUR_ANSI = 32
            elif ascii_grid[i][j] == "S":
                CODE_COULEUR_ANSI = 33
            elif ascii_grid[i][j] == "@":
                CODE_COULEUR_ANSI = 34
            elif ascii_grid[i][j] == "#":
                CODE_COULEUR_ANSI = logo_color
            else:
                CODE_COULEUR_ANSI = 37
            print(
                f"\033[0;{CODE_COULEUR_ANSI}m{ascii_grid[i][j]}\033[0m", end=""
            )


def display_ascii_labyrinthe(
    cells_grid: MazeGrid,
    show_path: bool,
    wall_color: int,
    logo_color: int,
) -> None:
    """Display a Labyrinthe with ASCII chars"""
    ascii_grid: list[list[str]]
    ascii_grid = labyrinthe_list(cells_grid, show_path)
    display_walls(ascii_grid, wall_color=wall_color, logo_color=logo_color)


def ascii_visualizer(generator: MazeGenerator) -> None:
    """Display a Maze with ASCII chars"""
    exit = False
    show_path = False
    wall_color = 37
    logo_color = 37
    while not exit:
        display_ascii_labyrinthe(
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
