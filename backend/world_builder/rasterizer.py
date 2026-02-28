import numpy as np
import random
from PIL import Image, ImageDraw
from .models import FinalFeatureGraph
from .road_generator import RoadGenerator

class MapRasterizer:
    def __init__(self, grid_width=64, grid_height=64, world_extent=1000, seed=None):
        self.width = grid_width
        self.height = grid_height
        self.scale_x = grid_width / world_extent
        self.scale_y = grid_height / world_extent
        
        s = seed if seed is not None else random.randint(0, 100000)
        self.rng = random.Random(s) 
        
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
        
        self.TREES_SEASONAL = ["tree_oak", "tree_pine", "tree_birch", "tree_maple"]
        self.TREES_TROPICAL = ["tree_palm"]
        self.TREES_SWAMP = ["tree_swamp"]
        self.ROCKS_SIMPLE = ["rockSimple"]
        self.LANDMARKS = ["sign"]
        
        #City Pairs
        self.CITY_PAIRS = [(0, 1), (2, 3), (4, 5), (6, 7)]
        self.CITY_SINGLE_IDX = 6 

    def _scale_point(self, x, y, r):
        sx = x * self.scale_x
        sy = self.height - (y * self.scale_y)
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
        
        #minimum radius
        sr = max(sr, 1.0)
        if feature.geometry.kind == "circle":
            draw.ellipse([sx-sr, sy-sr, sx+sr, sy+sr], fill=1)
        elif feature.geometry.kind == "spine":
            points = self._generate_interpolated_points(feature.geometry.nodes)
            for (cx, cy, r) in points:
                draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=1)
        return np.array(img, dtype=bool)

    def _is_surrounded(self, x, y, grid, target_val, radius=2):
        y_min = max(0, y - radius)
        y_max = min(self.height, y + radius + 1)
        x_min = max(0, x - radius)
        x_max = min(self.width, x + radius + 1)
        window = grid[y_min:y_max, x_min:x_max]
        if window.size == 0: return False
        return np.all(window == target_val)

    #Biome Context
    def _get_biome_context(self, category, x, y, is_deep=False):
        
        #1. Water
        if category in ["River", "Lake", "Sea"]:
            return {"base": "water", "base_part": 0, "overlay": None, "overlay_part": 0}

        #2. Mountains
        if category == "MountainRange":
            if is_deep:
                return {"base": "mountain", "base_part": 1, "overlay": None, "overlay_part": 0}
            is_snow = self.rng.random() > 0.7
            return {"base": "mountain", "base_part": 1 if is_snow else 0, "overlay": None, "overlay_part": 0}

        #3. Marsh
        if category == "Marsh":
            overlay = None
            overlay_part = 0
            if self.rng.random() < 0.6: 
                overlay = "tree_swamp"
                overlay_part = self.rng.randint(0, 1)
            return {"base": "swamp", "base_part": 0, "overlay": overlay, "overlay_part": overlay_part}

        #4. Forest
        if category == "Forest":
            overlay = None
            overlay_part = 0
            if self.rng.random() < 0.8:
                overlay = self.rng.choice(self.TREES_SEASONAL)
                overlay_part = 0
            return {"base": "ground", "base_part": 0, "overlay": overlay, "overlay_part": overlay_part}

        #5. Landmark
        if category == "Landmark":
            #Base: Ground, Overlay: Sign
            return {"base": "ground", "base_part": 0, "overlay": "sign", "overlay_part": 0}

        #6. Field/Region
        if category == "Field" or category == "Region":
            r = self.rng.random()
            if r < 0.05: 
                return {"base": "ground", "base_part": 0, "overlay": "rockSimple", "overlay_part": self.rng.randint(0, 2)}
            if r < 0.08: 
                return {"base": "ground", "base_part": 0, "overlay": "tree_oak", "overlay_part": 0}
            return {"base": "ground", "base_part": 0, "overlay": None, "overlay_part": 0}

        #Default
        return {"base": "ground", "base_part": 0, "overlay": None, "overlay_part": 0}

    def rasterize_to_json(self, graph: FinalFeatureGraph):
        img_landscape = Image.new("I", (self.width, self.height), 0)
        draw_landscape = ImageDraw.Draw(img_landscape)
        
        #1. Validation
        valid_features = []
        for f in graph.features:
            if not f.position:
                f.position = type("Vec2", (), {"x": 500, "y": 500})()
            if not f.geometry:
                f.geometry = type("Geometry", (), {"kind": "circle", "radius": 15})()
            valid_features.append(f)

        sorted_features = sorted(valid_features, key=lambda f: self.PRIORITY.get(f.category, 0))
        feature_lookup = {i: f for i, f in enumerate(sorted_features, 1)}
        
        #2. Draw Masks
        for i, feature in enumerate(sorted_features, 1):
            if feature.category == "Settlement": continue
            try:
                if feature.geometry.kind == "circle":
                    sx, sy, sr = self._scale_point(feature.position.x, feature.position.y, feature.geometry.radius)
                    sr = max(sr, 1.0)
                    draw_landscape.ellipse([sx-sr, sy-sr, sx+sr, sy+sr], fill=i)
                elif feature.geometry.kind == "spine":
                    points = self._generate_interpolated_points(feature.geometry.nodes)
                    if feature.category == "River":
                        xy = [(p[0], p[1]) for p in points]
                        for j in range(len(xy)-1):
                            w = 2 if points[j][2] > 0.6 else 1
                            draw_landscape.line([xy[j], xy[j+1]], fill=i, width=w)
                    else:
                        for (cx, cy, r) in points:
                            draw_landscape.ellipse([cx-r, cy-r, cx+r, cy+r], fill=i)
            except Exception: pass

        grid_final = np.array(img_landscape)
        
        #3. Settlement
        city_centers = []
        for i, feature in enumerate(sorted_features, 1):
            if feature.category != "Settlement": continue
            mask = self._get_feature_mask(feature)
            y_idxs, x_idxs = np.where(mask)
            if len(y_idxs) == 0: continue
            cx, cy = int(np.mean(x_idxs)), int(np.mean(y_idxs))
            city_centers.append((cx, cy))
            grid_final[mask] = i

        #4. Roads
        try:
            road_gen = RoadGenerator(self.width, self.height, grid_final, feature_lookup)
            road_pixels = road_gen.generate_network(city_centers)
            road_id = 999 
            for (rx, ry) in road_pixels:
                val = grid_final[ry, rx]
                if val not in feature_lookup or feature_lookup[val].category != "Settlement":
                     grid_final[ry, rx] = road_id
        except: road_pixels = []

        #5. Export
        entities_by_id = {}
        occupied = np.zeros((self.height, self.width), dtype=bool)

        def add_cell(fid, category, meta, cell_data):
            if fid not in entities_by_id:
                final_meta = meta.copy()
                if "name" not in final_meta and hasattr(feature_lookup.get(val, None), "name"):
                     final_meta["name"] = feature_lookup[val].name
                elif "name" not in final_meta:
                     final_meta["name"] = "Unknown"

                entities_by_id[fid] = {
                    "id": fid,
                    "category": category,
                    "metadata": final_meta,
                    "cells": []
                }
            entities_by_id[fid]["cells"].append(cell_data)

        for y in range(self.height):
            for x in range(self.width):
                val = grid_final[y, x]
                if val == 0: continue
                if occupied[y, x]: continue 

                #Roads
                if val == road_id:
                    add_cell("generated_roads", "Road", 
                             {"name": "Trade Routes", "description": "Roads connecting the settlements."}, 
                             {"x": x, "y": y, "prop": {"name": "path", "part": 0}})
                    continue

                feature = feature_lookup.get(val)
                if not feature: continue

                #Metadata prep
                meta = feature.attributes.copy()
                meta["name"] = feature.name
                meta["color"] = self.COLORS.get(feature.category, "#000")

                #Settlement
                if feature.category == "Settlement":
                    #Try vertical pair
                    if y < self.height - 1 and grid_final[y+1, x] == val and not occupied[y+1, x]:
                        pair = self.rng.choice(self.CITY_PAIRS)
                        add_cell(feature.id, "Settlement", meta, {"x": x, "y": y, "prop": {"name": "city", "part": pair[0]}})
                        add_cell(feature.id, "Settlement", meta, {"x": x, "y": y+1, "prop": {"name": "city", "part": pair[1]}})
                        occupied[y, x] = True
                        occupied[y+1, x] = True
                    else:
                        add_cell(feature.id, "Settlement", meta, {"x": x, "y": y, "prop": {"name": "city", "part": self.CITY_SINGLE_IDX}})
                        occupied[y, x] = True
                    continue

                #Biome/Scatter
                is_deep = False
                if feature.category == "MountainRange":
                    is_deep = self._is_surrounded(x, y, grid_final, val, radius=2)

                context = self._get_biome_context(feature.category, x, y, is_deep=is_deep)
                
                add_cell(feature.id, feature.category, meta, 
                         {"x": x, "y": y, "prop": {"name": context["base"], "part": context["base_part"]}})
                
                if context["overlay"]:
                    add_cell(feature.id, feature.category, meta, 
                             {"x": x, "y": y, "prop": {"name": context["overlay"], "part": context["overlay_part"]}})

        return {"entities": list(entities_by_id.values())}