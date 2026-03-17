# from mazegen import MazeGenerator  # WallBits, MazeGrid, Cell

# from tools import print_grid


def one_cell_list(width: int, height: int, cell: int) -> list[list]:
    """Create a List From ont Cell"""
    one_cell_list: list[list:int] = [
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
                one_cell_list[i][j] = " "
    return one_cell_list


def one_line_cell_list(cells) -> list[list]:
    """Create a List of List of Cells on One Line"""
    line_cells: list[list] = one_cell_list(7, 5, cells[0].walls)
    cell: list[list]
    for i in range(1, (len(cells))):
        cell = one_cell_list(7, 5, cells[i].walls)
        for j in range(len(cell)):
            if cell[j][0] == "+":
                line_cells[j][len(line_cells[j]) - 1] = "+"
            for k in range(1, len(cell[0])):
                line_cells[j].append(cell[j][k])
    return line_cells


def labyrinthe_list(cells: list[list:]) -> list[list]:
    """Create a Labyrinthe's List of List"""
    labyrinthe: list[list] = [[]]
    new_line_cells: list[list] = [[]]
    labyrinthe = one_line_cell_list(cells[0])
    for i in range(1, len(cells)):
        new_line_cells = one_line_cell_list(cells[i])
        for j in range(1, len(new_line_cells)):
            labyrinthe.append([])
            for k in range(len(new_line_cells[j])):
                if new_line_cells[0][k] == "+" and j == 1:
                    labyrinthe[len(labyrinthe) - 2][k] = "+"
                labyrinthe[len(labyrinthe) - 1].append(new_line_cells[j][k])
    return labyrinthe


def display_walls(one_cell: list[list]) -> None:
    """Display One Cell"""
    for i in range(len(one_cell)):
        print()
        for j in range(len(one_cell[i])):
            print(one_cell[i][j], end="")


def display_ascii_labyrinthe(cells_list: list[list:int]) -> None:
    """Display a Labyrinthe with ASCII chars"""
    test: list[list]
    test = labyrinthe_list(cells_list)
    display_walls(test)
