import sys, os, math, random
import pygame

# Set working directory to the script's location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from chars.sara import Hero
from engine.map import MapEngine
from engine.level_data import LEVEL_1_FOREST, LEVEL_2_SPACE
from engine.particles import ParticleSystem

class Saraadventure(object):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((400, 400))
        try:
            self.icon = pygame.image.load("assets/my_icon.png")
            pygame.display.set_icon(self.icon)
        except:
            pass
        self.caption = "Sara's Adventure"
        self.font = pygame.font.SysFont("knit", 24)
        self.big_font = pygame.font.SysFont("knit", 42)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption(self.caption)
        self.running = True
        self.game_state = "PLAYING" # PLAYING, WON
        self.current_level = 1
        
        # Initialize Map Engine
        self.map_engine = MapEngine(LEVEL_1_FOREST["tileset"], tile_size=20, colorkey=LEVEL_1_FOREST["colorkey"])
        self.load_level(LEVEL_1_FOREST)
        
        self.hero = Hero("Sara", "assets/sara/sara_spritesheet.png", self.start_x, self.start_y)
        self.particles = ParticleSystem()

    def load_level(self, level_config):
        self.map_engine.switch_tileset(level_config["tileset"], colorkey=level_config.get("colorkey"))
        for layer_name, data in level_config["layers"].items():
            self.map_engine.set_layer(layer_name, data)
        self.start_x, self.start_y = level_config["start_pos"]
        
        # Add special objects (Portal/Trophy)
        self.map_engine.clear_objects()
        if self.current_level == 1:
            px, py = level_config["portal_pos"]
            pcrop = level_config.get("portal_crop")
            if pcrop: pcrop = pygame.Rect(pcrop)
            self.map_engine.add_object(px, py, level_config["portal_img"], pcrop)
        elif self.current_level == 2:
            tx, ty = level_config["trophy_pos"]
            self.map_engine.add_object(tx, ty, level_config["trophy_img"])

    def restart_game(self):
        self.game_state = "PLAYING"
        self.current_level = 1
        self.load_level(LEVEL_1_FOREST)
        self.hero.rect.x, self.hero.rect.y = self.start_x, self.start_y

    def drow_text(self, text, position, color=(255, 255, 255), font_type="small", center=False, scale=1.0):
        # Handle Scaling for pulse effect
        if font_type == "big":
            base_font = self.big_font
            if scale != 1.0:
                # Approximate scaling by increasing size (Pygame fonts don't scale well live, so we adjust font if needed or just blit scaled)
                # For simplicity and performance, we'll just use the scale to slightly shift the text or use a pre-set big font
                # A better way is to render once and scale the surface
                pass
        else:
            base_font = self.font

        # Render original text surface
        text_surface = base_font.render(text, True, color)
        if scale != 1.0:
            w, h = text_surface.get_size()
            text_surface = pygame.transform.smoothscale(text_surface, (int(w * scale), int(h * scale)))

        # Calculate position
        if center:
            rect = text_surface.get_rect(center=position)
            pos = (rect.x, rect.y)
        else:
            pos = position

        # Draw Outline
        outline_color = (0, 0, 0)
        offsets = [(-2, -2), (2, -2), (-2, 2), (2, 2)]
        for ox, oy in offsets:
            outline_surf = base_font.render(text, True, outline_color)
            if scale != 1.0:
                outline_surf = pygame.transform.smoothscale(outline_surf, (int(w * scale), int(h * scale)))
            self.screen.blit(outline_surf, (pos[0] + ox, pos[1] + oy))
            
        self.screen.blit(text_surface, pos)
    
    def check_interaction(self):
        cx, cy = self.hero.rect.centerx // 20, self.hero.rect.centery // 20
        
        if self.current_level == 1:
            px, py = LEVEL_1_FOREST["portal_pos"]
            if px <= cx <= px+1 and py <= cy <= py+1:
                self.current_level = 2
                self.load_level(LEVEL_2_SPACE)
                self.hero.rect.x, self.hero.rect.y = self.start_x, self.start_y
            
        elif self.current_level == 2:
            tx, ty = LEVEL_2_SPACE["trophy_pos"]
            if tx <= cx <= tx+1 and ty <= cy <= ty+1:
                self.game_state = "WON"

    def headle_input(self):
        keys = pygame.key.get_pressed()
        if self.game_state == "WON":
            if keys[pygame.K_r]:
                self.restart_game()
            return
            
        if keys[pygame.K_LEFT]: self.hero.left(self.map_engine)
        if keys[pygame.K_RIGHT]: self.hero.right(self.map_engine)
        if keys[pygame.K_UP]: self.hero.up(self.map_engine)
        if keys[pygame.K_DOWN]: self.hero.down(self.map_engine)

    def start(self):
        self.start_time = pygame.time.get_ticks()
        while self.running:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - self.start_time
            self.start_time = current_time
            
            # Pulse calculation (sine wave)
            pulse = (math.sin(current_time * 0.005) + 1) / 2 # 0 to 1
            pulse_scale = 1.0 + (pulse * 0.2) # 1.0 to 1.2
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()
            
            bg_color = (25, 100, 25) if self.current_level == 1 else (5, 5, 30)
            self.screen.fill(bg_color)
            
            self.map_engine.draw(self.screen)
            
            if self.game_state == "PLAYING":
                self.hero.update(elapsed_time)
                self.check_interaction()
                
                # Update and trigger particles
                self.particles.update()
                
                # 1. Dust Trail
                if self.hero.is_moving:
                    self.particles.emit_dust(self.hero.rect.centerx, self.hero.rect.bottom - 5)
                
                # 2. Level Ambience/Objectives
                if self.current_level == 1:
                    if random.random() < 0.05: # Falling leaves
                        self.particles.emit_leaf()
                    
                    # Portal sparks
                    px, py = LEVEL_1_FOREST["portal_pos"]
                    if random.random() < 0.3:
                        msg_x = px * 20 + random.randint(0, 40)
                        msg_y = py * 20 + random.randint(0, 40)
                        self.particles.emit_spark(msg_x, msg_y, color=(150, 100, 255))
                else:
                    # Space Trophy sparks
                    tx, ty = LEVEL_2_SPACE["trophy_pos"]
                    if random.random() < 0.3:
                        msg_x = tx * 20 + random.randint(0, 40)
                        msg_y = ty * 20 + random.randint(0, 40)
                        self.particles.emit_spark(msg_x, msg_y, color=(255, 215, 0))
            
            self.hero.draw(self.screen)
            self.particles.draw(self.screen)
            
            # --- HUD (Semi-transparent so hero is visible behind) ---
            hud = pygame.Surface((400, 50), pygame.SRCALPHA)
            hud.fill((0, 0, 0, 180)) 
            self.screen.blit(hud, (0, 0))
            
            if self.game_state == "PLAYING":
                level_name = "Forest" if self.current_level == 1 else "Space"
                self.drow_text(f"Lvl: {level_name}", (10, 15))
                goal_txt = "GOAL: Find the portal!" if self.current_level == 1 else "GOAL: Get the trophy!"
                goal_color = (255, 255, 0) if self.current_level == 1 else (0, 255, 255)
                self.drow_text(goal_txt, (110, 15), color=goal_color)
            else:
                overlay = pygame.Surface((400, 400), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.screen.blit(overlay, (0, 0))
                
                # Animated Pulsing Text
                self.drow_text("VICTORY!", (200, 160), color=(255, 215, 0), font_type="big", center=True, scale=pulse_scale)
                self.drow_text("You saved the explorer!", (200, 220), center=True)
                
                # Restart Hint
                hint_color = (200, 200, 200) if pulse > 0.5 else (100, 100, 100)
                self.drow_text("Press 'R' to Play Again", (200, 300), color=hint_color, center=True)

            self.clock.tick(144)
            self.headle_input()
            pygame.display.flip()
if __name__ == "__main__":
    game = Saraadventure()
    game.start()
