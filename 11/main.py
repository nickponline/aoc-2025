import re

def read(filename):
    G = {}
    with open(filename, 'r') as f:
        for line in f:
            if match := re.match(r'(\w+):\s*(.*)', line.strip()):
                source, dests = match.groups()
                G[source] = dests.split() if dests else []
    return G

def count_paths(G, start, end, check_nodes=None):
    check_nodes = check_nodes or set()
    memo = {}
    
    def dfs(node, visited_nodes, visited_set):
        if node == end:
            return 1 if check_nodes <= visited_nodes else 0
        key = (node, frozenset(visited_nodes))
        if key in memo:
            return memo[key]
        total_paths = 0
        for neighbor in G.get(node, []):
            if neighbor not in visited_set:
                new_visited_nodes = visited_nodes | {neighbor} if neighbor in check_nodes else visited_nodes
                total_paths += dfs(neighbor, new_visited_nodes, visited_set | {neighbor})
        memo[key] = total_paths
        return total_paths
    
    return dfs(start, {start} & check_nodes, {start})

def solve(filename, start, end, passing=None):
    return count_paths(read(filename), start, end, passing)

if __name__ == "__main__":
    print(solve('sample1.in', 'you', 'out'))
    print(solve('part1.in', 'you', 'out'))
    print(solve('sample2.in', 'svr', 'out', {'fft', 'dac'}))
    print(solve('part1.in', 'svr', 'out', {'fft', 'dac'}))