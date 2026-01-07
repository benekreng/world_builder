import heapq
import math
import numpy as np

class RoadGenerator:
    def __init__(self, width, height, grid, category_ids):
        self.width = width
        self.height = height
        self.grid = grid
        self.cat_ids = category_ids

        # Reverse lookup to find Category Name from ID
        self.id_to_cat = {v: k for k, v in category_ids.items()}

        # DEFINE TERRAIN COSTS
        # Low cost = prefer path. High cost = avoid.
        self.COSTS = {
            "Region": 1, 
            "Field": 1,
            "Marsh": 4,      # Marshes are wet/slow
            "Forest": 3,     # Trees are hard to cut through
            "Road": 0.1,     # Existing roads are super fast (encourages merging)
            "Lake": 50,      # Go around
            "River": 20,     # Bridges are expensive
            "MountainRange": 30, 
            "Sea": 9999,
            "Settlement": 0.5 # Roads naturally go INTO cities
        }

    def _get_terrain_multiplier(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return 9999
        
        cell_id = self.grid[y, x]
        cat_name = self.id_to_cat.get(cell_id, "Region")
        
        return self.COSTS.get(cat_name, 1)

    def _heuristic(self, a, b):
        # Euclidean Distance is better for 8-way movement (more direct)
        return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

    def find_path(self, start, end):
        """A* Pathfinding with 8-Way Movement (Diagonals)."""
        start = (int(start[0]), int(start[1]))
        end = (int(end[0]), int(end[1]))
        
        pq = [(0, start)]
        came_from = {}
        cost_so_far = {start: 0}
        
        # Directions: (dx, dy, distance_cost)
        # Straight moves cost 1.0, Diagonals cost 1.414
        moves = [
            (0, 1, 1.0), (0, -1, 1.0), (1, 0, 1.0), (-1, 0, 1.0),       # Cardinals
            (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414) # Diagonals
        ]

        while pq:
            current_cost, current = heapq.heappop(pq)
            
            if current == end:
                break
            
            for dx, dy, move_cost in moves:
                nx, ny = current[0] + dx, current[1] + dy
                
                # Bounds Check
                if not (0 <= nx < self.width and 0 <= ny < self.height):
                    continue
                
                # Calculate Cost
                # Base Move Cost (1 or 1.41) * Terrain Multiplier
                terrain_mult = self._get_terrain_multiplier(nx, ny)
                
                # If terrain is effectively a wall (Sea), skip
                if terrain_mult >= 9999:
                    continue

                new_cost = cost_so_far[current] + (move_cost * terrain_mult)
                
                if (nx, ny) not in cost_so_far or new_cost < cost_so_far[(nx, ny)]:
                    cost_so_far[(nx, ny)] = new_cost
                    priority = new_cost + self._heuristic(end, (nx, ny))
                    heapq.heappush(pq, (priority, (nx, ny)))
                    came_from[(nx, ny)] = current
                    
        # Reconstruct Path
        path = []
        if end in came_from:
            curr = end
            while curr != start:
                path.append(curr)
                curr = came_from[curr]
            path.append(start)
            path.reverse()
            return path
        return []

    def generate_network(self, city_centers):
        if len(city_centers) < 2:
            return []

        road_pixels = set()
        connections = []

        # 1. Connect to nearest neighbors
        for i, c1 in enumerate(city_centers):
            distances = []
            for j, c2 in enumerate(city_centers):
                if i == j: continue
                # Squared Euclidean for sorting
                dist = (c1[0]-c2[0])**2 + (c1[1]-c2[1])**2
                distances.append((dist, c2))
            
            distances.sort(key=lambda x: x[0])
            
            # Connect to closest 2 cities to ensure a web
            nearest = [d[1] for d in distances[:2]]
            
            for target in nearest:
                pair = tuple(sorted((c1, target)))
                if pair not in connections:
                    connections.append(pair)

        # 2. Generate Paths
        print(f"Generating {len(connections)} trade routes...")
        for start, end in connections:
            path = self.find_path(start, end)
            for p in path:
                road_pixels.add(p)
                
                # Optional: Make heavily trafficked roads "cheaper" for future iterations
                # In a complex setup, we'd update self.grid or a separate cost_grid here
                
        return list(road_pixels)