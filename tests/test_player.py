import math

import pytest

from game.game_map import GameMap
from game.player import Player

OPEN_ROOM = GameMap([
    [1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1],
])


def make_player(x=2.5, y=2.5, angle=0.0):
    return Player(x, y, angle, radius=0.2)


def test_rotate_wraps_into_0_to_2pi():
    p = make_player(angle=0.1)
    p.rotate(-1.0)
    assert 0 <= p.angle < 2 * math.pi
    assert p.angle == pytest.approx((0.1 - 1.0) % (2 * math.pi))


def test_move_forward_in_open_space_moves_player():
    p = make_player()
    p.move_forward(OPEN_ROOM, 0.5)
    assert p.x == pytest.approx(3.0)
    assert p.y == pytest.approx(2.5)


def test_move_forward_into_wall_is_blocked():
    p = make_player(x=3.7, y=2.5)  # close to the east wall at x=4
    p.move_forward(OPEN_ROOM, 1.0)
    assert p.x == pytest.approx(3.7)  # blocked entirely, did not tunnel through


def test_movement_slides_along_wall_on_the_open_axis():
    # Push diagonally into a wall on the x-axis; y-axis movement should
    # still succeed even though x is blocked.
    p = make_player(x=3.75, y=2.5)
    p.try_move(OPEN_ROOM, dx=1.0, dy=0.3)
    assert p.y == pytest.approx(2.8)


def test_strafe_moves_perpendicular_to_facing_direction():
    p = make_player(angle=0.0)  # facing +x, so strafe moves along +/-y
    p.strafe(OPEN_ROOM, 0.5)
    assert p.x == pytest.approx(2.5, abs=1e-6)
    assert p.y == pytest.approx(3.0, abs=1e-6)


def test_take_damage_clamped_at_zero_and_marks_dead():
    p = make_player()
    p.take_damage(10_000)
    assert p.health == 0
    assert p.is_alive is False
