# Map data for 20x20 grid (400 tiles)
import random

# Forest Level Design
ground_f = [0] * 400
path_f = [-1] * 400
item_f = [-1] * 400

# Winding Path
for i in range(2, 6): path_f[3 * 20 + i] = 18
for i in range(3, 10): path_f[i * 20 + 5] = 18
for i in range(5, 15): path_f[10 * 20 + i] = 18
for i in range(10, 16): path_f[i * 20 + 15] = 18

# Dense Forest Layout
# Trees (indices 48, 49, 56, 57 form a 2x2 tree usually)
trees = [
    (1,1), (6,1), (12,1), (17,1), (1,7), (8,5), (2,14), (8,14), (13,16), (17,6)
]
for tx, ty in trees:
    item_f[ty * 20 + tx] = 48
    item_f[ty * 20 + tx + 1] = 49
    item_f[(ty + 1) * 20 + tx] = 56
    item_f[(ty + 1) * 20 + tx + 1] = 57

# Rocks and Flowers
for _ in range(30):
    rx, ry = random.randint(0, 19), random.randint(0, 19)
    if path_f[ry * 20 + rx] == -1 and item_f[ry * 20 + rx] == -1:
        item_f[ry * 20 + rx] = random.choice([32, 33, 10, 11, 8, 9])

LEVEL_1_FOREST = {
    "tileset": "assets/maps/forest_tileset.png",
    "colorkey": (255, 255, 255),
    "layers": {
        "ground": ground_f,
        "path": path_f,
        "item": item_f
    },
    "portal_pos": (14, 14),
    "portal_img": "assets/maps/forest_tileset.png",
    "portal_crop": (240, 240, 160, 160), 
    "start_pos": (50, 60)
}

# Space Level Design
ground_s = [16] * 400
path_s = [-1] * 400
item_s = [-1] * 400

# Laboratory - High Fidelity Professional Layout
# Ground variation
for _ in range(50):
    idx = random.randint(0, 399)
    ground_s[idx] = random.choice([16, 17, 18])

# Technical Floor Patterns (Paths as floor accents)
for y in [4, 15]: 
    for x in range(3, 17): path_s[y * 20 + x] = 2
for x in [4, 15]:
    for y in range(4, 16): path_s[y * 20 + x] = 2

# 1. SERVER ROOM (Top Section)
for sx in [6, 8, 11, 13]:
    item_s[2 * 20 + sx] = 48
    item_s[2 * 20 + sx + 1] = 49
    item_s[3 * 20 + sx] = 56
    item_s[3 * 20 + sx + 1] = 57

# 2. CRYO BAY (Bottom Section)
for sx in [6, 8, 11, 13]:
    item_s[17 * 20 + sx] = 24 # Base
    item_s[16 * 20 + sx] = 8  # Tech spire

# 3. CONTROL CENTER (Left/Right Sides)
for sy in [7, 9, 11]:
    item_s[sy * 20 + 2] = 40
    item_s[sy * 20 + 3] = 41
    item_s[sy * 20 + 17] = 42
    item_s[sy * 20 + 18] = 43

LEVEL_2_SPACE = {
    "tileset": "assets/maps/space_tileset.png",
    "colorkey": (252, 253, 251),
    "layers": {
        "ground": ground_s,
        "path": path_s,
        "item": item_s
    },
    "trophy_pos": (10, 10),
    "trophy_img": "assets/items/gold_trophy.png",
    "start_pos": (40, 300) # Bottom left (replaces overlap at 200,200)
}
