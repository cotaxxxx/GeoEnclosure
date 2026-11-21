# GeoEncloseReader 0.6.0

GeoEncloseReader is the audit tool of the GeoEnclosure method. It re-encloses interval-arithmetic covers with its own kernels, independent of the producer's, and checks the claimed signs.

This is research software. Every output is DIAGNOSTIC_ONLY until a human decides otherwise. The full documentation is in Japanese, in `GER2/README.md`.

## Start here (students)

`GER2/examples/` holds small examples that use only the Python standard library. They let you check, on your own computer, the numbers of the GeoEnclosure research note (§3–§4) and the rule for claims about roots (Standard v1.1 §6):

```bash
cd GER2/examples
python ex1_gradient_difference.py
python ex2_three_enclosures.py
python ex3_root_by_bisection.py
python selftest_examples.py
```

The last command ends with `FAILURES 0`.

## Layout

The package is `GER2/geoenclosereader/`:

| Module | Version | Content |
|---|---|---|
| `tri.py`, `tri2.py` | 0.3.0 | triaxial centre, pole and disk kernels |
| `tri3.py` | 0.4.0 | general-point kernels, first order in the parameters |
| `tri4.py`, `jet.py` | 0.5.0, 0.6.0 | general-point kernels, second order in the parameters (`lazy` option in 0.6.0) |
| `fiv.py`, `dual.py` | — | binary64 outward-rounded intervals and interval duals |
| `kernels.py`, `verify.py`, `ledger.py` | 0.1–0.2 | Arb kernels and the ledger reader for the rotational family |

Other files:
- `GER2/selftest_tri*.py`: self-tests of the kernels.
- `v57/`: the non-interval reference quadrature (Gauss–Legendre) that these self-tests compare against.

Version 0.6.0 adds `tri4.enclose(..., lazy=True)`: the first-order form is computed first, and the second-order form is added only when the first-order enclosure contains 0. The tree of boxes is the same as with 0.5.0, and the run is about 1.4 times faster (V61). `selftest_lazy.py` checks this. Version 0.5.1 added `examples/`.

## Requirements

- Python 3.11 or later, with numpy and mpmath, for the kernels.
- Python 3.9 or later, with nothing else, for `examples/`.
- `python-flint`, only for `kernels.py` and `verify.py`.

Tested with Python 3.11.18 and 3.13.18, numpy 2.4.6 and 2.5.3, and mpmath 1.4.1.

## Kernel self-tests

```bash
cd GER2
python -I selftest_tri.py
python -I selftest_tri2.py
python -I selftest_tri3.py
python -I selftest_tri4.py
python -I selftest_lazy.py
```

Each one ends with `FAILURES 0`.

## Known limits and corrections

See §7.3–§7.5 and §8 of `GER2/README.md`. They include correction E3: in 0.4.0, a box whose centre lies outside the ball was expanded at that centre. This is fixed in 0.5.0.
