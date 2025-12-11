import re

def read(filename):
    G = {}
    
    with open(filename, 'r') as f:
        for line in f:
            if match := re.match(r'(\w+):\s*(.*)', line.strip()):
                source, dests = match.groups()
                if dests:
                    G[source] = dests.split()
                else:
                    G[source] = []
    
    return G

def count_paths(G, start, end, check_nodes=None):
    if check_nodes is None:
        check_nodes = set()
    
    memo = {}
    
    def dfs(node, visited_nodes, visited_set):
        if node == end:
            return 1 if all(n in visited_nodes for n in check_nodes) else 0
        
        key = (node, frozenset(visited_nodes))
        if key in memo:
            return memo[key]
        
        total_paths = 0
        if node in G:
            for neighbor in G[node]:
                if neighbor not in visited_set:
                    new_visited_set = visited_set | {neighbor}
                    new_visited_nodes = visited_nodes | {neighbor} if neighbor in check_nodes else visited_nodes           
                    total_paths += dfs(neighbor, new_visited_nodes, new_visited_set)
        memo[key] = total_paths
        return total_paths
    
    initial_visited = {start} & check_nodes
    result = dfs(start, initial_visited, {start})
    return result

def solve1(filename):
    G = read(filename)
    return count_paths(G, 'you', 'out')

def solve2(filename):
    G = read(filename)
    return count_paths(G, 'svr', 'out', check_nodes={'fft', 'dac'})

if __name__ == "__main__":
    print(solve1('sample1.in'))
    print(solve1('part1.in'))

    print(solve2('sample2.in'))
    print(solve2('part1.in'))