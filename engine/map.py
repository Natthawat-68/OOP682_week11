import pygame

class Tileset:
    def __init__(self, filename, source_size=80, target_size=20, colorkey=None):
        self.filename = filename
        self.source_size = source_size
        self.target_size = target_size
        self.image = pygame.image.load(filename).convert_alpha()
        if colorkey:
            self.image.set_colorkey(colorkey)
            
        self.tiles = []
        self._load_tiles()

    def _load_tiles(self):
        width, height = self.image.get_size()
        for y in range(0, height, self.source_size):
            for x in range(0, width, self.source_size):
                rect = pygame.Rect(x, y, self.source_size, self.source_size)
                try:
                    # Create a clean alpha surface for the tile
                    tile = pygame.Surface((self.source_size, self.source_size), pygame.SRCALPHA)
                    tile.blit(self.image, (0, 0), rect)
                    
                    # ULTIMATE PURGE: Kill everything that ISN'T the intended art
                    for px in range(tile.get_width()):
                        for py in range(tile.get_height()):
                            c = tile.get_at((px, py))
                            
                            # Calculate properties
                            brightness = (c.r + c.g + c.b) / 3
                            diff = max(abs(c.r - c.g), abs(c.g - c.b), abs(c.r - c.b))
                            
                            # 1. Kill bright neutrals (White backgrounds, Grid lines, Grey artifacts)
                            # Bright pixels with low saturation (neutral) are 99% background/noise
                            is_neutral = diff < 35 # Grey/White/Black scale
                            is_bright = brightness > 140
                            
                            # 2. Kill absolute absolute white/grey even if slightly saturated
                            is_extreme_white = brightness > 220
                            
                            if is_extreme_white or (is_neutral and is_bright):
                                tile.set_at((px, py), (0, 0, 0, 0))
                    
                    # Scale to target size
                    scaled_tile = pygame.transform.scale(tile, (self.target_size, self.target_size))
                    self.tiles.append(scaled_tile)
                except Exception as e:
                    print(f"Error loading tile at {x},{y}: {e}")

    def get_tile(self, index):
        if 0 <= index < len(self.tiles):
            return self.tiles[index]
        return None

class MapLayer:
    def __init__(self, data, width=20, height=20):
        self.data = data # List of indices
        self.width = width
        self.height = height

    def get_tile_index(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.data[y * self.width + x]
        return -1

class MapEngine:
    def __init__(self, tileset_path, tile_size=20, colorkey=(255, 255, 255)):
        self.tileset = Tileset(tileset_path, source_size=80, target_size=tile_size, colorkey=colorkey)
        self.layers = {
            "ground": None,
            "path": None,
            "item": None
        }
        self.tile_size = tile_size
        self.special_objects = {} # {(grid_x, grid_y): image}

    def set_layer(self, layer_name, data, width=20, height=20):
        if layer_name in self.layers:
            self.layers[layer_name] = MapLayer(data, width, height)

    def switch_tileset(self, tileset_path, colorkey=(255, 255, 255)):
        self.tileset = Tileset(tileset_path, source_size=80, target_size=self.tile_size, colorkey=colorkey)

    def add_object(self, grid_x, grid_y, image_path, crop_rect=None):
        try:
            # Use per-pixel alpha for perfect transparency
            raw_img = pygame.image.load(image_path)
            img = raw_img.convert_alpha()
            
            if crop_rect:
                img = img.subsurface(crop_rect).copy()
            
            # ULTIMATE Object Purge: Kill checkerboards and halos
            ck = img.get_at((0,0)) # Top-left is usually the intended background
            for px in range(img.get_width()):
                for py in range(img.get_height()):
                    c = img.get_at((px, py))
                    
                    diff = max(abs(c.r - c.g), abs(c.g - c.b), abs(c.r - c.b))
                    brightness = (c.r + c.g + c.b) / 3
                    
                    # Detect if it's the specific background color
                    is_bg = (c.r == ck.r and c.g == ck.g and c.b == ck.b)
                    # Detect neutral bright artifacts
                    is_neutral_bright = (diff < 40 and brightness > 120)
                    
                    if is_bg or is_neutral_bright or brightness > 220:
                        img.set_at((px, py), (0, 0, 0, 0))
            
            # Scale based on tileset scaling factor
            scale_factor = self.tileset.target_size / self.tileset.source_size
            
            # Special case for the massive trophy
            if "trophy" in image_path.lower():
                scale_w, scale_h = (40, 40)
            else:
                scale_w = img.get_width() * scale_factor
                scale_h = img.get_height() * scale_factor
            
            img = pygame.transform.scale(img, (int(scale_w), int(scale_h)))
            self.special_objects[(grid_x, grid_y)] = img
        except Exception as e:
            print(f"Error adding object {image_path}: {e}")

    def clear_objects(self):
        self.special_objects = {}

    def get_item_at(self, pixel_x, pixel_y):
        layer = self.layers["item"]
        if layer:
            grid_x = int(pixel_x // self.tile_size)
            grid_y = int(pixel_y // self.tile_size)
            return layer.get_tile_index(grid_x, grid_y)
        return -1

    def is_walkable(self, pixel_x, pixel_y):
        # Boundary check
        if pixel_x < 0 or pixel_x >= 400 or pixel_y < 0 or pixel_y >= 400:
            return False
        # Check item layer for obstacles (any index >= 0 is a collision)
        item_idx = self.get_item_at(pixel_x, pixel_y)
        return item_idx == -1

    def draw(self, surface):
        for layer_name in ["ground", "path", "item"]:
            layer = self.layers[layer_name]
            if layer:
                for y in range(layer.height):
                    for x in range(layer.width):
                        tile_index = layer.get_tile_index(x, y)
                        if tile_index >= 0:
                            tile_image = self.tileset.get_tile(tile_index)
                            if tile_image:
                                # Ensure integer alignment for sharp rendering
                                surface.blit(tile_image, (int(x * self.tile_size), int(y * self.tile_size)))
        
        # Draw Special Objects
        for (gx, gy), img in self.special_objects.items():
            surface.blit(img, (int(gx * self.tile_size), int(gy * self.tile_size)))
