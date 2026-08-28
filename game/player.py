"""Player movement + collision. Pure logic, no pygame dependency."""

from __future__ import annotations

import math

from game.game_map import GameMap


class Player:
    def __init__(self, x: float, y: float, angle: float, radius: float):
        self.x = x
        self.y = y
        self.angle = angle
        self.radius = radius
        self.health = 100

    def rotate(self, delta_angle: float) -> None:
        self.angle = (self.angle + delta_angle) % (2 * math.pi)

    def try_move(self, game_map: GameMap, dx: float, dy: float) -> None:
        """Moves by (dx, dy) in world space, sliding along walls: each axis
        is resolved independently so bumping into a wall on one axis doesn't
        also cancel movement along the other."""
        new_x = self.x + dx
        if not self._collides(game_map, new_x, self.y):
            self.x = new_x

        new_y = self.y + dy
        if not self._collides(game_map, self.x, new_y):
            self.y = new_y

    def move_forward(self, game_map: GameMap, distance: float) -> None:
        self.try_move(game_map, math.cos(self.angle) * distance, math.sin(self.angle) * distance)

    def strafe(self, game_map: GameMap, distance: float) -> None:
        strafe_angle = self.angle + math.pi / 2
        self.try_move(game_map, math.cos(strafe_angle) * distance, math.sin(strafe_angle) * distance)

    def _collides(self, game_map: GameMap, x: float, y: float) -> bool:
        r = self.radius
        for corner_x, corner_y in ((x - r, y - r), (x + r, y - r), (x - r, y + r), (x + r, y + r)):
            if game_map.is_wall_at(corner_x, corner_y):
                return True
        return False

    def take_damage(self, amount: int) -> None:
        self.health = max(0, self.health - amount)

    @property
    def is_alive(self) -> bool:
        return self.health > 0
