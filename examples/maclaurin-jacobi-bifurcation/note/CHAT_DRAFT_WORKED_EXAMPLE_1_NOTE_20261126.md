# GeoEnclosure Worked Example 1: Certified Maclaurin–Jacobi Bifurcation

Nov 26, 2026 · @DAYBREAK

## Abstract

We give a reproducible, interval-certified account of the classical point where the Jacobi triaxial ellipsoids branch off the Maclaurin spheroids. On the Maclaurin sequence the branching condition is a single function F(e) of the eccentricity. We prove analytically that F is strictly increasing on (0,1), with F′(e) ≥ 44e/105, and close both ends e → 0 and e → 1 by expansions with explicit remainders. Rigorous MPFR interval arithmetic then confines the unique root to a box of width at most 2⁻⁵², and also encloses the dimensionless rotation rate Ω²/(πGρ) there. A second code re-encloses every sign using integer-ratio series. The certified values are e\* ∈ \[0.8126700106117429, 0.8126700106117432\] and Ω²/(πGρ) ∈ \[0.3742296747861903, 0.3742296747862011\], consistent with the classical 0.81267 and 0.3742. The value itself is known. The contribution is a complete GeoEnclosure worked example: method, result and reproduction code, each fixed and auditable.

Author: Katsushi Furuta (DAYBREAK), ORCID 0009-0005-3129-8043. Companion to Paper I, doi:10.5281/zenodo.24495446, and the GeoEnclosure note, doi:10.5281/zenodo.24421364.

## 1 Introduction

A uniformly rotating, self-gravitating, homogeneous fluid mass at slow rotation takes the shape of an oblate Maclaurin spheroid with semi-axes a = a ≥ c. As rotation increases, a sequence of triaxial Jacobi ellipsoids branches off at a single eccentricity. This was found by Meyer (1842) and Liouville (1846) and systematised by Chandrasekhar (1969). The classical values are e\* ≈ 0.81267 and Ω²/(πGρ) ≈ 0.3742.

We do not claim a new value. GeoEnclosure (Furuta 2026) is a methodology with three steps. Measure decides which quantity to look at. Enclose bounds it with guaranteed intervals. Read takes decisions from interval signs. This note applies the three steps to a problem whose answer can be checked against the literature. Every example is published as three parts: verification method, verification result and reproduction code. The method was fixed before any physical evaluation.

We write the eccentricity as e = √(1 − c²/a²) and set q = √(1 − e²) and s = e². With a₁ = a₂ = a and a₃ = c, the Jacobi equilibrium condition (Chandrasekhar 1969) reads f(e) = 0 with

```latex
f(e)=\int_0^\infty\left[\frac{a^4}{(a^2+u)^2}-\frac{c^2}{c^2+u}\right]\frac{du}{(a^2+u)\sqrt{c^2+u}} .
```

Since a > 0, the scale-free quantity F = a f has the same sign and the same zeros, and all statements below are about F.

## 2 Measure: closed form, monotonicity and the two ends

Uniqueness of the root is settled analytically in this section. Numerics are used only to locate it.

**Closed form.** Substitute v = u/a² and then t = √(q² + v), and reduce with the recursion for ∫(t²+s)⁻ⁿ dt. With α = arcsin e this gives

```latex
F(e)=\frac{\bigl(3+8e^2(1-e^2)\bigr)\arcsin e-e\sqrt{1-e^2}\,(3+10e^2)}{4e^5}.
```

The rotation rate on the Maclaurin sequence is

```latex
\omega=\frac{\Omega^2}{\pi G\rho}=\frac{2\sqrt{1-e^2}\,(3-2e^2)\arcsin e}{e^3}-\frac{6(1-e^2)}{e^2}.
```

**Monotonicity.** Write Ψ(s) = F(√s). Differentiating under the integral gives

```latex
\Psi'(s)=\int_0^\infty\frac{v\,[\,3+4v+2v^2-(1-s)(2+v)\,]}{2(1+v)^3(1-s+v)^{5/2}}\,dv .
```

The bracket is at least (1+v)(1+2v). The factor 1 − s + v is at most 1 + v. Therefore

```latex
\Psi'(s)\ \ge\ \tfrac12\int_0^\infty\frac{v(1+2v)}{(1+v)^{9/2}}\,dv=\tfrac12\Bigl(\tfrac{4}{35}+\tfrac{32}{105}\Bigr)=\frac{22}{105},\qquad F'(e)\ge\frac{44e}{105}>0 .
```

