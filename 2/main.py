from typing import List, Tuple


def read_input(filename: str) -> List[Tuple[int, int]]:
    with open(filename, 'r') as f:
        line = f.readline().strip()
    
    intervals = []
    for interval in line.split(','):
        a, b = interval.split('-')
        intervals.append((int(a), int(b)))
    
    return intervals

def is_invalid_id_1(id: str) -> bool:
    if len(id) % 2 != 0:
        return False
    half = len(id) // 2
    return id[:half] == id[half:]

def is_invalid_id_2(id: str) -> bool:
    id_len = len(id)
    for pattern_len in range(1, id_len // 2 + 1):
        if id_len % pattern_len == 0:
            pattern = id[:pattern_len]
            if pattern * (id_len // pattern_len) == id:
                return True
    return False


def solve_part_1(filename: str) -> int:
    sum_ids = 0
    for a, b in read_input(filename):
        for x in range(a, b + 1):
            if is_invalid_id_1(str(x)):
                sum_ids += x
    return sum_ids


def solve_part_2(filename: str) -> int:
    sum_ids = 0
    for a, b in read_input(filename):
        for x in range(a, b + 1):
            if is_invalid_id_2(str(x)):
                sum_ids += x
    return sum_ids


if __name__ == "__main__":
    print(solve_part_1('sample.in'))
    print(solve_part_1('part1.in'))
    print(solve_part_2('part1.in'))
