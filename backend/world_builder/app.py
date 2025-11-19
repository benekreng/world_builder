# main.py
import asyncio
from .router import LLMService 
import random

from langchain_core.output_parsers import PydanticOutputParser
from .chains.proto_chain import MapPipeline
from .models import FinalFeatureGraph

from pathlib import Path
import os
import json
import html

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

    # creates new world from scratch
    async def create_world(self, initial_prompt):
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
        CATEGORY_COLORS = {
            "Settlement": "#ffcc00",
            "River":      "#4da6ff",
            "Lake":       "#66ccff",
            "Sea":        "#0099ff",
            "MountainRange": "#996633",
            "Road":       "#999999",
            "Marsh":      "#669900",
            "Forest":     "#228b22",
            "Region":     "#cccccc",
            "Landmark":   "#ff6699",
            "Field":      "#b3d9b3",
            "Island":     "#ffd480"
        }

        svg_elements = []

        # Title & background
        svg_header = f"""<svg width="{width}" height="{height}" 
            viewBox="0 0 {width} {height}" 
            xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="#f8f8f8"/>
        """

        for feature in final_graph.features:
            if feature.position is None or feature.geometry is None:
                continue

            x = feature.position.x
            y = feature.position.y
            r = feature.geometry.radius
            color = CATEGORY_COLORS.get(feature.category, "#cc0000")  # fallback red

            # Escape label text
            label = html.escape(feature.name)

            # Draw circle
            svg_elements.append(f"""
                <circle 
                    cx="{x}" cy="{y}" r="{r}" 
                    fill="{color}" 
                    stroke="#333" 
                    stroke-width="1"
                    fill-opacity="0.8"
                />
            """)

            # Label (slightly offset)
            svg_elements.append(f"""
                <text 
                    x="{x + r + 5}" 
                    y="{y + 5}" 
                    font-size="12" 
                    font-family="Arial, sans-serif"
                    fill="#222">
                    {label}
                </text>
            """)

        svg_footer = "</svg>"

        return svg_header + "\n".join(svg_elements) + svg_footer

        
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