import re
from collections import defaultdict
from ortools.sat.python import cp_model

def read(filename):
    with open(filename) as f:
        lines = [line.rstrip('\n') for line in f]
    
    # Parse shapes
    shapes = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if ':' in line and line.endswith(':'):
            # Start of a shape definition
            shape_id = int(line.rstrip(':'))
            shape_lines = []
            i += 1
            while i < len(lines) and lines[i] and not lines[i].endswith(':'):
                shape_lines.append(lines[i])
                i += 1
            shapes.append((shape_id, shape_lines))
        elif not line:
            i += 1
        elif line:
            break
    
    # Parse grid specifications
    grids = []
    while i < len(lines):
        line = lines[i]
        if line:
            # Parse lines like "4x4: 0 0 0 0 2 0"
            match = re.match(r'(\d+)x(\d+):\s*(.*)', line)
            if match:
                width = int(match.group(1))
                height = int(match.group(2))
                numbers = list(map(int, match.group(3).split()))
                grids.append((width, height, numbers))
        i += 1
    
    return shapes, grids

def dihedral(shape):
    results = []
    current = shape
    
    # Generate 4 rotations
    for _ in range(4):
        results.append(current)
        # Rotate 90 degrees clockwise
        current = [''.join(current[len(current)-1-j][i] for j in range(len(current))) 
                   for i in range(len(current[0]))]
    
    # Flip horizontally and generate 4 more rotations
    flipped = [row[::-1] for row in shape]
    current = flipped
    for _ in range(4):
        results.append(current)
        # Rotate 90 degrees clockwise
        current = [''.join(current[len(current)-1-j][i] for j in range(len(current))) 
                   for i in range(len(current[0]))]
    
    # Remove duplicates while preserving order
    unique = []
    seen = set()
    for r in results:
        key = tuple(r)
        if key not in seen:
            seen.add(key)
            unique.append(r)
    
    return unique

def shape_to_cells(shape):
    cells = set()
    for r, row in enumerate(shape):
        for c, ch in enumerate(row):
            if ch == '#':
                cells.add((r, c))
    return cells


def normalize_cells(cells):
    if not cells:
        return frozenset()
    min_r = min(r for r, c in cells)
    min_c = min(c for r, c in cells)
    return frozenset((r - min_r, c - min_c) for r, c in cells)


def get_dihedral_cells(shape):
    variations = dihedral(shape)
    unique_cells = []
    seen = set()
    for var in variations:
        cells = normalize_cells(shape_to_cells(var))
        if cells not in seen:
            seen.add(cells)
            unique_cells.append(cells)
    return unique_cells


def get_valid_placements(cells, width, height):
    placements = []
    for anchor_r in range(height):
        for anchor_c in range(width):
            # Check if all cells fit within bounds
            valid = True
            for dr, dc in cells:
                r, c = anchor_r + dr, anchor_c + dc
                if r < 0 or r >= height or c < 0 or c >= width:
                    valid = False
                    break
            if valid:
                placements.append((anchor_r, anchor_c))
    return placements

