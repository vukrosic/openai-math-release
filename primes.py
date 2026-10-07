"""Counting primes: the real count next to the smooth estimate li(x).

The zeros of the zeta function decide how far apart these two can drift.
No zeros to the right of 1/2 (the Riemann hypothesis) would mean a gap of about sqrt(x).
No zeros to the right of 7/8 would mean a gap of at most about x^(7/8).
"""
import json
import math


def prime_counts(limit, marks):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(limit ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(range(i * i, limit + 1, i)))
    out, count, want = {}, 0, set(marks)
    for n in range(limit + 1):
        count += sieve[n]
        if n in want:
            out[n] = count
    return out


def li(x):
    """The logarithmic integral, by its series."""
    L = math.log(x)
    total, term = 0.5772156649015329 + math.log(L), 1.0
    for k in range(1, 200):
        term *= L / k
        total += term / k
    return total


if __name__ == "__main__":
    marks = [10 ** k for k in range(3, 8)]
    counts = prime_counts(marks[-1], marks)
    print(f"  {'x':>10s} {'primes':>9s} {'li(x)':>11s} {'gap':>7s} {'sqrt(x)':>8s} {'x^(7/8)':>10s}")
    rows = []
    for x in marks:
        est = li(x)
        rows.append([x, counts[x], round(est, 1), round(est - counts[x], 1),
                     round(x ** 0.5), round(x ** 0.875)])
        print(f"  {x:>10,d} {counts[x]:>9,d} {est:>11,.1f} {est - counts[x]:>7.1f} {x ** 0.5:>8.0f} {x ** 0.875:>10.0f}")
    small = prime_counts(200, range(201))
    stairs = [[x, small[x], round(li(x), 2)] for x in range(2, 201)]
    print(f"  up to 100: {small[100]} primes, li(100) = {li(100):.1f}")
    json.dump({"rows": rows, "stairs": stairs}, open("primes.json", "w"))
