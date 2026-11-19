"""Task 4 - Assembly-line scheduling with Dynamic Programming
CSA06 DAA | CO4 Assignment 4B | VISSHAAL R | 192421025

Convention: t1[i] = time to move from line 1 (after station i+1) to line 2 before station i+2 (0-based list);
            t2[i] likewise from line 2 to line 1.
"""


def assembly_line(a1, a2, t1, t2, e1, e2, x1, x2):
    n = len(a1)
    if n == 0 or len(a2) != n or len(t1) != n - 1 or len(t2) != n - 1:
        raise ValueError("inconsistent input sizes")
    f1, f2 = [0] * n, [0] * n
    from1, from2 = [None] * n, [None] * n  # which line we came from
    trace = []
    f1[0], f2[0] = e1 + a1[0], e2 + a2[0]
    for i in range(1, n):
        s1, x_1 = f1[i - 1] + a1[i], f2[i - 1] + t2[i - 1] + a1[i]
        s2, x_2 = f2[i - 1] + a2[i], f1[i - 1] + t1[i - 1] + a2[i]
        f1[i], from1[i] = (s1, 1) if s1 <= x_1 else (x_1, 2)
        f2[i], from2[i] = (s2, 2) if s2 <= x_2 else (x_2, 1)
        trace.append((i + 1, s1, x_1, "Stay" if s1 <= x_1 else "Transfer", s2, x_2, "Stay" if s2 <= x_2 else "Transfer"))
    total1, total2 = f1[-1] + x1, f2[-1] + x2
    last_line, total = (1, total1) if total1 <= total2 else (2, total2)
    route = [0] * n
    line = last_line
    for i in range(n - 1, -1, -1):
        route[i] = line
        if i > 0:
            line = from1[i] if line == 1 else from2[i]
    return total, route, f1, f2, trace, (total1, total2)


def print_trace(f1, f2, trace, e1, e2, a1, a2):
    print(f"{'Stn':<4}{'L1 stay':>8}{'L1 xfer':>8}{'Sel':>10}{'L2 stay':>9}{'L2 xfer':>8}{'Sel':>10}  f1  f2")
    print(f"{1:<4}{'-':>8}{'-':>8}{'Entry':>10}{'-':>9}{'-':>8}{'Entry':>10}  {f1[0]:<3} {f2[0]:<3} "
          f"(e1+a1[1]={e1}+{a1[0]}, e2+a2[1]={e2}+{a2[0]})")
    for (st, s1, x1_, sel1, s2, x2_, sel2) in trace:
        print(f"{st:<4}{s1:>8}{x1_:>8}{sel1:>10}{s2:>9}{x2_:>8}{sel2:>10}  {f1[st-1]:<3} {f2[st-1]:<3}")


def print_route(route):
    print("Entry")
    for i, line in enumerate(route):
        if i > 0 and route[i - 1] != line:
            print(f"  | Transfer (Line {route[i-1]} -> Line {line})")
        else:
            print("  |")
        print(f"Line {line} - Station {i+1}")
    print("  |\nExit")


def run(title, a1, a2, t1, t2, e1, e2, x1, x2, show_trace=True, show_route=True):
    total, route, f1, f2, trace, finals = assembly_line(a1, a2, t1, t2, e1, e2, x1, x2)
    print(f"--- {title} ---")
    if show_trace:
        print_trace(f1, f2, trace, e1, e2, a1, a2)
    print(f"Exit options: Line1 {f1[-1]}+{x1}={finals[0]} | Line2 {f2[-1]}+{x2}={finals[1]}")
    transfers = [(i + 1, route[i], route[i + 1]) for i in range(len(route) - 1) if route[i] != route[i + 1]]
    print("Lines chosen per station :", route)
    print("Transfer points          :", [f"after station {s}: L{a}->L{b}" for s, a, b in transfers] or "none")
    if show_route:
        print_route(route)
    print("Minimum Production Time =", total, "\n")
    return total, route


if __name__ == "__main__":
    a1 = [7, 9, 3, 4, 8, 4]; a2 = [8, 5, 6, 4, 5, 7]
    t1 = [2, 3, 1, 3, 4]; t2 = [2, 1, 2, 2, 1]
    e1, e2, x1, x2 = 2, 4, 3, 2
    print("INPUT a1 =", a1, " a2 =", a2, " t1 =", t1, " t2 =", t2, " e1,e2 =", e1, e2, " x1,x2 =", x1, x2, "\n")
    base_total, base_route = run("4.1 / 4.2 Baseline", a1, a2, t1, t2, e1, e2, x1, x2)

    print("=== 4.3 PREDICT BEFORE YOU EXECUTE ===")
    print("Change: t1[3] (Line1 station 3 -> Line2 station 4) from 1 to 15.")
    print("PREDICTION: route WILL change; the transfer L1->L2 before station 4 is the decision affected (the baseline")
    print("  uses it); the optimiser should stay on Line 2 or find another switch; total time will INCREASE above 38.\n")
    t1_mod = t1[:]; t1_mod[2] = 15
    tot, rt = run("4.3 Modified transfer time", a1, a2, t1_mod, t2, e1, e2, x1, x2, show_route=False)
    print("ACTUAL: route changed:", rt != base_route, "| total", base_total, "->", tot,
          "(", "increase" if tot > base_total else "no increase", ")\n")

    print("=== 4.4 PRODUCTION DISRUPTION ===")
    print("Station 3 on Line 1 slows from 3 to 25 (temporary fault).")
    a1_d = a1[:]; a1_d[2] = 25
    tot, rt = run("4.4 Disruption", a1_d, a2, t1, t2, e1, e2, x1, x2)
    print("Baseline route:", base_route, "-> New route:", rt, "| first changed station:",
          next(i + 1 for i in range(len(rt)) if rt[i] != base_route[i]), "| total", base_total, "->", tot)

    print("\n=== Boundary / failure tests ===")
    print("single station:", assembly_line([5], [4], [], [], 1, 1, 1, 1)[:2])
    try:
        assembly_line([1, 2], [1], [1], [1], 0, 0, 0, 0)
    except ValueError as e:
        print("invalid input ->", e)