def solve_ortools(width, height, counts, shape_variations, display=False):
    model = cp_model.CpModel()
    
    # placement_vars[shape_idx] = list of (BoolVar, var_idx, anchor_r, anchor_c) tuples
    placement_vars = []
    # cell_to_placements[(r,c)] = list of BoolVar that cover this cell
    cell_to_placements = defaultdict(list)
    
    for shape_idx, (shape_id, variations) in enumerate(shape_variations):
        shape_placements = []
        
        for var_idx, cells in enumerate(variations):
            valid_positions = get_valid_placements(cells, width, height)
            
            for anchor_r, anchor_c in valid_positions:
                # Create boolean variable for this placement
                var = model.NewBoolVar(f"p_{shape_idx}_{var_idx}_{anchor_r}_{anchor_c}")
                
                # Calculate actual cells covered
                covered = frozenset((anchor_r + dr, anchor_c + dc) for dr, dc in cells)
                # Store the variable along with metadata for reconstruction
                shape_placements.append((var, var_idx, anchor_r, anchor_c))
                
                # Register this placement for each cell it covers
                for cell in covered:
                    cell_to_placements[cell].append(var)
        
        placement_vars.append(shape_placements)
    
    # Constraint 1: Exactly counts[i] placements for each shape type
    for shape_idx, count in enumerate(counts):
        vars_for_shape = [var for var, _, _, _ in placement_vars[shape_idx]]
        if count > 0:
            if len(vars_for_shape) < count:
                # Not enough valid placements possible
                return False
            model.Add(sum(vars_for_shape) == count)
        else:
            # No placements allowed for this shape
            for v in vars_for_shape:
                model.Add(v == 0)
    
    # Constraint 2: Each cell can be covered by at most one placement
    for cell, vars_covering in cell_to_placements.items():
        if len(vars_covering) > 1:
            model.AddAtMostOne(vars_covering)
    
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 14  # Use multiple threads
    status = solver.Solve(model)
    if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL and display:
        # ANSI color codes for different shapes (26 colors for A-Z)
        colors = [
            '\033[91m',   # Red
            '\033[92m',   # Green
            '\033[93m',   # Yellow
            '\033[94m',   # Blue
            '\033[95m',   # Magenta
            '\033[96m',   # Cyan
            '\033[31m',   # Dark Red
            '\033[32m',   # Dark Green
            '\033[33m',   # Dark Yellow
            '\033[34m',   # Dark Blue
            '\033[35m',   # Dark Magenta
            '\033[36m',   # Dark Cyan
            '\033[97m',   # Bright White
            '\033[90m',   # Bright Black (Gray)
            '\033[91;1m', # Bright Red
            '\033[92;1m', # Bright Green
            '\033[93;1m', # Bright Yellow
            '\033[94;1m', # Bright Blue
            '\033[95;1m', # Bright Magenta
            '\033[96;1m', # Bright Cyan
            '\033[31;1m', # Bold Dark Red
            '\033[32;1m', # Bold Dark Green
            '\033[33;1m', # Bold Dark Yellow
            '\033[34;1m', # Bold Dark Blue
            '\033[35;1m', # Bold Dark Magenta
            '\033[36;1m', # Bold Dark Cyan
        ]
        reset = '\033[0m'
        
        # Display each shape as a colored grid
        print("\nShapes:")
        for shape_idx, (shape_id, variations) in enumerate(shape_variations):
            if counts[shape_idx] == 0:
                continue
            
            # Get the first variation to display
            cells = variations[0]
            
            # Find bounding box
            min_r = min(dr for dr, dc in cells)
            max_r = max(dr for dr, dc in cells)
            min_c = min(dc for dr, dc in cells)
            max_c = max(dc for dr, dc in cells)
            
            # Create a small grid for this shape
            shape_height = max_r - min_r + 1
            shape_width = max_c - min_c + 1
            shape_grid = [['.' for _ in range(shape_width)] for _ in range(shape_height)]
            
            # Fill in the shape
            for dr, dc in cells:
                r = dr - min_r
                c = dc - min_c
                shape_grid[r][c] = '#'
            
            # Print the shape with its color
            color = colors[shape_idx % len(colors)]
            print(f"Shape {shape_idx} (count: {counts[shape_idx]}):")
            for row in shape_grid:
                colored_row = ''
                for cell in row:
                    if cell == '#':
                        colored_row += color + '█' + reset
                    else:
                        colored_row += cell
                print(colored_row)
            print()
        
        # Create a grid to display the solution
        grid = [['.' for _ in range(width)] for _ in range(height)]
        
        # Fill in the grid with shape indices
        for shape_idx, shape_placements in enumerate(placement_vars):
            shape_id, variations = shape_variations[shape_idx]
            
            for var, var_idx, anchor_r, anchor_c in shape_placements:
                if solver.Value(var):
                    # Get the cells for this variation
                    cells = variations[var_idx]
                    # Place the shape on the grid
                    for dr, dc in cells:
                        r, c = anchor_r + dr, anchor_c + dc
                        grid[r][c] = shape_idx
        
        # Print the grid with colors
        print("\nSolution grid:")
        for row in grid:
            colored_row = ''
            for cell in row:
                if isinstance(cell, int):
                    shape_idx = cell
                    color = colors[shape_idx % len(colors)]
                    colored_row += color + '█' + reset
                else:
                    colored_row += cell
            print(colored_row)
        print()
    
    return status == cp_model.FEASIBLE or status == cp_model.OPTIMAL


