"""Check the arithmetic and ledger machinery with artificial inputs."""

import argparse
from contextlib import ExitStack
from ctypes import CDLL, POINTER, byref, c_int
from fractions import Fraction as Q
from pathlib import Path
from tempfile import TemporaryDirectory

from rational_series import Grid
from run_case import Bounds, analytic_cells, line, save, solve
from verify_certificate import decode_dyad, read_json, read_jsonl, verify_math


HERE = Path(__file__).resolve().parent


def toy_interval(mode, lo, hi):
    if mode == "f":
        center = Q(71, 128)
        return lo - center, hi - center
    if mode == "df":
        return Q(1), Q(1)
    if mode == "omega":
        return lo**2, hi**2
    raise ValueError("unknown artificial quantity")


class ToyKernel:
    def evaluate(self, mode, bits, lo, hi):
        return [[str(x.numerator), 1 - x.denominator.bit_length()]
                for x in toy_interval(mode, lo, hi)]


class ToyCheck:
    enclose = staticmethod(toy_interval)


def check_ledger(path):
    cfg = read_json(HERE / "PLAN_INPUTS.json")
    cfg.update(small_e_bounds=["-1", "-1/4"], small_q_bounds=["1/4", "1"])
    ledger = path / "SIGN_LEDGER.jsonl"
    steps = path / "STEPS.jsonl"
    records = analytic_cells(cfg)
    state = {"grade": "DIAGNOSTIC_ONLY", "status": "PARTIAL"}
    with ExitStack() as stack:
        evaluations, trace, signed = [
            stack.enter_context(file.open("x", encoding="utf-8"))
            for file in (path / "EVALUATIONS.jsonl", steps, ledger)
        ]
        solve(ToyKernel(), cfg, evaluations, trace, state, records)
        for row in sorted(records, key=lambda r: Q(r["box"][0])):
            line(signed, row)
    save(path / "RESULT.json", state)
    verified = verify_math(path, cfg, ToyCheck())
    lo, hi = map(Q, verified["e_interval_exact"])
    assert lo < Q(71, 128) < hi
    assert hi - lo <= Q(cfg["target_width"])
    first_step = next(read_jsonl(steps))
    assert [len(group) for group in first_step["probes"]] == [3, 1, 1]
    signed_rows = list(read_jsonl(ledger))
    signed_rows[1]["box"][0] = "1/7"
    with ledger.open("w", encoding="utf-8") as target:
        for row in signed_rows:
            line(target, row)
    try:
        verify_math(path, cfg, ToyCheck())
    except ValueError as exc:
        assert str(exc) == "signed ledger differs from the reconstructed cover"
    else:
        raise AssertionError("the verifier accepted a changed ledger")
    print(f"Artificial ledger: {verified['steps']} steps and "
          f"{verified['cover_boxes']} boxes, quarter-point replay and tamper detection verified.")


def check_integers():
    grid = Grid(192)
    left = grid.interval(Q(-2, 3), Q(3, 5))
    right = grid.interval(Q(3, 2), Q(8, 5))
    lo, hi = grid.exact_bounds(grid.mul(left, right))
    assert lo <= Q(-16, 15) and hi >= Q(24, 25)
    lo, hi = grid.exact_bounds(grid.sqrt(grid.number(2)))
    assert 0 < lo and lo**2 <= 2 <= hi**2
    lo, hi = grid.exact_bounds(grid.div(left, right))
    assert lo <= Q(-4, 9) and hi >= Q(2, 5)
    print("Artificial integer-grid fixture: product, quotient and square-root inclusion verified.")


def check_mpfr(library):
    lib = CDLL(str(library.resolve()))
    fixture = lib.mjb_arithmetic_fixture
    fixture.argtypes = [POINTER(Bounds)]
    fixture.restype = c_int
    endpoints = Bounds()
    assert fixture(byref(endpoints)) == 0
    lo = decode_dyad([endpoints.lo.decode("ascii"), endpoints.lo_exp])
    hi = decode_dyad([endpoints.hi.decode("ascii"), endpoints.hi_exp])
    assert -Q(1, 2) < lo < hi < 0
    assert 9 * (lo + Q(1, 2))**2 <= 2 <= 9 * (hi + Q(1, 2))**2
    print("Artificial MPFR fixture: sqrt(2)/3 - 1/2 is enclosed by directed rounding.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path)
    args = parser.parse_args()
    with TemporaryDirectory() as temporary:
        check_ledger(Path(temporary))
    check_integers()
    if args.library:
        check_mpfr(args.library)


if __name__ == "__main__":
    main()
