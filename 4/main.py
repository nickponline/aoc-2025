def read_input(filename):
    return [list(line.strip()) for line in open(filename, 'r') if line.strip()]

def get_removable_points(grid):
    removable_points = []
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] == '@':
                # Count @ neighbors in 8 directions
                neighbors = 0
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:
                            continue
                        ni, nj = i + di, j + dj
                        if 0 <= ni < rows and 0 <= nj < cols and grid[ni][nj] == '@':
                            neighbors += 1
                
                if neighbors < 4:
                    removable_points.append((i, j))
    
    return removable_points

def solve_part_1(filename):
    grid = read_input(filename)
    removable_points = get_removable_points(grid)
    return len(removable_points)

def solve_part_2(filename):
    grid = read_input(filename)
    total_removed = 0

    while True:
        removable_points = get_removable_points(grid)
        total_removed += len(removable_points)
        if len(removable_points) == 0:
            break
        for point in removable_points:
            grid[point[0]][point[1]] = '.'   
    return total_removed
    

if __name__ == "__main__":
    print(solve_part_1('sample.in'))
    print(solve_part_1('part1.in'))
    print(solve_part_2('part1.in'))