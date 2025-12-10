from fractions import Fraction

def read(filename):
    with open(filename) as f:
        lines = f.readlines()
    
    result = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Parse the first section [.##.]
        bracket_start = line.find('[')
        bracket_end = line.find(']')
        first_section = line[bracket_start+1:bracket_end]
        binary_list = [1 if c == '#' else 0 for c in first_section]
        
        # Parse all () sections
        paren_lists = []
        i = bracket_end + 1
        while i < len(line):
            if line[i] == '(':
                close_paren = line.find(')', i)
                content = line[i+1:close_paren]
                if ',' in content:
                    paren_lists.append([int(x) for x in content.split(',')])
                else:
                    paren_lists.append([int(content)])
                i = close_paren + 1
            else:
                i += 1
        
        # Parse the {} section
        brace_start = line.find('{')
        brace_end = line.find('}')
        brace_content = line[brace_start+1:brace_end]
        final_list = [int(x) for x in brace_content.split(',')]
        
        result.append((binary_list, paren_lists, final_list))
    
    return result


def solve_gf2_min_weight(coef_matrix, target):
    """
    Solve system over GF(2) and find minimum weight solution.
    coef_matrix[i][j] is coefficient of variable j in equation i.
    target[i] is RHS of equation i.
    Returns solution minimizing sum(solution) or None if no solution.
    """
    if not coef_matrix:
        return []
    
    num_eqs = len(coef_matrix)
    num_vars = len(coef_matrix[0])
    
    # Create augmented matrix [A | b]
    aug = [row[:] + [target[i]] for i, row in enumerate(coef_matrix)]
    
    # Gaussian elimination over GF(2)
    pivot_row = 0
    pivot_cols = []
    
    for col in range(num_vars):
        # Find pivot in this column
        pivot = None
        for row in range(pivot_row, num_eqs):
            if aug[row][col] == 1:
                pivot = row
                break
        
        if pivot is None:
            continue  # Free variable
        
        # Swap rows
        aug[pivot_row], aug[pivot] = aug[pivot], aug[pivot_row]
        pivot_cols.append((pivot_row, col))
        
        # Eliminate in all other rows (XOR)
        for row in range(num_eqs):
            if row != pivot_row and aug[row][col] == 1:
                aug[row] = [(aug[row][j] ^ aug[pivot_row][j]) for j in range(num_vars + 1)]
        
        pivot_row += 1
    
    # Check consistency: if any row has all-zero coefficients but non-zero RHS
    for row in range(pivot_row, num_eqs):
        if aug[row][num_vars] == 1:
            return None
    
    # Find free variables
    pivot_var_set = {col for (_, col) in pivot_cols}
    free_vars = [v for v in range(num_vars) if v not in pivot_var_set]
    
    # Enumerate all 2^|free_vars| solutions to find minimum weight
    best_solution = None
    best_weight = float('inf')
    
    for mask in range(1 << len(free_vars)):
        sol = [0] * num_vars
        
        # Set free variables according to mask
        for i, v in enumerate(free_vars):
            sol[v] = (mask >> i) & 1
        
        # Compute pivot variables using back substitution
        for prow, pcol in reversed(pivot_cols):
            val = aug[prow][num_vars]
            for j in range(pcol + 1, num_vars):
                val ^= aug[prow][j] * sol[j]
            sol[pcol] = val
        
        weight = sum(sol)
        if weight < best_weight:
            best_weight = weight
            best_solution = sol
    
    return best_solution


def solve_linear_min_sum(coef_matrix, target):
    """
    Solve linear system over rationals and find non-negative integer solution
    minimizing sum of variables.
    coef_matrix[i][j] is coefficient of variable j in equation i.
    target[i] is RHS of equation i.
    Returns solution or None if no valid solution.
    """
    if not coef_matrix:
        return []
    
    num_eqs = len(coef_matrix)
    num_vars = len(coef_matrix[0])
    
    # Convert to Fractions for exact arithmetic
    aug = [[Fraction(coef_matrix[i][j]) for j in range(num_vars)] + [Fraction(target[i])] 
           for i in range(num_eqs)]
    
    # Gaussian elimination
    pivot_row = 0
    pivot_cols = []
    
    for col in range(num_vars):
        # Find pivot (non-zero entry)
        pivot = None
        for row in range(pivot_row, num_eqs):
            if aug[row][col] != 0:
                pivot = row
                break
        
        if pivot is None:
            continue
        
        # Swap rows
        aug[pivot_row], aug[pivot] = aug[pivot], aug[pivot_row]
        pivot_cols.append((pivot_row, col))
        
        # Scale pivot row to make pivot = 1
        scale = aug[pivot_row][col]
        aug[pivot_row] = [x / scale for x in aug[pivot_row]]
        
        # Eliminate in all other rows
        for row in range(num_eqs):
            if row != pivot_row and aug[row][col] != 0:
                factor = aug[row][col]
                aug[row] = [aug[row][j] - factor * aug[pivot_row][j] for j in range(num_vars + 1)]
        
        pivot_row += 1
    
    # Check consistency
    for row in range(pivot_row, num_eqs):
        if aug[row][num_vars] != 0:
            return None
    
    pivot_var_set = {col for (_, col) in pivot_cols}
    free_vars = [v for v in range(num_vars) if v not in pivot_var_set]
    
    if len(free_vars) == 0:
        # Unique solution - extract it
        sol = [Fraction(0)] * num_vars
        for prow, pcol in pivot_cols:
            sol[pcol] = aug[prow][num_vars]
        
        # Check non-negativity and integrality
        if all(s >= 0 and s.denominator == 1 for s in sol):
            return [int(s) for s in sol]
        return None
    
    # Underdetermined system: parameterize solution and search
    # Express pivot vars in terms of free vars:
    # pivot_var[i] = constant[i] - sum(coef[i][j] * free_var[j])
    
    # Build the dependency: for each pivot var, get its constant and coefficients for free vars
    pivot_info = {}  # pcol -> (constant, {free_var: coef})
    for prow, pcol in pivot_cols:
        constant = aug[prow][num_vars]
        free_coefs = {}
        for fv in free_vars:
            if aug[prow][fv] != 0:
                free_coefs[fv] = -aug[prow][fv]  # negative because we move to RHS
        pivot_info[pcol] = (constant, free_coefs)
    
    # Now search for minimum sum solution
    # We need free vars >= 0 and pivot vars >= 0
    # This is a search problem - use bounded search
    
    def compute_solution(free_vals):
        sol = [Fraction(0)] * num_vars
        for i, fv in enumerate(free_vars):
            sol[fv] = Fraction(free_vals[i])
        for pcol, (constant, free_coefs) in pivot_info.items():
            val = constant
            for fv, coef in free_coefs.items():
                val += coef * sol[fv]
            sol[pcol] = val
        return sol
    
    def is_valid(sol):
        return all(s >= 0 and s.denominator == 1 for s in sol)
    
    # Search with increasing sum of free variables
    # Upper bound: try reasonable range based on target values
    max_val = max(target) + 1 if target else 1
    
    best_solution = None
    best_sum = float('inf')
    
    # BFS-style search over free variable values
    from itertools import product
    
    for total in range(max_val * len(free_vars) + 1):
        if best_solution is not None and total >= best_sum:
            break
        
        # Generate all combinations of free vars that sum to <= total
        for vals in product(range(total + 1), repeat=len(free_vars)):
            if sum(vals) > total:
                continue
            sol = compute_solution(vals)
            if is_valid(sol):
                s = sum(int(x) for x in sol)
                if s < best_sum:
                    best_sum = s
                    best_solution = [int(x) for x in sol]
    
    return best_solution


def solve_part_1(filename):
    machines = read(filename)
    total_sum = 0
    
    for machine in machines:
        target, switches, voltage = machine
        num_switches = len(switches)
        num_positions = len(target)
        
        # Build coefficient matrix for the GF(2) system
        # Equation for position p: sum(a[i] * masks[i][p]) ≡ target[p] (mod 2)
        # So coef_matrix[p][i] = 1 if switch i affects position p
        coef_matrix = [[0] * num_switches for _ in range(num_positions)]
        for i in range(num_switches):
            for pos in switches[i]:
                coef_matrix[pos][i] = 1
        
        solution = solve_gf2_min_weight(coef_matrix, target)
        if solution:
            total_sum += sum(solution)
        else:
            print("No solution found")
    
    return total_sum


def solve_part_2(filename):
    machines = read(filename)
    total_sum = 0
    
    for machine in machines:
        target, switches, voltage = machine
        num_switches = len(switches)
        num_positions = len(target)
        
        # Build coefficient matrix for the linear system
        # Equation for position p: sum(a[i] * masks[i][p]) = voltage[p]
        coef_matrix = [[0] * num_switches for _ in range(num_positions)]
        for i in range(num_switches):
            for pos in switches[i]:
                coef_matrix[pos][i] = 1
        
        solution = solve_linear_min_sum(coef_matrix, voltage)
        if solution:
            total_sum += sum(solution)
        else:
            print("No solution found")
    
    return total_sum


if __name__ == "__main__":
    print(solve_part_1('part1.in'))
    print(solve_part_2('part1.in'))
