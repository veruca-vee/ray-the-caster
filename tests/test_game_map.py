import pytest

from game.game_map import GameMap


def make_map():
    return GameMap([
        [1, 1, 1],
        [1, 0, 1],
        [1, 1, 1],
    ])


def test_is_wall_true_for_solid_cell():
    m = make_map()
    assert m.is_wall(0, 0) is True


def test_is_wall_false_for_empty_cell():
    m = make_map()
    assert m.is_wall(1, 1) is False


def test_out_of_bounds_counts_as_solid():
    m = make_map()
    assert m.is_wall(-1, 0) is True
    assert m.is_wall(0, -1) is True
    assert m.is_wall(m.width, 0) is True
    assert m.is_wall(0, m.height) is True


def test_is_wall_at_uses_floor_of_coordinates():
    m = make_map()
    assert m.is_wall_at(1.9, 1.9) is False
    assert m.is_wall_at(0.5, 0.5) is True


def test_ragged_rows_rejected():
    with pytest.raises(ValueError):
        GameMap([[1, 1, 1], [1, 0]])


def test_empty_grid_rejected():
    with pytest.raises(ValueError):
        GameMap([])
