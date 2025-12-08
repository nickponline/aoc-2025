from functools import reduce
from operator import mul
from scipy.cluster.hierarchy import DisjointSet

def read_input(filename):
    with open(filename) as f:
        coordinates = []
        for line in f:
            line = line.strip()
            if line:
                x, y, z = map(int, line.split(','))
                coordinates.append((x, y, z))
        return coordinates

def create_sorted_pairs(coordinates):
    return sorted([
        (((coordinates[i][0] - coordinates[j][0])**2 + (coordinates[i][1] - coordinates[j][1])**2 + (coordinates[i][2] - coordinates[j][2])**2)**0.5, coordinates[i], coordinates[j])
        for i in range(len(coordinates))
        for j in range(i + 1, len(coordinates))
    ])

def solve_part_1(filename, best_k=1000):
    coordinates = read_input(filename)
    pairs = create_sorted_pairs(coordinates)
    dsu = DisjointSet(coordinates)
    for i in range(min(best_k, len(pairs))):
        dist, coord1, coord2 = pairs[i]
        dsu.merge(coord1, coord2)
    
    # Get component sizes
    components = {}
    for coord in coordinates:
        root = dsu[coord]
        if root not in components:
            components[root] = 0
        components[root] += 1
    sizes = sorted(components.values(), reverse=True)[:3]
    return reduce(mul, sizes, 1)

def solve_part_2(filename):
    coordinates = read_input(filename)
    pairs = create_sorted_pairs(coordinates)
    dsu = DisjointSet(coordinates)
    for i in range(len(pairs)):
        dist, coord1, coord2 = pairs[i]
        dsu.merge(coord1, coord2)
        
        # Check if all coordinates are in one component
        num_components = len(set(dsu[coord] for coord in coordinates))
        if num_components == 1:
            return coord1[0] * coord2[0]
            
if __name__ == "__main__":
    print(solve_part_1('sample.in', best_k=10))
    print(solve_part_1('part1.in',  best_k=1000))
    print(solve_part_2('sample.in'))
    print(solve_part_2('part1.in'))


