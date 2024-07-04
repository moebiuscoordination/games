import pygame
import pygame.freetype
import math
import random

# Initialize Pygame
pygame.init()
pygame.freetype.init()

# Set up the display
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Enhanced Infinity Particle Simulation")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
LIGHT_BLUE = (173, 216, 230)
METAL_COLORS = [
    (192, 192, 192),  # Silver
    (255, 215, 0),    # Gold
    (184, 115, 51),   # Bronze
    (212, 175, 55),   # Brass
]

# Fonts
font = pygame.freetype.SysFont("Arial", 24)
large_font = pygame.freetype.SysFont("Arial", 36)

class Particle:
    def __init__(self, x, y):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.size = random.uniform(1, 2)
        self.color = random.choice(METAL_COLORS)
        self.speed = random.uniform(0.1, 0.5)
        self.wind_force = self.wind_angle = 0
        self.in_text = False
        self.target_x = self.target_y = None
        self.t = random.uniform(0, 4000)

    def update(self, mouse_pos, wind_effect):
        if self.in_text:
            self.move_to_text_position()
        elif wind_effect and mouse_pos:
            dx, dy = mouse_pos[0] - self.x, mouse_pos[1] - self.y
            distance = math.hypot(dx, dy)
            if distance < 150:
                self.wind_force = max(0, 150 - distance) / 10
                self.wind_angle = math.atan2(dy, dx)
            else:
                self.wind_force *= 0.98
            self.x += math.cos(self.wind_angle) * self.wind_force
            self.y += math.sin(self.wind_angle) * self.wind_force

        if not self.in_text:
            self.t += 0.05
            self.original_x = WIDTH // 2 + 200 * math.sin(self.t)
            self.original_y = HEIGHT // 3 + 100 * math.sin(self.t * 2)
            self.x += (self.original_x - self.x) * 0.05
            self.y += (self.original_y - self.y) * 0.05

    def move_to_text_position(self):
        if self.target_x is not None and self.target_y is not None:
            dx, dy = self.target_x - self.x, self.target_y - self.y
            distance = math.hypot(dx, dy)
            if distance > 1:
                self.x += dx * 0.1
                self.y += dy * 0.1
            else:
                self.x, self.y = self.target_x, self.target_y

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))
        shine_pos = (int(self.x + self.size / 2), int(self.y - self.size / 2))
        pygame.draw.circle(screen, WHITE, shine_pos, int(self.size / 3))

