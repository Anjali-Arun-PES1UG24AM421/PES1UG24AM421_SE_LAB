import random
import pygame


class Anvil:
    # --- Warning tint tiers (by speed in px/frame) ---
    FAST_SPEED = 7.0        # at or above this: orange "fast" tier
    VERY_FAST_SPEED = 9.0   # at or above this: red "very fast" tier

    # (top face, base body, outline) colors for each tier
    COLORS_NORMAL = ((120, 120, 130), (80, 80, 90), (200, 200, 210))
    COLORS_FAST = ((255, 150, 50), (200, 100, 30), (255, 200, 120))
    COLORS_VERY_FAST = ((240, 70, 60), (170, 35, 35), (255, 140, 130))

    def __init__(self, screen_width, speed_multiplier=1.0):
        self.screen_width = screen_width
        self.width = 40
        self.height = 32
        self.x = random.randint(20, screen_width - self.width - 20)
        self.y = -self.height
        # Base speed is randomized, then scaled by the current difficulty.
        self.speed = random.uniform(4.5, 7.0) * speed_multiplier

    def update(self):
        self.y += self.speed

    def is_off_screen(self, screen_height):
        return self.y > screen_height + 10

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def _tier_colors(self):
        """Pick the (top, base, outline) colors for this anvil's speed tier."""
        if self.speed >= self.VERY_FAST_SPEED:
            return self.COLORS_VERY_FAST
        if self.speed >= self.FAST_SPEED:
            return self.COLORS_FAST
        return self.COLORS_NORMAL

    def render(self, surface):
        top_color, base_color, outline_color = self._tier_colors()

        top_rect = pygame.Rect(int(self.x) + 4, int(self.y), self.width - 8, 14)
        pygame.draw.rect(surface, top_color, top_rect, border_radius=2)

        base_rect = pygame.Rect(int(self.x), int(self.y) + 14, self.width, 18)
        pygame.draw.rect(surface, base_color, base_rect, border_radius=3)
        pygame.draw.rect(surface, outline_color, base_rect, width=1, border_radius=3)
