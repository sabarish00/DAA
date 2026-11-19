"""Task 6 - Last-mile delivery route optimisation: TSP with bitmask Dynamic Programming
CSA06 DAA | CO4 Assignment 4B | VISSHAAL R | 192421025

Location 0 = distribution hub (H). Locations 1..n = delivery points.
DP[S][j] = minimum cost of a path that starts at the hub, visits exactly the delivery set S and ends at j (j in S).
"""
import itertools
import math
import random
import time
import tracemalloc

INF = float("inf")


def tsp_dp(cost):
    n = len(cost) - 1  # number of delivery locations
    if n < 1:
        return 0, [0, 0], {"states": 0, "transitions": 0, "table_entries": 0}
    full = (1 << n) - 1
    dp = [[INF] * (n + 1) for _ in range(1 << n)]
    parent = [[-1] * (n + 1) for _ in range(1 << n)]
    states = transitions = 0
    for j in range(1, n + 1):  # base: hub -> j
        dp[1 << (j - 1)][j] = cost[0][j]
        states += 1
    for S in range(1, 1 << n):
        for j in range(1, n + 1):
            if not S & (1 << (j - 1)) or dp[S][j] == INF:
                continue
            for k in range(1, n + 1):  # extend the path to an unvisited k
                if S & (1 << (k - 1)):
                    continue
                transitions += 1
                T = S | (1 << (k - 1))
                cand = dp[S][j] + cost[j][k]
                if dp[T][k] == INF:
                    states += 1
                if cand < dp[T][k]:
                    dp[T][k], parent[T][k] = cand, j
    best, last = INF, -1
    for j in range(1, n + 1):  # close the tour: return to hub
        if dp[full][j] + cost[j][0] < best:
            best, last = dp[full][j] + cost[j][0], j
    route, S, j = [], full, last
    while j != -1:
        route.append(j)
        pj = parent[S][j]
        S ^= 1 << (j - 1)
        j = pj
    route = [0] + route[::-1] + [0]
    return best, route, {"states": states, "transitions": transitions, "table_entries": (1 << n) * n}


def brute_force(cost):
    n = len(cost) - 1
    results = []
    for perm in itertools.permutations(range(1, n + 1)):
        r = [0, *perm, 0]
        results.append((sum(cost[r[i]][r[i + 1]] for i in range(len(r) - 1)), r))
    return sorted(results)


def names(route, labels):
    return " -> ".join(labels[i] for i in route)


def random_matrix(n, seed):
    rng = random.Random(seed)
    m = [[0] * (n + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        for j in range(i + 1, n + 1):
            m[i][j] = m[j][i] = rng.randint(5, 60)
    return m


if __name__ == "__main__":
    labels = ["Hub", "A", "B", "C", "D", "E", "F"]
    cost = [
        [0, 12, 29, 22, 13, 24, 18],
        [12, 0, 19, 3, 25, 6, 21],
        [29, 19, 0, 21, 23, 28, 8],
        [22, 3, 21, 0, 4, 14, 17],
        [13, 25, 23, 4, 0, 16, 26],
        [24, 6, 28, 14, 16, 0, 9],
        [18, 21, 8, 17, 26, 9, 0],
    ]
    print("##### 6.3 Dataset: hub + 6 delivery locations; symmetric cost matrix #####")
    print("      " + "".join(f"{l:>5}" for l in labels))
    for i, row in enumerate(cost):
        print(f"{labels[i]:>5} " + "".join(f"{x:>5}" for x in row))
    best, route, info = tsp_dp(cost)
    print("\nOptimal route :", names(route, labels))
    print("Visit order   :", [labels[i] for i in route[1:-1]])
    print("Minimum Travel Cost =", best, "| DP info:", info)
    print("Leg costs     :", [cost[route[i]][route[i + 1]] for i in range(len(route) - 1)])

    print("\n##### 6.4 Validation: hub + 4 delivery locations (24 routes) #####")
    small = [row[:5] for row in cost[:5]]
    allr = brute_force(small)
    for c, r in allr:
        print(f"  {names(r, labels):<32} cost = {c}")
    sb, sr, _ = tsp_dp(small)
    print(f"Exhaustive optimum = {allr[0][0]} via {names(allr[0][1], labels)}")
    print(f"DP optimum         = {sb} via {names(sr, labels)}")
    print("Match:", sb == allr[0][0])
    mism = 0
    for seed in range(300):
        m = random_matrix(random.Random(seed).randint(2, 7), seed)
        if tsp_dp(m)[0] != brute_force(m)[0][0]:
            mism += 1
    print(f"Extra validation: 300 random instances (2..7 deliveries) -> mismatches = {mism}")

    print("\n##### 6.5 State-space growth #####")
    print(f"{'n':>3} {'DP states':>11} {'transitions':>13} {'table entries':>14} {'time (s)':>10} {'peak mem (MB)':>14}")
    for n in range(4, 15):
        m = random_matrix(n, 100 + n)
        tracemalloc.start()
        t0 = time.perf_counter()
        b, r, info = tsp_dp(m)
        dt = time.perf_counter() - t0
        peak = tracemalloc.get_traced_memory()[1] / 1e6
        tracemalloc.stop()
        print(f"{n:>3} {info['states']:>11} {info['transitions']:>13} {info['table_entries']:>14} {dt:>10.3f} {peak:>14.1f}")
    print("\nPermutations an exhaustive search would need: n! ->", {n: math.factorial(n) for n in (4, 8, 12, 14)})
    print("Subsets of n locations: 2^n ->", {n: 2 ** n for n in (4, 8, 12, 14, 20)}, "| 2^200 = %.2e" % (2 ** 200))
