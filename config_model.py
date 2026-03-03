from __future__ import annotations

from pydantic import BaseModel, Field, field_validator, ValidationInfo
from typing import Tuple


class MazeConfig(BaseModel):
    """Pydantic model for maze configuration."""

    WIDTH: int = Field(default=21, gt=0)
    HEIGHT: int = Field(default=21, gt=0)
    ENTRY: Tuple[int, int]
    EXIT: Tuple[int, int]
    OUTPUT_FILE: str
    PERFECT: bool
    SEED: int = 42

    @field_validator("ENTRY", "EXIT", mode="before")
    def parse_coords(cls, v: str) -> Tuple[int, int]:
        """Parse comma-separated coordinates."""
        try:
            coords = tuple(int(x.strip()) for x in v.split(","))
            if len(coords) != 2:
                raise ValueError("Coordinates must be a pair of integers")
            return coords
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid coordinate format: {v}") from e

    @field_validator("ENTRY", "EXIT")
    def validate_coords(
        cls, v: Tuple[int, int], info: ValidationInfo
    ) -> Tuple[int, int]:
        """Validate coordinates are positive and within bounds."""
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
        """Validate that EXIT is different from ENTRY."""
        if hasattr(info, "data") and "ENTRY" in info.data:
            if v == info.data["ENTRY"]:
                raise ValueError(f"EXIT {v} cannot be the same as ENTRY")
        return v