So F is strictly increasing on (0,1), and it has at most one zero there.

**The end e → 0.** A binomial expansion with cₙ = C(2n,n)/4ⁿ gives F = −4/15 + Σ bₙ sⁿ, where

```latex
b_n=c_n\Bigl[\frac{2}{2n+5}+\frac{4}{2n+3}-\frac{2}{2n+1}\Bigr]>0,\qquad b_1=\frac{22}{105}.
```

Each bₙ lies between 0 and 1, so F = −4/15 + (22/105)e² + R₀ with 0 ≤ R₀ ≤ e⁴/(1 − e²). For 0 < e ≤ 1/8 this gives −4/15 < F < −1/4.

**The end e → 1.** Write F in terms of q. Then F = 3π/8 − 4q + R₁ with −11q³ ≤ R₁ ≤ (5π/2)q² for 0 ≤ q ≤ 1/4. For 63/64 ≤ e < 1 we have q < 3/16, which gives 1/4 < F < 3π/8 < 3/2.

Combined with monotonicity, the two ends give a negative value at e = 1/8 and a positive value at e = 63/64. Hence F has **exactly one** zero in (0,1), and it lies in (1/8, 63/64). Similar remainder bounds hold for ω at both ends: |ω − 8e²/15| ≤ 15e⁴ for e ≤ 1/8, and ω = πq − 8q² + R\_ω with −18q⁴ ≤ R\_ω ≤ 5πq³. Full derivations are in DERIVATION.md of the reproduction package.

## 3 Enclose and Read: interval bisection and the sign ledger

The interval (0,1) is covered by three kinds of boxes. Analytic boxes sit at the two ends. MPFR boxes fill the middle. One root box remains.

| Part of (0,1) | Method | Sign of F |
| --- | --- | --- |
| (0, 1/8\] | Expansion with remainder (§2) | negative, F ∈ \[−4/15, −1/4\] |
| \[1/8, root box\] | MPFR endpoint values plus monotonicity | negative |
| Root box, width ≤ 2⁻⁵² | MPFR: F(left) < 0 < F(right) | contains the unique zero |
| \[root box, 63/64\] | MPFR endpoint values plus monotonicity | positive |
| \[63/64, 1) | Expansion with remainder (§2) | positive, F ∈ \[1/4, 3/2\] |

**Enclose.** The kernel evaluates the closed forms of F, F′ and ω in MPFR. Every operation rounds outward: down for lower endpoints and up for upper ones. Products and quotients are taken over all four corners. All inputs are exact rationals. Working precision follows the fixed ladder 128, 256, 512 bits, and stops at the first precision that separates the sign from zero.

**Read.** Bisection starts from the bracket \[1/8, 63/64\]. At each step F is evaluated at the midpoint. If that enclosure still contains zero, both quarter points are evaluated as well. The bracket keeps the largest negative point and the smallest positive point. Because F is increasing, the interval \[F(l), F(r)\] encloses F over a whole box \[l, r\]. Every box dropped from the bracket therefore enters the ledger with a guaranteed sign. Bisection stops when the bracket width reaches 2⁻⁵² (about 52 steps). It is declared unresolved if no endpoint moves, if an enclosure is not finite, if the endpoints reverse, or if 160 steps pass. No reference value enters the starting bracket, the splitting or the sign decisions.

On the final root box the kernel also checks directly that the lower bound of F′ is strictly positive, and encloses ω over the whole box. The ledger must tile (0,1) exactly. Neighbouring boxes may meet only at shared endpoints, and 0 and 1 are open ends.

## 4 Independent re-check

A second program re-encloses every recorded sign without using the MPFR kernel, the closed form or floating point. It is independent in formula, arithmetic and language. It was written by the same producer, however; the auditor's run repeats it and is not a reimplementation.

|  | Primary computation | Independent check |
| --- | --- | --- |
| Formula | Closed form with arcsin | Series Σ bₙ sⁿ (2048 terms) with a geometric tail bound |
| Arithmetic | MPFR, directed rounding | Integers on a fixed 192-bit binary grid, with floor and ceiling |
| Square root | mpfr\_sqrt | Integer square root, rounded outward |
| Language | C | Python standard library only |

