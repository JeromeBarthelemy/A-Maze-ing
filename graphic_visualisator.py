"""Textual TUI for maze visualization."""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Footer, Static


class MazeApp(App):
    """A simple Textual app for displaying a maze."""

    CSS = """
    Screen {
        layout: vertical;
    }
    
    #title {
        dock: top;
        height: 1;
        background: $boost;
        content-align: center middle;
    }
    
    #maze {
        width: 1fr;
        height: 1fr;
        border: solid green;
        overflow: auto;
    }
    """

    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Static("A-Maze-ing", id="title")
        yield Static("Maze display here...", id="maze")
        yield Footer()


if __name__ == "__main__":
    app = MazeApp()
    app.run()
