def find_and_replace_start(grid, marker='S'):
    for row, line in enumerate(grid):
        for col, cell in enumerate(line):
            if cell == marker:
                grid[row][col] = '.'
                return (row, col)
    return (None, None)

def read_input(filename):
    with open(filename) as f:
        grid = [list(line.strip()) for line in f]
    start = find_and_replace_start(grid, 'S')
    return grid, start

def simulate_beams(filename, count_splits=True):
    grid, (s_row, s_col) = read_input(filename)
    
    rows = len(grid)
    cols = len(grid[0])
    
    # Track beams in each column for the current row
    current_beams = [0] * cols
    current_beams[s_col] = 1
    splits_encountered = 0
    
    # Process each row starting from the starting row
    for row in range(s_row, rows):
        next_beams = [0] * cols
        
        for col in range(cols):
            if current_beams[col] > 0:
                if grid[row][col] == '^':
                    # This is a split
                    splits_encountered += 1
                    
                    # Beams go left and right
                    if col - 1 >= 0:
                        next_beams[col - 1] += current_beams[col]
                    if col + 1 < cols:
                        next_beams[col + 1] += current_beams[col]
                else:
                    # No split, beam continues straight down
                    next_beams[col] += current_beams[col]
        
        current_beams = next_beams
    
    if count_splits:
        return splits_encountered
    else:
        return sum(current_beams)
    
def solve_part_1(filename):
    return simulate_beams(filename, count_splits=True)

def solve_part_2(filename):
    return simulate_beams(filename, count_splits=False)

if __name__ == "__main__":
    print(solve_part_1('sample.in'))
    print(solve_part_1('part1.in'))
    print(solve_part_2('sample.in'))
    print(solve_part_2('part1.in'))


