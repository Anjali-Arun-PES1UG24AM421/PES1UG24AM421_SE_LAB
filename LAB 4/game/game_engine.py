import random
import pygame
from game.player import Player
from game.anvil import Anvil

# Difficulty scaling settings (Task 2)
BASE_SPAWN_DELAY = 700      # ms between anvils at the start
MIN_SPAWN_DELAY = 260       # fastest allowed spawn rate
SPAWN_DECAY_PER_SEC = 8     # ms removed from the delay each second survived
SPEED_GROWTH_PER_SEC = 0.02 # speed multiplier gained each second survived
MAX_SPEED_MULT = 1.8        # cap so the game stays fair

# Impact FX settings (Task 4)
BG_COLOR = (35, 38, 45)
DUST_COLOR = (170, 160, 145)
SHAKE_FRAMES = 10
SHAKE_STRENGTH = 5
DUST_PER_IMPACT = 12


class DustParticle:
    """A small puff of dust that flies up, falls back and fades out."""

    def __init__(self, x, ground_y):
        self.ground_y = ground_y
        self.x = x + random.uniform(-14, 14)
        self.y = ground_y - 2
        self.vx = random.uniform(-2.8, 2.8)
        self.vy = random.uniform(-3.6, -0.8)
        self.radius = random.uniform(3, 6)
        self.max_life = random.randint(22, 38)
        self.life = self.max_life

    @property
    def alive(self):
        return self.life > 0

    def update(self):
        self.x += self.vx
        self.y = min(self.y + self.vy, self.ground_y - 1)
        self.vy += 0.18
        self.vx *= 0.97
        self.life -= 1

    def render(self, surface):
        t = max(0.0, self.life / self.max_life)
        color = tuple(int(b + (d - b) * t) for b, d in zip(BG_COLOR, DUST_COLOR))
        radius = max(1, int(self.radius * (0.4 + 0.6 * t)))
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), radius)


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.player = Player(width, height)
        self.anvils = []

        self.spawn_delay = BASE_SPAWN_DELAY
        self.speed_multiplier = 1.0
        self.last_spawn_time = pygame.time.get_ticks()

        self.start_ticks = pygame.time.get_ticks()
        self.survival_time = 0
        self.game_state = "PLAYING"

        # Impact FX state (Task 4)
        self.particles = []
        self.shake_frames = 0
        self.shake_offset = (0, 0)
        self.canvas = pygame.Surface((width, height))

        self.font_big = pygame.font.SysFont(None, 52)
        self.font_medium = pygame.font.SysFont(None, 34)
        self.font_small = pygame.font.SysFont(None, 24)

    def handle_event(self, event):
        if self.game_state == "GAME_OVER":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()

    def _update_difficulty(self, elapsed_sec):
        self.spawn_delay = max(MIN_SPAWN_DELAY, BASE_SPAWN_DELAY - SPAWN_DECAY_PER_SEC * elapsed_sec)
        self.speed_multiplier = min(MAX_SPEED_MULT, 1.0 + SPEED_GROWTH_PER_SEC * elapsed_sec)

    def _spawn_impact(self, anvil):
        ground_y = self.height - 20
        cx = anvil.x + anvil.width / 2
        for _ in range(DUST_PER_IMPACT):
            self.particles.append(DustParticle(cx, ground_y))
        self.shake_frames = SHAKE_FRAMES

    def _update_effects(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.alive]

        if self.shake_frames > 0:
            strength = max(1, int(SHAKE_STRENGTH * self.shake_frames / SHAKE_FRAMES))
            self.shake_offset = (random.randint(-strength, strength), random.randint(-strength, strength))
            self.shake_frames -= 1
        else:
            self.shake_offset = (0, 0)

    def update(self):
        # Effects keep animating even on the Game Over screen
        self._update_effects()

        if self.game_state != "PLAYING":
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move_left()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move_right()

        self.player.update()

        now = pygame.time.get_ticks()
        elapsed_ms = now - self.start_ticks
        self.survival_time = elapsed_ms // 1000
        self._update_difficulty(elapsed_ms / 1000)

        if now - self.last_spawn_time >= self.spawn_delay:
            self.anvils.append(Anvil(self.width, self.speed_multiplier))
            self.last_spawn_time = now

        ground_y = self.height - 20
        player_rect = self.player.rect
        for anvil in self.anvils[:]:
            anvil.update()

            if player_rect.colliderect(anvil.rect):
                self.game_state = "GAME_OVER"

            if anvil.rect.bottom >= ground_y:
                self._spawn_impact(anvil)
                self.anvils.remove(anvil)
            elif anvil.is_off_screen(self.height):
                self.anvils.remove(anvil)

    def reset(self):
        self.player = Player(self.width, self.height)
        self.anvils.clear()
        self.particles.clear()
        self.shake_frames = 0
        self.shake_offset = (0, 0)
        self.start_ticks = pygame.time.get_ticks()
        self.last_spawn_time = pygame.time.get_ticks()
        self.spawn_delay = BASE_SPAWN_DELAY
        self.speed_multiplier = 1.0
        self.survival_time = 0
        self.game_state = "PLAYING"

    def render(self, screen):
        # Draw the scene to an off-screen canvas, then blit it with the shake offset
        canvas = self.canvas
        canvas.fill(BG_COLOR)

        ground_y = self.height - 20
        pygame.draw.rect(canvas, (70, 75, 85), (0, ground_y, self.width, 20))
        pygame.draw.line(canvas, (160, 90, 40), (0, ground_y), (self.width, ground_y), 3)

        self.player.render(canvas)
        for anvil in self.anvils:
            anvil.render(canvas)
        for p in self.particles:
            p.render(canvas)

        time_surf = self.font_medium.render(f"Survival Time: {self.survival_time}s", True, (240, 240, 240))
        canvas.blit(time_surf, (20, 20))

        inst_surf = self.font_small.render("Use [A/D] or [Arrow Keys] to Dodge", True, (170, 175, 185))
        canvas.blit(inst_surf, (self.width - inst_surf.get_width() - 20, 25))

        if self.game_state == "GAME_OVER":
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 190))
            canvas.blit(overlay, (0, 0))

            over_surf = self.font_big.render("CRUSHED! GAME OVER", True, (235, 65, 65))
            canvas.blit(over_surf, (self.width // 2 - over_surf.get_width() // 2, self.height // 2 - 60))

            score_surf = self.font_medium.render(f"You survived: {self.survival_time} seconds", True, (255, 255, 255))
            canvas.blit(score_surf, (self.width // 2 - score_surf.get_width() // 2, self.height // 2))

            restart_surf = self.font_small.render("Press [R] to Play Again", True, (200, 200, 200))
            canvas.blit(restart_surf, (self.width // 2 - restart_surf.get_width() // 2, self.height // 2 + 50))

        screen.fill((0, 0, 0))
        screen.blit(canvas, self.shake_offset)
