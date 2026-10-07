"""Where is zeta zero? The first zeros of the Riemann zeta function, with mpmath.

Every zero found so far has real part exactly 1/2 (the centre line of the strip 0 < Re s < 1).
This prints the heights of the zeros below 150 and samples |zeta| along the centre line,
so you can see the curve touch zero at those heights.

Needs:  pip install mpmath
"""
import json

import mpmath

mpmath.mp.dps = 20

if __name__ == "__main__":
    zeros = []
    n = 1
    while True:
        z = mpmath.zetazero(n)
        if z.imag > 150:
            break
        zeros.append([float(z.real), round(float(z.imag), 4)])
        n += 1
    print("ZEROS OF ZETA BELOW HEIGHT 150")
    print(f"  found {len(zeros)}")
    print("  heights " + ", ".join(f"{h:.4f}" for _, h in zeros[:8]) + ", ...")
    print(f"  real part of every one: {sorted(set(re for re, _ in zeros))}")

    line = [[t / 4, round(float(abs(mpmath.zeta(mpmath.mpc(0.5, t / 4)))), 4)] for t in range(0, 201)]
    print(f"  |zeta| on the centre line, height 0 to 50: largest {max(v for _, v in line):.3f}, "
          f"smallest {min(v for _, v in line):.4f}")
    edge = [[t / 4, round(float(abs(mpmath.zeta(mpmath.mpc(0.875, t / 4)))), 4)] for t in range(0, 201)]
    print(f"  |zeta| on the line Re s = 7/8, height 0 to 50: smallest {min(v for _, v in edge):.4f}")
    json.dump({"heights": [h for _, h in zeros], "line": line, "edge": edge}, open("zeros.json", "w"))
