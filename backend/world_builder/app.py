import asyncio
from .router import LLMService 
import random
import json
import html
from pathlib import Path
import os
import copy 
from typing import Dict, Any, Optional, Literal, List

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

# Import models
from .models import (
    FinalFeatureGraph, 
    GenesisResponse, 
    EvolutionResponse, 
    WorldState, 
    AddFeatureOp, 
    EditFeatureOp, 
    RemoveFeatureOp,
    Vec2, 
    CircleGeometry, 
    SpineGeometry
)
from .chains.proto_chain import MapPipeline 
from .rasterizer import MapRasterizer

EXAMPLE_PROMPT_DIR = (Path(__file__).parent / 'test/example_user_prompts')
EXAMPLE_PROMPT = (EXAMPLE_PROMPT_DIR / "ex_1.prompt").read_text()

def generate_interpolated_spine(nodes, steps_per_segment=15):
    if not nodes or len(nodes) < 2:
        return []
    data = [(n.position.x, n.position.y, n.radius) for n in nodes]
    points = [data[0]] + data + [data[-1]]
    interpolated_circles = []
    for i in range(1, len(points) - 2):
        p0, p1, p2, p3 = points[i-1], points[i], points[i+1], points[i+2]
        for t_step in range(steps_per_segment):
            t = t_step / steps_per_segment
            t2 = t * t
            t3 = t2 * t
            def solve_axis(i_coord):
                c0 = p1[i_coord]
                c1 = 0.5 * (p2[i_coord] - p0[i_coord])
                c2 = 0.5 * (2*p0[i_coord] - 5*p1[i_coord] + 4*p2[i_coord] - p3[i_coord])
                c3 = 0.5 * (-p0[i_coord] + 3*p1[i_coord] - 3*p2[i_coord] + p3[i_coord])
                return c0 + c1*t + c2*t2 + c3*t3
            x = solve_axis(0)
            y = solve_axis(1)
            r = p1[2] + (p2[2] - p1[2]) * t
            interpolated_circles.append((x, y, r))
    last = data[-1]
    interpolated_circles.append((last[0], last[1], last[2]))
    return interpolated_circles

