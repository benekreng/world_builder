import json
from PIL import Image, ImageDraw

def hex_to_rgb(hex_color):
    """Converts '#RRGGBB' to (R, G, B) tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def render_json_to_image(json_path):
    print(f"Loading {json_path}...")
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: world_data.json not found. Run the world builder first.")
        return

    # Create a blank canvas
    width, height = 1000, 1000
    img = Image.new("RGB", (width, height), "#f4f1ea") # Parchment background
    pixels = img.load()
    draw = ImageDraw.Draw(img)

    print(f"Found {len(data['entities'])} entities. Rendering pixels...")

    # 1. Render Cells (The Terrain/Shapes)
    for entity in data['entities']:
        # Get color from metadata, default to black if missing
        hex_color = entity['metadata'].get('color', '#000000')
        rgb_color = hex_to_rgb(hex_color)
        
        # Draw every single cell defined in the JSON
        for cell in entity['cells']:
            x, y = cell['x'], cell['y']
            # Bounds check just in case
            if 0 <= x < width and 0 <= y < height:
                pixels[x, y] = rgb_color

    # 2. Render Icons (The Metadata Overlay)
    print("Rendering icons...")
    for entity in data['entities']:
        for icon in entity.get('icons', []):
            origin = icon['origin']
            ox, oy = origin['x'], origin['y']
            
            # Draw a simple marker for the icon
            if icon['type'] == 'city':
                # Draw a black square with white border for cities
                draw.rectangle([ox-4, oy-4, ox+4, oy+4], fill="black", outline="white")
            elif icon['type'] == 'poi':
                # Draw a small red triangle/circle for landmarks
                draw.ellipse([ox-3, oy-3, ox+3, oy+3], fill="red", outline="white")

    # Save output
    output_filename = "json_debug_view.png"
    img.save(output_filename)
    print(f"Success! Debug view saved to {output_filename}")

if __name__ == "__main__":
    render_json_to_image("world_data.json")