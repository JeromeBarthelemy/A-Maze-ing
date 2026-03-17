import random

from ascii_visualisator2 import labyrinthe_list, display_walls


class ExhaustiveLabyrinth:
    class Cell:
        """Defini One Cell"""

        def __init__(self, walls: int, visited: bool) -> None:
            self.walls: int = walls
            self.visited: bool = visited

    def __init__(self, file_name: str) -> None:
        """Initialise Labyrinth Caracteristics"""
        self.features_labyrinth: dict = {}
        with open(file_name, "r") as file_descriptor:
            self.read: str = file_descriptor.read()
        self.creat_features_dict()
        self.labyrinth: list[list[ExhaustiveLabyrinth.Cell]] = [
            [
                self.Cell(15, False)
                for _ in range(int(self.features_labyrinth["WIDTH"]))
            ]
            for _ in range(int(self.features_labyrinth["HEIGHT"]))
        ]
        self.init_labyrinth(0, 0)

    def move_east(self, y: int, x: int) -> None:
        """Open Wall on East"""
        if (
            x + 1 < int(self.features_labyrinth["WIDTH"])
            and self.labyrinth[y][x + 1].visited is False
        ):
            self.labyrinth[y][x].walls = self.labyrinth[y][x].walls - 2
            self.labyrinth[y][x + 1].walls = self.labyrinth[y][x + 1].walls - 8
            self.init_labyrinth(y, x + 1)

    def move_south(self, y: int, x: int) -> None:
        """Open Wall on South"""
        if (
            y + 1 < int(self.features_labyrinth["HEIGHT"])
            and self.labyrinth[y + 1][x].visited is False
        ):
            self.labyrinth[y][x].walls = self.labyrinth[y][x].walls - 4
            self.labyrinth[y + 1][x].walls = self.labyrinth[y + 1][x].walls - 1
            self.init_labyrinth(y + 1, x)

    def move_west(self, y: int, x: int) -> None:
        """Open Wall on West"""
        if x > 0 and self.labyrinth[y][x - 1].visited is False:
            self.labyrinth[y][x].walls = self.labyrinth[y][x].walls - 8
            self.labyrinth[y][x - 1].walls = self.labyrinth[y][x - 1].walls - 2
            self.init_labyrinth(y, x - 1)

    def move_north(self, y: int, x: int) -> None:
        """Open Wall on North"""
        if y > 0 and self.labyrinth[y - 1][x].visited is False:
            self.labyrinth[y][x].walls = self.labyrinth[y][x].walls - 1
            self.labyrinth[y - 1][x].walls = self.labyrinth[y - 1][x].walls - 4
            self.init_labyrinth(y - 1, x)

    def init_labyrinth(self, y: int, x: int) -> None:
        """Initialise Labyrinth"""
        desorder: list = list(range(4))
        random.shuffle(desorder)
        i: int = 0
        self.labyrinth[y][x].visited = True
        while i < 4:
            if desorder[i] == 0:
                i += 1
                self.move_east(y, x)
            elif desorder[i] == 1:
                i += 1
                self.move_south(y, x)
            elif desorder[i] == 2:
                i += 1
                self.move_west(y, x)
            elif desorder[i] == 3:
                i += 1
                self.move_north(y, x)

    def print_dict_content(self) -> None:
        """Display Dictionary Content"""
        print(self.features_labyrinth.items())

    def creat_features_dict(self) -> None:
        """Make a Dictionary with Content of File"""
        lignes: list = [str]
        ligne_split: list = [str]
        ligne = str
        lignes = self.read.split("\n")
        for ligne in lignes:
            ligne_split = ligne.split("=")
            if len(ligne_split) == 2:
                key, value = ligne_split
                self.features_labyrinth[key] = value


def main():
    """Testing Main"""
    class_test = ExhaustiveLabyrinth("config.txt")
    #  class_test.print_dict_content()
    #  print(class_test.labyrinth)
    test = labyrinthe_list(class_test.labyrinth)
    display_walls(test)
    print()


if __name__ == "__main__":
    main()
