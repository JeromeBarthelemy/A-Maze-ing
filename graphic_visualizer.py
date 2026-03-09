"""Textual TUI for maze visualization with Super-Units (V6).

Each cell is a SINGLE widget that renders its own 3x3 (or 4x4) block of units.
This approach is ultra-stable, modular, and perfectly preserves the V1 look.
"""

from typing import Any

from rich.text import Text
from textual.app import App, ComposeResult
from textual.widgets import Footer, Static, Header
from textual.containers import Container, Grid

from mazegen import MazeGenerator, WallBits, Cell


class MazeCell(Static):
    """A 'Super-Unit' widget representing a single maze cell and its walls."""

    def __init__(
        self,
        cell: Cell,
        maze_gen: MazeGenerator,
        is_last_row: bool,
        is_last_col: bool,
        palette: dict[str, str],
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.cell = cell
        self.maze_gen = maze_gen
        self.is_last_row = is_last_row
        self.is_last_col = is_last_col
        self.palette = palette

    def render(self) -> Text:
        """Render one maze cell as an expanded colored block.

        Returns:
            Rich ``Text`` containing a 3x3 cell (or 4x4 on boundaries)
            with walls, room background, and optional solution connectors.
        """
        rows_count = 4 if self.is_last_row else 3
        cols_count = 4 if self.is_last_col else 3

        room_kind = "empty"
        if self.cell.is_entry:
            room_kind = "entry"
        elif self.cell.is_exit:
            room_kind = "exit"
        elif self.cell.is_on_path:
            room_kind = "path"
        elif self.cell.is_pattern:
            room_kind = "pattern"

        wall_color = self.palette["wall"]
        empty_color = self.palette["empty"]
        path_color = self.palette["path"]
        cell_color = self.palette[room_kind]
        path_directions = {
            direction
            for neighbor, direction in self.maze_gen.get_reachable_neighbors(
                self.cell
            )
            if neighbor.is_on_path
        }

        # Initialize colors matrix
        color_grid = [
            [wall_color for _ in range(cols_count)]
            for _ in range(rows_count)
        ]

        # 1. Fill Room (2x2 area starting at 1,1)
        for dr in (1, 2):
            for dc in (1, 2):
                color_grid[dr][dc] = cell_color

        # 2. Carve North Wall
        if not self.cell.has_wall(WallBits.NORTH):
            color_grid[0][1] = color_grid[0][2] = empty_color

            if self.cell.is_on_path and WallBits.NORTH in path_directions:
                color_grid[0][1] = color_grid[0][2] = path_color

        # 3. Carve West Wall
        if not self.cell.has_wall(WallBits.WEST):
            color_grid[1][0] = color_grid[2][0] = empty_color

            if self.cell.is_on_path and WallBits.WEST in path_directions:
                color_grid[1][0] = color_grid[2][0] = path_color

        # 4. Handle Boundaries (South/East edges)
        if self.is_last_row and not self.cell.has_wall(WallBits.SOUTH):
            color_grid[3][1] = color_grid[3][2] = empty_color
        if self.is_last_col and not self.cell.has_wall(WallBits.EAST):
            color_grid[1][3] = color_grid[2][3] = empty_color

        # 5. Build Rich Text (each unit is 2 chars wide)
        lines = []
        for r in range(rows_count):
            line = Text()
            for c in range(cols_count):
                line.append("  ", style=f"on {color_grid[r][c]}")
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
        "empty": "grey19",
        "path": "yellow",
        "entry": "green",
        "exit": "bright_red",
        "pattern": "magenta",
    }

    CSS = """
    #maze-container {
        align: center middle;
        overflow: auto;
        border: none;
    }

    #maze-grid {
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
        """Initialize the TUI application.

        Args:
            maze_gen: Maze generator holding structure and solution data.
            **kwargs: Additional ``App`` keyword arguments.
        """
        super().__init__(**kwargs)
        self.maze_gen = maze_gen
        self.palette = self.DEFAULT_PALETTE.copy()

    def compose(self) -> ComposeResult:
        """Compose static UI widgets and maze cells.

        Ensures the shortest path is computed before rendering so path
        highlighting is immediately available.

        Yields:
            Header, centered maze grid, and footer widgets.
        """
        yield Header()

        if self.maze_gen.get_solution() is None:
            try:
                self.maze_gen.shortest_path()
            except ValueError:
                pass

        w, h = self.maze_gen.params.width, self.maze_gen.params.height
        maze_grid = self.maze_gen.get_structure()

        with Container(id="maze-container"):
            with Grid(id="maze-grid"):
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
                            maze_gen=self.maze_gen,
                            is_last_row=(r == h - 1),
                            is_last_col=(c == w - 1),
                            palette=self.palette,
                            classes=" ".join(classes)
                        )

        yield Footer()

    def on_mount(self) -> None:
        """Configure maze grid dimensions and explicit track sizes."""
        w, h = self.maze_gen.params.width, self.maze_gen.params.height
        maze_grid = self.query_one("#maze-grid")

        # Set grid dimensions (number of cells)
        maze_grid.styles.grid_size_columns = w
        maze_grid.styles.grid_size_rows = h

        # Fix track sizes explicitly to match MazeCell dimensions and avoid
        # layout rounding / drift when the last row/column is larger.
        maze_grid.styles.grid_columns = " ".join(["6"] * (w - 1) + ["8"])
        maze_grid.styles.grid_rows = " ".join(["3"] * (h - 1) + ["4"])

        # Explicit total size: content + 1-cell border on each side.
        # Content is (3*w+1) units by (3*h+1),
        # with 2 chars per horizontal unit.
        maze_grid.styles.width = (3 * w + 1) * 2 + 2
        maze_grid.styles.height = (3 * h + 1) + 2


if __name__ == "__main__":
    maze_gen = MazeGenerator(width=20, height=10, seed=42, perfect=True)
    maze_gen.generate(entry=(0, 0), exit_=(19, 9))
    MazeApp(maze_gen).run()
