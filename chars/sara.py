import pygame
from pygame.sprite import Sprite

class Hero:
    def __init__(self, name, filename, x, y):
        self.name = name
        # Load the advanced spritesheet (640x640)
        self.sheet = pygame.image.load(filename).convert() 
        self.sheet.set_colorkey((251, 250, 251))
        self.sheet = self.sheet.convert_alpha()
        
        # Manual Bake: Convert colorkey + near-white to absolute transparency to avoid halos during scaling
        ck = (251, 250, 251)
        for px in range(self.sheet.get_width()):
            for py in range(self.sheet.get_height()):
                color = self.sheet.get_at((px, py))
                if all(c >= 235 for c in color[:3]):
                    self.sheet.set_at((px, py), (color[0], color[1], color[2], 0))
                elif color[:3] == ck:
                    self.sheet.set_at((px, py), (ck[0], ck[1], ck[2], 0))
        
        # Spritesheet info: 4 rows (Down, Up, Right, Left), 3 columns
        self.frame_width = 213 # Approximate 640 / 3
        self.frame_height = 160 # 640 / 4
        self.scale_size = (96, 96) # Upscaled
        
        self.rect = pygame.Rect(x, y, self.scale_size[0], self.scale_size[1])
        self.direction = 0 # 0: Down, 1: Up, 2: Right, 3: Left
        self.frame = 0
        self.elapsed_time = 0
        self.is_moving = False
        self.speed = 5 # Even faster

    def update(self, delta_time=100):
        if self.is_moving:
            self.elapsed_time += delta_time
            if self.elapsed_time > 150: # Faster animation for smoother walking
                self.frame = (self.frame + 1) % 3
                self.elapsed_time = 0
        else:
            self.frame = 0 # Reset to idle/standing frame
        
        self.is_moving = False # Reset move flag for next frame

    def can_move_to(self, new_x, new_y, map_engine):
        # Extreme Forgiveness Box (12x8)
        # This allows Sara to pass through almost anything that isn't a solid tree trunk
        feet_w, feet_h = 12, 8
        feet_rect = pygame.Rect(
            new_x + (self.scale_size[0] - feet_w) // 2,
            new_y + self.scale_size[1] - feet_h - 4,
            feet_w,
            feet_h
        )
        
        # 5-point check for collision
        points = [
            feet_rect.topleft, feet_rect.topright,
            feet_rect.bottomleft, feet_rect.bottomright,
            feet_rect.center
        ]
        
        for px, py in points:
            if not map_engine.is_walkable(px, py):
                return False
        return True

    def left(self, map_engine):
        if self.rect.x > 0:
            if self.can_move_to(self.rect.x - self.speed, self.rect.y, map_engine):
                self.rect.x -= self.speed
            self.direction = 3
            self.is_moving = True
            
    def right(self, map_engine):
        if self.rect.right < 800:
            if self.can_move_to(self.rect.x + self.speed, self.rect.y, map_engine):
                self.rect.x += self.speed
            self.direction = 2
            self.is_moving = True
            
    def up(self, map_engine):
        if self.rect.y > 0:
            if self.can_move_to(self.rect.x, self.rect.y - self.speed, map_engine):
                self.rect.y -= self.speed
            self.direction = 1
            self.is_moving = True
            
    def down(self, map_engine):
        if self.rect.bottom < 800:
            if self.can_move_to(self.rect.x, self.rect.y + self.speed, map_engine):
                self.rect.y += self.speed
            self.direction = 0
            self.is_moving = True
            
    def draw(self, surface):
        # Calculate clip area from sheet
        clip_rect = pygame.Rect(
            self.frame * self.frame_width,
            self.direction * self.frame_height,
            self.frame_width,
            self.frame_height
        )
        # Handle edge cases (640 is not perfectly divisible by 3)
        if clip_rect.right > 640: clip_rect.width = 640 - clip_rect.x
        if clip_rect.bottom > 640: clip_rect.height = 640 - clip_rect.y
        
        frame_surface = self.sheet.subsurface(clip_rect)
        # Scale and draw
        scaled_hero = pygame.transform.scale(frame_surface, self.scale_size)
        surface.blit(scaled_hero, (self.rect.x, self.rect.y - 10)) # Offset a bit for depth