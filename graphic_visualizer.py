"""Textual TUI for maze visualization with Super-Units (V6).

Each cell is a SINGLE widget that renders its own 3x3 (or 4x4) block of units.
This approach is ultra-stable, modular, and perfectly preserves the V1 look.
"""

from typing import Any

from rich.text import Text
from textual.app import App, ComposeResult
from textual.widgets import Footer, Static, Header
from textual.containers import Center, Grid

from mazegen import MazeGenerator, WallBits, Cell


class MazeCell(Static):
    """A 'Super-Unit' widget representing a single maze cell and its walls."""

    def __init__(
        self,
        cell: Cell,
        is_last_row: bool,
        is_last_col: bool,
        palette: dict[str, str],
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.cell = cell
        self.is_last_row = is_last_row
        self.is_last_col = is_last_col
        self.palette = palette

    def render(self) -> Text:
        """Render the 3x3 (or 4x4) unit expansion for this cell."""
        rows_count = 4 if self.is_last_row else 3
        cols_count = 4 if self.is_last_col else 3

        room_kind = "path"
        if self.cell.is_entry:
            room_kind = "entry"
        elif self.cell.is_exit:
            room_kind = "exit"
        elif self.cell.is_pattern:
            room_kind = "pattern"

        wall_color = self.palette["wall"]
        path_color = self.palette["path"]
        room_color = self.palette[room_kind]

        # Initialize colors matrix
        grid = [[wall_color for _ in range(cols_count)]
                for _ in range(rows_count)]

        # 1. Fill Room (2x2 area starting at 1,1)
        for dr in (1, 2):
            for dc in (1, 2):
                grid[dr][dc] = room_color

        # 2. Carve North Wall
        if not self.cell.has_wall(WallBits.NORTH):
            grid[0][1] = grid[0][2] = path_color

        # 3. Carve West Wall
        if not self.cell.has_wall(WallBits.WEST):
            grid[1][0] = grid[2][0] = path_color

        # 4. Handle Boundaries (South/East edges)
        if self.is_last_row and not self.cell.has_wall(WallBits.SOUTH):
            grid[3][1] = grid[3][2] = path_color
        if self.is_last_col and not self.cell.has_wall(WallBits.EAST):
            grid[1][3] = grid[2][3] = path_color

        # 5. Build Rich Text (each unit is 2 chars wide)
        lines = []
        for r in range(rows_count):
            line = Text()
            for c in range(cols_count):
                line.append("  ", style=f"on {grid[r][c]}")
            lines.append(line)

        return Text("\n").join(lines)


class MazeApp(App[None]):
    """Textual app using stable Super-Unit MazeCell widgets."""

    TITLE = "A-Maze-ing Maze Viewer"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    DEFAULT_PALETTE = {
        "wall": "bright_blue",
        "path": "grey19",
        "entry": "green",
        "exit": "bright_red",
        "pattern": "magenta",
    }

    CSS = """
    #labyrinthe {
        layout: grid;
        border: heavy $primary;
        width: auto;
        height: auto;
        grid-gutter: 0;
    }

    MazeCell {
        /* Standard 3x3 cell = 6 chars wide, 3 chars high */
        width: 6;
        height: 3;
    }

    /* Edge cases (boundary cells) */
    MazeCell.last-row { height: 4; }
    MazeCell.last-col { width: 8; }
    MazeCell.corner   { width: 8; height: 4; }
    """

    def __init__(self, maze_gen: MazeGenerator, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.maze_gen = maze_gen
        self.palette = self.DEFAULT_PALETTE.copy()

    def compose(self) -> ComposeResult:
        yield Header()

        w, h = self.maze_gen.params.width, self.maze_gen.params.height
        maze_grid = self.maze_gen.get_structure()

        with Center():
            with Grid(id="labyrinthe"):
                for r in range(h):
                    for c in range(w):
                        classes = []
                        if r == h - 1:
                            classes.append("last-row")
                        if c == w - 1:
                            classes.append("last-col")
                        if r == h - 1 and c == w - 1:
                            classes.append("corner")

                        yield MazeCell(
                            maze_grid[r][c],
                            is_last_row=(r == h - 1),
                            is_last_col=(c == w - 1),
                            palette=self.palette,
                            classes=" ".join(classes)
                        )

        yield Footer()

    def on_mount(self) -> None:
        """Configure main grid layout."""
        w, h = self.maze_gen.params.width, self.maze_gen.params.height
        labyrinthe = self.query_one("#labyrinthe")

        # Set grid dimensions (number of cells)
        labyrinthe.styles.grid_size_columns = w
        labyrinthe.styles.grid_size_rows = h

        # Fix track sizes explicitly to match MazeCell dimensions and avoid
        # layout rounding / drift when the last row/column is larger.
        labyrinthe.styles.grid_columns = " ".join(["6"] * (w - 1) + ["8"])
        labyrinthe.styles.grid_rows = " ".join(["3"] * (h - 1) + ["4"])

        # Explicit total size: content + 1-cell border on each side.
        # Content is (3*w+1) units by (3*h+1),
        # with 2 chars per horizontal unit.
        labyrinthe.styles.width = (3 * w + 1) * 2 + 2
        labyrinthe.styles.height = (3 * h + 1) + 2


if __name__ == "__main__":
    maze_gen = MazeGenerator(width=20, height=10, seed=42, perfect=True)
    maze_gen.generate(entry=(0, 0), exit_=(19, 9))
    MazeApp(maze_gen).run()
