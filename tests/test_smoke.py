"""Headless integration smoke test: spins up the real Game/Renderer stack
(against pygame's SDL "dummy" driver, set in conftest.py) and drives it for
several frames, exercising raycasting + wall rendering + sprite rendering +
shooting together. This is the test most likely to catch a wiring mistake
that the isolated unit tests can't see (wrong argument order, mismatched
coordinate conventions between modules, etc).
"""

import math

import pygame
import pytest

from game import settings
from game.game import AMMO_START, Game


@pytest.fixture
def game():
    pygame.init()
    screen = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
    g = Game(screen)
    yield g
    pygame.quit()


def test_game_runs_several_frames_without_crashing(game):
    for _ in range(30):
        game.update(dt=1 / 60, keys=None, mouse_dx=0)
        game.render()


def test_shooting_an_enemy_directly_ahead_damages_it(game):
    target = game.enemies[0]
    game.player.x, game.player.y = target.x - 3, target.y
    game.player.angle = math.atan2(target.y - game.player.y, target.x - game.player.x)

    starting_health = target.health
    fired = game.handle_shoot()

    assert fired is True
    assert game.ammo == AMMO_START - 1
    assert target.health == starting_health - settings.WEAPON_DAMAGE


def test_shot_blocked_by_wall_does_not_damage_enemy(game):
    # enemies[1] sits south of a 2x2 wall block in the map, so firing at it
    # from just above that block should be blocked.
    target = game.enemies[1]
    game.player.x, game.player.y = 5.5, 3.5
    game.player.angle = math.atan2(target.y - game.player.y, target.x - game.player.x)

    # Sanity check the fixture premise: confirm a wall really is in the way.
    from game.raycasting import cast_ray
    wall_hit = cast_ray(game.game_map, game.player.x, game.player.y, game.player.angle,
                         settings.WEAPON_RANGE)
    target_distance = target.distance_to(game.player.x, game.player.y)
    assert wall_hit.tile_id != 0 and wall_hit.distance < target_distance - 0.1

    starting_health = target.health
    game.handle_shoot()
    assert target.health == starting_health


def test_running_out_of_ammo_stops_firing(game):
    game.ammo = 0
    assert game.handle_shoot() is False


def test_weapon_cooldown_prevents_rapid_refire(game):
    target = game.enemies[0]
    game.player.x, game.player.y = target.x - 3, target.y
    game.player.angle = math.atan2(target.y - game.player.y, target.x - game.player.x)

    assert game.handle_shoot() is True
    assert game.handle_shoot() is False  # still on cooldown
