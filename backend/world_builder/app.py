# main.py
import asyncio
from .router import LLMService 
import random

from langchain_core.output_parsers import PydanticOutputParser
from .chains.proto_chain import MapPipeline
from .models import FinalFeatureGraph
from .rasterizer import MapRasterizer

from pathlib import Path
import os
import json
import html

def generate_interpolated_spine(nodes, steps_per_segment=15):
    """
    Instead of returning an SVG path string, this returns a list of (x, y, radius) tuples.
    It interpolates position (Catmull-Rom) AND radius (Linear) to create a variable-width shape.
    """
    if not nodes or len(nodes) < 2:
        return []

    # Extract data: [(x, y, r), ...]
    data = [(n.position.x, n.position.y, n.radius) for n in nodes]
    
    # Duplicate start/end for Catmull-Rom control points
    points = [data[0]] + data + [data[-1]]
    
    interpolated_circles = []

    for i in range(1, len(points) - 2):
        p0, p1, p2, p3 = points[i-1], points[i], points[i+1], points[i+2]
        
        # Iterate through the segment between p1 and p2
        for t_step in range(steps_per_segment):
            t = t_step / steps_per_segment
            t2 = t * t
            t3 = t2 * t

            # 1. Catmull-Rom Position Interpolation
            # Formula: 0.5 * ( (2*p1) + (-p0 + p2)*t + (2*p0 - 5*p1 + 4*p2 - p3)*t2 + (-p0 + 3*p1 - 3*p2 + p3)*t3 )
            
            def solve_axis(i_coord):
                c0 = p1[i_coord]
                c1 = 0.5 * (p2[i_coord] - p0[i_coord])
                c2 = 0.5 * (2*p0[i_coord] - 5*p1[i_coord] + 4*p2[i_coord] - p3[i_coord])
                c3 = 0.5 * (-p0[i_coord] + 3*p1[i_coord] - 3*p2[i_coord] + p3[i_coord])
                return c0 + c1*t + c2*t2 + c3*t3

            x = solve_axis(0)
            y = solve_axis(1)

            # 2. Linear Radius Interpolation
            # Smoothly blend radius from p1 to p2
            r = p1[2] + (p2[2] - p1[2]) * t

            interpolated_circles.append((x, y, r))
    
    # Add the final point explicitly
    last = data[-1]
    interpolated_circles.append((last[0], last[1], last[2]))
    
    return interpolated_circles

def catmull_rom_spline(nodes):
    """
    Generates an SVG path string for a Catmull-Rom spline passing through all nodes.
    This makes lines curve smoothly through points instead of jagged straight lines.
    """
    if not nodes or len(nodes) < 2:
        return ""
    
    # Extract x,y coordinates
    points = [(n.position.x, n.position.y) for n in nodes]
    
    # Duplicate start and end points to ensure the curve goes through them
    points = [points[0]] + points + [points[-1]]
    
    path_data = f"M {points[1][0]},{points[1][1]}"
    
    for i in range(1, len(points) - 2):
        p0, p1, p2, p3 = points[i-1], points[i], points[i+1], points[i+2]
        
        # Catmull-Rom logic
        cp1x = p1[0] + (p2[0] - p0[0]) / 6.0
        cp1y = p1[1] + (p2[1] - p0[1]) / 6.0
        
        cp2x = p2[0] - (p3[0] - p1[0]) / 6.0
        cp2y = p2[1] - (p3[1] - p1[1]) / 6.0
        
        path_data += f" C {cp1x:.1f},{cp1y:.1f} {cp2x:.1f},{cp2y:.1f} {p2[0]},{p2[1]}"
        
    return path_data


