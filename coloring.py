"""Colouring the plane: two facts people proved by hand, checked by brute force.

Rule: two points exactly 1 apart may not share a colour.
  1. The Moser spindle (7 points, 11 unit distances) cannot be coloured with 3 colours.
  2. A tiling by hexagons in 7 colours obeys the rule everywhere.
So the answer to "how many colours does the plane need" was known to lie between 4 and 7.
"""
import itertools
import json
import math
import random


def spindle():
    """Two rhombi of unit triangles sharing point A, opened until their far tips are 1 apart."""
    turn = 2 * math.asin(1 / (2 * math.sqrt(3)))

    def at(angle):
        return (math.cos(angle), math.sin(angle))

    def add(p, q):
        return (p[0] + q[0], p[1] + q[1])

    base = -math.pi / 2 - math.pi / 6 - turn / 2
    a = (0.0, 0.0)
    b, c = at(base), at(base + math.pi / 3)
    e, f = at(base + turn), at(base + turn + math.pi / 3)
    pts = [a, b, c, add(b, c), e, f, add(e, f)]
    edges = [(i, j) for i, j in itertools.combinations(range(7), 2)
             if abs(math.dist(pts[i], pts[j]) - 1) < 1e-9]
    return pts, edges


def count_colourings(edges, n, k):
    return sum(all(col[i] != col[j] for i, j in edges)
               for col in itertools.product(range(k), repeat=n))


SIDE = 0.45  # hexagon side; any side between 1/sqrt(7) and 1/2 works


def hex_colour(x, y, colours=7):
    """Which hexagon is the point in, and what colour is that hexagon?"""
    q = (math.sqrt(3) / 3 * x - y / 3) / SIDE
    r = (2 / 3 * y) / SIDE
    s = -q - r
    rq, rr, rs = round(q), round(r), round(s)
    dq, dr, ds = abs(rq - q), abs(rr - r), abs(rs - s)
    if dq > dr and dq > ds:
        rq = -rr - rs
    elif dr > ds:
        rr = -rq - rs
    return (rq + 3 * rr) % colours if colours == 7 else (rq + 2 * rr) % colours


def clashes(colours, pairs, seed=1):
    rng = random.Random(seed)
    bad = 0
    for _ in range(pairs):
        x, y = rng.uniform(-50, 50), rng.uniform(-50, 50)
        t = rng.uniform(0, 2 * math.pi)
        bad += hex_colour(x, y, colours) == hex_colour(x + math.cos(t), y + math.sin(t), colours)
    return bad


if __name__ == "__main__":
    pts, edges = spindle()
    print("MOSER SPINDLE")
    print(f"  points {len(pts)}   unit distances {len(edges)}")
    c3 = count_colourings(edges, 7, 3)
    c4 = count_colourings(edges, 7, 4)
    print(f"  ways to colour it with 3 colours  {c3}")
    print(f"  ways to colour it with 4 colours  {c4}")

    best3 = min(itertools.product(range(3), repeat=7),
                key=lambda col: sum(col[i] == col[j] for i, j in edges))
    clash3 = [[i, j] for i, j in edges if best3[i] == best3[j]]
    ok4 = next(col for col in itertools.product(range(4), repeat=7)
               if all(col[i] != col[j] for i, j in edges))
    print(f"  best try with 3 colours {list(best3)} still has {len(clash3)} link with one colour at both ends")
    print(f"  one colouring with 4 colours {list(ok4)}")

    print("HEXAGON TILING")
    print(f"  hexagon side {SIDE}, widest point {2 * SIDE}")
    print(f"  nearest hexagon of the same colour is {math.sqrt(7) * SIDE:.3f} away")
    pairs = 1_000_000
    b7 = clashes(7, pairs)
    b4 = clashes(4, pairs)
    print(f"  7 colours: {pairs:,} random pairs at distance 1, same colour in {b7}")
    print(f"  4 colours, same tiling: same colour in {b4:,}")
    json.dump({"pts": [[round(x, 5), round(y, 5)] for x, y in pts], "edges": edges,
               "c3": c3, "c4": c4, "best3": list(best3), "clash3": clash3, "ok4": list(ok4), "side": SIDE, "gap": round(math.sqrt(7) * SIDE, 3),
               "pairs": pairs, "bad7": b7, "bad4": b4}, open("coloring.json", "w"))
