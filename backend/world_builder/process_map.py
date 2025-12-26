import json
import sys
from pathlib import Path

# --- 1. SYSTEM PATH SETUP ---
# Get the absolute path of the current file
current_file = Path(__file__).resolve()

# Get the 'backend' directory (parent of 'world_builder')
backend_dir = current_file.parent.parent

# Add 'backend' to python path so we can import 'world_builder' modules
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

# --- 2. ABSOLUTE IMPORTS ---
# Now we import starting from the package name, NO dots (.)
from world_builder.models import FinalFeatureGraph
from world_builder.rasterizer import MapRasterizer

def run_processing():
    # Define paths relative to where this script is located
    script_dir = current_file.parent
    
    # Check for graph_dump.json in the same folder as this script, 
    # or in the parent folder (backend root)
    possible_paths = [
        backend_dir / "graph_dump.json",
        script_dir / "graph_dump.json",
        Path("graph_dump.json") # Current working dir
    ]
    
    input_path = None
    for p in possible_paths:
        if p.exists():
            input_path = p
            break
            
    if not input_path:
        print("Error: 'graph_dump.json' not found.")
        print(f"Searched in: {[str(p) for p in possible_paths]}")
        print("Please run the AI generation step (app.py) first to generate the dump.")
        return

    print(f"Loading raw data from: {input_path}")
    with open(input_path, 'r') as f:
        raw_data = json.load(f)

    # Rehydrate the Graph
    graph = FinalFeatureGraph(**raw_data)

    # ---------------------------------------------------------
    # TWEAK SETTINGS HERE
    # ---------------------------------------------------------
    GRID_W = 100
    GRID_H = 100
    # ---------------------------------------------------------

    print(f"Rasterizing to {GRID_W}x{GRID_H} grid...")
    
    # Run Rasterizer
    rasterizer = MapRasterizer(grid_width=GRID_W, grid_height=GRID_H, world_extent=1000)
    world_data = rasterizer.rasterize_to_json(graph)

    # Save Output
    output_path = "world_data.json"
    with open(output_path, 'w') as f:
        json.dump(world_data, f, indent=None)

    print(f"Success! Saved to '{output_path}'")
    print(f"Entities generated: {len(world_data['entities'])}")

if __name__ == "__main__":
    run_processing()