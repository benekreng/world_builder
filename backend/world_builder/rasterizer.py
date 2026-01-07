import numpy as np
import random
from PIL import Image, ImageDraw
from .models import FinalFeatureGraph
# IMPORT THE NEW GENERATOR
from .road_generator import RoadGenerator

class MapRasterizer:
    def __init__(self, grid_width=64, grid_height=64, world_extent=1000):
        self.width = grid_width
        self.height = grid_height
        self.scale_x = grid_width / world_extent
        self.scale_y = grid_height / world_extent
        
        self.PRIORITY = {
            "Region": 0, "Field": 1, "Marsh": 2, "Forest": 3,
            "MountainRange": 4, "Road": 5, "Lake": 6, 
            "River": 7, "Sea": 7, 
            "Landmark": 8, "Settlement": 9
        }
        
        self.COLORS = {
            "Settlement": "#d4a017", "River": "#4f8cbf", "Lake": "#89c4d9",
            "Sea": "#2b6a99", "MountainRange": "#8c7b64", "Forest": "#5c8a56",
            "Region": "#dcd3c1", "Landmark": "#c25e5e", "Marsh": "#8f915e",
            "Road": "#b0a090", "Field": "#b5c99a"
        }
        
        self.CATEGORY_IDS = {k: i for i, k in enumerate(self.PRIORITY.keys(), 1)}
        self.TREE_TYPES = ["tree_oak", "tree_pine", "tree_palm", "tree_birch", "tree_maple", "tree_sakura"]

    def _scale_point(self, x, y, r):
        sx = x * self.scale_x
        sy = y * self.scale_y
        sr = r * max(self.scale_x, self.scale_y)
        return sx, sy, sr

    def _generate_interpolated_points(self, nodes, steps_per_segment=20):
        if not nodes or len(nodes) < 2: return []
        data = [(n.position.x, n.position.y, n.radius) for n in nodes]
        points = [data[0]] + data + [data[-1]]
        interpolated = []
        for i in range(1, len(points) - 2):
            p0, p1, p2, p3 = points[i-1], points[i], points[i+1], points[i+2]
            for t_step in range(steps_per_segment):
                t = t_step / steps_per_segment
                t2, t3 = t*t, t*t*t
                def solve(idx):
                    return 0.5 * ((2*p1[idx]) + (-p0[idx] + p2[idx])*t + 
                           (2*p0[idx] - 5*p1[idx] + 4*p2[idx] - p3[idx])*t2 + 
                           (-p0[idx] + 3*p1[idx] - 3*p2[idx] + p3[idx])*t3)
                world_r = p1[2] + (p2[2] - p1[2]) * t
                sx, sy, sr = self._scale_point(solve(0), solve(1), world_r)
                interpolated.append((sx, sy, sr))
        last = data[-1]
        sx, sy, sr = self._scale_point(last[0], last[1], last[2])
        interpolated.append((sx, sy, sr))
        return interpolated

    def _get_feature_mask(self, feature, override_pos=None):
        img = Image.new("1", (self.width, self.height), 0)
        draw = ImageDraw.Draw(img)
        if override_pos:
            sx, sy = override_pos
            _, _, sr = self._scale_point(0, 0, feature.geometry.radius)
        else:
            sx, sy, sr = self._scale_point(feature.position.x, feature.position.y, feature.geometry.radius)
        if feature.geometry.kind == "circle":
            draw.ellipse([sx-sr, sy-sr, sx+sr, sy+sr], fill=1)
        elif feature.geometry.kind == "spine":
            points = self._generate_interpolated_points(feature.geometry.nodes)
            for (cx, cy, r) in points:
                draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=1)
        return np.array(img, dtype=bool)

    def _create_square_mask_from_plus(self, mask):
        y_idxs, x_idxs = np.where(mask)
        if len(y_idxs) == 0: return mask
        min_y, min_x = np.min(y_idxs), np.min(x_idxs)
        new_mask = np.zeros_like(mask)
        new_mask[min_y:min_y+2, min_x:min_x+2] = True
        return new_mask

    def _find_new_position_mask(self, feature, landscape_grid, water_ids):
        sx, sy, _ = self._scale_point(feature.position.x, feature.position.y, 0)
        cx, cy = int(sx), int(sy)
        for dist in range(1, 8): 
            for dx in range(-dist, dist + 1):
                for dy in range(-dist, dist + 1):
                    if max(abs(dx), abs(dy)) != dist: continue
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        if landscape_grid[ny, nx] not in water_ids:
                            return self._get_feature_mask(feature, override_pos=(nx, ny))
        return self._get_feature_mask(feature)

    def _get_cell_prop(self, category, is_road=False, is_bridge=False):
        """Maps Categories to the specific asset names provided."""
        name = None
        
        if is_bridge: return {"name": "bridge", "part": 0}
        if is_road: return {"name": "path", "part": 0}

        if category == "Settlement": name = "city"
        elif category == "Landmark": name = "city"
        elif category == "River": name = "water"
        elif category == "Lake": name = "water"
        elif category == "Sea": name = "water"
        elif category == "Marsh": name = "water"
        elif category == "MountainRange": name = "rock"
        elif category == "Forest": name = random.choice(self.TREE_TYPES)
        elif category == "Region": name = "ground"
        elif category == "Field": name = "ground"
        
        if name:
            return {"name": name, "part": 0}
        return None
    
    def rasterize_to_json(self, graph: FinalFeatureGraph):
        # 1. SETUP IMAGES
        img_landscape = Image.new("I", (self.width, self.height), 0)
        draw_landscape = ImageDraw.Draw(img_landscape)
        
        sorted_features = sorted(graph.features, key=lambda f: self.PRIORITY.get(f.category, 0))
        feature_lookup = {i: f for i, f in enumerate(sorted_features, 1)}
        
        #Phase 1: Draw Base Landscape (Rivers, Terrain) - No Cities
        for i, feature in enumerate(sorted_features, 1):
            if feature.category == "Settlement": continue
            if not feature.geometry: continue

            if feature.category == "River":
                if feature.geometry.kind == "spine":
                    points = self._generate_interpolated_points(feature.geometry.nodes)
                    xy_points = [(p[0], p[1]) for p in points]
                    for j in range(len(xy_points) - 1):
                        width = 2 if points[j][2] > 0.6 else 1
                        draw_landscape.line([xy_points[j], xy_points[j+1]], fill=i, width=width)
            else:
                if feature.geometry.kind == "circle":
                    sx, sy, sr = self._scale_point(feature.position.x, feature.position.y, feature.geometry.radius)
                    draw_landscape.ellipse([sx-sr, sy-sr, sx+sr, sy+sr], fill=i)
                elif feature.geometry.kind == "spine":
                    points = self._generate_interpolated_points(feature.geometry.nodes)
                    for (cx, cy, r) in points:
                        draw_landscape.ellipse([cx-r, cy-r, cx+r, cy+r], fill=i)

        grid_final = np.array(img_landscape)
        river_id_val = self.CATEGORY_IDS["River"]
        water_ids = [river_id_val, self.CATEGORY_IDS["Sea"], self.CATEGORY_IDS["Lake"]]

        #Track City Centers for Roads
        city_centers = []

        #Phase 2: Place Settlements
        for i, feature in enumerate(sorted_features, 1):
            if feature.category != "Settlement": continue
            if not feature.geometry: continue

            mask_city = self._get_feature_mask(feature)
            pixel_count = np.sum(mask_city)

            if pixel_count == 5:
                mask_city = self._create_square_mask_from_plus(mask_city)
                pixel_count = 4 
            
            underlying_terrain = grid_final[mask_city]
            intersects_river = np.any(underlying_terrain == river_id_val)
            
            final_mask = mask_city
            
            if intersects_river:
                if pixel_count > 12: 
                    #Large City: Stay there
                    pass 
                else:
                    #Small City: Move
                    final_mask = self._find_new_position_mask(feature, grid_final, water_ids)
            
            # Place City on Grid
            grid_final[final_mask] = i
            
            # Calculate center for Roads
            y_idxs, x_idxs = np.where(final_mask)
            if len(x_idxs) > 0:
                cx = int(np.mean(x_idxs))
                cy = int(np.mean(y_idxs))
                city_centers.append((cx, cy))

        #Phase 3: Road Generation
        road_gen = RoadGenerator(self.width, self.height, grid_final, self.CATEGORY_IDS)
        road_pixels = road_gen.generate_network(city_centers)
        
        # Assign a NEW unique ID for the road network (higher than any existing feature)
        road_feature_id = max(feature_lookup.keys()) + 1
        
        # Helper to track if a road is a bridge
        road_is_bridge = {}

        for (rx, ry) in road_pixels:
            current_id = grid_final[ry, rx]
            #Look up the existing feature
            existing_feature = feature_lookup.get(current_id)
            #Protect Cities
            if existing_feature and existing_feature.category == "Settlement":
                continue
            #add bridge
            if existing_feature and existing_feature.category in ["River", "Sea", "Lake"]:
                road_is_bridge[(rx, ry)] = True
            #Write the Road ID
            grid_final[ry, rx] = road_feature_id

        #Phase 4: Export
        

        entities = []
        # 4a: Export Standard Features
        for int_id, feature in feature_lookup.items():
            y_idxs, x_idxs = np.where(grid_final == int_id)
            if len(x_idxs) == 0: continue

            #Merge LLM Attributes with basic Metadata
            meta = feature.attributes.copy()
            meta["name"] = feature.name
            meta["color"] = self.COLORS.get(feature.category, "#000000")
            #Making sure there is meta data
            if "description" not in meta:
                meta["description"] = f"A {feature.category} named {feature.name}."

            cells = []
            for y, x in zip(y_idxs, x_idxs):
                # NEW: Generate Prop Object
                prop_data = self._get_cell_prop(feature.category)
                
                cells.append({
                    "x": int(x), 
                    "y": int(y), 
                    "prop": prop_data
                })

            entities.append({
                "id": feature.id,
                "metadata": meta,
                "category": feature.category,
                "cells": cells
            })
            
        # 4b: Export Generated Roads
        road_y, road_x = np.where(grid_final == road_feature_id)
        
        if len(road_x) > 0:
            road_cells = []
            for y, x in zip(road_y, road_x):
                is_bridge = road_is_bridge.get((x, y), False)
                prop_data = self._get_cell_prop("Road", is_road=True, is_bridge=is_bridge)

                road_cells.append({
                    "x": int(x), 
                    "y": int(y), 
                    "prop": prop_data
                })
                
            entities.append({
                "id": "generated_roads",
                "metadata": {
                    "name": "Trade Routes",
                    "description": "Roads connecting the settlements.",
                    "color": self.COLORS["Road"]
                },
                "category": "Road",
                "cells": road_cells
            })

        return {"entities": entities}