"""Grid map helpers. Pure functions/classes only -- no pygame dependency,
so this module is fully unit-testable without a display.
"""

from __future__ import annotations


class GameMap:
    def __init__(self, grid: list[list[int]]):
        if not grid or not grid[0]:
            raise ValueError("grid must be a non-empty 2D list")
        self.grid = grid
        self.height = len(grid)
        self.width = len(grid[0])
        if any(len(row) != self.width for row in grid):
            raise ValueError("all map rows must have the same width")

    def is_inside(self, cell_x: int, cell_y: int) -> bool:
        return 0 <= cell_x < self.width and 0 <= cell_y < self.height

    def cell_value(self, cell_x: int, cell_y: int) -> int:
        """Returns the tile id at a cell. Out-of-bounds counts as solid (1)
        so a ray or player can never escape the map."""
        if not self.is_inside(cell_x, cell_y):
            return 1
        return self.grid[cell_y][cell_x]

    def is_wall(self, cell_x: int, cell_y: int) -> bool:
        return self.cell_value(cell_x, cell_y) != 0

    def is_wall_at(self, x: float, y: float) -> bool:
        return self.is_wall(int(x), int(y))
