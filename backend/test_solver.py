import json
import math
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.lines as mlines

# ==========================================
# 1. PASTE LLM OUTPUT HERE
# ==========================================

LLM_JSON_OUTPUT = """
{
  "map_metadata": {
    "flow_direction": "NW_TO_SE",
    "dominant_axis": "Horizontal",
    "region_name": "The Vale of Thareth"
  },
  "entities": [
    {
      "id": "loc_glimmerstone",
      "name": "Glimmerstone Peaks",
      "type": "Mountain",
      "elevation_tier": 10,
      "size": "Large"
    },
    {
      "id": "loc_hearthwind",
      "name": "Hearthwind Pass",
      "type": "Landmark",
      "elevation_tier": 9,
      "size": "Small"
    },
    {
      "id": "city_veylen",
      "name": "Veylen",
      "type": "City",
      "elevation_tier": 8,
      "size": "Small"
    },
    {
      "id": "poi_whispering_bridge",
      "name": "The Whispering Bridge",
      "type": "RiverNode",
      "elevation_tier": 7,
      "size": "Small"
    },
    {
      "id": "poi_mirror_lakes",
      "name": "The Mirror Lakes",
      "type": "Landmark",
      "elevation_tier": 6,
      "size": "Medium"
    },
    {
      "id": "city_thareths_gate",
      "name": "Thareth's Gate",
      "type": "City",
      "elevation_tier": 5,
      "size": "Large"
    },
    {
      "id": "poi_stonefather",
      "name": "Stonefather's Step",
      "type": "RiverNode",
      "elevation_tier": 4,
      "size": "Small"
    },
    {
      "id": "city_cendara",
      "name": "Cendara",
      "type": "City",
      "elevation_tier": 4,
      "size": "Medium"
    },
    {
      "id": "poi_othiriel",
      "name": "Ruins of Othiriel",
      "type": "Landmark",
      "elevation_tier": 5,
      "size": "Medium"
    },
    {
      "id": "city_woaden_ford",
      "name": "Woaden Ford",
      "type": "City",
      "elevation_tier": 3,
      "size": "Medium"
    },
    {
      "id": "env_blackfen",
      "name": "The Blackfen",
      "type": "Swamp",
      "elevation_tier": 2,
      "size": "Large"
    },
    {
      "id": "env_emberfields",
      "name": "The Emberfields",
      "type": "Plain",
      "elevation_tier": 2,
      "size": "Large"
    },
    {
      "id": "city_ashmere",
      "name": "Ashmere",
      "type": "City",
      "elevation_tier": 2,
      "size": "Small"
    },
    {
      "id": "env_serran_floodplain",
      "name": "Serran Floodplain",
      "type": "Plain",
      "elevation_tier": 1,
      "size": "Large"
    },
    {
      "id": "node_river_source_nw",
      "name": "Glacial Melt",
      "type": "RiverNode",
      "elevation_tier": 9,
      "size": "Small"
    }
  ],
  "paths": [
    {
      "id": "river_thareth",
      "type": "River",
      "ordered_node_ids": [
        "node_river_source_nw",
        "poi_whispering_bridge",
        "city_thareths_gate",
        "poi_stonefather",
        "city_cendara",
        "city_woaden_ford",
        "env_blackfen",
        "env_serran_floodplain"
      ]
    },
    {
      "id": "river_lune",
      "type": "River",
      "ordered_node_ids": [
        "poi_mirror_lakes",
        "city_woaden_ford"
      ]
    },
    {
      "id": "road_mountain_trade",
      "type": "Road",
      "ordered_node_ids": [
        "loc_hearthwind",
        "city_veylen",
        "city_thareths_gate"
      ]
    },
    {
      "id": "road_valley_main",
      "type": "Road",
      "ordered_node_ids": [
        "city_thareths_gate",
        "city_cendara",
        "city_woaden_ford",
        "city_ashmere"
      ]
    },
    {
      "id": "path_aqueduct",
      "type": "Road",
      "ordered_node_ids": [
        "poi_othiriel",
        "city_cendara"
      ]
    }
  ],
  "constraints": [
    {
      "source": "loc_glimmerstone",
      "target": "city_thareths_gate",
      "relation": "NorthOf",
      "strength": "High"
    },
    {
      "source": "city_veylen",
      "target": "city_thareths_gate",
      "relation": "NorthOf",
      "strength": "Medium"
    },
    {
      "source": "poi_whispering_bridge",
      "target": "city_thareths_gate",
      "relation": "WestOf",
      "strength": "High"
    },
    {
      "source": "city_cendara",
      "target": "city_thareths_gate",
      "relation": "EastOf",
      "strength": "Medium"
    },
    {
      "source": "poi_othiriel",
      "target": "city_cendara",
      "relation": "NorthOf",
      "strength": "High"
    },
    {
      "source": "poi_mirror_lakes",
      "target": "city_cendara",
      "relation": "NorthOf",
      "strength": "Medium"
    },
    {
      "source": "env_blackfen",
      "target": "city_cendara",
      "relation": "EastOf",
      "strength": "High"
    },
    {
      "source": "env_emberfields",
      "target": "city_woaden_ford",
      "relation": "SouthOf",
      "strength": "Medium"
    },
    {
      "source": "city_ashmere",
      "target": "env_emberfields",
      "relation": "Inside",
      "strength": "High"
    }
  ]
} 
"""

