def read_input(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f]
    
    # Find the blank line that separates intervals from query numbers
    blank_idx = lines.index('')
    
    # Parse intervals (lines before blank)
    intervals = []
    for line in lines[:blank_idx]:
        if line:
            start, end = line.split('-')
            intervals.append((int(start), int(end)))
    
    # Parse query numbers (lines after blank)
    query_numbers = []
    for line in lines[blank_idx + 1:]:
        if line:
            query_numbers.append(int(line))
    
    return intervals, query_numbers


def solve_part_1(filename):
    intervals, query_numbers = read_input(filename)

    num_fresh = 0
    for query_number in query_numbers:
        is_fresh = False
        for a, b in intervals:
            if a <= query_number <= b:
                is_fresh = True
                break
        if is_fresh:
            num_fresh += 1
    return num_fresh


def solve_part_2(filename):
    intervals, _ = read_input(filename)

    # Sort intervals by their endpoints (events)
    events = []
    for a, b in intervals:
        events.append((a, 0, 'open'))  # 0 sorts before 1
        events.append((b, 1, 'close'))  # 1 sorts after 0
    events.sort()
    
    # Extract just position and event type for processing
    events = [(pos, event_type) for pos, _, event_type in events]
    total_sum = 0
    open_count = 0
    range_start = None
    
    for pos, event_type in events:
        if event_type == 'open':
            if open_count == 0:
                range_start = pos
            open_count += 1
        else:  # close event
            open_count -= 1
            if open_count == 0:
                # Sum all numbers from range_start to pos (inclusive)
                # print(range_start, pos, '->', (pos - range_start + 1))
                total_sum += (pos - range_start + 1)

    
    return total_sum



if __name__ == "__main__":
    print(solve_part_1('sample.in'))
    print(solve_part_1('part1.in'))
    print(solve_part_2('sample.in'))
    print(solve_part_2('part1.in'))