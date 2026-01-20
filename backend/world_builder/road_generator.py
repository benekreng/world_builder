import heapq
import math

class RoadGenerator:
    def __init__(self, width, height, grid, feature_lookup):
        self.width = width
        self.height = height
        self.grid = grid
        
        #Mapping: { int_id: FeatureObject }
        self.feature_lookup = feature_lookup

        self.built_roads = set()

        #Adjusted Costs
        self.COSTS = {
            "Region": 1.0, 
            "Field": 1.0,
            "Marsh": 8.0,      
            "Forest": 4.0,     
            "Road": 0.1,       
            "Lake": 100.0,     
            "River": 50.0,     
            "MountainRange": 40.0, 
            "Sea": 9999.0,     
            "Settlement": 0.1
        }

    def _get_terrain_cost(self, x, y):
        #1. Bounds Check
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return 9999.0
        
        #2. Prefer existing roads
        if (x, y) in self.built_roads:
            return self.COSTS["Road"]
        
        #3. Look up the Feature ID from the grid
        cell_id = self.grid[y, x]
        
        #4. Find the Category using the lookup
        feature = self.feature_lookup.get(cell_id)
        if feature:
            category = feature.category
        else:
            category = "Region" # Default to ground if empty
            
        return self.COSTS.get(category, 1.0)

    def _heuristic(self, a, b):
        return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

    def find_path(self, start, end):
        start = (int(start[0]), int(start[1]))
        end = (int(end[0]), int(end[1]))
        
        #Optimization: Don't start/end in the ocean
        if self._get_terrain_cost(*start) >= 9999 or self._get_terrain_cost(*end) >= 9999:
            return []

        pq = [(0, start)]
        cost_so_far = {start: 0}
        came_from = {}
        
        moves = [
            (0, 1, 1.0), (0, -1, 1.0), (1, 0, 1.0), (-1, 0, 1.0), # Cardinal
            (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414) # Diagonal
        ]

        while pq:
            _, current = heapq.heappop(pq)
            
            if current == end:
                break
            
            for dx, dy, move_dist in moves:
                nx, ny = current[0] + dx, current[1] + dy
                
                terrain_cost = self._get_terrain_cost(nx, ny)
                if terrain_cost >= 9999: continue

                new_cost = cost_so_far[current] + (move_dist * terrain_cost)
                
                if (nx, ny) not in cost_so_far or new_cost < cost_so_far[(nx, ny)]:
                    cost_so_far[(nx, ny)] = new_cost
                    priority = new_cost + self._heuristic(end, (nx, ny))
                    heapq.heappush(pq, (priority, (nx, ny)))
                    came_from[(nx, ny)] = current

        #Reconstruct
        if end not in came_from: return []
        path = []
        curr = end
        while curr != start:
            path.append(curr)
            curr = came_from[curr]
        path.append(start)
        return path

    def generate_network(self, city_centers):
        if len(city_centers) < 2: return []
        
        self.built_roads.clear()
        connections = []

        #Connect nearest neighbors
        for i, c1 in enumerate(city_centers):
            distances = []
            for j, c2 in enumerate(city_centers):
                if i == j: continue
                dist = (c1[0]-c2[0])**2 + (c1[1]-c2[1])**2
                distances.append((dist, c2))
            
            distances.sort(key=lambda x: x[0])
            #Take closest 2
            for _, target in distances[:2]:
                pair = tuple(sorted((c1, target)))
                if pair not in connections: connections.append(pair)

        #Sort by distance (build short roads first)
        connections.sort(key=lambda p: (p[0][0]-p[1][0])**2 + (p[0][1]-p[1][1])**2)
        
        print(f"Generating {len(connections)} trade routes...")
        final_pixels = set()
        
        for start, end in connections:
            path = self.find_path(start, end)
            for p in path:
                final_pixels.add(p)
                self.built_roads.add(p)
                
        return list(final_pixels)