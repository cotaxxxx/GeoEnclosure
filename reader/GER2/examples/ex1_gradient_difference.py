"""Example 1 (research note §3): is there a stationary point of E(x, y) = (x + y)^2 / 2 - x on [0, 1]^2?

E_x = x + y - 1,  E_y = x + y.
(a) The usual way: split the square into boxes and, on each box, try to show that E_x or E_y is nonzero.
(b) The GeoEnclosure way: first ask what to measure. E_y - E_x = 1 vanishes at every stationary point,
    and it equals 1 everywhere, so there is none -- with zero boxes.
Run:  python ex1_gradient_difference.py"""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iv import Iv


def Ex(x, y): return x + y - 1
def Ey(x, y): return x + y


def by_bisection(max_depth=20):
    """Depth-first bisection. A box is decided when E_x or E_y has a sign on it. Returns (evaluated, decided)."""
    stack = [((0.0, 1.0), (0.0, 1.0), 0)]; evaluated = decided = 0
    while stack:
        (x0, x1), (y0, y1), d = stack.pop()
        X, Y = Iv(x0, x1), Iv(y0, y1); evaluated += 1
        ex, ey = Ex(X, Y), Ey(X, Y)
        if not ex.contains_zero() or not ey.contains_zero():
            decided += 1; continue
        if d >= max_depth: raise RuntimeError("undecided box at max depth")
        xm, ym = (x0 + x1)/2, (y0 + y1)/2            # dyadic midpoints: exact
        for bx in ((x0, xm), (xm, x1)):
            for by in ((y0, ym), (ym, y1)):
                stack.append((bx, by, d + 1))
    return evaluated, decided


def by_difference():
    """E_y - E_x simplified first (x + y cancels exactly), then enclosed: the constant 1."""
    diff = Iv(1)                                     # (x + y) - (x + y - 1) = 1, an algebraic identity
    return diff


if __name__ == "__main__":
    X = Iv(0, 1); Y = Iv(0, 1)
    print("on the whole square: E_x in", Ex(X, Y), " E_y in", Ey(X, Y), " -> both contain 0, undecided")
    ev, dec = by_bisection()
    print(f"(a) bisection: {ev} boxes evaluated, {dec} terminal boxes decided -> no stationary point")
    d = by_difference()
    print("(b) E_y - E_x =", d, "on the whole square -> no stationary point, 0 boxes split")
    naive = Ey(X, Y) - Ex(X, Y)
    print("    (enclosing E_y - E_x without simplifying first gives", naive, "-- the dependency problem of §4.1)")
