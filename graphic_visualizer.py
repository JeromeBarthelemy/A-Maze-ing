"""Textual TUI for maze visualization with Super-Units (V6).

Each cell is a SINGLE widget that renders its own 3x3 (or 4x4) block of units.
This approach is ultra-stable, modular, and perfectly preserves the V1 look.
"""

from typing import Any, Iterator

from rich.text import Text
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import (
    Footer,
    Static,
    Header,
)
from textual.containers import (
    Container,
    Grid,
)

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
        show_path = bool(getattr(self.app, "show_path", True))

        room_kind = "empty"
        if self.cell.is_entry:
            room_kind = "entry"
        elif self.cell.is_exit:
            room_kind = "exit"
        elif show_path and self.cell.is_on_path:
            room_kind = "path"
        elif self.cell.is_pattern:
            room_kind = "pattern"

        wall_color = self.palette["wall"]
        empty_color = self.palette["empty"]
        path_color = self.palette["path"]
        cell_color = self.palette[room_kind]
        path_directions = set()
        if show_path:
            path_directions = {
                direction
                for neighbor, direction in (
                    self.maze_gen.get_reachable_neighbors(self.cell)
                )
                if neighbor.is_on_path
            }

        # Initialize colors matrix
        color_grid = [
            [wall_color for _ in range(cols_count)] for _ in range(rows_count)
        ]

        # 1. Fill Room (2x2 area starting at 1,1)
        for dr in (1, 2):
            for dc in (1, 2):
                color_grid[dr][dc] = cell_color

        # 2. Carve North Wall
        if not self.cell.has_wall(WallBits.NORTH):
            color_grid[0][1] = color_grid[0][2] = empty_color

            if (
                show_path
                and self.cell.is_on_path
                and WallBits.NORTH in path_directions
            ):
                color_grid[0][1] = color_grid[0][2] = path_color

        # 3. Carve West Wall
        if not self.cell.has_wall(WallBits.WEST):
            color_grid[1][0] = color_grid[2][0] = empty_color

            if (
                show_path
                and self.cell.is_on_path
                and WallBits.WEST in path_directions
            ):
                color_grid[1][0] = color_grid[2][0] = path_color

        # 4. Handle Boundaries (South/East edges)
        if self.is_last_row and not self.cell.has_wall(WallBits.SOUTH):
            color_grid[3][1] = color_grid[3][2] = empty_color
        if self.is_last_col and not self.cell.has_wall(WallBits.EAST):
            color_grid[1][3] = color_grid[2][3] = empty_color

        # 5. Remove "Pillars" at (0,0) if unconnected
        # The corner at (0,0) is a wall by default. We remove it if no walls connect to it.
        pillar_connected = self.cell.has_wall(
            WallBits.NORTH
        ) or self.cell.has_wall(WallBits.WEST)
        if not pillar_connected:
            r, c = self.cell.row, self.cell.col
            grid = self.maze_gen.get_structure()
            # Check North neighbor for West wall
            if r > 0 and grid[r - 1][c].has_wall(WallBits.WEST):
                pillar_connected = True
            # Check West neighbor for North wall
            if (
                not pillar_connected
                and c > 0
                and grid[r][c - 1].has_wall(WallBits.NORTH)
            ):
                pillar_connected = True

        if not pillar_connected:
            color_grid[0][0] = empty_color

        # 6. Build Rich Text (each unit is 2 chars wide)
        lines = []
        for r in range(rows_count):
            line = Text()
            for c in range(cols_count):
                line.append("  ", style=f"on {color_grid[r][c]}")
            lines.append(line)

        return Text("\n").join(lines)


