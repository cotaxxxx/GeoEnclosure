"""A minimal outward-rounded interval type for the GeoEnclosure examples (pure Python, 3.9+).

Rule (GeoEnclosure Standard v1.1, §2.1 (b)): every +, -, * of IEEE binary64 is correctly rounded, so the exact
result lies within one ulp of the computed one. Moving each computed endpoint one ulp outward with math.nextafter
therefore gives an interval that is certain to contain the exact result. Inputs must be exactly representable
(small integers and dyadic fractions such as 0.5, 0.25 are; 0.1 is not -- use the Fraction examples for those)."""
import math

_dn = lambda x: math.nextafter(x, -math.inf)
_up = lambda x: math.nextafter(x, math.inf)


class Iv:
    __slots__ = ("lo", "hi")

    def __init__(self, lo, hi=None):
        self.lo = float(lo); self.hi = float(lo if hi is None else hi)
        assert self.lo <= self.hi, (lo, hi)

    @staticmethod
    def _c(b): return b if isinstance(b, Iv) else Iv(b)

    def __add__(a, b): b = Iv._c(b); return Iv(_dn(a.lo + b.lo), _up(a.hi + b.hi))
    __radd__ = __add__
    def __neg__(a): return Iv(-a.hi, -a.lo)
    def __sub__(a, b): b = Iv._c(b); return Iv(_dn(a.lo - b.hi), _up(a.hi - b.lo))
    def __rsub__(a, b): return Iv._c(b) - a

    def __mul__(a, b):
        b = Iv._c(b); p = (a.lo*b.lo, a.lo*b.hi, a.hi*b.lo, a.hi*b.hi)
        return Iv(_dn(min(p)), _up(max(p)))
    __rmul__ = __mul__

    def sq(a):
        """square from endpoints: never negative (Standard v1.1 §2.1, last item)"""
        lo = 0.0 if a.lo <= 0 <= a.hi else min(a.lo*a.lo, a.hi*a.hi)
        return Iv(_dn(lo) if lo > 0 else 0.0, _up(max(a.lo*a.lo, a.hi*a.hi)))

    def positive(a): return a.lo > 0
    def negative(a): return a.hi < 0
    def contains_zero(a): return a.lo <= 0 <= a.hi
    def __repr__(a): return f"[{a.lo!r}, {a.hi!r}]"
