"""All pygame drawing lives here. Everything this module depends on
(raycast hits, sprite projections) is produced by pure, independently
tested functions elsewhere in `game/`.
"""

from __future__ import annotations

import math

import pygame

from game.enemy import Enemy
from game.player import Player
from game.raycasting import RayHit
from game.sprites import project_sprite
from game.textures import TEXTURE_SIZE

CEILING_COLOR = (40, 40, 60)
FLOOR_COLOR = (55, 55, 55)
ENEMY_COLOR = (220, 90, 220)  # violet, contrasts against all wall palettes
ENEMY_HIT_FLASH_COLOR = (255, 220, 220)
HUD_TEXT_COLOR = (240, 240, 240)
CROSSHAIR_COLOR = (255, 140, 0)  # molten orange, matches Ray's disk caster

MAX_SHADE_DISTANCE = 12.0


def _shade_for_distance(color: tuple, distance: float, side: int) -> tuple:
    fog = max(0.25, 1.0 - min(distance, MAX_SHADE_DISTANCE) / MAX_SHADE_DISTANCE)
    side_factor = 0.75 if side == 1 else 1.0
    factor = fog * side_factor
    return tuple(max(0, min(255, int(c * factor))) for c in color)


class Renderer:
    def __init__(self, screen: pygame.Surface, render_width: int, render_height: int,
                 textures: dict[int, pygame.Surface]):
        self.screen = screen
        self.render_width = render_width
        self.render_height = render_height
        self.textures = textures
        self.render_surface = pygame.Surface((render_width, render_height)).convert()
        self.font = pygame.font.SysFont(None, 24)

    def draw_frame(self, wall_hits: list[RayHit], enemies: list[Enemy], player: Player,
                   fov: float, ammo: int) -> None:
        surface = self.render_surface
        half_h = self.render_height // 2

        surface.fill(CEILING_COLOR, pygame.Rect(0, 0, self.render_width, half_h))
        surface.fill(FLOOR_COLOR, pygame.Rect(0, half_h, self.render_width, self.render_height - half_h))

        depth_buffer = self._draw_walls(surface, wall_hits)
        self._draw_enemies(surface, enemies, player, fov, depth_buffer)
        self._draw_crosshair(surface)

        pygame.transform.scale(surface, self.screen.get_size(), self.screen)
        self._draw_hud(player, ammo, enemies)
        pygame.display.flip()

    def _draw_walls(self, surface: pygame.Surface, wall_hits: list[RayHit]) -> list[float]:
        depth_buffer = [math.inf] * len(wall_hits)
        for col, hit in enumerate(wall_hits):
            depth_buffer[col] = hit.distance
            if hit.tile_id == 0:
                continue

            line_height = int(self.render_height / hit.distance)
            line_height = min(line_height, self.render_height * 8)
            draw_start = max(0, self.render_height // 2 - line_height // 2)
            draw_end = min(self.render_height, self.render_height // 2 + line_height // 2)
            if draw_end <= draw_start:
                continue

            texture = self.textures.get(hit.tile_id) or self.textures[0]
            tex_x = int(hit.wall_x * TEXTURE_SIZE)
            tex_x = min(max(tex_x, 0), TEXTURE_SIZE - 1)

            column = texture.subsurface((tex_x, 0, 1, TEXTURE_SIZE))
            column = pygame.transform.scale(column, (1, draw_end - draw_start))
            shade = _shade_for_distance((255, 255, 255), hit.distance, hit.side)
            column.fill(shade, special_flags=pygame.BLEND_RGB_MULT)
            surface.blit(column, (col, draw_start))
        return depth_buffer

    def _draw_enemies(self, surface: pygame.Surface, enemies: list[Enemy], player: Player,
                       fov: float, depth_buffer: list[float]) -> None:
        living = [e for e in enemies if e.is_alive]
        living.sort(key=lambda e: e.distance_to(player.x, player.y), reverse=True)

        for enemy in living:
            projection = project_sprite(player, enemy, fov, self.render_width, self.render_height)
            if projection is None or projection.half_width <= 0:
                continue

            half = projection.half_width
            col_start = max(0, int(projection.screen_x - half))
            col_end = min(self.render_width - 1, int(projection.screen_x + half))
            if col_start > col_end:
                continue

            color = _shade_for_distance(ENEMY_COLOR, projection.distance, side=0)
            center_y = self.render_height // 2

            for col in range(col_start, col_end + 1):
                if projection.distance >= depth_buffer[col]:
                    continue
                nx = (col - projection.screen_x) / half
                if nx * nx > 1:
                    continue
                column_half_height = half * math.sqrt(max(0.0, 1 - nx * nx))
                pygame.draw.line(
                    surface, color,
                    (col, center_y - column_half_height),
                    (col, center_y + column_half_height),
                )

    def _draw_crosshair(self, surface: pygame.Surface) -> None:
        cx, cy = self.render_width // 2, self.render_height // 2
        pygame.draw.line(surface, CROSSHAIR_COLOR, (cx - 5, cy), (cx + 5, cy))
        pygame.draw.line(surface, CROSSHAIR_COLOR, (cx, cy - 5), (cx, cy + 5))

    def _draw_hud(self, player: Player, ammo: int, enemies: list[Enemy]) -> None:
        remaining = sum(1 for e in enemies if e.is_alive)
        text = f"HP: {player.health}   Disks: {ammo}   Enemies left: {remaining}"
        text_surface = self.font.render(text, True, HUD_TEXT_COLOR)
        self.screen.blit(text_surface, (10, self.screen.get_height() - 30))
