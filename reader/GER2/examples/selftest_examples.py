"""Self-test of the GeoEnclosure examples. Run: python selftest_examples.py  (ends with FAILURES 0)"""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as Q
from iv import Iv
import ex1_gradient_difference as e1, ex2_three_enclosures as e2, ex3_root_by_bisection as e3

bad = 0
def ok(name, c):
    global bad; bad += not c; print(("OK  " if c else "BAD ") + name)

# iv: outward rounding contains exact results
x = Iv(0.1) + Iv(0.2); ok("iv: 0.1 + 0.2 enclosure contains the float sum's exact value", Q(x.lo) <= Q(0.1) + Q(0.2) <= Q(x.hi))
ok("iv: square of [-1, 2] is [0, 4+]", Iv(-1, 2).sq().lo == 0.0 and Iv(-1, 2).sq().hi >= 4)
# ex1
X = Iv(0, 1); ok("ex1: E_x and E_y both contain 0 on the square", e1.Ex(X, X).contains_zero() and e1.Ey(X, X).contains_zero())
ok("ex1: bisection decides every box (9 evaluated, 7 decided)", e1.by_bisection() == (9, 7))
ok("ex1: simplified difference is exactly 1", (e1.by_difference().lo, e1.by_difference().hi) == (1.0, 1.0))
# ex2 (exact rationals, the three rows of the note's table)
ok("ex2: expanded [61/100, 141/100]", e2.naive == (Q(61, 100), Q(141, 100)))
ok("ex2: mean-value [49/50, 51/50]", e2.mv == (Q(49, 50), Q(51, 50)))
ok("ex2: completed square [1, 101/100]", e2.cs == (Q(1), Q(101, 100)))
ok("ex2: goal F>0.99 decided only by the third", [e[0] > Q(99, 100) for e in (e2.naive, e2.mv, e2.cs)] == [False, False, True])
# ex3
ok("ex3: sign change f(2) < 0 < f(3)", e3.existence()[2])
ok("ex3: f' > 0 on [2, 3]", e3.uniqueness()[1])
lo, hi = e3.locate(); r = 2.0945514815423265   # real root of x^3 - 2x - 5 (Wallis), for reference only
ok("ex3: located interval contains the reference root and is narrow", lo <= r <= hi and hi - lo < 1e-11)
print("FAILURES", bad)