The tails are bounded explicitly. For Ψ and for U(s) = arcsin(e)/e they lie in \[0, sᴺ⁺¹/(1 − s)\]. For Ψ′ they lie in \[0, sᴺ((N+1)/(1 − s) + s/(1 − s)²)\]. Here N = 2048.

The checker rebuilds the whole bisection from the evaluation tape. It requires the rebuilt ledger to equal the recorded ledger exactly. It also requires every strict sign to be reproduced by the series. At every evaluated point, and on the root box for F′ and ω, the MPFR interval and the series interval must overlap. The published ω interval is the hull of the two guaranteed intervals, rounded outward to 16 decimal places. The displayed e interval is rounded outward on the same grid, and its width stays below 2⁻⁵² + 2·10⁻¹⁶ < 10⁻¹⁵.

Before the run, an auditor (chat) checked every analytic claim in §2 numerically at 40 digits, and re-derived by hand the coefficients bₙ and the bound Ψ′ ≥ 22/105. Both the closed form and F′ matched the integrals to within 10⁻³⁸. The observed remainder constants sit well inside the stated bounds; for example, R₁/q² ≤ 6.09 against the bound 5π/2 ≈ 7.85.

## 5 Results

Theorem. On the Maclaurin sequence, the Jacobi branching condition F(e) = 0 has exactly one solution e\* in (0,1). It satisfies

```latex
\frac{117118091422919119}{2^{57}}\ <\ e_*\ <\ \frac{234236182845838293}{2^{58}},
```

an interval of width 55·2⁻⁵⁸ ≈ 1.9·10⁻¹⁶. In decimals, e\* ∈ \[0.8126700106117429, 0.8126700106117432\]. At e\* the rotation rate satisfies Ω²/(πGρ) ∈ \[0.3742296747861903, 0.3742296747862011\].

Uniqueness is proved analytically (§2). Both enclosures are computer-assisted (§3–§4). The theorem rests on three facts only: the monotonicity bound F′ ≥ 44e/105, and the two strict signs F(left) < 0 < F(right) at the ends of the root box. The analytic end boxes and the 55-box ledger are not needed for the theorem. They are there to show the GeoEnclosure pattern of covering all of (0,1). The numerical part assumes that MPFR 4.2.2 rounds correctly (mpfr\_asin, mpfr\_sqrt and the four operations); the signs are also re-enclosed independently with integer series. The run records keep the grade DIAGNOSTIC\_ONLY. The result was adopted by Judge ruling d1700a4218baae75a62be8d4707378bac4eea60f, after chat audit 4e0a884.

| Quantity | Certified interval | Classical value (Chandrasekhar 1969) |
| --- | --- | --- |
| e\* | \[0.8126700106117429, 0.8126700106117432\] | 0.81267 |
| Ω²/(πGρ) at e\* | \[0.3742296747861903, 0.3742296747862011\] | 0.3742 |
| F′ on the root box | \[1.3120452…, 1.3120452…\] > 0 (MPFR and series agree) | — |

| Run record | Value |
| --- | --- |
| Run | 2026-11-26 18:15:39–18:15:40 JST, one execution |
| Bisection steps | 52 |
| MPFR evaluations | 56, all at 128 bits |
| Boxes in the sign ledger | 55 (2 analytic, 53 MPFR), tiling (0,1) exactly |
| Root-box width | 55·2⁻⁵⁸ ≈ 1.9·10⁻¹⁶ (target ≤ 2⁻⁵²) |
| Independent check | CHECKS\_RECORDED; re-run by the auditor with identical output |
| Machine | AMD Ryzen 9 9900X, Ubuntu (Linux 7.0), GCC 15.2.0, MPFR 4.2.2, GMP 6.3.0 |

The ω interval is about 1.1·10⁻¹⁴ wide, wider than the true variation of ω over the root box (about 1.7·10⁻¹⁶). The extra width comes from dependency in plain interval evaluation. The bound is still guaranteed, so ω is certified to about 13 digits. As an outside cross-check, a 40-digit mpmath computation in the audit gives e\* ≈ 0.81267001061174294948 and Ω²/(πGρ) ≈ 0.37422967478619563435. Both lie inside the certified intervals. These values play no part in the certificate.

## 6 Discussion

