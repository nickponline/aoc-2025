import re
import math
from collections import defaultdict
from ortools.sat.python import cp_model
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import numpy as np

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

def solve_ortools(width, height, counts, shape_variations, display=False, line_number=0):
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
    
    if (status == cp_model.FEASIBLE or status == cp_model.OPTIMAL) and display:
        # Collect placement data for animation
        placements = []  # [(shape_idx, var_idx, anchor_r, anchor_c, cells), ...]
        
        for shape_idx, shape_placements in enumerate(placement_vars):
            shape_id, variations = shape_variations[shape_idx]
            
            for var, var_idx, anchor_r, anchor_c in shape_placements:
                if solver.Value(var):
                    cells = variations[var_idx]
                    original_cells = variations[0]  # The "canonical" form
                    placements.append((shape_idx, var_idx, anchor_r, anchor_c, cells, original_cells))
        
        # Generate the animation
        create_animation(width, height, counts, shape_variations, placements, line_number)
    
    return status == cp_model.FEASIBLE or status == cp_model.OPTIMAL


def match_cells_by_angle(original_cells, final_cells):
    """Match cells between original and final configurations by angle from centroid."""
    orig_list = list(original_cells)
    final_list = list(final_cells)
    
    # Compute centroids
    orig_cr = sum(r for r, c in orig_list) / len(orig_list)
    orig_cc = sum(c for r, c in orig_list) / len(orig_list)
    final_cr = sum(r for r, c in final_list) / len(final_list)
    final_cc = sum(c for r, c in final_list) / len(final_list)
    
    def angle_dist(r, c, cr, cc):
        ang = math.atan2(r - cr, c - cc)
        dist = math.sqrt((r - cr)**2 + (c - cc)**2)
        return (ang, dist)
    
    # Sort both by angle, then distance
    orig_with_key = [(angle_dist(r, c, orig_cr, orig_cc), (r, c)) for r, c in orig_list]
    final_with_key = [(angle_dist(r, c, final_cr, final_cc), (r, c)) for r, c in final_list]
    
    orig_sorted = [cell for _, cell in sorted(orig_with_key)]
    final_sorted = [cell for _, cell in sorted(final_with_key)]
    
    return list(zip(orig_sorted, final_sorted))


def compute_edges_for_cells(cells_set):
    """Compute external edges for a set of cells."""
    edges = []
    for dr, dc in cells_set:
        # Top edge (dr-1 not in cells)
        if (dr - 1, dc) not in cells_set:
            edges.append(('top', dr, dc))
        # Bottom edge (dr+1 not in cells)
        if (dr + 1, dc) not in cells_set:
            edges.append(('bottom', dr, dc))
        # Left edge (dc-1 not in cells)
        if (dr, dc - 1) not in cells_set:
            edges.append(('left', dr, dc))
        # Right edge (dc+1 not in cells)
        if (dr, dc + 1) not in cells_set:
            edges.append(('right', dr, dc))
    return edges


