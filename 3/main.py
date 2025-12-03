from typing import List

def read_input(filename: str) -> List[str]:
    return [line.strip() for line in open(filename, 'r')]

def get_max_joltage(bank: str, index: int, picks: int) -> int:
    n = len(bank)
    INF = 10**18
    dp = [[-INF] * (picks + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = 0
    for i in range(n - 1, index - 1, -1):
        for j in range(1, picks + 1):
            skip = dp[i + 1][j]
            pick = int(bank[i]) * (10 ** (j - 1)) + dp[i + 1][j - 1]
            dp[i][j] = max(skip, pick)
    
    return dp[index][picks]

def solve(filename: str, num_batteries: int) -> int:
    return sum([ get_max_joltage(line, 0, num_batteries) for line in read_input(filename) ])

if __name__ == "__main__":
    print(solve('sample.in', 2))
    print(solve('part1.in',  2))
    print(solve('part1.in',  12))