**What is new.** The bifurcation value has been known since the nineteenth century, and this note does not claim to discover it. It contributes one package that holds four things together: an analytic derivation of the branching condition, an analytic proof that the root is unique, rigorous enclosures of the root and of the rotation rate, and a ledger that a third party can re-verify. A preliminary search, using the terms interval arithmetic, validated numerics, computer-assisted proof and rigorous numerics combined with Maclaurin–Jacobi bifurcation, found no earlier interval certification of this point. The classical treatments (Chandrasekhar 1969; Bertin and Radicati 1976) are analytic. That search was not exhaustive, so no priority claim is made. Whether the classical literature already contains an equivalent analytic proof of uniqueness remains to be checked; if it does, §2 serves as an independent confirmation.

**Why it is a GeoEnclosure example.** Most of the work is in Measure. Removing the scale, finding the closed form and proving monotonicity turn a global root search into about fifty point evaluations. Analytic closure of the two ends keeps the computation away from the places where floating-point evaluation of F is ill-conditioned. The same pattern is planned for the triaxial family (Paper II, in preparation). There, numerical evidence suggests that stationary points are born or absorbed only at the centre or at the axis ends; this is not yet proved.

**Process and AI disclosure.** This work followed the REDDS process. The Judge (the author) made every decision. ChatGPT (Dig) operated the research PC. ChatGPT Work (Astra, Codex) prepared the plan, the derivation and the code. Claude (chat) audited the derivation and the bundle before the run and the results after it. Claude Code reviewed the draft independently; it checked the derivation, the constants and the registration records but did not read or run the code. The author read the whole text and approved it, together with this disclosure. All mathematical claims rest on the derivation and the recorded ledgers, not on any model's statement.

**Data and code availability.** The example lives on the branch codex/macl-jacobi-interval-20261126 of cotaxxxx/GeoEnclosure, in examples/maclaurin-jacobi-bifurcation/.

- Method and reproduction code, fixed before the run: [commit 4e52466bfd7be83c9af44f0add7907dee4cc36de](https://github.com/cotaxxxx/GeoEnclosure/tree/4e52466bfd7be83c9af44f0add7907dee4cc36de/examples/maclaurin-jacobi-bifurcation). Bundle SHA-256: da6a37be638a73892e79e7bbac743f319fe9896d0e1c73e6b3d3416414b47038.
- Result ledgers: [commit 53319d86cefbd6e9ef7c635db47790750f5777c2](https://github.com/cotaxxxx/GeoEnclosure/tree/53319d86cefbd6e9ef7c635db47790750f5777c2/examples/maclaurin-jacobi-bifurcation/results/2026-11-26-research-pc).
- Audit records and Judge decisions are in [cotaxxxx/experimental-mathematics-ai-collaboration](https://github.com/cotaxxxx/experimental-mathematics-ai-collaboration/tree/d1700a4218baae75a62be8d4707378bac4eea60f/docs): bundle audit 9dc279d, execution approval 6c34e7d, result audit 4e0a884 and adoption ruling d1700a4.

Code is under the MIT licence and text under CC BY 4.0.

## References

- C. G. J. Jacobi, “Ueber die Figur des Gleichgewichts,” Annalen der Physik 109 (1834) 229–233.
- C. O. Meyer, “De aequilibrii formis ellipsoidicis,” J. reine angew. Math. 24 (1842) 44–59. [EuDML](https://eudml.org/doc/183244)
- J. Liouville (1846), cited after the historical account in Chandrasekhar (1969), Chapter 1.
- S. Chandrasekhar, Ellipsoidal Figures of Equilibrium, Yale University Press, New Haven, 1969.
- G. Bertin, L. A. Radicati, “The bifurcation from the Maclaurin to the Jacobi sequence as a second-order phase transition,” ApJ 206 (1976) 815.
- K. Furuta, GeoEnclosure: A Methodology of Interval Enclosure and Sign Determination Based on Problem Structure, v1.0, Zenodo, 2026. doi:10.5281/zenodo.24421364
- K. Furuta, Paper I, Zenodo, 2026. doi:10.5281/zenodo.24495446
- R. Fitzpatrick, lecture notes on Jacobi ellipsoids. [farside.ph.utexas.edu](https://farside.ph.utexas.edu/teaching/336L/Fluid/node36.html)
- The MPFR library, version 4.2.2. https://www.mpfr.org
