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

def solve_part_1(filename, best_k=1000):
    coordinates = read_input(filename)

    # Create all pairs of coordinates
    pairs = []
    for i in range(len(coordinates)):
        for j in range(i + 1, len(coordinates)):
            dist = calculate_distance(coordinates[i], coordinates[j])
            pairs.append((dist, coordinates[i], coordinates[j]))
    
    # Sort pairs by distance
    pairs.sort(key=lambda x: x[0])


    # Initialize Union-Find structure
    parent = {coord: coord for coord in coordinates}
    size = {coord: 1 for coord in coordinates}
    
    def find(coord):
        if parent[coord] != coord:
            parent[coord] = find(parent[coord])
        return parent[coord]
    
    def union(coord1, coord2):
        root1 = find(coord1)
        root2 = find(coord2)
        if root1 != root2:
            if size[root1] < size[root2]:
                root1, root2 = root2, root1
            parent[root2] = root1
            size[root1] += size[root2]
    
    # Merge components using best_k closest pairs
    for i in range(min(best_k, len(pairs))):
        dist, coord1, coord2 = pairs[i]
        union(coord1, coord2)
    
    # Find all unique components and their sizes
    components = {}
    for coord in coordinates:
        root = find(coord)
        if root not in components:
            components[root] = 0
        components[root] += 1
    
    # Print component sizes
    component_sizes = sorted(components.values(), reverse=True)
    prod = component_sizes[0] * component_sizes[1] * component_sizes[2]
    return prod
    
    # return component_sizes

   

    
def solve_part_2(filename):
    coordinates = read_input(filename)

    # Create all pairs of coordinates
    pairs = []
    for i in range(len(coordinates)):
        for j in range(i + 1, len(coordinates)):
            dist = calculate_distance(coordinates[i], coordinates[j])
            pairs.append((dist, coordinates[i], coordinates[j]))
    
    # Sort pairs by distance
    pairs.sort(key=lambda x: x[0])
    best_k = len(pairs)

    # Initialize Union-Find structure
    parent = {coord: coord for coord in coordinates}
    size = {coord: 1 for coord in coordinates}
    
    def find(coord):
        if parent[coord] != coord:
            parent[coord] = find(parent[coord])
        return parent[coord]
    
    def union(coord1, coord2):
        root1 = find(coord1)
        root2 = find(coord2)
        if root1 != root2:
            if size[root1] < size[root2]:
                root1, root2 = root2, root1
            parent[root2] = root1
            size[root1] += size[root2]
    
    # Merge components using best_k closest pairs
    for i in range(min(best_k, len(pairs))):
        dist, coord1, coord2 = pairs[i]
        union(coord1, coord2)
        
        # Check if everything is in one component
        num_components = len(set(find(coord) for coord in coordinates))
        if num_components == 1:
            return coord1[0] * coord2[0]
    
  


if __name__ == "__main__":
    print(solve_part_1('sample.in', best_k=10))
    print(solve_part_1('part1.in', best_k=1000))
    print(solve_part_2('sample.in'))
    print(solve_part_2('part1.in'))


