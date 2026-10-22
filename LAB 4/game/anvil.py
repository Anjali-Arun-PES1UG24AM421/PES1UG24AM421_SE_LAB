import random
import pygame

# Speed tiers (pixels per frame) for warning tints (Task 3)
ORANGE_SPEED = 6.0   # fast
RED_SPEED = 8.5      # very fast / urgent


class Anvil:
    def __init__(self, screen_width, speed_multiplier=1.0):
        self.screen_width = screen_width
        self.width = 40
        self.height = 32
        self.x = random.randint(20, screen_width - self.width - 20)
        self.y = -self.height
        self.speed = random.uniform(4.5, 7.0) * speed_multiplier

    def update(self):
        self.y += self.speed

    def is_off_screen(self, screen_height):
        return self.y > screen_height + 10

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def tier_colors(self):
        """Return (top, base, outline) colours based on how fast this anvil is."""
        if self.speed >= RED_SPEED:
            return (255, 110, 90), (200, 35, 35), (255, 170, 150)
        if self.speed >= ORANGE_SPEED:
            return (255, 190, 90), (220, 110, 30), (255, 220, 160)
        return (120, 120, 130), (80, 80, 90), (200, 200, 210)

    def render(self, surface):
        top_c, base_c, outline_c = self.tier_colors()

        top_rect = pygame.Rect(int(self.x) + 4, int(self.y), self.width - 8, 14)
        pygame.draw.rect(surface, top_c, top_rect, border_radius=2)

        base_rect = pygame.Rect(int(self.x), int(self.y) + 14, self.width, 18)
        pygame.draw.rect(surface, base_c, base_rect, border_radius=3)
        pygame.draw.rect(surface, outline_c, base_rect, width=1, border_radius=3)
