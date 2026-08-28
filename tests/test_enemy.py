import math

import pytest

from game.enemy import Enemy, find_closest_hit_enemy


def test_take_damage_reduces_health():
    e = Enemy(0, 0, health=3, radius=0.3)
    e.take_damage(1)
    assert e.health == 2
    assert e.is_alive is True


def test_take_damage_kills_at_zero():
    e = Enemy(0, 0, health=3, radius=0.3)
    e.take_damage(3)
    assert e.health == 0
    assert e.is_alive is False


def test_take_damage_does_not_go_negative():
    e = Enemy(0, 0, health=3, radius=0.3)
    e.take_damage(999)
    assert e.health == 0


def test_dead_enemy_ignores_further_damage():
    e = Enemy(0, 0, health=1, radius=0.3)
    e.take_damage(1)
    e.take_damage(1)
    assert e.health == 0


def test_distance_to_uses_euclidean_distance():
    e = Enemy(3, 4, health=1, radius=0.3)
    assert e.distance_to(0, 0) == pytest.approx(5.0)


def test_find_closest_hit_enemy_picks_nearest_in_cone():
    near = Enemy(2, 0, health=1, radius=0.3)
    far = Enemy(5, 0, health=1, radius=0.3)
    result = find_closest_hit_enemy([far, near], shooter_x=0, shooter_y=0,
                                     shooter_angle=0.0, max_range=10)
    assert result is near


def test_find_closest_hit_enemy_ignores_dead_enemies():
    dead = Enemy(1, 0, health=0, radius=0.3)
    result = find_closest_hit_enemy([dead], shooter_x=0, shooter_y=0,
                                     shooter_angle=0.0, max_range=10)
    assert result is None


def test_find_closest_hit_enemy_ignores_out_of_cone():
    behind = Enemy(-2, 0, health=1, radius=0.3)  # directly behind the shooter
    result = find_closest_hit_enemy([behind], shooter_x=0, shooter_y=0,
                                     shooter_angle=0.0, max_range=10)
    assert result is None


def test_find_closest_hit_enemy_respects_max_range():
    too_far = Enemy(100, 0, health=1, radius=0.3)
    result = find_closest_hit_enemy([too_far], shooter_x=0, shooter_y=0,
                                     shooter_angle=0.0, max_range=10)
    assert result is None
