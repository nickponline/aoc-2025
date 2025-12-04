import numpy as np
from scipy.signal import convolve2d

def read_input(filename):
    lines = np.array([line.strip() for line in open(filename, 'r') if line.strip()])
    return np.array([[1 if c == '@' else 0 for c in line] for line in lines])

def get_removable_points(grid):
    kernel = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])
    neighbor_count = convolve2d(grid, kernel, mode='same', boundary='fill', fillvalue=0)
    removable_mask = (grid == 1) & (neighbor_count < 4)
    return removable_mask

def solve_part_1(filename):
    grid = read_input(filename)
    return np.sum(get_removable_points(grid))

def solve_part_2(filename):
    grid = read_input(filename)
    total_removed = 0
    while (removable_mask := get_removable_points(grid)).any():
        total_removed += np.sum(removable_mask)
        grid[removable_mask] = 0
    return total_removed

if __name__ == "__main__":
    print(solve_part_1('sample.in'))
    print(solve_part_1('part1.in'))
    print(solve_part_2('part1.in'))