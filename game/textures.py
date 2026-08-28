"""Procedural wall textures, so the project needs no external image assets.

Each texture is a small pygame.Surface with a distinct pattern per tile id,
generated once at startup and sampled by column in the renderer.
"""

from __future__ import annotations

import pygame

TEXTURE_SIZE = 64

# tile id -> (base_color, mortar_color)
_TILE_PALETTE = {
    1: ((150, 60, 60), (90, 30, 30)),    # red brick
    2: ((70, 110, 160), (40, 70, 110)),  # blue stone
    3: ((110, 140, 70), (70, 95, 40)),   # green panel
}
_DEFAULT_PALETTE = ((120, 120, 120), (70, 70, 70))


def _brick_pattern(surface: pygame.Surface, base: tuple, mortar: tuple) -> None:
    surface.fill(mortar)
    brick_w, brick_h = 16, 8
    for row, y in enumerate(range(0, TEXTURE_SIZE, brick_h)):
        offset = (brick_w // 2) if row % 2 else 0
        for x in range(-offset, TEXTURE_SIZE, brick_w):
            rect = pygame.Rect(x + 1, y + 1, brick_w - 2, brick_h - 2)
            pygame.draw.rect(surface, base, rect)


def build_textures() -> dict[int, pygame.Surface]:
    """Builds one Surface per known tile id. Requires pygame's video system
    to be initialized (even with the dummy driver) since it creates Surfaces."""
    textures: dict[int, pygame.Surface] = {}
    all_ids = set(_TILE_PALETTE) | {0}
    for tile_id in all_ids:
        base, mortar = _TILE_PALETTE.get(tile_id, _DEFAULT_PALETTE)
        surface = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE)).convert()
        _brick_pattern(surface, base, mortar)
        textures[tile_id] = surface
    return textures
