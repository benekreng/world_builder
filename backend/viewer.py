import json
import math
from PIL import Image, ImageDraw

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def render_json_to_image(json_path):
    print(f"Loading {json_path}...")
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: world_data.json not found.")
        return

    # 1. AUTO-DETECT GRID SIZE
    max_x = 0
    max_y = 0
    for ent in data['entities']:
        for cell in ent['cells']:
            if cell['x'] > max_x: max_x = cell['x']
            if cell['y'] > max_y: max_y = cell['y']
    
    # Grid dimensions (add 1 because coords are 0-indexed)
    grid_w = max_x + 1
    grid_h = max_y + 1
    
    print(f"Detected Grid Resolution: {grid_w}x{grid_h}")

    # 2. SCALE UP FOR VIEWING
    # We want the output image to be roughly 1000px so we can see it
    target_size = 1000
    scale = max(1, target_size // max(grid_w, grid_h))
    
    img_w = grid_w * scale
    img_h = grid_h * scale
    
    print(f"Upscaling by {scale}x for viewing (Output: {img_w}x{img_h})")
    
    img = Image.new("RGB", (img_w, img_h), "#f4f1ea") # Parchment
    draw = ImageDraw.Draw(img)

    # 3. RENDER TERRAIN (Cells)
    for entity in data['entities']:
        # Get color
        hex_color = entity['metadata'].get('color', '#000000')
        fill_color = hex_to_rgb(hex_color)
        
        for cell in entity['cells']:
            gx, gy = cell['x'], cell['y']
            
            # Calculate pixel rect for this tile
            px = gx * scale
            py = gy * scale
            
            # Draw rectangle (Pixel Art style)
            draw.rectangle([px, py, px + scale - 1, py + scale - 1], fill=fill_color)

    # 4. RENDER ICONS (Centered in the tile)
    for entity in data['entities']:
        for icon in entity.get('icons', []):
            origin = icon['origin']
            gx, gy = origin['x'], origin['y']
            
            # Center of the scaled tile
            cx = (gx * scale) + (scale // 2)
            cy = (gy * scale) + (scale // 2)
            
            # Draw a simple marker relative to tile size
            icon_size = max(3, scale // 2) # Half the tile size
            
            if icon['type'] == 'city':
                draw.rectangle([cx - icon_size//2, cy - icon_size//2, 
                                cx + icon_size//2, cy + icon_size//2], 
                                fill="black", outline="white")
            elif icon['type'] == 'poi':
                draw.ellipse([cx - icon_size//3, cy - icon_size//3, 
                              cx + icon_size//3, cy + icon_size//3], 
                              fill="red", outline="white")

    img.save("json_debug_view.png")
    print("Saved 'json_debug_view.png'")

if __name__ == "__main__":
    render_json_to_image("world_data.json")