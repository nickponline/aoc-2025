import z3
import re

def read(filename):
    with open(filename) as f:
        lines = f.readlines()
    
    result = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Extract binary list from [...]
        binary_match = re.search(r'\[(.*?)\]', line)
        binary_list = [1 if c == '#' else 0 for c in binary_match.group(1)]
        
        # Extract all parenthesized lists
        paren_lists = []
        for match in re.finditer(r'\(([0-9,]+)\)', line):
            content = match.group(1)
            paren_lists.append([int(x) for x in content.split(',')])
        
        # Extract final list from {...}
        brace_match = re.search(r'\{([0-9,]+)\}', line)
        final_list = [int(x) for x in brace_match.group(1).split(',')]
        
        result.append((binary_list, paren_lists, final_list))
    
    return result

def create_masks(switches, target_length):
    masks = [ [ 0 ] * target_length for _ in range(len(switches)) ]
    for i in range(len(switches)):
        for j in range(len(switches[i])):
            masks[i][switches[i][j]] = 1
    return masks

def solve_machine(target, switches, voltage, part):
    masks = create_masks(switches, len(target))
    
    a = [z3.Int(f'a_{i}') for i in range(len(switches))]
    
    s = z3.Optimize()
    
    if part == 1:
        for var in a:
            s.add(z3.Or(var == 0, var == 1))
        for pos in range(len(target)):
            total = z3.Sum([a[i] * masks[i][pos] for i in range(len(switches))])
            s.add(total % 2 == target[pos])
    else:  # part == 2
        for var in a:
            s.add(var >= 0)
        for pos in range(len(target)):
            total = z3.Sum([a[i] * masks[i][pos] for i in range(len(switches))])
            s.add(total == voltage[pos])
    
    s.minimize(z3.Sum(a))
    if s.check() == z3.sat:
        model = s.model()
        solution = [model.evaluate(a[i]).as_long() for i in range(len(switches))]
        return sum(solution)
    else:
        print("No solution found")
        return 0

def solve(filename, part):
    machines = read(filename)

    total_sum = 0
    for machine in machines:
        target, switches, voltage = machine
        total_sum += solve_machine(target, switches, voltage, part=part)

    return total_sum

if __name__ == "__main__":
    print(solve('part1.in', part=1))
    print(solve('part1.in', part=2))