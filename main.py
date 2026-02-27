import sys, os, math, random, json
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
        self.screen = pygame.display.set_mode((800, 800))
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
        
        # Initialize Map Engine (Scale target up to 40px)
        self.map_engine = MapEngine(LEVEL_1_FOREST["tileset"], tile_size=40, colorkey=LEVEL_1_FOREST["colorkey"])
        self.load_level(LEVEL_1_FOREST)
        
        self.hero = Hero("Sara", "assets/sara/sara_spritesheet.png", self.start_x, self.start_y)
        self.particles = ParticleSystem()
        
        # Editor State
        self.mode = "GAME" # "GAME" or "EDITOR"
        self.selected_tile = 0
        self.palette_scroll = 0
        self.save_feedback_timer = 0

    def load_level(self, level_config):
        self.map_engine.switch_tileset(level_config["tileset"], colorkey=level_config.get("colorkey"))
        
        # Check for Persistent Custom Map for this level
        save_file = f"level_{self.current_level}_custom.json"
        custom_data = None
        if os.path.exists(save_file):
            try:
                with open(save_file, "r") as f:
                    custom_data = json.load(f)
            except Exception as e:
                print(f"Error loading {save_file}: {e}")

        for layer_name, data in level_config["layers"].items():
            if custom_data and layer_name in custom_data:
                self.map_engine.set_layer(layer_name, custom_data[layer_name])
            else:
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
        # Grid is logically 20x20, but rendered at 40px per tile
        # Center of hero in grid coordinates
        cx, cy = self.hero.rect.centerx // 40, self.hero.rect.centery // 40
        
        if self.current_level == 1:
            # Level 1 portal is at (14, 14) in the 20x20 grid
            px, py = LEVEL_1_FOREST["portal_pos"]
            # Check for proximity to portal center
            if abs(cx - px) < 1.5 and abs(cy - py) < 1.5:
                self.current_level = 2
                self.load_level(LEVEL_2_SPACE)
                # Ensure spawn is in 800x800 space (start_pos is logical 0-400)
                self.hero.rect.x, self.hero.rect.y = self.start_x * 2, self.start_y * 2
            
        elif self.current_level == 2:
            tx, ty = LEVEL_2_SPACE["trophy_pos"]
            if abs(cx - tx) < 1.5 and abs(cy - ty) < 1.5:
                self.game_state = "WON"

    def save_map(self):
        # Save current map structure to a JSON file
        save_file = f"level_{self.current_level}_custom.json"
        map_data = {
            "ground": self.map_engine.get_layer_data("ground"),
            "path": self.map_engine.get_layer_data("path"),
            "item": self.map_engine.get_layer_data("item")
        }
        try:
            with open(save_file, "w") as f:
                json.dump(map_data, f)
            self.save_feedback_timer = 60 
            print(f"\n--- MAP SAVED TO {save_file} ---")
        except Exception as e:
            print(f"Error saving map: {e}")

    def headle_input(self):
        keys = pygame.key.get_pressed()
        if self.game_state == "WON":
            if keys[pygame.K_r]:
                self.restart_game()
            return
            
        if self.mode == "GAME":
            if keys[pygame.K_LEFT]: self.hero.left(self.map_engine)
            if keys[pygame.K_RIGHT]: self.hero.right(self.map_engine)
            if keys[pygame.K_UP]: self.hero.up(self.map_engine)
            if keys[pygame.K_DOWN]: self.hero.down(self.map_engine)
        else:
            # Editor Scroll
            if keys[pygame.K_UP]: self.palette_scroll -= 2
            if keys[pygame.K_DOWN]: self.palette_scroll += 2
            self.palette_scroll = max(0, self.palette_scroll)

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
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        self.mode = "EDITOR" if self.mode == "GAME" else "GAME"
                    if self.mode == "EDITOR":
                        if event.key == pygame.K_s: self.save_map()
                        # Layer switching (Both top row and Numpad)
                        if event.key in [pygame.K_1, pygame.K_KP1]: self.current_editor_layer = "ground"
                        if event.key in [pygame.K_2, pygame.K_KP2]: self.current_editor_layer = "path"
                        if event.key in [pygame.K_3, pygame.K_KP3]: self.current_editor_layer = "item"
                
                if self.mode == "EDITOR":
                    if event.type == pygame.MOUSEWHEEL:
                        self.palette_scroll -= event.y * 30
                        self.palette_scroll = max(0, self.palette_scroll)
                
                if self.mode == "EDITOR" and event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    
                    # 1. Save Button Check (Bottom Left)
                    if mx < 120 and my > 740:
                        self.save_map()
                        continue

                    # 2. Sidebar Interaction
                    if mx > 650:
                        # Palette selection (Scrollable area)
                        if my > 10:
                            tile_y_in_palette = my + self.palette_scroll - 20
                            idx = (tile_y_in_palette // 50)
                            if 0 <= idx < len(self.map_engine.tileset.tiles):
                                self.selected_tile = idx
                    else:
                        # 3. Smart Placement
                        gx, gy = mx // 40, my // 40
                        if event.button == 1: # Left click (PLACE)
                            self.smart_place_tile(gx, gy, self.selected_tile)
                        elif event.button == 3: # Right click (ERASE ALL)
                            base_ground = 0 if self.current_level == 1 else 16
                            self.map_engine.update_tile("ground", gx, gy, base_ground)
                            self.map_engine.update_tile("path", gx, gy, -1)
                            self.map_engine.update_tile("item", gx, gy, -1)
            
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
                        msg_x = px * 40 + random.randint(0, 80)
                        msg_y = py * 40 + random.randint(0, 80)
                        self.particles.emit_spark(msg_x, msg_y, color=(150, 100, 255))
                else:
                    # Space Trophy sparks
                    tx, ty = LEVEL_2_SPACE["trophy_pos"]
                    if random.random() < 0.3:
                        msg_x = tx * 40 + random.randint(0, 80)
                        msg_y = ty * 40 + random.randint(0, 80)
                        self.particles.emit_spark(msg_x, msg_y, color=(255, 215, 0))
            
            self.hero.draw(self.screen)
            self.particles.draw(self.screen)
            
            # --- HUD (Scaled for 800x800) ---
            hud = pygame.Surface((800, 60), pygame.SRCALPHA)
            hud.fill((0, 0, 0, 180)) 
            self.screen.blit(hud, (0, 0))
            
            if self.game_state == "PLAYING":
                level_name = "Forest" if self.current_level == 1 else "Space"
                self.drow_text(f"Lvl: {level_name}", (10, 15))
                goal_txt = "GOAL: Find the portal!" if self.current_level == 1 else "GOAL: Get the trophy!"
                goal_color = (255, 255, 0) if self.current_level == 1 else (0, 255, 255)
                self.drow_text(goal_txt, (110, 15), color=goal_color)
            else:
                overlay = pygame.Surface((800, 800), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.screen.blit(overlay, (0, 0))
                
                # Animated Pulsing Text
                self.drow_text("VICTORY!", (400, 320), color=(255, 215, 0), font_type="big", center=True, scale=pulse_scale)
                self.drow_text("You saved the explorer!", (400, 400), center=True)
                
                # Restart Hint
                hint_color = (200, 200, 200) if pulse > 0.5 else (100, 100, 100)
                self.drow_text("Press 'R' to Play Again", (400, 600), color=hint_color, center=True)

            if self.mode == "EDITOR":
                self.draw_editor()
                if self.save_feedback_timer > 0:
                    self.save_feedback_timer -= 1
                    self.drow_text("SAVED!", (400, 700), color=(0, 255, 0), font_type="big", center=True)

            self.clock.tick(144)
            self.headle_input()
            pygame.display.flip()

    def smart_place_tile(self, gx, gy, tile_index):
        if self.current_level == 1:
            ground_indices = [0]
            path_indices = [18]
        else:
            ground_indices = [16, 17, 18]
            path_indices = [2]
        
        if tile_index in ground_indices:
            # Place on ground, clear overlays
            self.map_engine.update_tile("ground", gx, gy, tile_index)
            self.map_engine.update_tile("path", gx, gy, -1)
            self.map_engine.update_tile("item", gx, gy, -1)
        elif tile_index in path_indices:
            # Place on path, keep current ground
            self.map_engine.update_tile("path", gx, gy, tile_index)
            self.map_engine.update_tile("item", gx, gy, -1)
        else:
            # Place on item, keep ground and path
            self.map_engine.update_tile("item", gx, gy, tile_index)

    def draw_editor(self):
        # Draw Palette Sidebar
        sidebar = pygame.Surface((150, 800))
        sidebar.fill((25, 25, 30))
        pygame.draw.line(sidebar, (0, 255, 255), (0, 0), (0, 800), 2)
        self.screen.blit(sidebar, (650, 0))
        
        # Draw tiles in palette (Unified list)
        y_offset = 20 - self.palette_scroll
        for i, tile in enumerate(self.map_engine.tileset.tiles):
            if -40 < y_offset < 800:
                # Highlight selected
                if i == self.selected_tile:
                    pygame.draw.rect(self.screen, (255, 255, 255), (670, y_offset, 40, 40), 3)
                    pygame.draw.rect(self.screen, (0, 255, 255), (670, y_offset, 40, 40), 1)
                self.screen.blit(tile, (670, y_offset))
                self.drow_text(str(i), (720, y_offset + 10))
            y_offset += 50

        # Grid Highlight
        mx, my = pygame.mouse.get_pos()
        if mx < 650:
            gx, gy = mx // 40, my // 40
            highlight = pygame.Surface((40, 40), pygame.SRCALPHA)
            highlight.fill((255, 255, 255, 80))
            self.screen.blit(highlight, (gx * 40, gy * 40))
            
        # Visual SAVE Button (Bottom Left)
        save_btn = pygame.Surface((100, 40), pygame.SRCALPHA)
        pygame.draw.rect(save_btn, (0, 0, 0, 180), (0, 0, 100, 40), border_radius=8)
        pygame.draw.rect(save_btn, (0, 255, 0), (0, 0, 100, 40), 2, border_radius=8)
        self.screen.blit(save_btn, (10, 750))
        self.drow_text("SAVE", (35, 758), color=(0, 255, 0))
if __name__ == "__main__":
    game = Saraadventure()
    game.start()
