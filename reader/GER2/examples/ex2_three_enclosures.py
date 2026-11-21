"""Example 2 (research note §4.2-4.3): three correct enclosures of F(x) = x^2 - 2x + 2 on X = [0.9, 1.1].

The endpoints 0.9 and 1.1 are not binary floats, so this example uses exact rationals (fractions.Fraction):
every number printed is exact. The point is not which enclosure is narrowest, but which one the goal needs:
  goal A: F > 0      -> the first, cheapest enclosure already suffices;
  goal B: F > 0.99   -> only the third one decides it.
Run:  python ex2_three_enclosures.py"""
from fractions import Fraction as Q


def mul(a, b):
    p = [a[0]*b[0], a[0]*b[1], a[1]*b[0], a[1]*b[1]]; return (min(p), max(p))
def add(a, b): return (a[0] + b[0], a[1] + b[1])
def sq(a):
    lo = Q(0) if a[0] <= 0 <= a[1] else min(a[0]**2, a[1]**2); return (lo, max(a[0]**2, a[1]**2))
def const(c): return (Q(c), Q(c))


X = (Q(9, 10), Q(11, 10)); c = Q(1)

# 1. the expanded formula, interval by interval: X*X - 2X + 2 (X*X treated as two independent factors)
naive = add(add(mul(X, X), mul(const(-2), X)), const(2))
# 2. mean-value form around c = 1: F(c) + F'(X) (X - c),  F'(x) = 2x - 2
mv = add(const(c*c - 2*c + 2), mul(add(mul(const(2), X), const(-2)), add(X, const(-c))))
# 3. completing the square: (x - 1)^2 + 1, the square taken from endpoints (never negative)
cs = add(sq(add(X, const(-1))), const(1))

if __name__ == "__main__":
    for name, e in (("expanded", naive), ("mean-value form", mv), ("completed square", cs)):
        print(f"{name:17s} [{e[0]}, {e[1]}]  width {e[1] - e[0]}   F>0: {e[0] > 0}   F>0.99: {e[0] > Q(99, 100)}")
