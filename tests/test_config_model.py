"""Pytest unit tests for maze configuration validation."""

import pytest
from pydantic import ValidationError

from config_model import MazeConfig


def test_valid_config_parses_coordinates() -> None:
    """Parse valid coordinates from config strings.

    Verifies:
        ENTRY and EXIT are converted to integer tuples.
    """
    config = MazeConfig.model_validate(
        {
            "WIDTH": 5,
            "HEIGHT": 4,
            "ENTRY": "0,0",
            "EXIT": "4,3",
            "OUTPUT_FILE": "maze.txt",
            "PERFECT": True,
            "SEED": 42,
        }
    )
    assert config.ENTRY == (0, 0)
    assert config.EXIT == (4, 3)


def test_missing_width_or_height_raises() -> None:
    """Reject config when mandatory WIDTH/HEIGHT keys are missing."""
    with pytest.raises(ValidationError):
        MazeConfig.model_validate(
            {
                "HEIGHT": 4,
                "ENTRY": "0,0",
                "EXIT": "4,3",
                "OUTPUT_FILE": "maze.txt",
                "PERFECT": True,
            }
        )

    with pytest.raises(ValidationError):
        MazeConfig.model_validate(
            {
                "WIDTH": 5,
                "ENTRY": "0,0",
                "EXIT": "4,3",
                "OUTPUT_FILE": "maze.txt",
                "PERFECT": True,
            }
        )


def test_invalid_coordinate_format_raises() -> None:
    """Reject malformed coordinate values.

    Raises:
        ValidationError: When coordinate string is not an ``x,y`` pair.
    """
    with pytest.raises(ValidationError):
        MazeConfig.model_validate(
            {
                "WIDTH": 5,
                "HEIGHT": 4,
                "ENTRY": "0,0,1",
                "EXIT": "4,3",
                "OUTPUT_FILE": "maze.txt",
                "PERFECT": True,
                "SEED": 42,
            }
        )


def test_out_of_bounds_coordinates_raise() -> None:
    """Reject coordinates outside configured dimensions."""
    with pytest.raises(ValidationError):
        MazeConfig.model_validate(
            {
                "WIDTH": 5,
                "HEIGHT": 4,
                "ENTRY": "5,0",
                "EXIT": "4,3",
                "OUTPUT_FILE": "maze.txt",
                "PERFECT": True,
                "SEED": 42,
            }
        )


def test_exit_must_differ_from_entry() -> None:
    """Reject configuration where entry equals exit."""
    with pytest.raises(ValidationError):
        MazeConfig.model_validate(
            {
                "WIDTH": 5,
                "HEIGHT": 4,
                "ENTRY": "1,1",
                "EXIT": "1,1",
                "OUTPUT_FILE": "maze.txt",
                "PERFECT": True,
                "SEED": 42,
            }
        )