# ==========================================
# 2. DATA MODELS
# ==========================================

class EntityNode:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.type = data['type']
        self.tier = data.get('elevation_tier', 5)
        self.size = data.get('size', 'Medium')
        self.x = 50.0 
        self.y = 50.0

class PathObject:
    def __init__(self, data):
        self.id = data['id']
        self.type = data['type'] # River vs Road
        self.node_ids = data['ordered_node_ids']

class SpatialConstraint:
    def __init__(self, data):
        self.source = data['source']
        self.target = data['target']
        self.relation = data['relation']
        self.strength = data.get('strength', 'Medium')

class MapGraph:
    def __init__(self, json_data):
        data = json.loads(json_data)
        self.metadata = data.get('map_metadata', {})
        self.entities = [EntityNode(e) for e in data['entities']]
        self.paths = [PathObject(p) for p in data.get('paths', [])]
        self.constraints = [SpatialConstraint(c) for c in data.get('constraints', [])]

# ==========================================
# 3. SOLVER V5 (Separated Road/River Physics)
# ==========================================

class LayoutSolverV5:
    def __init__(self):
        self.ITERATIONS = 500
        self.REPULSION = 600.0
        self.MAX_SPEED = 2.0
        
        # Physics Config
        self.RIVER_TENSION = 0.8       # Rivers are tight
        self.ROAD_TENSION = 0.4        # Roads are looser
        self.RIVER_STRAIGHTNESS = 0.5  # Rivers resist bending
        self.GLOBAL_GRAVITY = 0.15     # Water flows downhill
        
    def _get_start_vector(self, direction):
        if direction == "NW_TO_SE": return (10, 10), (90, 90), (0.5, 0.5)
        elif direction == "N_TO_S": return (50, 10), (50, 90), (0.0, 1.0)
        elif direction == "W_TO_E": return (10, 50), (90, 50), (1.0, 0.0)
        return (50, 50), (50, 50), (0,0)

    def solve(self, graph):
        nodes = graph.entities
        node_map = {n.id: n for n in nodes}
        
        # --- PHASE 1: SMART INITIALIZATION ---
        flow_dir = graph.metadata.get('flow_direction', "NW_TO_SE")
        start_pos, end_pos, gravity_vec = self._get_start_vector(flow_dir)
        
        print(f"   > Initializing layout based on {flow_dir} flow...")
        for n in nodes:
            t = (10 - n.tier) / 9.0 
            t = max(0.0, min(1.0, t))
            ideal_x = start_pos[0] + (end_pos[0] - start_pos[0]) * t
            ideal_y = start_pos[1] + (end_pos[1] - start_pos[1]) * t
            n.x = ideal_x + random.uniform(-10, 10)
            n.y = ideal_y + random.uniform(-10, 10)

        # --- PHASE 2: SIMULATION ---
        print(f"   > Running {self.ITERATIONS} iterations...")
        
        for i in range(self.ITERATIONS):
            temp = 1.0 - (i / self.ITERATIONS)
            forces = {n.id: {'x': 0.0, 'y': 0.0} for n in nodes}

            # 1. REPULSION
            for j, n1 in enumerate(nodes):
                for k, n2 in enumerate(nodes):
                    if j == k: continue
                    dx = n1.x - n2.x
                    dy = n1.y - n2.y
                    dist_sq = dx*dx + dy*dy + 0.5
                    dist = math.sqrt(dist_sq)
                    if dist < 12.0:
                        f = self.REPULSION / dist_sq
                        forces[n1.id]['x'] += (dx/dist) * f
                        forces[n1.id]['y'] += (dy/dist) * f

            # 2. PATH PHYSICS
            for path in graph.paths:
                node_ids = path.node_ids
                is_river = (path.type == "River")
                
                # Tension Config
                tension = self.RIVER_TENSION if is_river else self.ROAD_TENSION
                straightness = self.RIVER_STRAIGHTNESS if is_river else 0.1
                
                for idx in range(len(node_ids)):
                    curr_id = node_ids[idx]
                    if curr_id not in node_map: continue
                    
                    # A. GRAVITY (Rivers Only!)
                    # Roads do not flow downhill automatically.
                    if is_river:
                        forces[curr_id]['x'] += gravity_vec[0] * self.GLOBAL_GRAVITY * 5
                        forces[curr_id]['y'] += gravity_vec[1] * self.GLOBAL_GRAVITY * 5

                    # B. SPRING TENSION (Connect to Next)
                    if idx < len(node_ids) - 1:
                        next_id = node_ids[idx+1]
                        if next_id in node_map:
                            s, t = node_map[curr_id], node_map[next_id]
                            dx, dy = t.x - s.x, t.y - s.y
                            dist = math.sqrt(dx*dx + dy*dy) + 0.1
                            
                            target_dist = 10.0 if is_river else 15.0 # Roads are longer/looser
                            disp = dist - target_dist
                            f = disp * tension
                            
                            fx = (dx/dist) * f
                            fy = (dy/dist) * f
                            
                            forces[s.id]['x'] += fx
                            forces[s.id]['y'] += fy
                            forces[t.id]['x'] -= fx
                            forces[t.id]['y'] -= fy

                    # C. STRAIGHTENING (Spline Smoothing) - Mostly for Rivers
                    if idx > 0 and idx < len(node_ids) - 1:
                        prev_id = node_ids[idx-1]
                        next_id = node_ids[idx+1]
                        if prev_id in node_map and next_id in node_map:
                            p, c, n = node_map[prev_id], node_map[curr_id], node_map[next_id]
                            mid_x = (p.x + n.x) / 2
                            mid_y = (p.y + n.y) / 2
                            dx = mid_x - c.x
                            dy = mid_y - c.y
                            forces[c.id]['x'] += dx * straightness
                            forces[c.id]['y'] += dy * straightness

            # 3. CONSTRAINTS
            for c in graph.constraints:
                if c.source not in node_map or c.target not in node_map: continue
                s, t = node_map[c.source], node_map[c.target]
                
                # Directional
                if c.relation in ["NorthOf", "SouthOf", "EastOf", "WestOf"]:
                    STRENGTH = 1.0 if c.strength == "Medium" else 2.5
                    PENALTY = 5.0
                    
                    if c.relation == "NorthOf":
                        forces[s.id]['y'] -= STRENGTH
                        forces[t.id]['y'] += STRENGTH
                        if s.y > t.y: forces[s.id]['y'] -= PENALTY
                    elif c.relation == "SouthOf":
                        forces[s.id]['y'] += STRENGTH
                        forces[t.id]['y'] -= STRENGTH
                        if s.y < t.y: forces[s.id]['y'] += PENALTY
                    elif c.relation == "EastOf":
                        forces[s.id]['x'] += STRENGTH
                        forces[t.id]['x'] -= STRENGTH
                        if s.x < t.x: forces[s.id]['x'] += PENALTY
                    elif c.relation == "WestOf":
                        forces[s.id]['x'] -= STRENGTH
                        forces[t.id]['x'] += STRENGTH
                        if s.x > t.x: forces[s.id]['x'] -= PENALTY
                        
                # Special Logic: INSIDE
                elif c.relation == "Inside":
                    # Strong Magnet to Center
                    STRENGTH = 2.0
                    dx = t.x - s.x
                    dy = t.y - s.y
                    forces[s.id]['x'] += dx * STRENGTH
                    forces[s.id]['y'] += dy * STRENGTH
                    
                # Proximity (Near)
                else:
                    target_dist = 5.0
                    stiffness = 0.5
                    dx = t.x - s.x; dy = t.y - s.y
                    dist = math.sqrt(dx*dx + dy*dy) + 0.1
                    f = (dist - target_dist) * stiffness
                    fx = (dx/dist)*f; fy = (dy/dist)*f
                    forces[s.id]['x'] += fx; forces[s.id]['y'] += fy
                    forces[t.id]['x'] -= fx; forces[t.id]['y'] -= fy

            # 4. UPDATE
            for n in nodes:
                fx = max(-self.MAX_SPEED, min(self.MAX_SPEED, forces[n.id]['x']))
                fy = max(-self.MAX_SPEED, min(self.MAX_SPEED, forces[n.id]['y']))
                n.x += fx * temp
                n.y += fy * temp
                n.x = max(5, min(95, n.x))
                n.y = max(5, min(95, n.y))

