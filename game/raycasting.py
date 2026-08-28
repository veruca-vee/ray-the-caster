"""Grid-DDA raycasting. Pure math, no pygame -- fully unit-testable.

Implementation follows the standard "Digital Differential Analysis" approach
(as popularized by Lode Vandevenne's raycasting tutorial): step the ray one
grid line at a time (whichever axis is closer) until a solid cell is hit,
then compute the *perpendicular* distance to avoid fish-eye distortion.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from game.game_map import GameMap


@dataclass(frozen=True)
class RayHit:
    distance: float  # perpendicular distance to the wall (not euclidean)
    tile_id: int  # value of the map cell that was hit
    side: int  # 0 = hit a vertical grid line (N/S face), 1 = horizontal (E/W face)
    wall_x: float  # fractional [0, 1) position along the hit wall, for texturing
    map_x: int
    map_y: int


def cast_ray(game_map: GameMap, pos_x: float, pos_y: float, angle: float,
             max_depth: float) -> RayHit:
    ray_dir_x = math.cos(angle)
    ray_dir_y = math.sin(angle)

    map_x = int(math.floor(pos_x))
    map_y = int(math.floor(pos_y))

    delta_dist_x = abs(1.0 / ray_dir_x) if ray_dir_x != 0 else math.inf
    delta_dist_y = abs(1.0 / ray_dir_y) if ray_dir_y != 0 else math.inf

    if ray_dir_x < 0:
        step_x = -1
        side_dist_x = (pos_x - map_x) * delta_dist_x
    else:
        step_x = 1
        side_dist_x = (map_x + 1.0 - pos_x) * delta_dist_x

    if ray_dir_y < 0:
        step_y = -1
        side_dist_y = (pos_y - map_y) * delta_dist_y
    else:
        step_y = 1
        side_dist_y = (map_y + 1.0 - pos_y) * delta_dist_y

    # Any grid, however large, is fully crossed within width+height steps;
    # the max_depth term bounds it further for open (borderless) test maps.
    max_steps = game_map.width + game_map.height + int(max_depth) + 4
    side = 0

    for _ in range(max_steps):
        if side_dist_x < side_dist_y:
            side_dist_x += delta_dist_x
            map_x += step_x
            side = 0
        else:
            side_dist_y += delta_dist_y
            map_y += step_y
            side = 1

        if game_map.is_wall(map_x, map_y):
            break

        perp_probe = side_dist_x - delta_dist_x if side == 0 else side_dist_y - delta_dist_y
        if perp_probe > max_depth:
            return RayHit(distance=max_depth, tile_id=0, side=side,
                          wall_x=0.0, map_x=map_x, map_y=map_y)
    else:
        return RayHit(distance=max_depth, tile_id=0, side=side,
                      wall_x=0.0, map_x=map_x, map_y=map_y)

    if side == 0:
        perp_dist = (map_x - pos_x + (1 - step_x) / 2) / ray_dir_x
        wall_x = pos_y + perp_dist * ray_dir_y
    else:
        perp_dist = (map_y - pos_y + (1 - step_y) / 2) / ray_dir_y
        wall_x = pos_x + perp_dist * ray_dir_x

    wall_x -= math.floor(wall_x)

    return RayHit(
        distance=max(perp_dist, 1e-6),
        tile_id=game_map.cell_value(map_x, map_y),
        side=side,
        wall_x=wall_x,
        map_x=map_x,
        map_y=map_y,
    )


def cast_column_rays(game_map: GameMap, pos_x: float, pos_y: float, view_angle: float,
                      fov: float, num_columns: int, max_depth: float) -> list[RayHit]:
    """Casts one ray per screen column across the field of view, sweeping
    from the leftmost to the rightmost column angle."""
    if num_columns <= 0:
        return []
    half_fov = fov / 2
    hits = []
    for col in range(num_columns):
        t = col / max(num_columns - 1, 1)  # 0..1 across the screen
        ray_angle = view_angle - half_fov + t * fov
        hits.append(cast_ray(game_map, pos_x, pos_y, ray_angle, max_depth))
    return hits