def solve(filename, display=False):
    shapes, grids = read(filename)
    
    # Precompute all dihedral variations for each shape as cell sets
    shape_variations = []
    for shape_id, shape_lines in shapes:
        variations = get_dihedral_cells(shape_lines)
        shape_variations.append((shape_id, variations))
    
    results = []
    for line_number, grid_spec in enumerate(grids):
        width, height, counts = grid_spec
        
        # Quick area check
        total_area = sum(
            counts[i] * len(shape_variations[i][1][0]) 
            for i in range(len(counts))
        )

        if total_area > width * height:
            print(f"Line {line_number}/{len(grids)}: False")
            results.append(False)
            continue
       
        result = solve_ortools(width, height, counts, shape_variations, display)
        print(f"Line {line_number}/{len(grids)}: {result}")
        results.append(result)
    
    return sum([1 for result in results if result])
def generate_puzzle(width, height, num_shapes=5, output_file='new.in'):
    """Generate a puzzle by splitting width x height into connected components."""
    import random
    
    # Create a grid
    grid = [[None for _ in range(width)] for _ in range(height)]
    
    # Assign each cell to one of num_shapes shapes using flood fill
    shape_id = 0
    cells_per_shape = (width * height) // num_shapes
    
    unassigned = set((r, c) for r in range(height) for c in range(width))
    
    for shape_id in range(num_shapes):
        if not unassigned:
            break
            
        # Start from a random unassigned cell
        start = random.choice(list(unassigned))
        queue = [start]
        shape_cells = []
        
        # Target size for this shape
        target_size = cells_per_shape if shape_id < num_shapes - 1 else len(unassigned)
        
        while queue and len(shape_cells) < target_size:
            r, c = queue.pop(0)
            if (r, c) not in unassigned:
                continue
                
            unassigned.remove((r, c))
            shape_cells.append((r, c))
            grid[r][c] = shape_id
            
            # Add neighbors
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < height and 0 <= nc < width and (nr, nc) in unassigned:
                    if (nr, nc) not in queue:
                        queue.append((nr, nc))
    # Write the shapes to file
    with open(output_file, 'w') as f:
        for sid in range(num_shapes):
            f.write(f"{sid}:\n")
            # Find bounding box
            cells = [(r, c) for r in range(height) for c in range(width) if grid[r][c] == sid]
            if not cells:
                continue
            min_r = min(r for r, c in cells)
            max_r = max(r for r, c in cells)
            min_c = min(c for r, c in cells)
            max_c = max(c for r, c in cells)
            
            # Extract shape into a grid
            shape_grid = []
            for r in range(min_r, max_r + 1):
                row = []
                for c in range(min_c, max_c + 1):
                    if grid[r][c] == sid:
                        row.append('#')
                    else:
                        row.append('.')
                shape_grid.append(row)
            
            # Apply random dihedral transformation
            transform = random.randint(0, 7)
            
            # Apply transformation
            if transform & 1:  # Flip horizontally
                shape_grid = [row[::-1] for row in shape_grid]
            if transform & 2:  # Flip vertically
                shape_grid = shape_grid[::-1]
            if transform & 4:  # Transpose (swap rows and columns)
                shape_grid = [list(row) for row in zip(*shape_grid)]
            
            # Write transformed shape
            for row in shape_grid:
                f.write(''.join(row) + "\n")
            f.write("\n")
        
        f.write(f'{width}x{height}: {" ".join(str(1) for _ in range(num_shapes))}\n')

if __name__ == "__main__":
    print(solve('sample1.in', display=True))
    print(solve('part1.in', display=True))
    # for _ in range(10):
    #     generate_puzzle(8, 8, 6)
    #     print(solve('new.in', display=True))
    