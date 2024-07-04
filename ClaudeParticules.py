import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 1000, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Particle Simulation")

# Colors
BLACK = (0, 0, 0)
METAL_COLORS = [

    (255, 250, 250),   # Snow
    (255, 235, 205),   # Blanched Almond
    (255, 245, 238),   # Seashell
    (255, 248, 220),   # Cornsilk
    (255, 255, 240),   # Ivory
    (250, 240, 230)    # Linen
]

# Particle class
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.original_x = x
        self.original_y = y
        self.size = random.uniform(1, 2)
        self.color = random.choice(METAL_COLORS)
        self.speed = random.uniform(0.1, 0.5)
        self.angle = random.uniform(0, 2 * math.pi)
        self.rotation_angle = random.uniform(0, 2 * math.pi)
        self.wind_force = 0
        self.wind_angle = 0
        self.lifespan = random.randint(100, 10000)
        self.alive = True
        self.escaping = random.choice([True, False])
        self.gravitating = False
        self.gravity_center = (WIDTH // 0.1, HEIGHT // 0.1)

    def update(self, mouse_pos):
        if not self.alive:
            return

        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance < 150:
            self.wind_force = max(0, 125 - distance) / 1  # Less impact from wind force
            self.wind_angle = math.atan2(dy, dx)
        else:
            self.wind_force *= 0.98  # Increase damping factor to slow down wind force decay

        self.x += math.cos(self.wind_angle) * self.wind_force
        self.y += math.sin(self.wind_angle) * self.wind_force

        if self.gravitating:
            gx, gy = self.gravity_center
            dx = gx - self.x
            dy = gy - self.y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            gravity_force = min(10, max(0.05, 1 / (distance + 1)))
            self.x += dx * gravity_force
            self.y += dy * gravity_force

            if distance < 10:
                self.gravitating = False
                self.original_x, self.original_y = self.x, self.y

        if self.escaping:
            self.x += math.cos(self.angle) * self.speed * 5
            self.y += math.sin(self.angle) * self.speed * 5
            if random.random() < 0.001:
                self.escaping = False
                self.gravitating = True
        else:
            self.x += (self.original_x - self.x) * 0.02  # More gradual return to the original position
            self.y += (self.original_y - self.y) * 0.02

            # Rotate upon itself
            self.rotation_angle += 0.1
            self.x += math.cos(self.rotation_angle) * self.speed
            self.y += math.sin(self.rotation_angle) * self.speed

        # Update lifespan
        self.lifespan -= 1
        if self.lifespan <= 0:
            self.alive = False

    def draw(self):
        if not self.alive:
            return

        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))
        # Add a shine effect
        shine_pos = (int(self.x + self.size / 2), int(self.y - self.size / 2))
        pygame.draw.circle(screen, (255, 255, 255), shine_pos, int(self.size / 3))

    def regenerate(self):
        if random.random() < 0.5:  # 50% chance to start from the center
            self.x = WIDTH // 2
            self.y = HEIGHT // 2
        else:  # 50% chance to start from outside the screen
            self.x = random.choice([random.uniform(-WIDTH * 0.1, 0), random.uniform(WIDTH, WIDTH * 1.1)])
            self.y = random.choice([random.uniform(-HEIGHT * 0.1, 0), random.uniform(HEIGHT, HEIGHT * 1.1)])
            self.gravitating = True

        # Recalculate original position to join the infinity symbol at any point
        angle = random.uniform(0, 2 * math.pi)
        self.original_x = WIDTH // 2 + 100 * math.sin(angle)
        self.original_y = HEIGHT // 2 + 50 * math.sin(angle * 2)
        self.size = random.uniform(0.1, 0.5)
        self.color = random.choice(METAL_COLORS)
        self.speed = random.uniform(0.1, 0.5)
        self.angle = random.uniform(0, 2 * math.pi)
        self.rotation_angle = random.uniform(0, 2 * math.pi)
        self.wind_force = 0
        self.wind_angle = 0
        self.lifespan = random.randint(100, 10000)
        self.alive = True
        self.escaping = random.choice([True, False])
        self.gravity_center = self.find_closest_point_on_infinity()

    def find_closest_point_on_infinity(self):
        min_distance = float('inf')
        closest_point = (self.original_x, self.original_y)

        for t in range(0, 2000):
            angle = t * 0.05
            x = WIDTH // 2 + 100 * math.sin(angle)
            y = HEIGHT // 2 + 50 * math.sin(angle * 2)
            distance = math.sqrt((self.x - x) ** 2 + (self.y - y) ** 2)

            if distance < min_distance:
                min_distance = distance
                closest_point = (x, y)

        return closest_point


# Create particles
particles = []
for t in range(0, 4000):
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
        if not particle.alive:
            particle.regenerate()
        particle.update(mouse_pos)
        particle.draw()

    pygame.display.flip()

pygame.quit()
