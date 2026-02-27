import pygame
import random
import math

class Particle:
    def __init__(self, x, y, dx, dy, life, color, size, gravity=0, friction=1.0):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.life = life # in frames
        self.max_life = life
        self.color = color
        self.size = size
        self.gravity = gravity
        self.friction = friction

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += self.gravity
        self.dx *= self.friction
        self.dy *= self.friction
        self.life -= 1
        return self.life > 0

    def draw(self, surface):
        alpha = int((self.life / self.max_life) * 255)
        # Create a tiny surface for per-particle alpha
        p_surf = pygame.Surface((int(self.size), int(self.size)), pygame.SRCALPHA)
        p_color = list(self.color)
        if len(p_color) < 4: p_color.append(alpha)
        else: p_color[3] = alpha
        
        pygame.draw.circle(p_surf, p_color, (int(self.size // 2), int(self.size // 2)), int(self.size // 2))
        surface.blit(p_surf, (int(self.x - self.size // 2), int(self.y - self.size // 2)))

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit_dust(self, x, y):
        # Larger puffs
        for _ in range(2):
            dx = random.uniform(-1.0, 1.0)
            dy = random.uniform(-1.5, -0.4)
            life = random.randint(20, 40)
            size = random.uniform(4, 8)
            color = (139, 115, 85)
            self.particles.append(Particle(x, y, dx, dy, life, color, size, friction=0.95))

    def emit_spark(self, x, y, color=(255, 255, 100)):
        # Brighter sparks
        for _ in range(1):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1.0, 4.0)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            life = random.randint(30, 60)
            size = random.uniform(2, 6)
            self.particles.append(Particle(x, y, dx, dy, life, color, size, friction=0.98))

    def emit_leaf(self):
        # Green/Orange leaves for 800px width
        x = random.randint(0, 800)
        y = -20
        dx = random.uniform(-1.5, 1.5)
        dy = random.uniform(1.5, 3.0)
        life = 400 
        size = random.uniform(6, 12)
        color = random.choice([(34, 139, 34), (107, 142, 35), (218, 165, 32)])
        self.particles.append(Particle(x, y, dx, dy, life, color, size, gravity=0.02, friction=0.99))

    def update(self):
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)