# ==========================================
# 4. VISUALIZER
# ==========================================

def draw_map(graph):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_ylim(100, 0) # 0 is North
    ax.set_xlim(0, 100)
    ax.set_facecolor('#f0f4f8')
    ax.set_title("Solver V5: Road vs River Physics")

    node_map = {n.id: n for n in graph.entities}

    # Draw Paths
    for path in graph.paths:
        coords = []
        for nid in path.node_ids:
            if nid in node_map:
                n = node_map[nid]
                coords.append((n.x, n.y))
        
        if len(coords) > 1:
            color = '#3b82f6' if path.type == "River" else '#d97706'
            width = 4 if path.type == "River" else 2
            style = '-' if path.type == "River" else '--'
            
            for i in range(len(coords)-1):
                p1 = coords[i]
                p2 = coords[i+1]
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], c=color, lw=width, ls=style, alpha=0.7, zorder=2)
                
                if path.type == "River":
                    ax.annotate("", xy=p2, xytext=p1, arrowprops=dict(arrowstyle="->", color=color, lw=2))

    # Draw Nodes
    for n in graph.entities:
        color = 'grey'
        size = 2
        
        if n.type == "City": color = '#ef4444'; size=4
        elif n.type == "Mountain": color = '#1f2937'; size=5
        elif n.type == "Plain": color = '#84cc16'; size=6; alpha=0.3
        elif n.type == "Swamp": color = '#7e22ce'
        elif n.type == "RiverNode": color = '#3b82f6'; size=1.5
        
        circle = patches.Circle((n.x, n.y), radius=size, color=color, zorder=5)
        ax.add_patch(circle)
        
        if n.type != "RiverNode":
            ax.text(n.x, n.y+size+1.5, n.name, ha='center', fontsize=8, fontweight='bold',
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=0.5), zorder=6)

    plt.grid(True, alpha=0.1)
    plt.show()

if __name__ == "__main__":
    g = MapGraph(LLM_JSON_OUTPUT)
    solver = LayoutSolverV5()
    solver.solve(g)
    draw_map(g)