class WorldBuilder:
    def __init__(self):
        self._running = False
        self.llm_service = LLMService()
        #self.llm = self.llm_service.get_model("google/gemini-3.1-pro-preview")
        self.llm = self.llm_service.get_model("google/gemini-3-flash-preview")
        self.map_pipeline = MapPipeline(self.llm)

        #History State Management
        self.nodes: Dict[str, WorldState] = {}
        self.current_node_id: str | None = None
        self.root_node_id: str | None = None

    def get_current_state(self) -> WorldState | None:
        if self.current_node_id and self.current_node_id in self.nodes:
            return self.nodes[self.current_node_id]
        return None

    def get_history_meta(self):
        meta_list = []
        for nid, state in self.nodes.items():
            meta_list.append({
                "id": state.id,
                "parent_id": state.parent_id,
                "prompt": state.prompt,
                "type": state.step_type,
                "is_current": (nid == self.current_node_id)
            })
        return meta_list

    def get_ancestors(self, target_node_id: str) -> list[str]:
        path = []
        curr = target_node_id
        while curr and curr in self.nodes:
            node = self.nodes[curr]
            path.append(node.prompt)
            curr = node.parent_id
        return list(reversed(path))

    def jump_to_node(self, node_id: str):
        if node_id in self.nodes:
            self.current_node_id = node_id
            return True
        return False

    def delete_subtree(self, node_id: str):
        if node_id not in self.nodes: return
        
        #1. Find children
        children = [nid for nid, n in self.nodes.items() if n.parent_id == node_id]
        
        #2. Recurse
        for child in children:
            self.delete_subtree(child)
            
        #3. Delete self
        if self.current_node_id == node_id:
            #If we delete the current node, jump to parent
            self.current_node_id = self.nodes[node_id].parent_id
            
        del self.nodes[node_id]
        
        if node_id == self.root_node_id:
            self.root_node_id = None
            self.current_node_id = None
    
    #Wipes entire history
    def reset(self):
        self.nodes = {}
        self.current_node_id = None
        self.root_node_id = None

    #Genesis
    async def create_world(self, prompt: str):
        print(f"GENESIS: Generating new world from prompt...")
        
        final_graph = await self.map_pipeline.run(prompt)
        
        parser = PydanticOutputParser(pydantic_object=GenesisResponse)
        genesis_prompt = PromptTemplate(
            template="You are a world builder. Based on the user prompt: '{prompt}', write a thorough, novelistic fluid ground truth description of the world. \n\n{format_instructions}\n\nExisting Graph JSON to incorporate:\n{graph_json}",
            input_variables=["prompt", "graph_json"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        chain = genesis_prompt | self.llm | parser
        
        response: GenesisResponse = await chain.ainvoke({
            "prompt": prompt,
            "graph_json": final_graph.model_dump_json()
        })
        
        response.initial_graph = final_graph

        new_state = WorldState(
            fluid_truth=response.fluid_ground_truth, 
            graph=final_graph,
            prompt=prompt,
            step_type="genesis",
            parent_id=None
        )
        
        self.nodes[new_state.id] = new_state
        self.root_node_id = new_state.id
        self.current_node_id = new_state.id
        
        return new_state

    #Evolution
    async def update_world(self, user_prompt: str):
        print(f"Evolution: Updating world based on: '{user_prompt}'")
        current_state = self.get_current_state()
        if not current_state:
            raise Exception("Cannot update: No existing world.")

        #1. Prepare context
        simple_graph_context = []
        for f in current_state.graph.features:
            item = {
                "id": f.id, 
                "name": f.name, 
                "category": f.category,
                "attributes": f.attributes
            }
            if f.position:
                item["pos"] = {"x": int(f.position.x), "y": int(f.position.y)}
            simple_graph_context.append(item)
        
        parser = PydanticOutputParser(pydantic_object=EvolutionResponse)
        evolution_prompt = PromptTemplate(
            template="""You are the Keeper of History for a fantasy world.
            
            CURRENT WORLD STATE (Fluid Truth): 
            {fluid_truth}
            
            CURRENT LOCATIONS (Data): 
            {features}
            
            USER ACTION: {user_prompt}
            
            TASK:
            1. Update the Fluid Truth. Preserving existing details unless contradicted.
            2. Output Graph Operations to sync the map data.
            
            CRITICAL GEOMETRY RULES:
            - Every "ADD" or "EDIT" operation MUST include a valid "geometry" and "position".
            - Do NOT return null for geometry.
            - Coordinates are x,y (0-1000). (0,0) is Top-Left.
            
            ONE-SHOT EXAMPLE (Follow this format):
            {{
                "updated_fluid_ground_truth": "The city of Eldoria expanded...",
                "graph_updates": [
                    {{
                        "action": "add",
                        "feature": {{
                            "id": "f5", "name": "Eldoria", "category": "Settlement",
                            "attributes": {{ "population": "large" }},
                            "position": {{ "x": 450, "y": 300 }},
                            "geometry": {{ "kind": "circle", "radius": 20 }}
                        }}
                    }},
                    {{
                        "action": "edit", 
                        "id": "f2",
                        "changes": {{
                            "geometry": {{ "kind": "spine", "nodes": [ {{ "position": {{ "x": 100, "y": 100 }}, "radius": 5 }} ] }}
                        }}
                    }}
                ]
            }}
            
            {format_instructions}""",
            input_variables=["fluid_truth", "features", "user_prompt"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )

        chain = evolution_prompt | self.llm | parser
        response: EvolutionResponse = await chain.ainvoke({
            "fluid_truth": current_state.fluid_truth,
            "features": json.dumps(simple_graph_context),
            "user_prompt": user_prompt
        })

        print(f"Evolution generated {len(response.graph_updates)} operations.")

        #2. Apply operations
        new_graph = copy.deepcopy(current_state.graph)
        new_features = new_graph.features

        ops = response.graph_updates
        has_add = any(isinstance(op, AddFeatureOp) for op in ops)
        has_edit = any(isinstance(op, EditFeatureOp) for op in ops)
        has_remove = any(isinstance(op, RemoveFeatureOp) for op in ops)

        #Logic for step_type
        step_type = "mixed"
        if has_add and not has_edit and not has_remove: 
            step_type = "add"
        elif has_remove and not has_add and not has_edit: 
            step_type = "remove"
        elif has_edit and not has_add and not has_remove: 
            step_type = "edit"
        elif not ops: 
            step_type = "edit"

        for op in response.graph_updates:
            if isinstance(op, AddFeatureOp):
                new_features.append(op.feature)
            
            elif isinstance(op, RemoveFeatureOp):
                new_features = [f for f in new_features if f.id != op.id]
            
            elif isinstance(op, EditFeatureOp):
                for feature in new_features:
                    if feature.id == op.id:
                        for key, val in op.changes.items():
                            if hasattr(feature, key):
                                if key == 'position' and isinstance(val, dict):
                                    val = Vec2(**val)
                                elif key == 'geometry' and isinstance(val, dict):
                                    if val.get('kind') == 'spine':
                                        val = SpineGeometry(**val)
                                    else:
                                        val = CircleGeometry(**val)
                                setattr(feature, key, val)

        new_graph.features = new_features

        #3. Save State
        new_state = WorldState(
            fluid_truth=response.updated_fluid_ground_truth,
            graph=new_graph,
            prompt=user_prompt,
            step_type=step_type,
            parent_id=current_state.id,
            seed=current_state.seed
        )

        self.nodes[new_state.id] = new_state
        self.current_node_id = new_state.id

        return new_state

    def save_to_dict(self) -> Dict[str, Any]:
        return {
            "root_node_id": self.root_node_id,
            "current_node_id": self.current_node_id,
            "nodes": {
                nid: node.model_dump() 
                for nid, node in self.nodes.items()
            }
        }

    def load_from_dict(self, data: Dict[str, Any]):
        try:
            self.nodes = {}
            for nid, raw_node in data["nodes"].items():
                self.nodes[nid] = WorldState(**raw_node)
            
            self.root_node_id = data.get("root_node_id")
            self.current_node_id = data.get("current_node_id")
            return True
        except Exception as e:
            print(f"Load failed: {e}")
            return False

    #Renderer
    def render_svg(self, final_graph, width=1000, height=1000):
        CATEGORY_COLORS = {
            "Settlement": "#d4a017", "River": "#4f8cbf", "Lake": "#89c4d9",
            "Sea": "#2b6a99", "MountainRange": "#8c7b64", "Forest": "#5c8a56",
            "Region": "#dcd3c1", "Landmark": "#c25e5e", "Marsh": "#8f915e",
            "Road": "#b0a090"
        }
        svg_out = [f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">']
        svg_out.append('''
        <defs>
            <filter id="solid-area">
                <feMorphology operator="dilate" radius="1" in="SourceGraphic" result="dilated"/>
                <feGaussianBlur stdDeviation="0.5" in="dilated" />
            </filter>
        </defs>
        <rect width="100%" height="100%" fill="#f4f1ea"/> 
        ''')

        priority_order = ["Sea", "Region", "Marsh", "Forest", "MountainRange", "Lake", "River", "Road", "Landmark", "Settlement"]
        def get_prio(cat):
            try: return priority_order.index(cat)
            except: return -1

        sorted_features = sorted(final_graph.features, key=lambda f: get_prio(f.category))

        for feature in sorted_features:
            if not feature.geometry: continue
            name = html.escape(feature.name)
            color = CATEGORY_COLORS.get(feature.category, "#aaaaaa")
            style = 'style="mix-blend-mode: multiply;"'

            if feature.geometry.kind == "spine":
                nodes = feature.geometry.nodes
                if not nodes: continue
                spine_points = generate_interpolated_spine(nodes, steps_per_segment=20)
                svg_out.append(f'<g filter="url(#solid-area)" fill="{color}" fill-opacity="0.5" {style}>')
                for (cx, cy, r) in spine_points:
                    svg_out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" stroke="none" />')
                svg_out.append('</g>')
                if spine_points:
                    mid = spine_points[len(spine_points)//2]
                    svg_out.append(f'''
                        <text x="{mid[0]:.1f}" y="{mid[1]:.1f}" 
                            text-anchor="middle" font-size="14" font-family="Georgia, serif" fill="#222" 
                            font-style="italic" style="text-shadow: 1px 1px 2px #fff; pointer-events: none;">{name}</text>
                    ''')

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
