from __future__ import annotations

import math

import pygame

from game import settings
from game.enemy import Enemy, find_closest_hit_enemy
from game.game_map import GameMap
from game.player import Player
from game.raycasting import cast_column_rays, cast_ray
from game.renderer import Renderer
from game.textures import build_textures

AMMO_START = 50


class Game:
    """Owns all game state and the frame loop. `run()` is the only method
    that touches the real display/clock/event queue, which keeps everything
    else here testable by calling update()/handle_shoot() directly.
    """

    def __init__(self, screen: pygame.Surface):
        self.game_map = GameMap(settings.GAME_MAP)
        self.player = Player(
            settings.PLAYER_START_X, settings.PLAYER_START_Y,
            settings.PLAYER_START_ANGLE, settings.PLAYER_RADIUS,
        )
        self.enemies = [
            Enemy(x, y, settings.ENEMY_HEALTH, settings.ENEMY_RADIUS)
            for x, y in settings.ENEMY_START_POSITIONS
        ]
        self.ammo = AMMO_START
        self.shot_cooldown_remaining = 0.0
        self.renderer = Renderer(screen, settings.RENDER_WIDTH, settings.RENDER_HEIGHT,
                                  build_textures())

    def update(self, dt: float, keys: pygame.key.ScancodeWrapper | None = None,
               mouse_dx: int = 0) -> None:
        self.shot_cooldown_remaining = max(0.0, self.shot_cooldown_remaining - dt)
        self.player.rotate(mouse_dx * settings.MOUSE_SENSITIVITY)

        for enemy in self.enemies:
            enemy.tick(dt)

        if keys is not None:
            if keys[pygame.K_LEFT]:
                self.player.rotate(-settings.ROTATE_SPEED * dt)
            if keys[pygame.K_RIGHT]:
                self.player.rotate(settings.ROTATE_SPEED * dt)

            move = settings.MOVE_SPEED * dt
            if keys[pygame.K_w]:
                self.player.move_forward(self.game_map, move)
            if keys[pygame.K_s]:
                self.player.move_forward(self.game_map, -move)
            if keys[pygame.K_a]:
                self.player.strafe(self.game_map, -move)
            if keys[pygame.K_d]:
                self.player.strafe(self.game_map, move)

    def handle_shoot(self) -> bool:
        """Fires the weapon if possible. Returns True if a shot was fired
        (regardless of whether it hit anything)."""
        if self.ammo <= 0 or self.shot_cooldown_remaining > 0:
            return False

        self.ammo -= 1
        self.shot_cooldown_remaining = settings.WEAPON_COOLDOWN

        target = find_closest_hit_enemy(
            self.enemies, self.player.x, self.player.y, self.player.angle,
            settings.WEAPON_RANGE,
        )
        if target is None:
            return True

        angle_to_target = math.atan2(target.y - self.player.y, target.x - self.player.x)
        wall_hit = cast_ray(self.game_map, self.player.x, self.player.y,
                             angle_to_target, settings.WEAPON_RANGE)
        target_distance = target.distance_to(self.player.x, self.player.y)
        blocked_by_wall = wall_hit.tile_id != 0 and wall_hit.distance < target_distance - 0.1
        if not blocked_by_wall:
            target.take_damage(settings.WEAPON_DAMAGE)
        return True

    def render(self) -> None:
        wall_hits = cast_column_rays(
            self.game_map, self.player.x, self.player.y, self.player.angle,
            settings.FOV, settings.RENDER_WIDTH, settings.MAX_DEPTH,
        )
        weapon_flash_elapsed = settings.WEAPON_COOLDOWN - self.shot_cooldown_remaining
        self.renderer.draw_frame(wall_hits, self.enemies, self.player, settings.FOV, self.ammo,
                                  weapon_flash_elapsed)

    def run(self) -> None:
        clock = pygame.time.Clock()
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        pygame.mouse.get_rel()  # discard any accumulated motion before the loop starts

        running = True
        while running:
            dt = clock.tick(settings.FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self.handle_shoot()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_shoot()

            mouse_dx, _ = pygame.mouse.get_rel()
            self.update(dt, pygame.key.get_pressed(), mouse_dx)
            self.render()

            if not self.player.is_alive:
                running = False