class Button:
    def __init__(self, x, y, width, height, text, color, text_color, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.action = action

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        font.render_to(screen, (self.rect.x + 10, self.rect.y + 10), self.text, self.text_color)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            self.action()

class Simulation:
    def __init__(self):
        self.particles = []
        self.text_particles = []
        self.wind_effect = True
        self.show_controls = False
        self.show_utility_panel = False
        self.show_config_panel = False
        self.input_text = ""
        self.input_active = False
        self.particle_color = METAL_COLORS[0]
        self.create_infinity_particles()
        self.create_ui()

    def create_infinity_particles(self):
        self.particles = [Particle(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(10000)]

    def create_ui(self):
        toolbar_height = 60
        self.input_box = pygame.Rect(10, HEIGHT - toolbar_height + 10, 300, 40)
        self.wind_button = Button(WIDTH - 220, HEIGHT - toolbar_height + 10, 200, 40, "Toggle Wind", LIGHT_BLUE, BLACK, self.toggle_wind)
        self.utility_button = Button(WIDTH - 440, HEIGHT - toolbar_height + 10, 200, 40, "Utility Panel", LIGHT_BLUE, BLACK, self.toggle_utility_panel)
        self.config_button = Button(WIDTH - 660, HEIGHT - toolbar_height + 10, 200, 40, "Config Panel", LIGHT_BLUE, BLACK, self.toggle_config_panel)
        self.controls_button = Button(WIDTH - 880, HEIGHT - toolbar_height + 10, 200, 40, "Show Controls", LIGHT_BLUE, BLACK, self.toggle_controls)

    def toggle_wind(self):
        self.wind_effect = not self.wind_effect

    def toggle_utility_panel(self):
        self.show_utility_panel = not self.show_utility_panel
        self.show_config_panel = False

    def toggle_config_panel(self):
        self.show_config_panel = not self.show_config_panel
        self.show_utility_panel = False

    def toggle_controls(self):
        self.show_controls = not self.show_controls

    def create_text_particles(self):
        text_surface, _ = large_font.render(self.input_text, WHITE)
        text_array = pygame.surfarray.array3d(text_surface)
        self.text_particles.clear()

        for y in range(text_array.shape[1]):
            for x in range(text_array.shape[0]):
                if text_array[x][y].any():
                    if self.particles:
                        particle = self.particles.pop()
                    else:
                        particle = Particle(WIDTH // 2, HEIGHT // 3)
                    particle.target_x = x + (WIDTH - text_surface.get_width()) // 2
                    particle.target_y = y + HEIGHT * 2 // 3
                    particle.in_text = True
                    self.text_particles.append(particle)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            for button in [self.wind_button, self.utility_button, self.config_button, self.controls_button]:
                button.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.input_active = self.input_box.collidepoint(event.pos)

            if event.type == pygame.KEYDOWN and self.input_active:
                if event.key == pygame.K_RETURN:
                    self.create_text_particles()
                    self.input_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                else:
                    self.input_text += event.unicode

        return True

    def update(self):
        mouse_pos = pygame.mouse.get_pos() if self.wind_effect else None

        for particle in self.particles + self.text_particles:
            particle.update(mouse_pos, self.wind_effect)

        if len(self.particles) < 10000 and random.random() < 0.1:
            self.particles.append(Particle(random.randint(0, WIDTH), random.randint(0, HEIGHT)))

    def draw(self):
        screen.fill(BLACK)

        for particle in self.particles + self.text_particles:
            particle.draw()

        pygame.draw.rect(screen, GRAY, (0, HEIGHT - 60, WIDTH, 60))

        for button in [self.wind_button, self.utility_button, self.config_button, self.controls_button]:
            button.draw()

        pygame.draw.rect(screen, WHITE if self.input_active else GRAY, self.input_box, 2)
        font.render_to(screen, (self.input_box.x + 5, self.input_box.y + 5), self.input_text, WHITE)

        if self.show_utility_panel:
            self.draw_utility_panel()
        if self.show_config_panel:
            self.draw_config_panel()
        if self.show_controls:
            self.draw_controls()

        pygame.display.flip()

    def draw_utility_panel(self):
        panel_surface = pygame.Surface((300, 400), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 192))
        screen.blit(panel_surface, (WIDTH - 310, HEIGHT - 470))

        font.render_to(screen, (WIDTH - 300, HEIGHT - 460), "Utility Panel", WHITE)
        font.render_to(screen, (WIDTH - 300, HEIGHT - 420), "Particle Color:", WHITE)

        for i, color in enumerate(METAL_COLORS):
            color_rect = pygame.Rect(WIDTH - 300 + i * 60, HEIGHT - 390, 50, 50)
            pygame.draw.rect(screen, color, color_rect)
            if color == self.particle_color:
                pygame.draw.rect(screen, WHITE, color_rect, 2)

    def draw_config_panel(self):
        panel_surface = pygame.Surface((300, 400), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 192))
        screen.blit(panel_surface, (WIDTH - 310, HEIGHT - 470))

        font.render_to(screen, (WIDTH - 300, HEIGHT - 460), "Config Panel", WHITE)
        # Add configuration options here

    def draw_controls(self):
        control_surface = pygame.Surface((400, 200), pygame.SRCALPHA)
        control_surface.fill((0, 0, 0, 192))
        screen.blit(control_surface, (WIDTH // 2 - 200, HEIGHT // 2 - 100))

        controls = [
            "Controls:",
            "- Type text and press Enter to create text particles",
            "- Toggle wind effect with the button",
            "- Click anywhere to interact with particles"
        ]

        for i, text in enumerate(controls):
            font.render_to(screen, (WIDTH // 2 - 180, HEIGHT // 2 - 80 + i * 30), text, WHITE)

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            clock.tick(60)

if __name__ == "__main__":
    simulation = Simulation()
    simulation.run()