"""Example 3: one root of f(x) = x^3 - 2x - 5 on [2, 3], with outward-rounded intervals (Standard v1.1 §2.1, §6).

A claim "exactly one root" needs three separate things (Standard v1.1 §6):
  existence  : f(2) < 0 < f(3), each proved by an enclosure of a point value, plus continuity;
  uniqueness : f'(x) = 3x^2 - 2 > 0 on the whole interval [2, 3], proved by one enclosure;
  location   : bisect, keep only the halves whose enclosure contains 0, and report an interval.
Note: a box whose enclosure contains 0 is NOT a proof that a root is there. Here the root is proved by the
sign change and the derivative; the boxes only localise it.
Run:  python ex3_root_by_bisection.py"""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iv import Iv


def f(X): return X*X*X - 2*X - 5
def df(X): return 3*X.sq() - 2


def existence():
    a, b = f(Iv(2)), f(Iv(3)); return a, b, a.negative() and b.positive()


def uniqueness():
    d = df(Iv(2, 3)); return d, d.positive()


def locate(steps=40):
    lo, hi = 2.0, 3.0
    for _ in range(steps):
        m = (lo + hi)/2
        if m == lo or m == hi: break                 # no float strictly between: stop
        fm = f(Iv(m))
        if fm.contains_zero(): break                 # cannot tell which half; keep [lo, hi]
        if fm.negative(): lo = m                     # f(lo) < 0 is kept as an invariant
        else: hi = m
    return lo, hi


if __name__ == "__main__":
    a, b, ok = existence(); print("f(2) in", a, " f(3) in", b, " sign change proved:", ok)
    d, ok2 = uniqueness(); print("f'([2,3]) in", d, " f' > 0 proved, so at most one root:", ok2)
    lo, hi = locate(); print(f"the unique root lies in [{lo!r}, {hi!r}]  (width {hi - lo:.3g})")
