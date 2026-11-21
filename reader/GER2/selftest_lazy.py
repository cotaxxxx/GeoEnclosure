"""selftest for the lazy option of tri4 (GeoEncloseReader 0.6.0).
For each test box: lazy=True and lazy=False must give the same sign decision; when lazy=True computes the second-order
form (no skip), the enclosure and the split data (terms, angular width) must be bit-identical to lazy=False; when it
skips, the lazy enclosure must contain the non-lazy one (it is the first-order form, a superset of the intersection).
Run from this folder: python3 -I selftest_lazy.py  (ends with FAILURES 0)"""
import sys; sys.path.insert(0, '.')
from fractions import Fraction as Fr
from geoenclosereader import tri4
bad = 0
def ok(name, cond, msg=""):
    global bad; bad += not cond; print(("OK  " if cond else "BAD ") + name + " " + msg, flush=True)

def box_of(c, r): return [(x - r, x + r) for x in c]
cases = [  # (centre, half-width, kind, N, grade)  -- decided and undecided boxes, with and without contact
    ((Fr(6, 5), Fr(3, 2), Fr(1, 4), Fr(1, 4), Fr(1, 2)), Fr(1, 128), "H33", 64, 0),
    ((Fr(6, 5), Fr(3, 2), Fr(1, 4), Fr(1, 4), Fr(1, 2)), Fr(1, 16), "E3", 64, 0),
    ((Fr(117, 40), Fr(91, 16), Fr(1, 64), Fr(47, 64), Fr(1, 64)), Fr(1, 512), "H33", 256, 4),
    ((Fr(117, 40), Fr(91, 16), Fr(1, 64), Fr(47, 64), Fr(1, 64)), Fr(1, 64), "H33", 256, 4),
    ((Fr(3, 2), Fr(2), Fr(1, 2), Fr(1, 2), Fr(1, 64)), Fr(1, 128), "T12", 64, 0),
    ((Fr(6, 5), Fr(3, 2), Fr(19, 32), Fr(19, 32), Fr(9, 16)), Fr(1, 64), "E3", 64, 0),
]
seen_skip = seen_full = False
for c, r, kind, N, g in cases:
    b = box_of(c, r)
    e0 = tri4.enclose(kind, b, N, g, None, False); L0 = dict(tri4.enclose.last)
    e1 = tri4.enclose(kind, b, N, g, None, True); L1 = dict(tri4.enclose.last)
    dec = lambda e: (e.lo > 0, e.hi < 0)
    same_dec = dec(e0) == dec(e1)
    if L1["lazy_skip"]:
        seen_skip = True
        cond = same_dec and e1.lo <= e0.lo and e0.hi <= e1.hi
    else:
        seen_full = L1["order"] == 2 or seen_full
        cond = same_dec and (e0.lo, e0.hi) == (e1.lo, e1.hi) and L0["terms"] == L1["terms"] and L0["angular_width"] == L1["angular_width"]
    ok(f"{kind} N={N} r={r}", bool(cond), f"skip={L1['lazy_skip']} order={L1['order']} [{float(e0.lo):.6g},{float(e0.hi):.6g}] vs [{float(e1.lo):.6g},{float(e1.hi):.6g}]")
ok("both branches exercised (a skip and a full second-order evaluation)", seen_skip and seen_full)
print("FAILURES", bad)
