# OpenAI's math release, counted and checked

Five short Python programs (415 lines) that produce every number in the video about
[github.com/openai/math](https://github.com/openai/math), the folder of 722 mathematics papers OpenAI
published in September and October 2026 and says were written by one of its models.

The programs do not prove or disprove any of the papers. They count what is in the folder and run small
experiments that show what three of the claims are about.

## Run it

```bash
git clone --filter=blob:none --sparse https://github.com/openai/math
git -C math sparse-checkout set --no-cone '/*.md' /overview.tex /lean/docs/ /lean/ComparatorChallenges/ /lean/formalization.yaml
pip install mpmath
bash run_all.sh math
```

The sparse clone fetches the catalogue and the Lean statement files without the 722 PDFs (32 MB on disk).
`demo-output.txt` is one saved run, counted on commit `adc7f12` of 2026-10-06; the repository gets
corrections, so a later clone can give different counts. Python 3.9+. Only `zeros.py` needs `mpmath`; the
rest use the standard library. The whole script takes about 6 seconds.

## The files

| file | what it does |
| --- | --- |
| `catalog.py` | reads `overview.tex`, `lean/docs/`, `lean/ComparatorChallenges/` and the git file list of a clone and counts them |
| `coloring.py` | colours the Moser spindle by brute force, then tests a 7-colour hexagon tiling of the plane |
| `pi_fractions.py` | best fractions for π and their scores; partial sums of the Flint Hills series |
| `primes.py` | counts primes with a sieve and compares with the logarithmic integral li(x) |
| `zeros.py` | finds the zeros of the zeta function below height 150 and measures the size of zeta on two lines |

## What the catalogue count shows

| | |
| --- | --- |
| results (families of papers) | 372 |
| papers | 722 |
| subjects | 17 |
| results with a Lean page | 235 of 372 (63.2%) |
| results with only a paper | 137 |
| Lean statements (Comparator challenges) | 405 |
| statement length | shortest 6 lines, median 57, longest 17,384 |
| statements of 20 lines or fewer | 28 |
| Lean files in `lean/OAI` | 121,733 |

A result with a Lean page has two parts: a short statement file a person can read, and a proof the Lean
checker accepted. A result without one is a paper waiting for referees. The repository README says some of
the unformalized results could have issues.

Coverage is uneven: Mathematical logic 6 of 6, Combinatorics 33 of 37, Algebraic and complex geometry 7 of 36,
Topology 3 of 18.

## The three claims the video walks through

**Zeta has no zeros to the right of 7/8** (statement: `QuasiRiemannHypothesis.lean`, 6 lines).
`zeros.py` finds the 52 zeros below height 150. Every one has real part 0.5. On the line Re s = 7/8 the
smallest value of |zeta| between heights 0 and 50 is 0.2699. That is an illustration, not evidence for the
theorem. `primes.py` shows what such a bound buys: the gap between the prime count and li(x) at ten million
is 339, against √x = 3,162 and x^(7/8) = 1,333,521.

**Five colours are not enough for the plane** (`EuclideanFiveColor.lean`, 9 lines).
The question: colour every point of the plane so that no two points exactly 1 apart share a colour. How many
colours are needed? `coloring.py` shows the two classical bounds. The Moser spindle (7 points, 11 unit
distances) has 0 valid colourings with 3 colours and 384 with 4, so 3 are not enough. A hexagon tiling with
side 0.45 and 7 colours passes 1,000,000 random unit-distance pairs with 0 clashes, so 7 are enough.

**The irrationality exponent of π is 2** (`PiExponent.lean`, 14 lines).
`pi_fractions.py` lists the best fractions for π with a score ν: the miss is 1/q^ν. 22/7 scores 3.43,
355/113 scores 3.20, the later ones stay near 2. It also sums the Flint Hills series 1/(n³ sin² n): the sum is
4.8074 up to n = 354 and 29.4056 one term later, because 355 is almost exactly 113π. Up to n = 1,000,000
the sum is 30.3145. The Lean page for this result checks the exponent; its Scope section says the
convergence of the series is outside the checked statement.

## Checking a Lean proof yourself

From the `lean/` folder of the OpenAI repository (commands from its README; not run for the video):

```bash
lake update
lake exe cache get
lake env comparator ComparatorChallenges/QuasiRiemannHypothesis.json
```

## Sources

- https://github.com/openai/math
- https://openai.com/index/sharing-ai-progress-in-mathematics/
