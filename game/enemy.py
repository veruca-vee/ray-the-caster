"""Enemy sprite state. Pure logic, no pygame dependency."""

from __future__ import annotations

import math


class Enemy:
    def __init__(self, x: float, y: float, health: int, radius: float):
        self.x = x
        self.y = y
        self.health = health
        self.radius = radius

    @property
    def is_alive(self) -> bool:
        return self.health > 0

    def take_damage(self, amount: int) -> None:
        if not self.is_alive:
            return
        self.health = max(0, self.health - amount)

    def distance_to(self, x: float, y: float) -> float:
        return math.hypot(self.x - x, self.y - y)


def find_closest_hit_enemy(enemies: list[Enemy], shooter_x: float, shooter_y: float,
                            shooter_angle: float, max_range: float,
                            hit_cone: float = 0.15) -> Enemy | None:
    """Simple hitscan target selection: among living enemies roughly in front
    of the shooter (within `hit_cone` radians of the aim angle) and within
    range, returns the nearest one. `hit_cone` gives forgiving "auto-aim"
    typical of simple raycaster shooters rather than requiring a pixel-perfect
    crosshair.
    """
    best: Enemy | None = None
    best_distance = math.inf
    for enemy in enemies:
        if not enemy.is_alive:
            continue
        distance = enemy.distance_to(shooter_x, shooter_y)
        if distance > max_range or distance <= 0:
            continue
        angle_to_enemy = math.atan2(enemy.y - shooter_y, enemy.x - shooter_x)
        angle_diff = (angle_to_enemy - shooter_angle + math.pi) % (2 * math.pi) - math.pi
        if abs(angle_diff) > hit_cone:
            continue
        if distance < best_distance:
            best_distance = distance
            best = enemy
    return best
