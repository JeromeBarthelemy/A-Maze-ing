"""Textual TUI example - simple interactive app."""

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Button, Static


class MazeApp(App):
    """A simple Textual app demonstrating basic widgets."""

    CSS = """
    Screen {
        align: center middle;
    }
    
    Container {
        width: 60;
        height: 20;
        border: solid green;
    }
    
    Static {
        width: 100%;
        content-align: center middle;
        padding: 1;
    }
    
    Button {
        margin: 1;
    }
    """

    BINDINGS = [("q", "quit", "Quit"), ("d", "toggle_dark", "Toggle dark")]

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()
        yield Container(
            Static("Welcome to Textual!\n\nPress buttons or Q to quit."),
            Button("Click me!", id="btn1", variant="primary"),
            Button("Another button", id="btn2", variant="success"),
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        self.query_one(Static).update(
            f"Button '{event.button.label}' clicked!\n\nPress Q to quit."
        )

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.theme = (
            "textual-dark"
            if self.theme == "textual-light"
            else "textual-light"
        )


if __name__ == "__main__":
    app = MazeApp()
    app.run()
