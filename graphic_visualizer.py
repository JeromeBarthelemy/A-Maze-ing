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
        """Initialize one visual maze cell widget.

        Args:
            cell: Backing maze cell model.
            maze_gen: Maze generator used for neighbor/path state.
            is_last_row: True if this cell is in the bottom row.
            is_last_col: True if this cell is in the rightmost column.
            palette: Color mapping used during rendering.
            **kwargs: Additional keyword arguments passed to ``Static``.
        """
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
        # The corner at (0,0) is a wall by default.
        #  We remove it if no walls connect to it.
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
    _is_mounted = False

    TITLE = "A-Maze-ing Maze Viewer"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("t", "toggle_path", "Show/hide path"),
        ("c", "cycle_theme", "Theme"),
        ("w", "cycle_wall_color", "Wall"),
        ("f", "cycle_pattern_color", "Logo"),
        ("g", "regenerate", "Generate"),
        ("i", "toggle_random_io", "Random entry/exit"),
        ("plus", "increase_ratio", "More imperfect"),
        ("minus", "decrease_ratio", "Less imperfect"),
        ("right", "increase_width", "Increase width"),
        ("left", "decrease_width", "Decrease width"),
        ("up", "increase_height", "Increase height"),
        ("down", "decrease_height", "Decrease height"),
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

    # Reactive toggles for maze generation
    is_perfect = reactive(True)
    random_io = reactive(False)
    ratio = reactive(0.10)

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

    Footer {
        height: auto;
        overflow-x: auto;
        overflow-y: hidden;
        scrollbar-size: 1 1;
    }
    """

    def __init__(self, maze_gen: MazeGenerator, **kwargs: Any) -> None:
        """Initialize the TUI application.
        Args:
            maze_gen: Maze generator holding structure and solution data.
            **kwargs: Additional ``App`` keyword arguments.
        """
        super().__init__(**kwargs)
        self.maze_gen = maze_gen
        self.is_perfect = self.maze_gen.params.perfect
        # In perfect mode, ratio is irrelevant; normalize it to 0.0 so
        # first +/- adjustment starts from 0% instead of config value.
        if self.is_perfect:
            self.ratio = 0.0
            self.maze_gen.params = self.maze_gen.params.__class__(
                width=self.maze_gen.params.width,
                height=self.maze_gen.params.height,
                seed=self.maze_gen.params.seed,
                perfect=self.maze_gen.params.perfect,
                ratio=0.0,
            )
        else:
            self.ratio = self.maze_gen.params.ratio
        self._cell_widgets: list[MazeCell] = []
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
        yield Static(self._status_text(), id="maze-status")
        if self.maze_gen.get_solution() is None:
            try:
                self.maze_gen.shortest_path()
            except ValueError:
                pass

        with Container(id="maze-container"):
            with Grid(id="maze-grid"):
                self._cell_widgets = list(self._generate_maze_cells())
                yield from self._cell_widgets
        footer = Footer()
        footer.compact = True
        yield footer

    def watch_is_perfect(self, _: bool, __: bool) -> None:
        """Refresh status text when perfect/imperfect mode changes.

        Args:
            _: Previous value.
            __: New value.
        """
        # Update the status Static widget directly
        if self._is_mounted:
            self._update_status_widget()

    def watch_random_io(self, _: bool, __: bool) -> None:
        """Refresh status text when random entry/exit mode changes.

        Args:
            _: Previous value.
            __: New value.
        """
        # Update the status Static widget directly
        if self._is_mounted:
            self._update_status_widget()

    def _update_status_widget(self) -> None:
        """Update the status line widget if it exists in the DOM."""
        # Only update if the widget exists (after compose)
        try:
            status_widget = self.query_one("#maze-status", expect_type=Static)
        except Exception:
            return
        status_widget.update(self._status_text())

    def _format_coord(self, coord: tuple[int, int] | None) -> str:
        """Format a coordinate for the status line."""
        if coord is None:
            return "N/A"
        return f"({coord[0]}, {coord[1]})"

    def _nearest_valid_coord(
        self,
        preferred: tuple[int, int],
        exclude: tuple[int, int] | None = None,
    ) -> tuple[int, int]:
        """Pick the closest valid coordinate, avoiding logo and exclusion."""
        w, h = self.maze_gen.params.width, self.maze_gen.params.height
        candidates: list[tuple[int, int]] = []
        for y in range(h):
            for x in range(w):
                coord = (x, y)
                if exclude is not None and coord == exclude:
                    continue
                if self.maze_gen._is_in_logo(x, y):
                    continue
                candidates.append(coord)

        if not candidates:
            raise ValueError("No valid coordinate available for entry/exit.")

        return min(
            candidates,
            key=lambda c: (
                abs(c[0] - preferred[0]) + abs(c[1] - preferred[1]),
                c[1],
                c[0],
            ),
        )

    def _sanitize_fixed_endpoints(
        self,
        entry: tuple[int, int],
        exit_: tuple[int, int],
    ) -> tuple[tuple[int, int], tuple[int, int]]:
        """Clamp and relocate fixed entry/exit to valid reachable cells."""
        max_x = self.maze_gen.params.width - 1
        max_y = self.maze_gen.params.height - 1

        entry_pref = (
            min(max(entry[0], 0), max_x),
            min(max(entry[1], 0), max_y),
        )
        exit_pref = (
            min(max(exit_[0], 0), max_x),
            min(max(exit_[1], 0), max_y),
        )

        safe_entry = self._nearest_valid_coord(entry_pref)
        # If the stored exit no longer fits the resized maze,
        # use a deterministic placement at bottom-right.
        exit_out_of_bounds = (
            exit_[0] < 0
            or exit_[0] > max_x
            or exit_[1] < 0
            or exit_[1] > max_y
        )
        exit_invalid = (
            self.maze_gen._is_in_logo(exit_pref[0], exit_pref[1])
            or exit_pref == safe_entry
        )
        if exit_out_of_bounds or exit_invalid:
            for candidate in (
                (max_x, max_y),  # bottom-right
                (0, max_y),      # bottom-left
                (max_x, 0),      # top-right
                (0, 0),          # top-left
            ):
                if (
                    candidate != safe_entry
                    and not self.maze_gen._is_in_logo(
                        candidate[0], candidate[1]
                    )
                ):
                    return safe_entry, candidate

        safe_exit = self._nearest_valid_coord(exit_pref, exclude=safe_entry)
        return safe_entry, safe_exit

    def _status_text(self) -> str:
        """Build the full status text shown under the header."""
        mode = ("Parfait" if self.is_perfect
                else f"Imparfait ({int(self.ratio * 100)}%)")
        io_mode = (
            "Entrées/Sorties fixes"
            if not self.random_io
            else "Entrées/Sorties aléatoires"
        )
        size = f"{self.maze_gen.params.width}x{self.maze_gen.params.height}"
        entry = self._format_coord(self.maze_gen._entry)
        exit_ = self._format_coord(self.maze_gen._exit)
        return (
            f"[Mode] {mode} | {io_mode} | "
            f"Taille: {size} | Entrée: {entry} | Sortie: {exit_}"
        )

    def _configure_grid_dimensions(self) -> None:
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

    def on_mount(self) -> None:
        """Configure initial maze grid dimensions."""
        self._configure_grid_dimensions()
        self._is_mounted = True

    async def _rebuild_maze_grid(self) -> None:
        """Rebuild maze widgets when dimensions change."""
        maze_grid = self.query_one("#maze-grid", expect_type=Grid)
        await maze_grid.remove_children()
        self._cell_widgets = list(self._generate_maze_cells())
        await maze_grid.mount_all(self._cell_widgets)
        self._configure_grid_dimensions()

    def refresh_maze_view(self) -> None:
        """Update and refresh the maze grid widgets from generator state."""
        if not self._cell_widgets:
            return

        resolved_palette = self._resolved_palette()
        maze_grid_data = self.maze_gen.get_structure()

        # Flatten the 2D grid data to iterate easily
        flat_maze_data = [cell for row in maze_grid_data for cell in row]

        for i, widget in enumerate(self._cell_widgets):
            widget.cell = flat_maze_data[i]
            widget.palette = resolved_palette
            widget.refresh()

    async def action_regenerate(self, force_rebuild: bool = False) -> None:
        """Re-generate the maze and refresh the view."""
        try:
            old_size = (
                self.maze_gen.params.width,
                self.maze_gen.params.height,
            )
            self.maze_gen.params = self.maze_gen.params.__class__(
                width=self.maze_gen.params.width,
                height=self.maze_gen.params.height,
                seed=self.maze_gen.params.seed,
                perfect=self.is_perfect,
                ratio=self.ratio,
            )
            # 2. Determine entry/exit positions
            if self.random_io:
                entry, exit_ = self.maze_gen.random_entry_exit()
            else:
                stored_entry = self.maze_gen._entry
                stored_exit = self.maze_gen._exit
                if stored_entry is None or stored_exit is None:
                    entry = (0, 0)
                    exit_ = (
                        self.maze_gen.params.width - 1,
                        self.maze_gen.params.height - 1,
                    )
                else:
                    entry, exit_ = self._sanitize_fixed_endpoints(
                        stored_entry, stored_exit
                    )

            # 3. Generate new maze data
            self.maze_gen.generate(entry=entry, exit_=exit_)

            # 4. Re-calculate the shortest path for the new maze
            try:
                self.maze_gen.shortest_path()
            except ValueError:
                pass  # No path found, that's fine

            # 5. Refresh UI depending on whether dimensions changed.
            new_size = (
                self.maze_gen.params.width,
                self.maze_gen.params.height,
            )
            if force_rebuild or new_size != old_size:
                await self._rebuild_maze_grid()
            else:
                self.maze_revision += 1

            self._update_status_widget()
        except Exception as e:
            import traceback
            with open("/tmp/maze_error.log", "a") as f:
                f.write(f"Error in action_regenerate: {e}\n")
                traceback.print_exc(file=f)

    def action_toggle_random_io(self) -> None:
        """Toggle fixed/random entry/exit mode for next regeneration."""
        self.random_io = not self.random_io

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
        if self._is_mounted:
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
        if self._is_mounted:
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
        if self._is_mounted:
            self.refresh_maze_view()

    def watch_show_path(self, _: bool, __: bool) -> None:
        """Refresh maze when path visibility changes."""
        if self._is_mounted:
            self.refresh_maze_view()

    def watch_ratio(self, _: float, __: float) -> None:
        """Update UI and adjust imperfections when ratio changes."""
        if self._is_mounted:
            self._update_status_widget()
            if not self.is_perfect and self.maze_gen.params.perfect:
                self.maze_gen.params = self.maze_gen.params.__class__(
                    width=self.maze_gen.params.width,
                    height=self.maze_gen.params.height,
                    seed=self.maze_gen.params.seed,
                    perfect=False,
                    ratio=self.ratio,
                )
            self.maze_gen.regenerate_imperfect(self.ratio)
            try:
                self.maze_gen.shortest_path()
            except ValueError:
                pass
            self.maze_revision += 1

    def action_increase_ratio(self) -> None:
        """Increase imperfection ratio by 5% up to 100%."""
        new_ratio = min(1.0, round(self.ratio + 0.05, 2))
        if new_ratio != self.ratio:
            # Editing ratio means the user wants imperfect mode.
            if self.is_perfect:
                self.is_perfect = False
            self.ratio = new_ratio

    def action_decrease_ratio(self) -> None:
        """Decrease imperfection ratio by 5% down to 0%."""
        new_ratio = max(0.0, round(self.ratio - 0.05, 2))
        if new_ratio != self.ratio:
            # Editing ratio means the user wants imperfect mode.
            if self.is_perfect:
                self.is_perfect = False
            self.ratio = new_ratio

    async def _resize_and_regenerate(self, dw: int = 0, dh: int = 0) -> None:
        """Resize maze dimensions and regenerate."""
        current_w = self.maze_gen.params.width
        current_h = self.maze_gen.params.height
        new_w = max(2, current_w + dw)
        new_h = max(2, current_h + dh)
        if new_w == current_w and new_h == current_h:
            return

        self.maze_gen.params = self.maze_gen.params.__class__(
            width=new_w,
            height=new_h,
            seed=self.maze_gen.params.seed,
            perfect=self.is_perfect,
            ratio=self.ratio,
        )
        await self.action_regenerate(force_rebuild=True)

    async def action_increase_width(self) -> None:
        """Increase maze width by one cell and regenerate."""
        await self._resize_and_regenerate(dw=1)

    async def action_decrease_width(self) -> None:
        """Decrease maze width by one cell and regenerate."""
        await self._resize_and_regenerate(dw=-1)

    async def action_increase_height(self) -> None:
        """Increase maze height by one cell and regenerate."""
        await self._resize_and_regenerate(dh=1)

    async def action_decrease_height(self) -> None:
        """Decrease maze height by one cell and regenerate."""
        await self._resize_and_regenerate(dh=-1)

    def watch_maze_revision(self, _: int, __: int) -> None:
        """Refresh maze when a new maze generation is committed."""
        if self._is_mounted:
            self.refresh_maze_view()


if __name__ == "__main__":
    maze_gen = MazeGenerator(width=20, height=10, seed=42, perfect=True)
    maze_gen.generate(entry=(0, 0), exit_=(19, 9))
    MazeApp(maze_gen).run()
