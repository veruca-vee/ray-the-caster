#!/usr/bin/env python3
import pygame

from game import settings
from game.game import Game


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
    pygame.display.set_caption("RAY THE CASTER")

    game = Game(screen)
    try:
        game.run()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
