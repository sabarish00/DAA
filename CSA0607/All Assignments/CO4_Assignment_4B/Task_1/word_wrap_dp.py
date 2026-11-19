"""Task 1 - Word Wrap as a Document-Layout Engine (Dynamic Programming)
CSA06 DAA | CO4 Assignment 4B | VISSHAAL R | 192421025

Penalty model (assumption): a NON-FINAL line with `extra` unused spaces costs extra**2.
The FINAL line costs 0. Words are separated by exactly one space.
State: best[i] = minimum penalty for laying out words i..n-1 (suffix formulation)
Choice: choice[i] = j -> words i..j-1 form the next line.
"""
import random
from itertools import combinations

INF = float("inf")


def extra_spaces(words, i, j, width):
    """Unused spaces if words[i..j-1] share a single line."""
    used = sum(len(w) for w in words[i:j]) + (j - i - 1)
    return width - used


def line_penalty(words, i, j, width):
    extra = extra_spaces(words, i, j, width)
    if extra < 0:
        return INF  # does not fit
    if j == len(words):
        return 0  # final line carries no penalty
    return extra ** 2


def validate(words, width):
    if width <= 0:
        raise ValueError("line width must be positive")
    for w in words:
        if len(w) > width:
            raise ValueError(f"word '{w}' (length {len(w)}) is longer than width {width}")


def word_wrap(words, width, trace=None):
    """Returns (total_penalty, [(i,j),...], best[], choice[])."""
    validate(words, width)
    n = len(words)
    best = [INF] * (n + 1)
    choice = [-1] * (n + 1)
    best[n] = 0  # base state: nothing left to place
    for i in range(n - 1, -1, -1):
        for j in range(i + 1, n + 1):
            pen = line_penalty(words, i, j, width)
            if pen == INF:
                break  # adding more words can only overflow further
            cand = pen + best[j]
            if trace is not None:
                trace.append((i, j, pen, best[j], cand))
            if cand < best[i]:
                best[i], choice[i] = cand, j
    lines, i = [], 0
    while i < n:
        lines.append((i, choice[i]))
        i = choice[i]
    return best[0], lines, best, choice


def report(words, width, show_states=False):
    trace = [] if show_states else None
    total, lines, best, choice = word_wrap(words, width, trace)
    print(f"=== width = {width} ===")
    if show_states:
        print("DP states (i = first word of suffix, j = first word of NEXT line):")
        cur = None
        for (i, j, pen, rest, cand) in trace:
            if i != cur:
                cur = i
                print(f"  state i={i} ('{words[i]}')")
            mark = " <== chosen" if choice[i] == j and cand == best[i] else ""
            print(f"    line=words[{i}..{j-1}] penalty={pen:>3} best[{j}]={rest:>3} total={cand:>3}{mark}")
        print("  best[]   =", best)
        print("  choice[] =", choice)
    print(f"{'Line':<5}{'Words on line':<{width + 2}}{'Unused':>7}{'Penalty':>9}")
    for k, (i, j) in enumerate(lines, 1):
        txt = " ".join(words[i:j])
        print(f"{k:<5}{txt:<{width + 2}}{extra_spaces(words, i, j, width):>7}{line_penalty(words, i, j, width):>9}")
    print(f"Minimum total penalty = {total}\n")
    return total, lines


def brute_force(words, width):
    """Exhaustive reference: try every set of break positions."""
    n = len(words)
    best = INF
    for r in range(n):
        for cuts in combinations(range(1, n), r):
            bounds = [0, *cuts, n]
            pens = [line_penalty(words, bounds[k], bounds[k + 1], width) for k in range(len(bounds) - 1)]
            best = min(best, sum(pens))
    return best


TEXT = ("Dynamic programming solves complex problems by breaking them "
        "into overlapping subproblems and storing every answer").split()

if __name__ == "__main__":
    print("TEXT:", " ".join(TEXT), f"({len(TEXT)} words)\n")
    print("##### 1.1 / 1.2 Baseline run with DP states (width 20) #####")
    base_total, base_lines = report(TEXT, 20, show_states=True)

    print("##### 1.3 Requirement change: three further widths #####")
    # Predictions recorded BEFORE execution (see report):
    predictions = {26: ("changes", "line 1", "decrease"),
                   32: ("changes", "line 1", "decrease"),
                   40: ("changes", "line 1", "decrease")}
    for w, (p_change, p_where, p_pen) in predictions.items():
        total, lines = report(TEXT, w)
        changed = lines != base_lines
        first = next((k for k in range(min(len(lines), len(base_lines))) if lines[k] != base_lines[k]), None)
        actual_pen = "decrease" if total < base_total else ("increase" if total > base_total else "same")
        print(f"PREDICTED: arrangement {p_change}; first change at {p_where}; penalty {p_pen}")
        print(f"ACTUAL   : arrangement {'changes' if changed else 'same'}; first change at "
              f"line {first + 1 if first is not None else '-'}; penalty {base_total} -> {total} ({actual_pen})\n")

    print("##### 1.4 Boundary tests #####")
    b = "aaa bbb cc".split()
    print("Boundary case: words =", b, ", width = 7 (exact fit 'aaa bbb' + short final line)")
    t, _ = report(b, 7)
    assert t == 0, "defect: exact-fit or final-line rule wrong"
    for bad_words, bad_w in (([], 5), (["x"], 1), (["abcdefgh"], 5)):
        try:
            print("case", bad_words, bad_w, "->", word_wrap(bad_words, bad_w)[0])
        except ValueError as e:
            print("case", bad_words, bad_w, "-> ValueError:", e)

    print("\n##### Validation against exhaustive search (500 random cases) #####")
    random.seed(7)
    ok = 0
    for _ in range(500):
        n = random.randint(1, 9)
        ws = ["x" * random.randint(1, 8) for _ in range(n)]
        W = random.randint(max(map(len, ws)), 20)
        assert word_wrap(ws, W)[0] == brute_force(ws, W), (ws, W)
        ok += 1
    print(f"{ok}/500 random cases: DP penalty == brute-force penalty")
