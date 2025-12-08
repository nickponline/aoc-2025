from functools import reduce
from operator import mul

class DSU:
    def __init__(self, elements):
        self.parent = {elem: elem for elem in elements}
        self.size = {elem: 1 for elem in elements}
    
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x, y):
        root_x = self.find(x)
        root_y = self.find(y)
        
        if root_x == root_y:
            return False
        
        if self.size[root_x] < self.size[root_y]:
            root_x, root_y = root_y, root_x
        
        self.parent[root_y] = root_x
        self.size[root_x] += self.size[root_y]
        return True
    
    def get_component_sizes(self):
        components = {}
        for elem in self.parent:
            root = self.find(elem)
            if root not in components:
                components[root] = 0
            components[root] += 1
        return sorted(components.values(), reverse=True)
    
    def num_components(self):
        return len(set(self.find(elem) for elem in self.parent))

def read_input(filename):
    with open(filename) as f:
        coordinates = []
        for line in f:
            line = line.strip()
            if line:
                x, y, z = map(int, line.split(','))
                coordinates.append((x, y, z))
        return coordinates

def calculate_distance(coord1, coord2):
    x1, y1, z1 = coord1
    x2, y2, z2 = coord2
    return ((x1 - x2)**2 + (y1 - y2)**2 + (z1 - z2)**2)**0.5

def create_sorted_pairs(coordinates):
    """Create all pairs of coordinates and sort by distance."""
    pairs = []
    for i in range(len(coordinates)):
        for j in range(i + 1, len(coordinates)):
            dist = calculate_distance(coordinates[i], coordinates[j])
            pairs.append((dist, coordinates[i], coordinates[j]))
    
    pairs.sort(key=lambda x: x[0])
    return pairs

def solve_part_1(filename, best_k=1000):
    coordinates = read_input(filename)
    pairs = create_sorted_pairs(coordinates)
    dsu = DSU(coordinates)
    for i in range(min(best_k, len(pairs))):
        dist, coord1, coord2 = pairs[i]
        dsu.union(coord1, coord2)
    sizes = dsu.get_component_sizes()[:3]
    return reduce(mul, sizes, 1)

def solve_part_2(filename):
    coordinates = read_input(filename)
    pairs = create_sorted_pairs(coordinates)
    dsu = DSU(coordinates)
    for i in range(len(pairs)):
        dist, coord1, coord2 = pairs[i]
        dsu.union(coord1, coord2)
        if dsu.num_components() == 1:
            return coord1[0] * coord2[0]
            
if __name__ == "__main__":
    print(solve_part_1('sample.in', best_k=10))
    print(solve_part_1('part1.in',  best_k=1000))
    print(solve_part_2('sample.in'))
    print(solve_part_2('part1.in'))


