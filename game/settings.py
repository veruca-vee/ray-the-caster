import math

# Window / render resolution. Internal render width is lower than the window
# and scaled up, which keeps the pure-Python per-column raycast loop fast.
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 600
RENDER_WIDTH = 320
RENDER_HEIGHT = 200
FPS = 60

FOV = math.pi / 3  # 60 degrees
MAX_DEPTH = 20.0

MOVE_SPEED = 3.0  # tiles per second
ROTATE_SPEED = 2.5  # radians per second (keyboard rotation)
MOUSE_SENSITIVITY = 0.0025  # radians per pixel of mouse motion

PLAYER_RADIUS = 0.2  # for wall collision

WEAPON_COOLDOWN = 0.35  # seconds between shots
WEAPON_RANGE = MAX_DEPTH
WEAPON_DAMAGE = 1

ENEMY_HEALTH = 3
ENEMY_RADIUS = 0.3

# 1 = wall, 0 = empty. Outer border must be solid so rays always terminate.
GAME_MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 2, 2, 0, 0, 0, 0, 1, 1, 0, 1],
    [1, 0, 2, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 3, 3, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 3, 3, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 0, 0, 0, 0, 2, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 2, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

PLAYER_START_X = 2.5
PLAYER_START_Y = 1.5
PLAYER_START_ANGLE = 0.0

ENEMY_START_POSITIONS = [
    (8.5, 1.5),
    (5.5, 7.5),
    (9.5, 8.5),
]
