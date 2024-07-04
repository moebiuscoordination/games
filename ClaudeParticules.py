import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Particle Simulation")

# Colors
BLACK = (0, 0, 0)
METAL_COLORS = [
    (192, 192, 192),  # Silver
    (255, 215, 0),  # Gold
    (184, 115, 51),  # Bronze
    (212, 175, 55),  # Brass
]

# Particle class
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.original_x = x
        self.original_y = y
        self.size = random.uniform(0.5, 1.5)
        self.color = random.choice(METAL_COLORS)
        self.speed = random.uniform(0.05, 0.2)
        self.angle = random.uniform(0, 2 * math.pi)
        self.wind_force = 0
        self.wind_angle = 0

    import math

    def update(self, mouse_pos):
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance < 150:
            self.wind_force = max(0, 150 - distance) / 500  # Less impact from wind force
            self.wind_angle = math.atan2(dy, dx)
        else:
            self.wind_force *= 0.98  # Increase damping factor to slow down wind force decay

        self.x += math.cos(self.wind_angle) * self.wind_force
        self.y += math.sin(self.wind_angle) * self.wind_force

        self.x += (self.original_x - self.x) * 0.02  # More gradual return to the original position
        self.y += (self.original_y - self.y) * 0.02

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        # Add a shine effect
        shine_pos = (int(self.x + self.size / 2), int(self.y - self.size / 2))
        pygame.draw.circle(screen, (255, 255, 255), shine_pos, self.size / 3)

# Create particles
particles = []
for t in range(0, 2000):
    angle = t * 0.05
    x = WIDTH // 2 + 100 * math.sin(angle)
    y = HEIGHT // 2 + 50 * math.sin(angle * 2)
    particles.append(Particle(x, y))

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mouse_pos = pygame.mouse.get_pos()

    screen.fill(BLACK)

    for particle in particles:
        particle.update(mouse_pos)
        particle.draw()

    pygame.display.flip()

pygame.quit()