def create_animation(width, height, counts, shape_variations, placements, line_number):
    """Create an MP4 animation showing shapes moving into their final positions."""
    
    # Color palette - vibrant and distinct colors
    colors = [
        '#E63946',  # Red
        '#2A9D8F',  # Teal
        '#E9C46A',  # Yellow
        '#264653',  # Dark Blue
        '#F4A261',  # Orange
        '#9B5DE5',  # Purple
        '#00F5D4',  # Cyan
        '#F15BB5',  # Pink
        '#00BBF9',  # Sky Blue
        '#FEE440',  # Bright Yellow
        '#8338EC',  # Violet
        '#3A86FF',  # Blue
        '#06D6A0',  # Green
        '#EF476F',  # Coral
        '#FFD166',  # Gold
    ]
    
    # Calculate layout dimensions
    # Shapes on left, grid on right
    active_shapes = [(i, shape_variations[i]) for i in range(len(counts)) if counts[i] > 0]
    
    if not active_shapes:
        return
    
    max_shape_width = max(
        max(dc for dr, dc in variations[0]) - min(dc for dr, dc in variations[0]) + 1
        for _, (_, variations) in active_shapes if variations
    )
    max_shape_height = max(
        max(dr for dr, dc in variations[0]) - min(dr for dr, dc in variations[0]) + 1
        for _, (_, variations) in active_shapes if variations
    )
    
    # Layout: shapes stacked on left, gap, then grid on right
    shapes_total_height = sum(
        max(dr for dr, dc in shape_variations[i][1][0]) - min(dr for dr, dc in shape_variations[i][1][0]) + 1
        for i in range(len(counts)) if counts[i] > 0
    ) + len(active_shapes) - 1  # Add spacing between shapes
    
    # Calculate figure size with proper margins
    left_margin = 2
    gap = 2
    right_margin = 2
    top_margin = 2
    bottom_margin = 2
    
    total_width = left_margin + max_shape_width + gap + width + right_margin
    total_height = max(height, shapes_total_height) + top_margin + bottom_margin
    
    fig, ax = plt.subplots(figsize=(total_width * 0.8, total_height * 0.8))
    ax.set_xlim(0, total_width)
    ax.set_ylim(0, total_height)
    ax.set_aspect('equal')
    ax.axis('off')
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#1a1a2e')
    
    # Grid position (on the right, centered vertically)
    grid_offset_x = left_margin + max_shape_width + gap
    grid_offset_y = (total_height - height) / 2
    
    # Draw static grid background
    for r in range(height):
        for c in range(width):
            rect = patches.Rectangle(
                (grid_offset_x + c, grid_offset_y + (height - 1 - r)),
                1, 1, linewidth=1, edgecolor='#4a4e69', facecolor='#16213e'
            )
            ax.add_patch(rect)
    
    # Calculate starting positions for shapes (stacked on left, centered vertically)
    shape_start_positions = {}
    current_y = (total_height + shapes_total_height) / 2
    
    for shape_idx, (shape_id, variations) in active_shapes:
        cells = variations[0]
        min_r = min(dr for dr, dc in cells)
        max_r = max(dr for dr, dc in cells)
        min_c = min(dc for dr, dc in cells)
        max_c = max(dc for dr, dc in cells)
        shape_h = max_r - min_r + 1
        shape_w = max_c - min_c + 1
        
        current_y -= shape_h
        
        # Center the shape horizontally in the left area
        shape_x = left_margin + (max_shape_width - shape_w) / 2
        
        shape_start_positions[shape_idx] = (shape_x, current_y)
        current_y -= 1  # Add spacing between shapes
    
    # Animation parameters
    fps = 30
    hold_frames = fps * 2  # 2 seconds to show initial state
    move_frames = fps * 2  # 2 seconds for movement
    final_hold = fps * 2   # 2 seconds to hold final state
    total_frames = hold_frames + move_frames + final_hold
    
    # Create placement data - shapes start in original orientation and morph to final
    placement_data = []
    
    for placement_idx, (shape_idx, var_idx, anchor_r, anchor_c, final_cells, original_cells) in enumerate(placements):
        color = colors[shape_idx % len(colors)]
        
        # Match cells between original and final orientations
        cell_matches = match_cells_by_angle(original_cells, final_cells)
        
        # Starting position base (left side)
        start_base_x, start_base_y = shape_start_positions[shape_idx]
        
        # Normalize original cells for positioning
        orig_list = list(original_cells)
        orig_min_r = min(r for r, c in orig_list)
        orig_max_r = max(r for r, c in orig_list)
        orig_min_c = min(c for r, c in orig_list)
        
        cell_patches = []
        
        for orig_cell, final_cell in cell_matches:
            orig_r, orig_c = orig_cell
            final_r, final_c = final_cell
            
            # Start position (on left, using original orientation)
            start_rel_x = orig_c - orig_min_c
            start_rel_y = orig_max_r - orig_r  # Flip y for matplotlib
            start_x = start_base_x + start_rel_x
            start_y = start_base_y + start_rel_y
            
            # End position (on grid, using final orientation)
            end_x = grid_offset_x + anchor_c + final_c
            end_y = grid_offset_y + (height - 1 - (anchor_r + final_r))
            
            # Create rectangle
            rect = patches.Rectangle(
                (start_x, start_y), 1, 1,
                linewidth=0, edgecolor='none', facecolor=color, alpha=0.9
            )
            ax.add_patch(rect)
            
            cell_patches.append({
                'rect': rect,
                'start': (start_x, start_y),
                'end': (end_x, end_y),
                'orig_cell': orig_cell,
                'final_cell': final_cell,
            })
        
        # Create edge lines for original configuration (shown at start)
        orig_edges = compute_edges_for_cells(set(original_cells))
        start_edge_lines = []
        
        for edge_type, dr, dc in orig_edges:
            rel_x = dc - orig_min_c
            rel_y = orig_max_r - dr
            
            if edge_type == 'top':
                x1, y1, x2, y2 = rel_x, rel_y + 1, rel_x + 1, rel_y + 1
            elif edge_type == 'bottom':
                x1, y1, x2, y2 = rel_x, rel_y, rel_x + 1, rel_y
            elif edge_type == 'left':
                x1, y1, x2, y2 = rel_x, rel_y, rel_x, rel_y + 1
            else:  # right
                x1, y1, x2, y2 = rel_x + 1, rel_y, rel_x + 1, rel_y + 1
            
            line, = ax.plot(
                [start_base_x + x1, start_base_x + x2],
                [start_base_y + y1, start_base_y + y2],
                color='white', linewidth=2, solid_capstyle='round'
            )
            start_edge_lines.append({
                'line': line,
                'rel_coords': (x1, y1, x2, y2),
            })
        
        # Create edge lines for final configuration (shown at end)
        final_min_r = min(r for r, c in final_cells)
        final_min_c = min(c for r, c in final_cells)
        final_max_r = max(r for r, c in final_cells)
        
        final_edges = compute_edges_for_cells(set(final_cells))
        end_edge_lines = []
        
        for edge_type, dr, dc in final_edges:
            # Final position on grid
            base_x = grid_offset_x + anchor_c + dc
            base_y = grid_offset_y + (height - 1 - (anchor_r + dr))
            
            if edge_type == 'top':
                x1, y1, x2, y2 = 0, 1, 1, 1
            elif edge_type == 'bottom':
                x1, y1, x2, y2 = 0, 0, 1, 0
            elif edge_type == 'left':
                x1, y1, x2, y2 = 0, 0, 0, 1
            else:  # right
                x1, y1, x2, y2 = 1, 0, 1, 1
            
            line, = ax.plot(
                [base_x + x1, base_x + x2],
                [base_y + y1, base_y + y2],
                color='white', linewidth=2, solid_capstyle='round', alpha=0
            )
            end_edge_lines.append({
                'line': line,
                'abs_coords': (base_x + x1, base_y + y1, base_x + x2, base_y + y2),
            })
        
        placement_data.append({
            'cell_patches': cell_patches,
            'start_edge_lines': start_edge_lines,
            'end_edge_lines': end_edge_lines,
            'start_base': (start_base_x, start_base_y),
        })
    
    def ease_in_out(t):
        """Smooth easing function."""
        return t * t * (3 - 2 * t)
    
    def animate(frame):
        if frame < hold_frames:
            # Hold initial position
            t = 0
        elif frame < hold_frames + move_frames:
            # Animate movement
            raw_t = (frame - hold_frames) / move_frames
            t = ease_in_out(raw_t)
        else:
            # Hold final position
            t = 1
        
        # Edge fade: edges visible at t=0 and t=1, fade during transition
        # Use a curve that fades out in first half, fades in second half
        if t <= 0.5:
            edge_alpha = 1.0 - (t * 2)  # 1 -> 0 as t goes 0 -> 0.5
        else:
            edge_alpha = (t - 0.5) * 2  # 0 -> 1 as t goes 0.5 -> 1
        
        all_artists = []
        
        for pdata in placement_data:
            # Update all cell rectangles - interpolate from start to end
            for cell_data in pdata['cell_patches']:
                rect = cell_data['rect']
                sx, sy = cell_data['start']
                ex, ey = cell_data['end']
                
                # Interpolate position
                x = sx + (ex - sx) * t
                y = sy + (ey - sy) * t
                
                rect.set_xy((x, y))
                all_artists.append(rect)
            
            # Update start edge lines (fade out during first half)
            start_alpha = 1.0 - t if t <= 0.5 else 0
            for edge_data in pdata['start_edge_lines']:
                line = edge_data['line']
                x1, y1, x2, y2 = edge_data['rel_coords']
                base_x, base_y = pdata['start_base']
                
                # Move edges with centroid of original cells during first half
                # Compute current centroid position
                if pdata['cell_patches']:
                    avg_x = sum(cp['start'][0] + (cp['end'][0] - cp['start'][0]) * t 
                               for cp in pdata['cell_patches']) / len(pdata['cell_patches'])
                    avg_y = sum(cp['start'][1] + (cp['end'][1] - cp['start'][1]) * t 
                               for cp in pdata['cell_patches']) / len(pdata['cell_patches'])
                    orig_avg_x = sum(cp['start'][0] for cp in pdata['cell_patches']) / len(pdata['cell_patches'])
                    orig_avg_y = sum(cp['start'][1] for cp in pdata['cell_patches']) / len(pdata['cell_patches'])
                    
                    delta_x = avg_x - orig_avg_x
                    delta_y = avg_y - orig_avg_y
                else:
                    delta_x = delta_y = 0
                
                line.set_data(
                    [base_x + x1 + delta_x, base_x + x2 + delta_x],
                    [base_y + y1 + delta_y, base_y + y2 + delta_y]
                )
                line.set_alpha(max(0, 1.0 - t * 2))
                all_artists.append(line)
            
            # Update end edge lines (fade in during second half)
            for edge_data in pdata['end_edge_lines']:
                line = edge_data['line']
                line.set_alpha(max(0, (t - 0.5) * 2) if t > 0.5 else 0)
                all_artists.append(line)
        
        return all_artists
    
    anim = FuncAnimation(fig, animate, frames=total_frames, interval=1000/fps, blit=True)
    
    # Save as GIF
    filename = f"solution_{line_number}.gif"
    anim.save(filename, writer='pillow', fps=fps, dpi=72,
              savefig_kwargs={'facecolor': '#1a1a2e'})
    plt.close(fig)
    print(f"Animation saved to {filename}")


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
       
        result = solve_ortools(width, height, counts, shape_variations, display, line_number)
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
    # print(solve('sample1.in', display=True))
    print(solve('part1.in', display=True))
    # for _ in range(10):
    #     generate_puzzle(8, 8, 6)
    #     print(solve('new.in', display=True))