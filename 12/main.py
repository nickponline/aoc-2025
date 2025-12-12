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


def solve_ortools(width, height, counts, shape_variations):
    model = cp_model.CpModel()
    
    # placement_vars[shape_idx] = list of BoolVar for all valid placements of that shape
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
                shape_placements.append(var)
                
                # Register this placement for each cell it covers
                for cell in covered:
                    cell_to_placements[cell].append(var)
        
        placement_vars.append(shape_placements)
    
    # Constraint 1: Exactly counts[i] placements for each shape type
    for shape_idx, count in enumerate(counts):
        vars_for_shape = placement_vars[shape_idx]
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
    
    return status == cp_model.FEASIBLE or status == cp_model.OPTIMAL


def solve(filename):
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
        
        result = solve_ortools(width, height, counts, shape_variations)
        print(f"Line {line_number}/{len(grids)}: {result}")
        results.append(result)
    
    return sum([1 for result in results if result])


if __name__ == "__main__":
    print(solve('sample1.in'))
    print(solve('part1.in'))