class MazeApp(App[None]):
    """Textual app using stable Super-Unit MazeCell widgets."""

    show_path = reactive(True)
    maze_revision = reactive(0)

    TITLE = "A-Maze-ing Maze Viewer"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("p", "toggle_path", "Toggle solution path"),
        ("c", "cycle_theme", "Change theme"),
        ("w", "cycle_wall_color", "Cycle wall color"),
        ("f", "cycle_pattern_color", "Cycle 42 color"),
        ("r", "regenerate", "Re-generate maze"),
    ]

    PALETTE: dict[str, str] = {
        "wall": "$foreground",
        "empty": "$background",
        "path": "$secondary",
        "entry": "$success",
        "exit": "$error",
        "pattern": "$primary",
    }

    WALL_COLOR_CYCLE: tuple[str, ...] = (
        "$primary",
        "$surface",
        "$panel",
        "$warning",
        "$foreground",
    )

    PATTERN_COLOR_CYCLE: tuple[str, ...] = (
        "$surface",
        "$panel",
        "$warning",
        "$foreground",
        "$primary",
    )

    EXCLUDED_THEMES: tuple[str, ...] = ("textual-ansi",)

    # Debug flag: randomize entry/exit on regenerate (change in source only)
    RANDOM_IO: bool = False

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
        # Avoid reading a reactive value in __init__, which can trigger
        # watchers before the widget tree exists.
        self.palette = self.PALETTE.copy()

    def _resolve_color(self, color_value: str) -> str:
        """Resolve `$theme_var` color names to concrete colors."""
        if not color_value.startswith("$"):
            return color_value

        var_name = color_value[1:]
        css_vars = self.get_css_variables()
        resolved = css_vars.get(var_name, "white")
        return str(resolved)

    def _resolved_palette(self) -> dict[str, str]:
        """Return palette with all theme vars resolved to concrete colors."""
        return {
            key: self._resolve_color(value)
            for key, value in self.palette.items()
        }

    def _generate_maze_cells(self) -> Iterator[MazeCell]:
        """Generates MazeCell widgets for the current maze structure."""
        w, h = self.maze_gen.params.width, self.maze_gen.params.height
        maze_grid_data = self.maze_gen.get_structure()
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
                    maze_grid_data[r][c],
                    maze_gen=self.maze_gen,
                    is_last_row=(r == h - 1),
                    is_last_col=(c == w - 1),
                    palette=self._resolved_palette(),
                    classes=" ".join(classes),
                )

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

        with Container(id="maze-container"):
            with Grid(id="maze-grid"):
                yield from self._generate_maze_cells()
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

    def refresh_maze_view(self) -> None:
        """Rebuild and refresh the maze grid widgets from generator state."""
        grid_nodes = list(self.query("#maze-grid"))
        if not grid_nodes:
            return
        grid = grid_nodes[0]
        grid.remove_children()
        grid.mount(*self._generate_maze_cells())

    def action_regenerate(self) -> None:
        """Re-generate the maze and refresh the view."""
        # 1. Determine entry/exit positions
        if self.RANDOM_IO:
            entry, exit_ = self.maze_gen.random_entry_exit()
        else:
            stored_entry = self.maze_gen._entry
            stored_exit = self.maze_gen._exit
            if stored_entry is None or stored_exit is None:
                return
            entry, exit_ = stored_entry, stored_exit

        # 2. Generate new maze data
        self.maze_gen.generate(entry=entry, exit_=exit_)

        # 3. Re-calculate the shortest path for the new maze
        try:
            self.maze_gen.shortest_path()
        except ValueError:
            pass  # No path found, that's fine

        # 4. Trigger UI refresh via reactive state.
        self.maze_revision += 1

    def action_toggle_path(self) -> None:
        """Toggle solution path visibility and refresh maze cells."""
        self.show_path = not self.show_path

    def action_cycle_theme(self) -> None:
        """Cycle through predefined Textual themes."""
        theme_names = [
            name
            for name in self.available_themes.keys()
            if name not in self.EXCLUDED_THEMES
        ]
        if not theme_names:
            return

        current_theme = str(getattr(self, "theme", ""))
        try:
            index = theme_names.index(current_theme)
        except ValueError:
            index = -1

        setattr(self, "theme", theme_names[(index + 1) % len(theme_names)])
        if self.is_mounted:
            self.refresh_maze_view()

    def action_cycle_wall_color(self) -> None:
        """Cycle wall color independently from the active palette."""
        current = self.palette["wall"]
        try:
            index = self.WALL_COLOR_CYCLE.index(current)
        except ValueError:
            index = -1
        self.palette["wall"] = self.WALL_COLOR_CYCLE[
            (index + 1) % len(self.WALL_COLOR_CYCLE)
        ]
        if self.is_mounted:
            self.refresh_maze_view()

    def action_cycle_pattern_color(self) -> None:
        """Cycle 42 pattern color independently from the active palette."""
        current = self.palette["pattern"]
        try:
            index = self.PATTERN_COLOR_CYCLE.index(current)
        except ValueError:
            index = -1
        self.palette["pattern"] = self.PATTERN_COLOR_CYCLE[
            (index + 1) % len(self.PATTERN_COLOR_CYCLE)
        ]
        if self.is_mounted:
            self.refresh_maze_view()

    def watch_show_path(self, _: bool, __: bool) -> None:
        """Refresh maze when path visibility changes."""
        if self.is_mounted:
            self.refresh_maze_view()

    def watch_maze_revision(self, _: int, __: int) -> None:
        """Refresh maze when a new maze generation is committed."""
        if self.is_mounted:
            self.refresh_maze_view()


if __name__ == "__main__":
    maze_gen = MazeGenerator(width=20, height=10, seed=42, perfect=True)
    maze_gen.generate(entry=(0, 0), exit_=(19, 9))
    MazeApp(maze_gen).run()
