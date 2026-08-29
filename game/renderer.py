"""All pygame drawing lives here. Everything this module depends on
(raycast hits, sprite projections) is produced by pure, independently
tested functions elsewhere in `game/`.
"""

from __future__ import annotations

import math

import pygame

from game.enemy import HIT_FLASH_DURATION, Enemy
from game.player import Player
from game.raycasting import RayHit
from game.sprites import project_sprite
from game.textures import TEXTURE_SIZE

CEILING_TOP_COLOR = (22, 22, 38)
CEILING_HORIZON_COLOR = (52, 52, 78)
FLOOR_HORIZON_COLOR = (68, 68, 68)
FLOOR_BOTTOM_COLOR = (32, 32, 32)
BACKGROUND_BANDS = 8

ENEMY_COLOR = (220, 90, 220)  # violet, contrasts against all wall palettes
ENEMY_CORE_COLOR = (255, 250, 220)  # bright "molten core" highlight on each enemy
ENEMY_HIT_FLASH_COLOR = (255, 255, 255)
HUD_TEXT_COLOR = (240, 240, 240)
HUD_PANEL_COLOR = (15, 15, 20)
CROSSHAIR_COLOR = (255, 140, 0)  # molten orange, matches Ray's disk caster

WEAPON_RING_COLOR = (110, 45, 10)
WEAPON_GLOW_COLOR = (255, 150, 40)
WEAPON_CORE_COLOR = (255, 140, 30)
WEAPON_FLASH_CORE_COLOR = (255, 235, 190)
WEAPON_BASE_RADIUS = 34
MUZZLE_FLASH_DURATION = 0.12

MAX_SHADE_DISTANCE = 12.0


def _shade_for_distance(color: tuple, distance: float, side: int) -> tuple:
    fog = max(0.25, 1.0 - min(distance, MAX_SHADE_DISTANCE) / MAX_SHADE_DISTANCE)
    side_factor = 0.75 if side == 1 else 1.0
    factor = fog * side_factor
    return tuple(max(0, min(255, int(c * factor))) for c in color)


def _lerp_color(a: tuple, b: tuple, t: float) -> tuple:
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


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
                   fov: float, ammo: int, weapon_flash_elapsed: float = math.inf) -> None:
        surface = self.render_surface
        self._draw_background(surface)

        depth_buffer = self._draw_walls(surface, wall_hits)
        self._draw_enemies(surface, enemies, player, fov, depth_buffer)
        self._draw_weapon(surface, weapon_flash_elapsed)
        self._draw_crosshair(surface)

        pygame.transform.scale(surface, self.screen.get_size(), self.screen)
        self._draw_hud(player, ammo, enemies)
        pygame.display.flip()

    def _draw_background(self, surface: pygame.Surface) -> None:
        half_h = self.render_height // 2
        band_height = max(1, half_h // BACKGROUND_BANDS)

        for i in range(BACKGROUND_BANDS):
            t = i / (BACKGROUND_BANDS - 1)
            y0 = i * band_height
            y1 = half_h if i == BACKGROUND_BANDS - 1 else y0 + band_height
            color = _lerp_color(CEILING_TOP_COLOR, CEILING_HORIZON_COLOR, t)
            surface.fill(color, pygame.Rect(0, y0, self.render_width, y1 - y0))

        floor_height = self.render_height - half_h
        band_height = max(1, floor_height // BACKGROUND_BANDS)
        for i in range(BACKGROUND_BANDS):
            t = i / (BACKGROUND_BANDS - 1)
            y0 = half_h + i * band_height
            y1 = self.render_height if i == BACKGROUND_BANDS - 1 else y0 + band_height
            color = _lerp_color(FLOOR_HORIZON_COLOR, FLOOR_BOTTOM_COLOR, t)
            surface.fill(color, pygame.Rect(0, y0, self.render_width, y1 - y0))

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
            if enemy.hit_flash_timer > 0:
                flash_t = enemy.hit_flash_timer / HIT_FLASH_DURATION
                color = _lerp_color(color, ENEMY_HIT_FLASH_COLOR, flash_t)
            center_y = self.render_height // 2

            center_col = int(round(projection.screen_x))
            center_visible = (0 <= center_col < self.render_width
                               and projection.distance < depth_buffer[center_col])

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

            if center_visible:
                # A small bright "molten core" so sprites read as glowing
                # creatures rather than flat silhouettes.
                core_color = _shade_for_distance(ENEMY_CORE_COLOR, projection.distance, side=0)
                core_radius = max(1, int(half * 0.25))
                core_pos = (center_col, int(center_y - half * 0.3))
                pygame.draw.circle(surface, core_color, core_pos, core_radius)

    def _draw_weapon(self, surface: pygame.Surface, flash_elapsed: float) -> None:
        flash_t = max(0.0, 1.0 - flash_elapsed / MUZZLE_FLASH_DURATION) if flash_elapsed < MUZZLE_FLASH_DURATION else 0.0
        recoil = int(14 * flash_t)
        radius = WEAPON_BASE_RADIUS + int(6 * flash_t)

        cx = self.render_width // 2
        cy = self.render_height + 8 - recoil  # mostly off-screen; only the top cap pokes up

        pygame.draw.circle(surface, WEAPON_RING_COLOR, (cx, cy), radius + 5)
        pygame.draw.circle(surface, WEAPON_GLOW_COLOR, (cx, cy), radius)
        core_color = _lerp_color(WEAPON_CORE_COLOR, WEAPON_FLASH_CORE_COLOR, flash_t)
        pygame.draw.circle(surface, core_color, (cx, cy), max(2, radius - 10))

        if flash_t > 0:
            flash_radius = int(26 * flash_t)
            flash_pos = (cx, self.render_height // 2 + 14)
            flash_surface = pygame.Surface((flash_radius * 2, flash_radius * 2), pygame.SRCALPHA)
            alpha = int(200 * flash_t)
            pygame.draw.circle(flash_surface, (*WEAPON_FLASH_CORE_COLOR, alpha), (flash_radius, flash_radius), flash_radius)
            surface.blit(flash_surface, (flash_pos[0] - flash_radius, flash_pos[1] - flash_radius))

    def _draw_crosshair(self, surface: pygame.Surface) -> None:
        cx, cy = self.render_width // 2, self.render_height // 2
        pygame.draw.line(surface, CROSSHAIR_COLOR, (cx - 5, cy), (cx + 5, cy))
        pygame.draw.line(surface, CROSSHAIR_COLOR, (cx, cy - 5), (cx, cy + 5))

    def _draw_hud(self, player: Player, ammo: int, enemies: list[Enemy]) -> None:
        remaining = sum(1 for e in enemies if e.is_alive)
        text = f"HP: {player.health}   Disks: {ammo}   Enemies left: {remaining}"
        text_surface = self.font.render(text, True, HUD_TEXT_COLOR)

        panel_height = 34
        panel = pygame.Surface((self.screen.get_width(), panel_height), pygame.SRCALPHA)
        panel.fill((*HUD_PANEL_COLOR, 160))
        self.screen.blit(panel, (0, self.screen.get_height() - panel_height))
        self.screen.blit(text_surface, (10, self.screen.get_height() - panel_height + 6))
