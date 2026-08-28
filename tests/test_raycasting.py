import math

import pytest

from game.game_map import GameMap
from game.raycasting import cast_column_rays, cast_ray

ROOM = GameMap([
    [1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1],
])

CENTER_X, CENTER_Y = 2.5, 2.5


@pytest.mark.parametrize("angle", [0, math.pi / 2, math.pi, 3 * math.pi / 2])
def test_cardinal_rays_from_center_hit_symmetric_walls(angle):
    hit = cast_ray(ROOM, CENTER_X, CENTER_Y, angle, max_depth=20)
    assert hit.distance == pytest.approx(1.5, abs=1e-6)
    assert hit.tile_id == 1


def test_wall_x_is_fractional_position_along_hit_face():
    # Straight east from (2.5, 2.5) hits the wall face at y=2.5 -> fractional
    # position 0.5 along that grid line.
    hit = cast_ray(ROOM, CENTER_X, CENTER_Y, 0.0, max_depth=20)
    assert hit.wall_x == pytest.approx(0.5, abs=1e-6)


def test_ray_never_escapes_bordered_map_regardless_of_angle():
    for degrees in range(0, 360, 15):
        hit = cast_ray(ROOM, CENTER_X, CENTER_Y, math.radians(degrees), max_depth=20)
        assert hit.tile_id == 1
        assert 0 < hit.distance <= 3.0


def test_ray_reports_capped_miss_within_max_depth_when_nothing_in_range():
    # 20x20 open interior (with a solid border far outside max_depth) so the
    # ray legitimately travels the full max_depth without hitting anything.
    grid = [[0] * 20 for _ in range(20)]
    open_map = GameMap(grid)
    hit = cast_ray(open_map, 10.0, 10.0, 0.0, max_depth=5.0)
    assert hit.distance == pytest.approx(5.0)
    assert hit.tile_id == 0


def test_cast_column_rays_sweeps_left_to_right_across_fov():
    hits = cast_column_rays(ROOM, CENTER_X, CENTER_Y, view_angle=0.0,
                             fov=math.pi / 2, num_columns=5, max_depth=20)
    assert len(hits) == 5
    # The center column should point straight ahead (angle 0 -> due east).
    assert hits[2].wall_x == pytest.approx(0.5, abs=1e-6)


def test_cast_column_rays_handles_zero_columns():
    assert cast_column_rays(ROOM, CENTER_X, CENTER_Y, 0.0, math.pi / 3, 0, 20) == []
