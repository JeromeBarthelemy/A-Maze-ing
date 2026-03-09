"""Pytest unit tests for utility helpers."""

import io
from contextlib import redirect_stdout

from tools import print_grid


def test_print_grid_empty() -> None:
    """Print explicit marker for empty grid input."""
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        print_grid([])
    output = buffer.getvalue()
    assert "(empty grid)" in output


def test_print_grid_non_empty() -> None:
    """Print separator and formatted rows for non-empty grids."""
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        print_grid([["A", "B"], ["C", "D"]])
    output = buffer.getvalue()
    assert "====" in output
    assert "A B" in output
    assert "C D" in output
