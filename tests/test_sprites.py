import math

import pytest

from game.enemy import Enemy
from game.player import Player
from game.sprites import project_sprite

RENDER_WIDTH = 320
RENDER_HEIGHT = 200
FOV = math.pi / 3


def test_enemy_straight_ahead_projects_to_screen_center():
    player = Player(0, 0, angle=0.0, radius=0.2)
    enemy = Enemy(5, 0, health=1, radius=0.3)
    projection = project_sprite(player, enemy, FOV, RENDER_WIDTH, RENDER_HEIGHT)
    assert projection is not None
    assert projection.screen_x == pytest.approx(RENDER_WIDTH / 2, abs=1e-6)
    assert projection.distance == pytest.approx(5.0)
    assert projection.half_width == pytest.approx((RENDER_HEIGHT / 5.0) / 2)


def test_enemy_behind_player_is_not_visible():
    player = Player(0, 0, angle=0.0, radius=0.2)
    enemy = Enemy(-5, 0, health=1, radius=0.3)
    assert project_sprite(player, enemy, FOV, RENDER_WIDTH, RENDER_HEIGHT) is None


def test_enemy_at_same_position_as_player_is_not_visible():
    player = Player(1, 1, angle=0.0, radius=0.2)
    enemy = Enemy(1, 1, health=1, radius=0.3)
    assert project_sprite(player, enemy, FOV, RENDER_WIDTH, RENDER_HEIGHT) is None


def test_closer_enemy_projects_larger_than_farther_enemy():
    player = Player(0, 0, angle=0.0, radius=0.2)
    near = Enemy(2, 0, health=1, radius=0.3)
    far = Enemy(8, 0, health=1, radius=0.3)
    near_proj = project_sprite(player, near, FOV, RENDER_WIDTH, RENDER_HEIGHT)
    far_proj = project_sprite(player, far, FOV, RENDER_WIDTH, RENDER_HEIGHT)
    assert near_proj.half_width > far_proj.half_width


def test_enemy_to_the_side_shifts_screen_x_away_from_center():
    player = Player(0, 0, angle=0.0, radius=0.2)
    enemy = Enemy(5, 2, health=1, radius=0.3)  # up and to the "left" in angle terms
    projection = project_sprite(player, enemy, FOV, RENDER_WIDTH, RENDER_HEIGHT)
    assert projection is not None
    assert projection.screen_x != pytest.approx(RENDER_WIDTH / 2)
