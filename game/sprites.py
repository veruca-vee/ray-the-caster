"""Sprite screen-projection math for billboarded enemies. Pure functions,
no pygame dependency -- kept separate from renderer.py so the projection
geometry (screen position, apparent size, visibility) is unit-testable
without a display.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from game.enemy import Enemy
from game.player import Player


def _normalize_angle(angle: float) -> float:
    """Wraps an angle to (-pi, pi]."""
    return (angle + math.pi) % (2 * math.pi) - math.pi


@dataclass(frozen=True)
class SpriteProjection:
    screen_x: float  # horizontal center of the sprite, in render-space pixels
    half_width: float  # half the sprite's on-screen width/height in pixels
    distance: float  # euclidean distance from the player, for depth testing


def project_sprite(player: Player, enemy: Enemy, fov: float,
                    render_width: int, render_height: int,
                    fov_margin: float = 0.3) -> SpriteProjection | None:
    """Projects an enemy into screen space, or returns None if it's fully
    outside the field of view (with a small margin so sprites don't pop in
    abruptly right at the FOV edge)."""
    dx = enemy.x - player.x
    dy = enemy.y - player.y
    distance = math.hypot(dx, dy)
    if distance < 1e-6:
        return None

    angle_to_enemy = math.atan2(dy, dx)
    relative_angle = _normalize_angle(angle_to_enemy - player.angle)
    if abs(relative_angle) > fov / 2 + fov_margin:
        return None

    size = render_height / distance
    screen_x = (0.5 + relative_angle / fov) * render_width
    return SpriteProjection(screen_x=screen_x, half_width=size / 2, distance=distance)
