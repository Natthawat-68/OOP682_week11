import pygame
import sys

def generate_index_sheet(source_path, output_path, tile_size=80):
    pygame.init()
    try:
        sheet = pygame.image.load(source_path)
    except:
        print(f"Error loading {source_path}")
        return

    w, h = sheet.get_size()
    rows = h // tile_size
    cols = w // tile_size
    
    # Create a surface with indices drawn over tiles
    font = pygame.font.SysFont("Arial", 24, bold=True)
    for r in range(rows):
        for c in range(cols):
            idx = r * cols + c
            # Draw a small background for the text
            bg_rect = pygame.Rect(c * tile_size, r * tile_size, 40, 30)
            pygame.draw.rect(sheet, (0, 0, 0, 150), bg_rect)
            
            text = font.render(str(idx), True, (255, 255, 0))
            sheet.blit(text, (c * tile_size + 5, r * tile_size + 2))
            
            # Draw grid lines
            pygame.draw.rect(sheet, (255, 255, 255, 50), (c * tile_size, r * tile_size, tile_size, tile_size), 1)

    pygame.image.save(sheet, output_path)
    print(f"Saved indexed sheet to {output_path}")

if __name__ == "__main__":
    generate_index_sheet("c:/68_Natthawat/OOP_682/week11/Sara/assets/maps/forest_tileset.png", "forest_indices.png")
    generate_index_sheet("c:/68_Natthawat/OOP_682/week11/Sara/assets/maps/space_tileset.png", "space_indices.png")
    pygame.quit()
