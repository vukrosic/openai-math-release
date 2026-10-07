"""How well do fractions hit pi?

For a fraction p/q the miss is |pi - p/q|. Write the miss as 1 / q^nu.
A big nu means the fraction is far better than its size deserves.
The irrationality exponent of pi is the largest nu that keeps happening forever.
"""
import json
import math
from decimal import Decimal, getcontext
from fractions import Fraction

getcontext().prec = 60
PI = Decimal("3.14159265358979323846264338327950288419716939937510582097494")


def convergents(count):
    """The best fractions for pi, from its continued fraction."""
    out, x = [], PI
    h0, h1, k0, k1 = 0, 1, 1, 0
    for _ in range(count):
        a = int(x)
        h0, h1 = h1, a * h1 + h0
        k0, k1 = k1, a * k1 + k0
        out.append(Fraction(h1, k1))
        x = 1 / (x - a)
    return out


def flint_hills(limit):
    """Partial sums of 1 / (n^3 sin^2 n). A term is huge when n is almost a multiple of pi."""
    total, marks, big, curve = 0.0, {}, [], []
    for n in range(1, limit + 1):
        term = 1 / (n ** 3 * math.sin(n) ** 2)
        total += term
        big.append((term, n))
        if n <= 500:
            curve.append(round(total, 4))
        if n in (354, 355, 1000, 100000, limit):
            marks[n] = total
    big.sort(reverse=True)
    return marks, big[:4], curve


if __name__ == "__main__":
    print("FRACTIONS FOR PI")
    print(f"  {'fraction':>16s}  {'miss':>10s}  {'1/q^2':>10s}   nu")
    rows = []
    for f in convergents(9)[1:]:
        miss = abs(PI - Decimal(f.numerator) / Decimal(f.denominator))
        nu = float(-miss.ln() / Decimal(f.denominator).ln())
        rows.append([f.numerator, f.denominator, float(miss), nu])
        print(f"  {f.numerator:>9d}/{f.denominator:<6d}  {float(miss):10.2e}  {1 / f.denominator ** 2:10.2e}   {nu:.2f}")

    print("FLINT HILLS SERIES   sum of 1 / (n^3 sin^2 n)")
    marks, big, curve = flint_hills(1_000_000)
    print(f"  term n = 103993 adds {1 / (103993 ** 3 * math.sin(103993) ** 2):.7f}")
    for n, s in marks.items():
        print(f"  sum up to n = {n:<7d} {s:.4f}")
    for term, n in big:
        print(f"  term n = {n:<6d} adds {term:.4f}   sin(n) = {math.sin(n):+.6f}")
    json.dump({"rows": rows, "marks": {str(k): round(v, 4) for k, v in marks.items()},
               "big": [[n, round(t, 4), round(math.sin(n), 6)] for t, n in big], "curve": curve},
              open("pi_fractions.json", "w"))
