"""Task 3 - Routing engine: Dijkstra, Bellman-Ford, Floyd, Warshall
CSA06 DAA | CO4 Assignment 4B | VISSHAAL R | 192421025
"""
import heapq

INF = float("inf")
V = list("ABCDEFGH")

# Directed weighted network: 8 vertices, 12 non-negative edges (+ stage edges below)
BASE_EDGES = [
    ("A", "B", 6), ("A", "C", 2), ("C", "D", 3), ("D", "E", 4), ("C", "E", 8),
    ("B", "F", 1), ("F", "H", 2), ("E", "F", 7), ("E", "G", 3), ("G", "H", 5),
    ("D", "G", 10), ("F", "G", 4),
]
NEG_EDGE = ("E", "B", -5)     # Stage B : negative edge, no cycle
CYCLE_EDGE = ("G", "E", -5)   # Stage C : E->G (3) + G->E (-5) = -2 (negative cycle)


def adjacency(edges):
    adj = {v: [] for v in V}
    for u, v, w in edges:
        adj[u].append((v, w))
    return adj


def path_to(pred, src, dst):
    if dst != src and pred[dst] is None:
        return None
    p = [dst]
    while p[-1] != src:
        p.append(pred[p[-1]])
    return p[::-1]


def dijkstra(edges, src):
    """Strict Dijkstra: a vertex is FINAL once extracted and is never updated again."""
    adj = adjacency(edges)
    dist = {v: INF for v in V}; pred = {v: None for v in V}
    dist[src] = 0; final = set(); order = []
    pq = [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if u in final:
            continue
        final.add(u); order.append((u, d))
        for v, w in adj[u]:
            if v not in final and d + w < dist[v]:
                dist[v] = d + w; pred[v] = u
                heapq.heappush(pq, (dist[v], v))
    return dist, pred, order


def bellman_ford(edges, src):
    """Returns dist, pred, negative_cycle (list of vertices or None), passes used."""
    dist = {v: INF for v in V}; pred = {v: None for v in V}; dist[src] = 0
    passes = 0
    for _ in range(len(V) - 1):
        passes += 1
        changed = False
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w; pred[v] = u; changed = True
        if not changed:
            break
    for u, v, w in edges:  # n-th pass: any improvement => negative cycle
        if dist[u] != INF and dist[u] + w < dist[v]:
            pred[v] = u
            x = v
            for _ in range(len(V)):  # step back n times to land inside the cycle
                x = pred[x]
            cycle, cur = [x], pred[x]
            while cur != x:
                cycle.append(cur); cur = pred[cur]
            cycle = cycle[::-1]
            return dist, pred, cycle + [cycle[0]], passes + 1
    return dist, pred, None, passes


def print_sssp(title, dist, pred, src):
    print(title)
    print(f"{'Vertex':<7}{'Distance':<10}{'Pred':<6}Path")
    for v in V:
        p = path_to(pred, src, v)
        print(f"{v:<7}{str(dist[v]):<10}{str(pred[v]):<6}{' -> '.join(p) if p else 'unreachable'}")


def floyd(edges):
    idx = {v: i for i, v in enumerate(V)}; n = len(V)
    D = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for u, v, w in edges:
        D[idx[u]][idx[v]] = min(D[idx[u]][idx[v]], w)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if D[i][k] + D[k][j] < D[i][j]:
                    D[i][j] = D[i][k] + D[k][j]
    return D


def warshall(edges):
    idx = {v: i for i, v in enumerate(V)}; n = len(V)
    R = [[i == j for j in range(n)] for i in range(n)]
    for u, v, _ in edges:
        R[idx[u]][idx[v]] = True
    for k in range(n):
        for i in range(n):
            for j in range(n):
                R[i][j] = R[i][j] or (R[i][k] and R[k][j])
    return R


def print_matrix(M, cell):
    print("     " + "".join(f"{v:>5}" for v in V))
    for i, row in enumerate(M):
        print(f"{V[i]:>4} " + "".join(f"{cell(x):>5}" for x in row))


if __name__ == "__main__":
    print("GRAPH (directed): vertices", V)
    print("Edges:", BASE_EDGES, f"-> {len(V)} vertices, {len(BASE_EDGES)} edges\n")

    print("################ STAGE A - Dijkstra from A (normal routing) ################")
    d, p, order = dijkstra(BASE_EDGES, "A")
    print_sssp("Shortest paths:", d, p, "A")
    print("Order in which vertices are finalised:", ", ".join(f"{u}({dd})" for u, dd in order))

    print("\n################ STAGE B - negative edge E->B (-5) ################")
    print("PREDICTION (before running): Dijkstra will NOT stay valid. B is finalised at 6 (via A) before E (9) is")
    print("  processed; the new edge E->B gives B = 9-5 = 4, but B is already final. Expected wrong vertices:")
    print("  B and everything routed through B (F, H, G).")
    edges_b = BASE_EDGES + [NEG_EDGE]
    d1, p1, o1 = dijkstra(edges_b, "A")
    print_sssp("Dijkstra on modified graph:", d1, p1, "A")
    print("Finalisation order:", ", ".join(f"{u}({dd})" for u, dd in o1))
    d2, p2, cyc, passes = bellman_ford(edges_b, "A")
    print_sssp("\nBellman-Ford on modified graph:", d2, p2, "A")
    print(f"Negative cycle: {cyc} (passes used: {passes})")
    print("\nComparison (Dijkstra vs Bellman-Ford):")
    for v in V:
        flag = "" if d1[v] == d2[v] else "   <== Dijkstra WRONG"
        print(f"  {v}: Dijkstra={d1[v]}  Bellman-Ford={d2[v]}{flag}")

    print("\n################ STAGE C - reachable negative cycle (add G->E -5) ################")
    edges_c = edges_b + [CYCLE_EDGE]
    dj, pj, oj = dijkstra(edges_c, "A")
    print("Dijkstra still 'terminates' and returns misleading numbers:", dj)
    dist, pred, cyc, passes = bellman_ford(edges_c, "A")
    if cyc:
        print("Bellman-Ford: NEGATIVE-WEIGHT CYCLE DETECTED on pass", passes, "- shortest paths are undefined.")
        print("Cycle:", " -> ".join(cyc))
        wmap = {(a, b): w for a, b, w in edges_c}
        print("Cycle weight:", sum(wmap[(cyc[k], cyc[k + 1])] for k in range(len(cyc) - 1)))
    print("Detection rule: after |V|-1 passes every shortest path is final; if any edge still relaxes on pass |V|, a")
    print("  negative cycle is reachable. The cycle is recovered by walking predecessors |V| steps back and then until a repeat.")

    print("\n################ STAGE D - all pairs (graph with the negative edge, no cycle) ################")
    D = floyd(edges_b)
    print("Floyd distance matrix:")
    print_matrix(D, lambda x: "INF" if x == INF else str(x))
    print("Negative values on diagonal (would mean negative cycle):",
          [V[i] for i in range(len(V)) if D[i][i] < 0] or "none")
    R = warshall(edges_b)
    print("\nWarshall reachability matrix (1 = reachable):")
    print_matrix(R, lambda x: "1" if x else "0")
    print("\nFloyd on the cycle graph, diagonal check:",
          [V[i] for i, r in enumerate(floyd(edges_c)) if r[i] < 0], "have negative D[i][i]")
