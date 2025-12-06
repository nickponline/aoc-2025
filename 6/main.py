def read_input(filename, vertical=True):
    with open(filename) as f:
        lines = f.read().rstrip('\n').split('\n')
    
    # Last line contains operators, everything else is the grid
    operator_line = lines[-1]
    grid_lines = lines[:-1]
    
    # Extract operators from the operator line
    operators = [c for c in operator_line if c in '*+']
    
    if vertical:
        # Pad all lines to the same length
        max_len = max(len(line) for line in grid_lines)
        grid_lines = [line.ljust(max_len) for line in grid_lines]
        
        # Read columns vertically to form new numbers
        num_rows = len(grid_lines)
        
        # For each column, read digits vertically
        column_values = []
        for col in range(max_len):
            digits = ''
            for row in range(num_rows):
                char = grid_lines[row][col] if col < len(grid_lines[row]) else ' '
                if char.isdigit():
                    digits += char
            column_values.append(digits)  # Empty string if all spaces (separator)
        
        # Group columns by separator columns (empty strings)
        # Each group becomes a column in the output grid
        groups = []
        current_group = []
        for val in column_values:
            if val == '':
                if current_group:
                    groups.append(current_group)
                    current_group = []
            else:
                current_group.append(val)
        if current_group:
            groups.append(current_group)
        
        # Convert to grid: each group is a column, each position in group is a row
        max_rows = max(len(g) for g in groups) if groups else 0
        
        output_grid = []
        for row_idx in range(max_rows):
            row = []
            for group in groups:
                if row_idx < len(group):
                    row.append(int(group[row_idx]))
                else:
                    row.append(0)
            output_grid.append(row)
    else:
        # Read numbers normally as whitespace-separated values
        output_grid = []
        for line in grid_lines:
            row = [int(x) for x in line.split()]
            output_grid.append(row)
    
    return output_grid, operators

def calculate(grid, operators):
    if not grid:
        return [], []
    
    num_cols = len(grid[0])
    
    # Calculate sum of each column
    a = []
    for col in range(num_cols):
        col_sum = sum(grid[row][col] for row in range(len(grid)))
        a.append(col_sum)
    
    # Calculate product of each column
    b = []
    for col in range(num_cols):
        col_prod = 1
        for row in range(len(grid)):
            if grid[row][col] != 0:
                col_prod *= grid[row][col]
        b.append(col_prod)

    ret = [ a[i] if operators[i] == '+' else b[i] for i in range(num_cols) ]
    return sum(ret)


def solve_part_1(filename):
    grid, operators = read_input(filename, vertical=False)
    return calculate(grid, operators)


def solve_part_2(filename):
    grid, operators = read_input(filename, vertical=True)
    return calculate(grid, operators)



if __name__ == "__main__":
    print(solve_part_1('sample.in'))
    print(solve_part_1('part1.in'))
    print(solve_part_2('sample.in'))
    print(solve_part_2('part1.in'))


