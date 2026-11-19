"""Task 2 - Greedy (Fractional Knapsack) vs Dynamic Programming (0/1 Knapsack)
CSA06 DAA | CO4 Assignment 4B | VISSHAAL R | 192421025
"""
import random
from functools import cmp_to_key
from fractions import Fraction


def fractional_greedy(items, capacity, verbose=False):
    """Solution A. items = [(id, weight, value)]. Returns value, picks[(id,fraction)], ops."""
    comparisons = 0

    def cmp(a, b):
        nonlocal comparisons
        comparisons += 1
        ra, rb = Fraction(a[2], a[1]), Fraction(b[2], b[1])
        return -1 if ra > rb else (1 if ra < rb else 0)

    order = sorted(items, key=cmp_to_key(cmp))
    remaining, value, picks, steps = capacity, Fraction(0), [], 0
    for (iid, w, v) in order:
        steps += 1
        if remaining == 0:
            break
        take = min(Fraction(1), Fraction(remaining) / w)
        if verbose:
            print(f"  consider {iid}: w={w} v={v} ratio={v/w:.2f} remaining={float(remaining):g} -> take {float(take):.2f}")
        value += take * v
        remaining -= take * w
        picks.append((iid, take))
    return float(value), picks, {"comparisons": comparisons, "selection_steps": steps,
                                 "memory_cells": len(items)}


def greedy_01(items, capacity):
    """Same value/weight intuition applied naively to 0/1 (whole item or skip)."""
    order = sorted(items, key=lambda t: t[2] / t[1], reverse=True)
    remaining, value, picks = capacity, 0, []
    for (iid, w, v) in order:
        if w <= remaining:
            picks.append(iid); remaining -= w; value += v
    return value, picks, order


def knapsack_dp(items, capacity):
    """Solution B. Returns optimum, chosen ids, ops (cell updates) and memory cells."""
    n = len(items)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    cells = 0
    for i in range(1, n + 1):
        _, w, v = items[i - 1]
        for c in range(capacity + 1):
            cells += 1
            dp[i][c] = dp[i - 1][c]
            if w <= c and dp[i - 1][c - w] + v > dp[i][c]:
                dp[i][c] = dp[i - 1][c - w] + v
    chosen, c = [], capacity
    for i in range(n, 0, -1):
        if dp[i][c] != dp[i - 1][c]:
            chosen.append(items[i - 1][0]); c -= items[i - 1][1]
    return dp[n][capacity], chosen[::-1], {"cell_updates": cells, "memory_cells": (n + 1) * (capacity + 1)}


def show_fraction_picks(picks):
    return ", ".join(f"{i} x {float(f):.2f}" for i, f in picks)


if __name__ == "__main__":
    print("########## 2.1 NORMAL CASE (capacity 40) ##########")
    normal = [("L1", 12, 36), ("L2", 8, 32), ("L3", 20, 50), ("L4", 10, 45), ("L5", 15, 30)]
    print("Items (id, weight, value):", normal)
    print("Solution A - Fractional Knapsack decision sequence:")
    v, picks, ops = fractional_greedy(normal, 40, verbose=True)
    print(f"  Selected: {show_fraction_picks(picks)}   Value = {v}   ops = {ops}")
    vd, chosen, opsd = knapsack_dp(normal, 40)
    print(f"Solution B - 0/1 DP: items {chosen}   Value = {vd}   ops = {opsd}")
    print("(Fractional optimum is an upper bound for 0/1: 138 >= 127)")

    print("\n########## 2.2 BREAK THE GREEDY INTUITION (own instance, capacity 10) ##########")
    bad = [("A", 6, 13), ("B", 5, 10), ("C", 5, 10)]
    print("Items:", bad, "ratios: A=%.2f B=%.2f C=%.2f" % tuple(v / w for _, w, v in bad))
    gv, gp, order = greedy_01(bad, 10)
    dv, dc, _ = knapsack_dp(bad, 10)
    fv, fp, _ = fractional_greedy(bad, 10)
    print("Greedy order by ratio:", [o[0] for o in order])
    print(f"Greedy 0/1 picks {gp} value = {gv}")
    print(f"DP optimum picks {dc} value = {dv}")
    print(f"Gap = {dv - gv} (greedy achieves {100*gv/dv:.1f}% of optimum)")
    print("Fractional relaxation value (upper bound):", fv)
    print("First harmful commitment: greedy takes A (best ratio 2.17) -> remaining capacity 4,")
    print("  which fits neither B nor C, so 4 units of capacity are wasted and B+C (value 20) is lost.")

    print("\n########## 2.3 ENGINEERING COMPARISON (capacity 1000, random instances) ##########")
    random.seed(42)
    print(f"{'n':>5} {'greedy cmp':>11} {'greedy mem':>11} {'DP cell upd':>12} {'DP mem cells':>13} "
          f"{'greedy01':>9} {'DP opt':>8} {'frac UB':>9} {'quality%':>9}")
    for n in (10, 50, 100, 200, 400):
        its = [(f"i{k}", random.randint(5, 120), random.randint(10, 300)) for k in range(n)]
        fv, _, fo = fractional_greedy(its, 1000)
        gv, _, _ = greedy_01(its, 1000)
        dv, _, do = knapsack_dp(its, 1000)
        print(f"{n:>5} {fo['comparisons']:>11} {fo['memory_cells']:>11} {do['cell_updates']:>12} "
              f"{do['memory_cells']:>13} {gv:>9} {dv:>8} {fv:>9.1f} {100*gv/dv:>9.2f}")

    print("\n########## 2.4 CHANGED REQUIREMENT - quality of greedy 0/1 over many instances ##########")
    random.seed(2026)
    for label, n_range, cap_frac in (("small (n=4..8)", (4, 8), 0.5), ("large (n=100..200)", (100, 200), 0.3)):
        ratios, optimal_hits, trials = [], 0, 300
        for _ in range(trials):
            n = random.randint(*n_range)
            its = [(f"i{k}", random.randint(1, 40), random.randint(1, 100)) for k in range(n)]
            cap = max(1, int(cap_frac * sum(w for _, w, _ in its)))
            gv, _, _ = greedy_01(its, cap)
            dv, _, _ = knapsack_dp(its, cap)
            ratios.append(gv / dv)
            optimal_hits += (gv == dv)
        print(f"{label:<20} trials={trials} mean quality={100*sum(ratios)/trials:.2f}% "
              f"worst={100*min(ratios):.2f}% exactly optimal in {optimal_hits}/{trials}")
