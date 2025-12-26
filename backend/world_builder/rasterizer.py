import numpy as np
import random
from PIL import Image, ImageDraw
from .models import FinalFeatureGraph

class MapRasterizer:
    def __init__(self, grid_width=100, grid_height=100, world_extent=1000):
        """
        grid_width/height: The resolution of the output JSON (e.g., 100x100 cells).
        world_extent: The coordinate space of the input data (e.g., 0-1000).
        """
        self.width = grid_width
        self.height = grid_height
        
        # Calculate scaling factors
        self.scale_x = grid_width / world_extent
        self.scale_y = grid_height / world_extent
        
        # Priority: Higher overwrites Lower
        self.PRIORITY = {
            "Region": 0, "Field": 1, 
            "Marsh": 2, "Forest": 3,
            "MountainRange": 4, 
            "Road": 5, 
            "Lake": 6, "River": 7, "Sea": 7,
            "Landmark": 8, "Settlement": 9
        }
        
        self.COLORS = {
            "Settlement": "#d4a017", "River": "#4f8cbf", "Lake": "#89c4d9",
            "Sea": "#2b6a99", "MountainRange": "#8c7b64", "Forest": "#5c8a56",
            "Region": "#dcd3c1", "Landmark": "#c25e5e", "Marsh": "#8f915e",
            "Road": "#b0a090", "Field": "#b5c99a"
        }

    def _scale_point(self, x, y, r):
        """Helper to convert World Coords (0-1000) to Grid Coords (0-100)."""
        sx = x * self.scale_x
        sy = y * self.scale_y
        sr = r * max(self.scale_x, self.scale_y) # Scale radius uniformly
        return sx, sy, sr

    def _generate_interpolated_points(self, nodes, steps_per_segment=20):
        """Generates organic curve points in World Space, then Scales them."""
        if not nodes or len(nodes) < 2: return []
        
        # 1. Generate in high-res world space first (keeps math accurate)
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
                
                # 2. Scale immediately before storing
                sx, sy, sr = self._scale_point(solve(0), solve(1), world_r)
                interpolated.append((sx, sy, sr))
        
        # Last point
        last = data[-1]
        sx, sy, sr = self._scale_point(last[0], last[1], last[2])
        interpolated.append((sx, sy, sr))
        
        return interpolated

    def _get_props_for_category(self, category):
        if category == "Forest" and random.random() < 0.3: return ["tree"]
        if category == "MountainRange" and random.random() < 0.2: return ["rock"]
        if category == "Marsh" and random.random() < 0.2: return ["grass"]
        return []

    def rasterize_to_json(self, graph: FinalFeatureGraph):
        # Create smaller grid image
        img = Image.new("I", (self.width, self.height), 0)
        draw = ImageDraw.Draw(img)
        
        feature_lookup = {} 
        
        # Sort by priority
        sorted_features = sorted(
            graph.features, 
            key=lambda f: self.PRIORITY.get(f.category, 0)
        )

        for i, feature in enumerate(sorted_features, 1):
            feature_lookup[i] = feature
            
            if not feature.geometry: continue
            
            # --- Draw Logic (With Scaling) ---
            if feature.geometry.kind == "circle":
                # Scale World -> Grid
                sx, sy, sr = self._scale_point(feature.position.x, feature.position.y, feature.geometry.radius)
                draw.ellipse([sx-sr, sy-sr, sx+sr, sy+sr], fill=i)
                
            elif feature.geometry.kind == "spine":
                # Points are already scaled by the helper
                points = self._generate_interpolated_points(feature.geometry.nodes)
                for (cx, cy, r) in points:
                    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=i)

        grid = np.array(img)

        # --- Build Entities JSON ---
        entities = []

        for int_id, feature in feature_lookup.items():
            y_idxs, x_idxs = np.where(grid == int_id)
            if len(x_idxs) == 0: continue

            cells = []
            for y, x in zip(y_idxs, x_idxs):
                cells.append({
                    "x": int(x), # This is now 0-100
                    "y": int(y), # This is now 0-100
                    "props": self._get_props_for_category(feature.category)
                })

            # Calculate Icons positions in Grid Space
            icons = []
            if feature.category == "Settlement":
                sx, sy, _ = self._scale_point(feature.position.x, feature.position.y, 0)
                icons.append({
                    "type": "city",
                    "origin": {"x": int(sx), "y": int(sy)}
                })
            elif feature.category == "Landmark":
                 sx, sy, _ = self._scale_point(feature.position.x, feature.position.y, 0)
                 icons.append({
                    "type": "poi",
                    "origin": {"x": int(sx), "y": int(sy)}
                 })

            entity_obj = {
                "id": feature.id,
                "metadata": {
                    "name": feature.name,
                    "description": feature.attributes.get("description", ""),
                    "color": self.COLORS.get(feature.category, "#000000")
                },
                "category": feature.category,
                "cells": cells,
                "icons": icons
            }
            entities.append(entity_obj)

        return {"entities": entities}