class WorldBuilder:
    def __init__(self):
        self._running = False
        self.llm_service = LLMService()
        self.llm = self.llm_service.get_model("google/gemini-3-pro-preview")
        self.current_world = -1
        self.map_pipeline = MapPipeline(self.llm)

    async def start(self):
        self._running = True

    async def stop(self):
        self._running = False 

    async def test_async(self):
        await asyncio.sleep(1)

    async def create_world(self, initial_prompt):
        print(f"Generating world from prompt...")
        
        # 1. Run AI Pipeline
        final_graph = await self.map_pipeline.run(initial_prompt)
        
        # 2. Render Visual SVG (For your reference)
        svg_string = self.render_svg(final_graph)
        with open('map.svg', 'w') as f:
            f.write(svg_string)

        # 3. DUMP RAW DATA (This is the key step!)
        # We save the graph structure to disk so the standalone script can load it.
        with open('graph_dump.json', 'w') as f:
            f.write(final_graph.model_dump_json(indent=4))
            
        print("Success! Saved 'map.svg' and 'graph_dump.json'.")
        print("Now run 'python -m world_builder.process_map' to tweak rasterization.")
        return 0

    def save_debug_grid(self, grid):
        """Helper to visualize the raw data grid."""
        import numpy as np
        from PIL import Image
        
        # Normalize grid to 0-255 for visualization
        # We multiply by 20 just to make different IDs distinct shades of gray/color
        visual_grid = (grid * 20).astype(np.uint8)
        img = Image.fromarray(visual_grid, mode='L') # L = Grayscale
        img.save("map_debug_raster.png")
        print("Saved map_debug_raster.png")

    # creates new world from scratch
    async def create_worldOld(self, initial_prompt):
        new_world = World()
        self.current_world_id = new_world.id


        final_graph = await self.map_pipeline.run(initial_prompt)
        print(json.dumps(final_graph.model_dump(), indent=4))

        # print(os.getcwd())
        # with open('world_builder/test.json') as f:
        #     data = json.load(f)
        #     final_graph = FinalFeatureGraph(**data)

        svg_string = self.render_svg(final_graph)
        with open('map.svg', 'w') as f:
            f.write(svg_string)

        # try:
        # except Exception as e:
        #     print(f"Processing world failed {e}")

        # update world
        
        # store world timestamp
        return new_world.id

    import html

    def render_svg(self, final_graph, width=1000, height=1000):
        # Colors optimized for a "Parchment Map" style
        CATEGORY_COLORS = {
            "Settlement": "#d4a017",      # Gold
            "River":      "#4f8cbf",      # Blue
            "Lake":       "#89c4d9",      # Light Blue
            "Sea":        "#2b6a99",      # Deep Sea
            "MountainRange": "#8c7b64",   # Brown
            "Forest":     "#5c8a56",      # Green
            "Region":     "#dcd3c1",      # Darker Parchment
            "Landmark":   "#c25e5e",      # Red
            "Marsh":      "#8f915e",      # Swamp
            "Road":       "#b0a090"       # Faded Road
        }

        # Header
        svg_out = [f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">']
        
        # Filters to blend the overlapping circles into one organic shape
        svg_out.append('''
        <defs>
            <filter id="solid-area">
                 <!-- Dilate slightly to merge gaps, then blur to smooth edges -->
                 <feMorphology operator="dilate" radius="1" in="SourceGraphic" result="dilated"/>
                 <feGaussianBlur stdDeviation="0.5" in="dilated" />
            </filter>
        </defs>
        <rect width="100%" height="100%" fill="#f4f1ea"/> 
        ''')

        # Sorting: Draw large/flat areas first, points last
        priority_order = ["Sea", "Region", "Marsh", "Forest", "MountainRange", "Lake", "River", "Road", "Landmark", "Settlement"]
        
        def get_prio(cat):
            try: return priority_order.index(cat)
            except: return -1

        sorted_features = sorted(final_graph.features, key=lambda f: get_prio(f.category))

        for feature in sorted_features:
            if not feature.geometry: continue
            
            name = html.escape(feature.name)
            color = CATEGORY_COLORS.get(feature.category, "#aaaaaa")
            
            # Use 'multiply' so overlapping shapes (forest on region) look like layered ink
            style = 'style="mix-blend-mode: multiply;"'

            # --- SPINE GEOMETRY (The "Proper Area" Logic) ---
            if feature.geometry.kind == "spine":
                nodes = feature.geometry.nodes
                if not nodes: continue

                # Generate the "slug" of circles
                # Increase 'steps_per_segment' if you see gaps (e.g., 20 or 30)
                spine_points = generate_interpolated_spine(nodes, steps_per_segment=20)
                
                # Group them so we can apply one filter to the whole shape
                svg_out.append(f'<g filter="url(#solid-area)" fill="{color}" fill-opacity="0.5" {style}>')
                
                for (cx, cy, r) in spine_points:
                    # Draw overlapping circles to create the variable-width area
                    svg_out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" stroke="none" />')
                
                svg_out.append('</g>')

                # Label at the visual center (middle sample)
                if spine_points:
                    mid = spine_points[len(spine_points)//2]
                    svg_out.append(f'''
                        <text x="{mid[0]:.1f}" y="{mid[1]:.1f}" 
                            text-anchor="middle" font-size="14" font-family="Georgia, serif" fill="#222" 
                            font-style="italic" style="text-shadow: 1px 1px 2px #fff; pointer-events: none;">{name}</text>
                    ''')

            # --- CIRCLE GEOMETRY ---
            elif feature.geometry.kind == "circle":
                x, y, r = feature.position.x, feature.position.y, feature.geometry.radius
                
                svg_out.append(f'''
                    <circle cx="{x}" cy="{y}" r="{r}" 
                        fill="{color}" fill-opacity="0.8" stroke="#333" stroke-width="1"
                         {style} />
                ''')
                
                svg_out.append(f'''
                    <text x="{x}" y="{y}" dy="{r + 15}" 
                        text-anchor="middle" font-size="12" font-family="Georgia, serif" fill="#111" font-weight="bold"
                        style="text-shadow: 1px 1px 0 #fff;">{name}</text>
                ''')

        svg_out.append("</svg>")
        return "\n".join(svg_out)

    def render_svgOld(self, final_graph, width=1000, height=1000):
        CATEGORY_COLORS = {
            "Settlement": "#ffcc00", "River": "#4da6ff", "Lake": "#66ccff",
            "Sea": "#0099ff", "MountainRange": "#996633", "Forest": "#228b22",
            "Region": "#cccccc", "Landmark": "#ff6699"
        }

        # START: The critical SVG header
        svg_out = [f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">']
        svg_out.append('<rect width="100%" height="100%" fill="#f4f1ea"/>')

        for feature in final_graph.features:
            if not feature.geometry: continue
            color = CATEGORY_COLORS.get(feature.category, "#aaaaaa")
            name = html.escape(feature.name)

            if feature.geometry.kind == "circle":
                x, y, r = feature.position.x, feature.position.y, feature.geometry.radius
                svg_out.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}" fill-opacity="0.7" stroke="#333" />')
                svg_out.append(f'<text x="{x + r + 5}" y="{y + 5}" font-size="10" font-family="serif">{name}</text>')

            elif feature.geometry.kind == "spine":
                nodes = feature.geometry.nodes
                if not nodes: continue

                # Volume: Draw a line between nodes and circles at every node
                d_pts = [f"{n.position.x},{n.position.y}" for n in nodes]
                path_data = f"M {d_pts[0]} " + " ".join([f"L {p}" for p in d_pts[1:]])
                avg_r = sum(n.radius for n in nodes) / len(nodes)
                
                # The 'Bridge' line
                svg_out.append(f'<path d="{path_data}" fill="none" stroke="{color}" stroke-width="{avg_r * 1.5}" stroke-opacity="0.4" stroke-linecap="round" />')
                
                # The Circles at nodes (Varying Width)
                for node in nodes:
                    svg_out.append(f'<circle cx="{node.position.x}" cy="{node.position.y}" r="{node.radius}" fill="{color}" fill-opacity="0.5" />')

                # Label at center
                lx, ly = (feature.position.x, feature.position.y) if feature.position else (nodes[0].position.x, nodes[0].position.y)
                svg_out.append(f'<text x="{lx}" y="{ly}" text-anchor="middle" font-size="12" font-weight="bold" font-family="serif">{name}</text>')

        svg_out.append("</svg>") # END: Close the tag
        return "\n".join(svg_out)

    async def _process_world_start(self, world):
        return 0

    async def fetch_worlds():
        return
    
    async def append_to_world(self, initial_message, world_id):
        return

class World:
    def __init__(self):
        self.id = random.getrandbits(256)
        self._entities_hist = [{}]
        self._world_state_hist = [""]
    
    def rewind(self):
        del self._entities_hist[:-1]
        del self._world_state_hist[:-1]
    
    def get_entities_obj(self, t=0):
        # get entities as timestamp t
        t_idx = (len_(self.entities_hist) - 1) - t
        return self._entities_hist[t_idx] 
    
    def get_world_state_str(self, t=0):
        # get entities as timestamp t
        t_idx = (len_(self._world_state_hist) - 1) - t
        return self._world_state_hist[t_idx] 

    def update(self, entities, world_state):
        if not isinstance(entities, obj):
            raise TypeError("Entities is not of type object!")
        self._entities_hist.append(entities)

        if not isinstance(world_state, str):
            raise TypeError("World_state is not of type object!")
        self._world_state_hist.append(world_state)