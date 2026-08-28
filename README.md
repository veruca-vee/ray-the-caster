# RAY THE CASTER

A minimal Wolfenstein-3D-style raycaster built with Python + Pygame. You
play as Ray, armed with a molten disk caster, in a grid-DDA raycasting
engine with textured walls, WASD + mouse-look movement, and billboarded
enemy sprites that take damage and die.

No external art assets — wall textures are generated procedurally at
startup, and enemies render as simple shaded, occluded circular sprites.

## Requirements

- Python 3.11+
- SDL2 (installed automatically as part of the `pygame` wheel on most
  platforms)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python3 main.py
```

**Controls**

| Key | Action |
| --- | --- |
| `W` / `S` | Move forward / backward |
| `A` / `D` | Strafe left / right |
| Mouse / Left / Right arrows | Look / turn |
| Left click / Space | Cast disk |
| Esc | Quit |

The mouse is captured for look control while the window is focused.

## Development

```bash
pip install -r requirements-dev.txt
pytest
```

All raycasting, movement, collision, and combat logic lives in pure
Python modules under `game/` with no pygame dependency, so it's unit
tested directly. A separate headless smoke test (`tests/test_smoke.py`)
drives the full `Game` loop — rendering included — against SDL's `dummy`
video driver, so the whole stack is exercised in CI without a display.

## Project layout

```
game/
  settings.py     constants + the map layout
  game_map.py     grid lookup helpers (pure)
  raycasting.py   grid-DDA ray casting (pure)
  player.py       movement + collision (pure)
  enemy.py        enemy state + hitscan target selection (pure)
  sprites.py      enemy screen-space projection (pure)
  textures.py     procedural wall textures (pygame)
  renderer.py     drawing: walls, sprites, HUD (pygame)
  game.py         wires it all together + the frame loop (pygame)
main.py           entry point
tests/            pytest suite (unit tests + headless smoke test)
```

## Known limitations

This is intentionally a *minimal* raycaster, not a full game:

- Enemies are static targets — they don't move or attack back.
- No recharge; disks are a fixed pool for the session.
- Sprite occlusion is per-column against the wall depth buffer, but sprite
  distance itself is euclidean rather than perpendicular, so there's minor
  fisheye distortion at the very edge of sprites near the edge of the FOV.
