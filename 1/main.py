import re
from typing import Generator, Tuple

START_POSITION = 50

def read_input(filename) -> Generator[Tuple[str, int], None, None]:
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line:       
                match = re.match(r'([LR])(\d+)', line)
                if match:
                    direction = match.group(1)
                    steps = int(match.group(2))
                    yield (direction, steps)

def solve_part_1(filename) -> int:
    position = START_POSITION
    zeros = 0

    for direction, steps in read_input(filename):
        position = position + steps if direction == 'R' else position - steps
        if position % 100 == 0:
            zeros += 1

    return zeros

def solve_part_2(filename) -> int:
    curr = START_POSITION
    zeros = 0

    for direction, steps in read_input(filename):
        zeros += steps // 100
        steps = steps % 100
        nextp = (curr + steps if direction == 'R' else curr - steps) % 100

        k1 = (nextp > curr and direction == 'L')
        k2 = (nextp < curr and direction == 'R')
        
        if (nextp == 0) or (curr != 0 and (k1 or k2)):
            zeros += 1
        
        curr = nextp

    return zeros

if __name__ == "__main__":
    print(solve_part_1('example.in'));
    print(solve_part_1('part1.in'));
    print(solve_part_2('part2.in'));