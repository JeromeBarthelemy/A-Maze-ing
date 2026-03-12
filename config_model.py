"""Pydantic schema and validators for maze configuration values."""

from __future__ import annotations

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
    ValidationInfo,
)
from typing import Tuple
from typing_extensions import Self

# Logo "42" dimensions (must match mazegen.py)
LOGO_WIDTH = 7
LOGO_HEIGHT = 5

# Logo "42" pattern (1 = logo cell, 0 = normal maze cell)
LOGO_42_PATTERN = [
    [1, 0, 0, 0, 1, 1, 1],  # row 0
    [1, 0, 0, 0, 0, 0, 1],  # row 1
    [1, 1, 1, 0, 1, 1, 1],  # row 2
    [0, 0, 1, 0, 1, 0, 0],  # row 3
    [0, 0, 1, 0, 1, 1, 1],  # row 4
]


class MazeConfig(BaseModel):
    """Pydantic model for maze configuration."""

    WIDTH: int = Field(default=21, gt=0)
    HEIGHT: int = Field(default=21, gt=0)
    ENTRY: Tuple[int, int]
    EXIT: Tuple[int, int]
    OUTPUT_FILE: str
    PERFECT: bool
    SEED: int = 42
    RATIO: float = Field(default=0.10, ge=0.0, le=1.0)

    @field_validator("ENTRY", "EXIT", mode="before")
    def parse_coords(cls, v: str | Tuple[int, int]) -> Tuple[int, int]:
        """Parse comma-separated coordinates into an ``(x, y)`` tuple.

        Args:
            v: Raw coordinate value from configuration input (string or tuple).

        Returns:
            Parsed coordinate pair.

        Raises:
            ValueError: If the coordinate format is invalid.
        """
        # Already a tuple, validate and return
        if isinstance(v, tuple):
            if len(v) == 2 and all(isinstance(x, int) for x in v):
                return v
            raise ValueError(f"Invalid coordinate tuple: {v}")
        try:
            coords = tuple(int(x.strip()) for x in v.split(","))
            if len(coords) != 2:
                raise ValueError("Coordinates must be a pair of integers")
            return coords
        except (ValueError, TypeError, AttributeError) as e:
            raise ValueError(f"Invalid coordinate format: {v}") from e

    @field_validator("ENTRY", "EXIT")
    def validate_coords(
        cls, v: Tuple[int, int], info: ValidationInfo
    ) -> Tuple[int, int]:
        """Validate coordinates are non-negative and within bounds.

        Args:
            v: Parsed coordinate pair.
            info: Validation context containing peer field values.

        Returns:
            The validated coordinate pair.

        Raises:
            ValueError: If coordinates are out of allowed range.
        """
        x, y = v
        # Check coordinates are non-negative
        if x < 0 or y < 0:
            raise ValueError(f"Coordinates must be non-negative, got {v}")
        # Check coordinates are within dimensions
        if hasattr(info, "data"):
            width = info.data.get("WIDTH")
            height = info.data.get("HEIGHT")
            if width is not None and x >= width:
                raise ValueError(
                    f"X coordinate {x} out of bounds (width={width})"
                )
            if height is not None and y >= height:
                raise ValueError(
                    f"Y coordinate {y} out of bounds (height={height})"
                )
        return v

    @field_validator("EXIT")
    def validate_exit_different_from_entry(
        cls, v: Tuple[int, int], info: ValidationInfo
    ) -> Tuple[int, int]:
        """Ensure ``EXIT`` differs from ``ENTRY``.

        Args:
            v: Exit coordinate pair.
            info: Validation context containing peer field values.

        Returns:
            The validated exit coordinate pair.

        Raises:
            ValueError: If ``EXIT`` equals ``ENTRY``.
        """
        if hasattr(info, "data") and "ENTRY" in info.data:
            if v == info.data["ENTRY"]:
                raise ValueError(f"EXIT {v} cannot be the same as ENTRY")
        return v

    @model_validator(mode="after")
    def validate_not_in_logo(self) -> Self:
        """Ensure ENTRY and EXIT are not inside the '42' logo pattern.

        The logo is placed at the center of the maze when dimensions allow.

        Returns:
            The validated model instance.

        Raises:
            ValueError: If ENTRY or EXIT falls on a logo cell.
        """
        # Skip validation if maze is too small for the logo
        if self.WIDTH < LOGO_WIDTH or self.HEIGHT < LOGO_HEIGHT:
            return self

        # Calculate logo position (centered)
        logo_start_col = (self.WIDTH - LOGO_WIDTH) // 2
        logo_start_row = (self.HEIGHT - LOGO_HEIGHT) // 2

        for name, coord in [("ENTRY", self.ENTRY), ("EXIT", self.EXIT)]:
            x, y = coord
            # Check if coordinate is within logo bounding box
            rel_col = x - logo_start_col
            rel_row = y - logo_start_row

            if 0 <= rel_col < LOGO_WIDTH and 0 <= rel_row < LOGO_HEIGHT:
                # Check if this specific cell is part of the logo pattern
                if LOGO_42_PATTERN[rel_row][rel_col] == 1:
                    raise ValueError(
                        f"{name} {coord} is inside the '42' logo pattern"
                    )

        return self
