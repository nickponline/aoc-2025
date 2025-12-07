def read_input(filename):
    with open(filename) as f:
        grid = [list(line.strip()) for line in f]
    
    # Find S position
    for row, line in enumerate(grid):
        for col, cell in enumerate(line):
            if cell == 'S':
                grid[row][col] = '.'
                return grid, (row, col)
    
    return grid, (None, None)
    
def solve_part_1(filename):
    grid, (s_row, s_col) = read_input(filename)
    
    rows = len(grid)
    cols = len(grid[0])
    
    # Track which columns have beams in the current row
    current_beams = [False] * cols
    current_beams[s_col] = True
    splits_encountered = 0
    
    # Process each row starting from the starting row
    for row in range(s_row, rows):
        next_beams = [False] * cols
        
        for col in range(cols):
            if current_beams[col]:
                if grid[row][col] == '^':
                    # This is a split - increment counter
                    splits_encountered += 1
                    
                    # Add beams on either side (left and right)
                    if col - 1 >= 0:
                        next_beams[col - 1] = True
                    if col + 1 < cols:
                        next_beams[col + 1] = True
                else:
                    # No split, beam continues straight down
                    next_beams[col] = True
        
        current_beams = next_beams
    
    return splits_encountered

def solve_part_2(filename):
    grid, (s_row, s_col) = read_input(filename)
    # Count paths from S to bottom of grid using dynamic programming
    # At each ^, we can choose to go left or right, then continue down
    
    rows = len(grid)
    cols = len(grid[0])
    
    # dp[row][col] = number of ways to reach bottom from (row, col)
    # We'll build bottom-up from the last row to the starting position
    dp = [[0] * cols for _ in range(rows + 1)]
    
    # Base case: bottom row (row == rows) has 1 way (we've reached the bottom)
    for col in range(cols):
        dp[rows][col] = 1
    
    # Fill the DP table from bottom to top
    for row in range(rows - 1, -1, -1):
        for col in range(cols):
            cell = grid[row][col]
            
            if cell == '^':
                # Split: can go left or right, then continue down from those positions
                left_paths = 0
                right_paths = 0
                
                if col - 1 >= 0:
                    left_paths = dp[row + 1][col - 1]
                if col + 1 < cols:
                    right_paths = dp[row + 1][col + 1]
                
                dp[row][col] = left_paths + right_paths
            else:
                # Continue down
                dp[row][col] = dp[row + 1][col]
    
    return dp[s_row][s_col]

if __name__ == "__main__":
    print(solve_part_1('sample.in'))
    print(solve_part_1('part1.in'))
    print(solve_part_2('sample.in'))
    print(solve_part_2('part1.in'))


