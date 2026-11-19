"""Task 5 - Kruskal, Prim and Boruvka on one network
CSA06 DAA | CO4 Assignment 4B | VISSHAAL R | 192421025
"""
import heapq
from itertools import combinations

V = list("ABCDEFGH")
IDX = {v: i for i, v in enumerate(V)}

# (u, v, weight) - 8 facilities, 13 candidate links, all weights distinct
EDGES = [("A", "B", 4), ("A", "C", 8), ("B", "C", 6), ("B", "D", 11), ("C", "D", 3),
         ("C", "E", 9), ("D", "E", 5), ("D", "F", 12), ("E", "F", 2), ("E", "G", 10),
         ("F", "G", 7), ("F", "H", 13), ("G", "H", 1)]
# Modified network: A-C 8->6 (ties with B-C) and E-G 10->7 (ties with F-G)
TIE_EDGES = [(u, v, {("A", "C"): 6, ("E", "G"): 7}.get((u, v), w)) for u, v, w in EDGES]


class DSU:
    def __init__(self, items):
        self.p = {x: x for x in items}

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        self.p[ra] = rb
        return True


def fmt(e):
    return f"{e[0]}-{e[1]}({e[2]})"


def kruskal(edges, reverse_ties=False, verbose=False):
    order = sorted(range(len(edges)), key=lambda k: (edges[k][2], -k if reverse_ties else k))
    dsu, tree, total = DSU(V), [], 0
    for k in order:
        u, v, w = edges[k]
        ok = dsu.union(u, v)
        if verbose:
            print(f"  consider {fmt(edges[k]):<8} -> {'ACCEPT (joins two components)' if ok else 'REJECT (would form a cycle)'}")
        if ok:
            tree.append(edges[k]); total += w
    return tree, total


def prim(edges, start="A", verbose=False):
    adj = {v: [] for v in V}
    for k, (u, v, w) in enumerate(edges):
        adj[u].append((w, k, v)); adj[v].append((w, k, u))
    seen, tree, total, pq = {start}, [], 0, list(adj[start])
    heapq.heapify(pq)
    if verbose:
        print(f"  start at {start}; frontier = {sorted((w, edges[k][0] + '-' + edges[k][1]) for w, k, _ in pq)}")
    while pq and len(seen) < len(V):
        w, k, v = heapq.heappop(pq)
        if v in seen:
            continue
        seen.add(v); tree.append(edges[k]); total += w
        for item in adj[v]:
            if item[2] not in seen:
                heapq.heappush(pq, item)
        if verbose:
            print(f"  add {fmt(edges[k]):<8} (new vertex {v}); tree vertices = {sorted(seen)}")
    return tree, total


def boruvka(edges, reverse_ties=False, verbose=False):
    dsu, tree, total, rnd = DSU(V), [], 0, 0
    comps = len(V)
    while comps > 1:
        rnd += 1
        cheapest = {}
        for k, (u, v, w) in enumerate(edges):
            ru, rv = dsu.find(u), dsu.find(v)
            if ru == rv:
                continue
            key = (w, -k if reverse_ties else k)  # consistent total order => no cycles
            for r in (ru, rv):
                if r not in cheapest or key < cheapest[r][0]:
                    cheapest[r] = (key, k)
        added = []
        for r, (_, k) in cheapest.items():
            u, v, w = edges[k]
            if dsu.union(u, v):
                tree.append(edges[k]); total += w; comps -= 1; added.append(edges[k])
        if verbose:
            print(f"  round {rnd}: cheapest edge per component = "
                  f"{ {r: fmt(edges[k]) for r, (_, k) in sorted(cheapest.items())} }")
            print(f"           edges added = {[fmt(e) for e in added]}; components left = {comps}")
    return tree, total


def all_msts(edges):
    """Brute force: every (|V|-1)-edge acyclic subset with minimum total weight."""
    best, found = None, []
    for subset in combinations(range(len(edges)), len(V) - 1):
        dsu = DSU(V)
        if all(dsu.union(edges[k][0], edges[k][1]) for k in subset):
            w = sum(edges[k][2] for k in subset)
            if best is None or w < best:
                best, found = w, [subset]
            elif w == best:
                found.append(subset)
    return best, found


def canon(tree):
    return sorted(fmt(e) for e in tree)


if __name__ == "__main__":
    print("NETWORK 1 (distinct weights):", [fmt(e) for e in EDGES], "\n")
    print("---- Kruskal (sort edges; next safe edge = lightest edge joining two different components) ----")
    kt, kw = kruskal(EDGES, verbose=True)
    print("  MST:", canon(kt), "total =", kw, "\n  state kept: sorted edge list + union-find (component labels)\n")
    print("---- Prim from A (grow one tree; next safe edge = lightest edge leaving the tree) ----")
    pt, pw = prim(EDGES, "A", verbose=True)
    print("  MST:", canon(pt), "total =", pw, "\n  state kept: visited set + priority queue of frontier edges\n")
    print("---- Boruvka (all components pick their cheapest outgoing edge each round) ----")
    bt, bw = boruvka(EDGES, verbose=True)
    print("  MST:", canon(bt), "total =", bw,
          "\n  state kept: component label per vertex + cheapest-edge slot per component\n")
    print("Same MST from all three:", canon(kt) == canon(pt) == canon(bt))
    best, found = all_msts(EDGES)
    print(f"Brute force: minimum spanning cost = {best}, number of minimum spanning trees = {len(found)}\n")

    print("=" * 90)
    print("NETWORK 2 (ties introduced: A-C = 6 ties with B-C = 6; E-G = 7 ties with F-G = 7)")
    print([fmt(e) for e in TIE_EDGES])
    best2, found2 = all_msts(TIE_EDGES)
    msts = {tuple(sorted(fmt(TIE_EDGES[k]) for k in s)) for s in found2}
    print(f"Brute force: min cost = {best2}; number of distinct MSTs = {len(msts)}")
    for m in sorted(msts):
        print("  ", m)
    print("\nResults of each algorithm / tie-breaking rule:")
    runs = {
        "Kruskal (ties: earlier edge first)": kruskal(TIE_EDGES),
        "Kruskal (ties: later edge first)": kruskal(TIE_EDGES, reverse_ties=True),
        "Prim from A": prim(TIE_EDGES, "A"),
        "Prim from H": prim(TIE_EDGES, "H"),
        "Boruvka (ties: lower edge index)": boruvka(TIE_EDGES),
        "Boruvka (ties: higher edge index)": boruvka(TIE_EDGES, reverse_ties=True),
    }
    for name, (t, w) in runs.items():
        c = tuple(canon(t))
        print(f"  {name:<38} cost={w} edges={list(c)} valid MST: {c in msts}")
    distinct = {tuple(canon(t)) for t, _ in runs.values()}
    print(f"\nDistinct edge sets produced: {len(distinct)} (all with cost {best2})")
