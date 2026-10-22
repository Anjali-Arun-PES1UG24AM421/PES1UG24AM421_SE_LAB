import random
import pygame
from game.player import Player
from game.anvil import Anvil


class DustParticle:
    """A small dust puff that drifts, slows, and fades out."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3.0, 3.0)
        self.vy = random.uniform(-3.2, -0.8)
        self.max_life = random.randint(25, 45)
        self.life = self.max_life
        self.size = random.uniform(3.0, 6.0)
        self.color = (170, 160, 145)

    @property
    def dead(self):
        return self.life <= 0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.95          # air drag
        self.vy += 0.12          # light gravity
        self.life -= 1

    def render(self, surface):
        t = self.life / self.max_life          # 1.0 -> 0.0 as it fades
        alpha = int(200 * t)
        radius = max(1, int(self.size * (1.6 - 0.6 * t)))  # puff grows slightly
        puff = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(puff, (*self.color, alpha), (radius, radius), radius)
        surface.blit(puff, (int(self.x) - radius, int(self.y) - radius))


class GameEngine:
    # --- Difficulty tuning ---
    BASE_SPAWN_DELAY = 700        # ms between spawns at the start
    MIN_SPAWN_DELAY = 300         # spawn delay never goes below this (cap)
    SPAWN_DELAY_DROP_PER_SEC = 14  # ms removed from the delay per second survived

    BASE_SPEED_MULTIPLIER = 1.0   # anvil speed multiplier at the start
    MAX_SPEED_MULTIPLIER = 1.6    # speed multiplier never exceeds this (cap)
    SPEED_GAIN_PER_SEC = 0.03     # multiplier added per second survived

    # --- Impact FX tuning ---
    SHAKE_DECAY = 0.85            # shake strength multiplier applied each frame
    SHAKE_MAX = 8.0               # strongest shake in pixels
    SHAKE_CUTOFF = 0.5            # below this the shake stops

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.ground_y = height - 20
        self.player = Player(width, height)
        self.anvils = []

        self.spawn_delay = self.BASE_SPAWN_DELAY
        self.speed_multiplier = self.BASE_SPEED_MULTIPLIER
        self.last_spawn_time = pygame.time.get_ticks()

        self.particles = []
        self.shake_intensity = 0.0
        self.world_surface = pygame.Surface((width, height))

        self.start_ticks = pygame.time.get_ticks()
        self.survival_time = 0
        self.game_state = "PLAYING"

        self.font_big = pygame.font.SysFont(None, 52)
        self.font_medium = pygame.font.SysFont(None, 34)
        self.font_small = pygame.font.SysFont(None, 24)

    def handle_event(self, event):
        if self.game_state == "GAME_OVER":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()

    def _update_difficulty(self, elapsed_seconds):
        """Scale spawn rate and anvil speed with survival time, within caps."""
        self.spawn_delay = max(
            self.MIN_SPAWN_DELAY,
            self.BASE_SPAWN_DELAY - self.SPAWN_DELAY_DROP_PER_SEC * elapsed_seconds,
        )
        self.speed_multiplier = min(
            self.MAX_SPEED_MULTIPLIER,
            self.BASE_SPEED_MULTIPLIER + self.SPEED_GAIN_PER_SEC * elapsed_seconds,
        )

    def _spawn_impact(self, anvil):
        """Dust burst + screen shake where an anvil hits the ground line."""
        impact_x = anvil.x + anvil.width / 2
        for _ in range(8 + int(anvil.speed)):
            self.particles.append(DustParticle(impact_x + random.uniform(-14, 14),
                                               self.ground_y - 2))
        # Faster anvils hit harder; never exceed the cap, never weaken a bigger shake.
        strength = min(self.SHAKE_MAX, 2.0 + anvil.speed * 0.5)
        self.shake_intensity = max(self.shake_intensity, strength)

    def _update_effects(self):
        for particle in self.particles:
            particle.update()
        self.particles = [p for p in self.particles if not p.dead]

        self.shake_intensity *= self.SHAKE_DECAY
        if self.shake_intensity < self.SHAKE_CUTOFF:
            self.shake_intensity = 0.0

    def _shake_offset(self):
        if self.shake_intensity <= 0:
            return 0, 0
        amount = int(round(self.shake_intensity))
        return random.randint(-amount, amount), random.randint(-amount, amount)

    def update(self):
        # Effects keep animating even on the Game Over screen.
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
        elapsed_seconds = (now - self.start_ticks) / 1000
        self.survival_time = int(elapsed_seconds)
        self._update_difficulty(elapsed_seconds)

        if now - self.last_spawn_time >= self.spawn_delay:
            self.anvils.append(Anvil(self.width, self.speed_multiplier))
            self.last_spawn_time = now

        player_rect = self.player.rect
        for anvil in self.anvils[:]:
            anvil.update()

            if player_rect.colliderect(anvil.rect):
                self.game_state = "GAME_OVER"

            if anvil.rect.bottom >= self.ground_y:
                self._spawn_impact(anvil)
                self.anvils.remove(anvil)
            elif anvil.is_off_screen(self.height):
                self.anvils.remove(anvil)

    def reset(self):
        self.player = Player(self.width, self.height)
        self.anvils.clear()
        self.particles.clear()
        self.shake_intensity = 0.0
        self.start_ticks = pygame.time.get_ticks()
        self.last_spawn_time = pygame.time.get_ticks()
        self.survival_time = 0
        # Restore starting difficulty.
        self.spawn_delay = self.BASE_SPAWN_DELAY
        self.speed_multiplier = self.BASE_SPEED_MULTIPLIER
        self.game_state = "PLAYING"

    def render(self, screen):
        # Draw the game world off-screen so the shake can offset only the world,
        # leaving the HUD and Game Over overlay steady and readable.
        world = self.world_surface
        world.fill((35, 38, 45))

        pygame.draw.rect(world, (70, 75, 85), (0, self.ground_y, self.width, 20))
        pygame.draw.line(world, (160, 90, 40), (0, self.ground_y), (self.width, self.ground_y), 3)

        self.player.render(world)
        for anvil in self.anvils:
            anvil.render(world)
        for particle in self.particles:
            particle.render(world)

        screen.fill((35, 38, 45))
        screen.blit(world, self._shake_offset())

        time_surf = self.font_medium.render(f"Survival Time: {self.survival_time}s", True, (240, 240, 240))
        screen.blit(time_surf, (20, 20))

        inst_surf = self.font_small.render("Use [A/D] or [Arrow Keys] to Dodge", True, (170, 175, 185))
        screen.blit(inst_surf, (self.width - inst_surf.get_width() - 20, 25))

        if self.game_state == "GAME_OVER":
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 190))
            screen.blit(overlay, (0, 0))

            over_surf = self.font_big.render("CRUSHED! GAME OVER", True, (235, 65, 65))
            screen.blit(over_surf, (self.width // 2 - over_surf.get_width() // 2, self.height // 2 - 60))

            score_surf = self.font_medium.render(f"You survived: {self.survival_time} seconds", True, (255, 255, 255))
            screen.blit(score_surf, (self.width // 2 - score_surf.get_width() // 2, self.height // 2))

            restart_surf = self.font_small.render("Press [R] to Play Again", True, (200, 200, 200))
            screen.blit(restart_surf, (self.width // 2 - restart_surf.get_width() // 2, self.height // 2 + 50))
