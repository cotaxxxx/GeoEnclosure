# GeoEnclosure

## A Methodology of Interval Enclosure and Sign Determination Based on Problem Structure

### — Decide what to measure. Enclose values. Read signs. —

**Katsushi Furuta (DAYBREAK)**
Independent researcher

Research note v1.0, English translation (21 November 2026)

*This is a translation. The Japanese text `GeoEnclosure_Note_v1_0_JA.md` is authoritative. Where the two differ, follow the Japanese. The claim IDs (G01–G18), the formulas, the numbers and the references are the same in both. The translation was made by Claude (Anthropic, dialogue on claude.ai) from the Japanese v1.0 (sha256 `db152ea3…`), with terms aligned to the English translation of the GeoEnclosure Standard v1.1.*

---

# Abstract

In computer-assisted proofs, once a candidate solution or a proof strategy has been found, guaranteeing that it is correct can require checking a large parameter region and a great deal of computation. Now that AI makes candidates and strategies easier to obtain, this verification cost tends to limit the pace of research as a whole.

This note organises one research methodology for the problem of verification cost, called **GeoEnclosure**. Its basic idea is to work backwards from the desired conclusion and, according to the structure of the problem, to choose again which quantity to verify and in which representation. Its basic operations are summarised in three steps: "Decide what to measure. Enclose values. Read signs."

Using an elementary two-variable example and the records of a study of volume-preserving spheroids, the note shows that the same region yields different mathematical information depending on the quantity decided. In particular, on a box that actually contains a zero, the sign of that quantity cannot be decided however finely the box is subdivided, so a different kind of decision (transversality at the zero) is needed in principle, distinct from exclusion by sign. The note confirms this concretely on the records of 186 boxes.

GeoEnclosure does not claim a new theory of interval analysis. It is a working procedure and a set of verification criteria for combining existing interval arithmetic, analytic estimates, sign decisions and independent checks according to the goal. The note presents its ideas, its verification conditions, its scope and its limits.

**Keywords:** GeoEnclosure; interval analysis; verified numerical computation; computer-assisted proof; sign determination; parameter space; verification cost; computational design

---

# 1　What must be computed to answer the question?

## 1.1　Problem setting

Raise the performance of the computer, raise the precision, subdivide the region further. Even so, the needed conclusion is not guaranteed. So, before computing more, we think.

**What, in the first place, must be computed to guarantee the intended conclusion?**

It may not be necessary to find the value of a quantity itself. Sometimes it is enough to fix its sign. And even when a direct sign decision is hard, the needed conclusion may follow from another derivative, from monotonicity, from symmetry, or from a combination of two formulas. What matters is **to match the desired conclusion, the quantity to be decided and the region to which it is applied**.

This note organises this approach to computational design as GeoEnclosure. It gives no general guarantee of reduced computation. Through examples, it shows why changing the choice of the decided quantity matters, and what the limits of this are for verification.

## 1.2　Relation to existing work and contribution of this note

Every individual technique used in this note is an existing one. Systematic accounts are given of: guaranteed interval enclosure and verified numerical computation in [1, 2, 7, 8, 12]; the dependency problem of interval arithmetic and centred forms such as the mean-value form in [7, 10]; the subdivision of a region while excluding boxes by tests such as monotonicity, in interval global optimisation [9]; guaranteeing the existence and uniqueness of zeros by the interval Newton method or the Krawczyk method in [2, 7]; and cases and methods of computer-assisted proof in [8, 11]. The operation "choose a linear combination of gradients" in Section 3 rests on the same idea as preconditioning in the interval Newton method, in that a system of equations is recombined into a form that is easier to solve.

The contribution of this note is limited to the following three points.

1. It separates the choice of the decided quantity as an explicit design stage carried out before computing, and states it as three basic operations.
2. Using the records of the spheroid study, it shows, as a reproducible tally, that "exclusion by sign" and "transversality at a zero" give different information on the same set of boxes (Section 6).
3. It presents the verification conditions and the two levels (A1, A2) for adopting a computational result as a mathematical claim, in correspondence with the standard document [3] (Section 7, Appendix B).

The "Geo" in the name comes from the fact that the method arose from the study of a geometric problem (angles and ellipsoids). The method itself is not limited to geometric problems.

---

# 2　Definition of GeoEnclosure

## 2.1　Basic structure of the method

The input of GeoEnclosure has three parts: the region to be examined, the function in question, and the mathematical conclusion one wants.

Consider, for example, the question "Is there a stationary point in this square?" First, find out what is needed for a stationary point to exist. Next, choose a quantity with which to test that necessary condition. Then enclose, with a guarantee, the values that quantity can take over the whole region, and read its sign.

In this note, GeoEnclosure is defined as follows.

**GeoEnclosure is a research methodology that chooses, from the structure of the problem, the quantity to be decided that the intended conclusion needs, and examines the range in which a mathematical claim holds by combining guaranteed interval enclosure, independent checking and analytic estimates.**

"Structure" here includes symmetry, geometric relations, terms shared between variables, monotonicity, properties of derivatives and so on. This definition is not a mathematical theorem; it fixes how the work is carried out.

## 2.2　Three basic operations

### Measure — decide what to measure

First, make the desired conclusion clear. Next, find the necessary conditions for that conclusion to hold. Look for points that symmetry lets one group together, directions in which to examine change, terms shared by several formulas, and so on. Then decide: if the sign of which quantity were known, how much of the conclusion would be known?

### Enclose — enclose values

Find an interval containing every value the chosen quantity takes at every point of the region. For example, if one can guarantee that

$$
2\leq F(x)\leq 5
$$

holds over the whole region, then $F$ is certainly positive there. When floating-point computation is used, rounding errors and estimation errors such as those of numerical quadrature are included in the interval. Maxima and minima observed only at grid points are not, by themselves, guaranteed upper and lower bounds over the whole region.

### Read — read signs

Compare the interval obtained with the necessary condition decided at the start.

| What was guaranteed | Conclusion obtained |
| --- | --- |
| A quantity that must vanish at a stationary point is positive, or negative, on the whole box | There is no stationary point in the box |
| At every point where a function of one variable vanishes, its derivative is negative | A root, if any, crosses from positive to negative |
| The interval contains 0, and no other usable condition is available | Left undecided |

What matters is that **the same sign gives different conclusions depending on which quantity was examined**. "There is no root" and "a root, if any, crosses downward" are different pieces of information, and the two must not be confused.

## 2.3　Four principles that support rigour

The GeoEnclosure Standard v1.1 [3, §0] organises the methodology into the following four principles. The explanation below paraphrases the wording of the standard for the context of this note.

**First principle: choose a representation that fits the shape.** Following the structure of the object, rewrite the formulas in a representation in which the values are bounded and the errors can be estimated, and only then compute.

**Second principle: enclose, then decide the sign.** Decide with an interval that certainly contains the true value, rounding included, not with approximate values at sample points.

**Third principle: regenerate from scratch and check independently.** Do not reuse stored outputs; rebuild the results from the inputs and definitions alone. Further, confirm the same sign with formulas and code different from the producer's.

**Fourth principle: close with analysis.** Connect the results on finitely many boxes to a conclusion about the whole region by analytic arguments such as symmetry, monotonicity and inequalities.

The three basic operations express the research approach concisely; the four principles are the conditions under which those operations stand as a mathematical claim.

---

# 3　Why subtract two formulas?

On the unit square $(x,y)\in[0,1]^2$, consider the function

$$
E(x,y)=\frac{(x+y)^2}{2}-x .
$$

Its partial derivatives are

$$
E_x=x+y-1,\qquad E_y=x+y .
$$

Their ranges on the square are $E_x\in[-1,1]$ and $E_y\in[0,2]$, and both intervals contain 0. So the signs of the individual partial derivatives alone cannot decide whether there is a stationary point.

But the same $x+y$ appears in both formulas. So take the difference:

$$
E_y-E_x=1 .
$$

At a stationary point $E_x=E_y=0$ must hold simultaneously, so the difference must also be 0. But the difference is always 1. Hence there is no stationary point in this square. **The conclusion was obtained without subdividing the region even once.**

Why choose this difference? In general, for any vector field $v(x,y)$, the directional derivative $v\cdot\nabla E$ vanishes at a stationary point. So if, for some $v$, $v\cdot\nabla E$ does not vanish anywhere on a box, there is no stationary point in that box. In this example, choosing $v=(-1,1)$ makes the shared $x+y$ disappear, because $x+y$ does not change when one moves in the direction $(-1,1)$. Examining the change in that direction is the geometric reason for subtracting the two formulas in this example.

This example is the special case in which the difference is a constant, and it does not even need interval arithmetic. In general $v\cdot\nabla E$ is not constant, and one looks for a $v$ whose enclosure does not contain 0. The differentiation and algebra used here are existing mathematics. GeoEnclosure puts weight on looking for such relations **before computing**.

---

# 4　How to enclose the same function

## 4.1　The dependency problem of interval arithmetic

Consider the function $F(x)=x-x+1$. Mathematically, $F(x)=1$. But if $x\in[-1,1]$ and the formula is evaluated as written in interval arithmetic,

$$
[-1,1]-[-1,1]+1=[-1,3] .
$$

This interval contains the true value 1, but it also contains 0, so it is too wide to read a positive sign. The two occurrences of $x$ in the formula are the same value. Using this relation to simplify $x-x=0$ gives the enclosure $[1,1]$. There is no need to raise the numerical precision or to subdivide the region. This is a basic example of the dependency problem known in interval arithmetic [7].

## 4.2　Comparing three enclosures

Next, consider $F(x)=x^2-2x+2$ on the range $X=[0.9,1.1]$. The endpoints below are treated exactly as decimal rationals.

| Representation | Method | Enclosure obtained | Width |
| --- | --- | --- | ---: |
| Expanded formula | Evaluate $X^2-2X+2$ in intervals | $[0.61,\,1.41]$ | 0.80 |
| Mean-value form | Add $F'(X)(X-1)$ to the value at the centre 1 | $[0.98,\,1.02]$ | 0.04 |
| Completed square | Evaluate $(x-1)^2+1$ | $[1,\,1.01]$ | 0.01 |

In the mean-value form, $F'(x)=2x-2$ gives $F'(X)\subset[-0.2,0.2]$. The deviation from the centre 1 is at most 0.1, so

$$
F(X)\subset 1+[-0.2,0.2]\times[-0.1,0.1]=[0.98,\,1.02] .
$$

Completing the square further gives $F(x)=(x-1)^2+1$, and since $|x-1|\leq 0.1$, $F(X)\subset[1,\,1.01]$. In this example the enclosure by the completed square equals the true range.

All three enclosures are correct. But the information they give differs in precision.

## 4.3　Which computation is needed?

Now consider two goals.

**Goal A: to show that the function is positive.** In this case the first enclosure $[0.61,\,1.41]$ alone is enough. The whole interval is positive, so no further computation is needed.

**Goal B: to show that the function is greater than 0.99.** In this case the first enclosure cannot decide. Neither can the mean-value form, whose lower bound is 0.98. But the enclosure $[1,\,1.01]$ by the completed square can.

This shows the basic idea of GeoEnclosure. **Finding the narrowest interval is not always the goal.** Once the conclusion the goal needs has been obtained, the computation may stop. Conversely, if the needed conclusion is not obtained, change the representation of the formula. So it becomes important to decide, before starting to compute, what one wants to prove.

---

# 5　The choice on spheroids

## 5.1　The object, and an example of an angle

A volume-preserving spheroid $K_\lambda$ is represented as the image of the unit ball $\mathbb{B}$ (below, the reference ball) under a linear map [4]:

$$
K_\lambda=M_\lambda\mathbb{B},\qquad M_\lambda=\mathrm{diag}\bigl(\lambda^{-1/3},\ \lambda^{-1/3},\ \lambda^{2/3}\bigr),\qquad \lambda>0 .
$$

$\lambda$ is the shape parameter: $\lambda<1$ is oblate, $\lambda=1$ is the sphere, and $\lambda>1$ is prolate. The determinant is 1, so the volume does not depend on $\lambda$. The position of the observation point is expressed in the coordinates of the reference ball, before mapping to the ellipsoid.

Place an observation point $p$ inside a convex body $K$, and let $\theta_p(x)$ be the angle between the direction from the observation point to a surface point $x$ and the outward unit normal $n(x)$ at $x$. The energy is the square of this angle averaged with the cone-volume weight [4]:

$$
E_K(p)=\int_{\partial K}\theta_p(x)^2\,d\mu_{K,p}(x),\qquad
\theta_p(x)=\arccos\!\left(\frac{x-p}{|x-p|}\cdot n(x)\right),\qquad
d\mu_{K,p}(x)=\frac{(x-p)\cdot n(x)}{3\,\mathrm{vol}(K)}\,dA(x) .
$$

By the divergence theorem, $\mu_{K,p}$ is a measure of total weight 1. Reference [4] writes the angle as $\alpha_p$. Below, $K=K_\lambda$, abbreviated to $E$.

One concrete example of the angle. For the oblate ellipsoid $\lambda=0.5$, place the observation point at the centre. In the first row of the exploration record of the angle field [6] (an unpublished record), the surface point is approximately

$$
(0.359129,\ 0.023539,\ -0.603712) .
$$

For $\lambda=0.5$ the equatorial radius is $\lambda^{-1/3}\approx1.259921$ and the polar radius is $\lambda^{2/3}\approx0.629961$, and this point satisfies the equation of the ellipsoid's surface to six digits. The distance from the centre to this point is about 0.702848. Normalising the line-of-sight direction and the outward normal to unit vectors and taking their inner product gives

$$
\cos\theta\approx0.925049,\qquad \theta\approx0.389632\ \text{rad}\approx22.32^\circ .
$$

This distance and angle can be recomputed from the coordinates above and the definition of the ellipsoid alone, and the displayed digits agree (Appendix A, G06a). That the same values are recorded in the first row of the CSV on the research computer was confirmed separately, but this is a check of agreement with the original record and does not mean an independent verification of the whole CSV (G06b). This CSV is not public, so what the reader can check is the computation from the coordinates shown here onward.

The original exploration record has 28,800 rows for each of seven shapes, 201,600 rows in all. Each row records one pair of an observation position and a surface point. These are records of a numerical exploration, and the number of rows alone does not guarantee any mathematical property over the whole region. Note that the 186 boxes of Section 6 are a computation separate from this list of angles.

## 5.2　From angles to stationary points

In an early experiment that examined the stationary points of the volume-preserving spheroid family, the sign of the chosen quantity could not be decided on 21,254 of 31,340 terminal boxes [4]. "Undecided" here does not mean that a stationary point exists; it means that the conclusion could not be reached with that enclosure and that decision rule.

**Is it necessary to decide the sign of the first chosen quantity on all of those boxes?**

Here, instead of holding on to the first decided quantity, we use another partial derivative and rotational symmetry. Let the height of the equatorial plane be $z=0$, and write $\rho$ for the distance from the axis of rotation in the coordinates of the reference ball ($0\leq\rho<1$).

In the prolate shape range $2\leq\lambda\leq5$, first examine the vertical derivative. If it is known that the vertical derivative does not vanish off the equatorial plane, there is no stationary point in that region. Then it suffices to examine the candidates remaining on the equatorial plane. Because of rotational symmetry, if there is one stationary point of positive radius on the equatorial plane, the whole circle obtained by rotating it consists of stationary points. So the problem of counting stationary circles can be moved to a one-variable problem in the radius.

## 5.3　If there is a root, in which direction does it cross?

On the equatorial plane, examine the quantity

$$
H=\frac{E_\rho}{\rho},\qquad \rho>0 ,
$$

where $E_\rho$ is the radial partial derivative of the energy. If the sign of $H$ is bounded away from 0, there is no stationary point of positive radius there.

But even when the sign of $H$ is not decided, other information can be used. Differentiating $E_\rho=\rho H$ gives

$$
E_{\rho\rho}=H+\rho H_\rho .
$$

So **at a point where $H=0$**, $E_{\rho\rho}=\rho H_\rho$. Hence, **if $E_{\rho\rho}<0$ at a point of positive radius where $H=0$**, then $H_\rho<0$. This means that **if a root exists, $H$ crosses from positive to negative at that root**. What is needed here is the condition $H=0$. Without this condition, one cannot conclude that negative curvature always gives $H_\rho<0$.

Further, by rotational symmetry, at a point $(\rho,0,0)$ on the equator, with $y$ the tangent direction of the circle, for $\rho>0$ there is the relation [4, §6]

$$
E_{yyyy}=\frac{3H_\rho}{\rho} .
$$

This relation does not assume $H=0$. So if the fourth derivative is negative on a whole box, then $H_\rho<0$ on the part of that box with $\rho>0$, whether or not there is a root. This is stronger information than the decision by curvature.

What matters here is that, without locating every root, **one can decide the behaviour at a root, if there is one**.

## 5.4　From the crossing direction to the number of roots

**Lemma.** Let $f$ be a continuously differentiable function on an open interval $(a,b)$, and suppose that $f'(c)<0$ at every root $c$ of $f$. Then $f$ has at most one root.

**Proof.** Suppose there are two roots $c_1<c_2$. Since $f'(c_1)<0$, $f<0$ just after $c_1$. Put $c=\inf\{x\in(c_1,c_2] : f(x)=0\}$. Then $c>c_1$, $f(c)=0$ by continuity, and $f<0$ on $(c_1,c)$. Taking the difference quotient from the left of $c$, $(f(x)-f(c))/(x-c)>0$ for $x<c$, so $f'(c)\geq0$. This contradicts the assumption. □

Further, if $f$ is positive near the left end of the interval and negative near the right end, the intermediate value theorem gives at least one root. So under these conditions there is exactly one root. Showing existence, uniqueness and location separately follows the standard [3, §6]. The cases where $f$ vanishes at an endpoint, or where degeneracy occurs at the centre $\rho=0$, must be examined separately.

---

# 6　A comparison — what can be read from the same 186 boxes

## 6.1　Conditions of the comparison and the covering of the region

Using actual research records, we examine how the information obtained changes with the choice of the decided quantity. The object is the 186 terminal boxes of an early exploration on the equatorial plane of the spheroid, recorded in computation ledger N3 of the computational supplement of reference [4]. The shape range is $2\leq\lambda\leq5$ and the radius range is $0\leq\rho\leq1$. This rectangle is divided by 12 binary trees. The endpoints in the ledger are recorded as integers in units of $2^{-20}$.

The covering of the region was confirmed by checks in integer arithmetic on ledger N3 (Appendix A, G16). What was confirmed is as follows.

1. The 12 initial boxes (the boxes from which the binary trees start) each have width $1/4$ in the $\lambda$ direction and $[0,1]$ in the $\rho$ direction, and they tile $[2,5]\times[0,1]$ exactly.
2. Every split is an exact bisection in the $\rho$ direction (161 times) or in the $\lambda$ direction (13 times), and the two children divide the parent exactly.
3. Terminal boxes have no children. The total area of the terminal boxes is exactly 3 as a rational number.

So the union of the 186 terminal boxes equals the target rectangle. However, that the region is covered correctly and that the endpoints of the intervals computed on each box are correct are separate checks.

In the comparison, this partition into 186 boxes is fixed. On the same boxes, two decision rules are then applied.

**Rule A:** examine only the sign of $H$.

**Rule B:** examine the sign of $H$; if that cannot decide, examine the radial curvature $E_{\rho\rho}$; if that still cannot decide, examine the tangential fourth derivative $E_{yyyy}$.

Each box is evaluated with the same quadrature grid as recorded in ledger N3 and the same computing program (below, the original kernel).

## 6.2　Results of the comparison

| Decision on the same boxes | Rule A: sign of $H$ only | Rule B: $H$, curvature, fourth derivative |
| --- | ---: | ---: |
| Roots excluded by the sign of $H$ | 56 | 56 |
| A root, if any, decided to cross downward | 0 | 130 |
| Neither conclusion obtained | 130 | 0 |
| **Terminal boxes in question** | **186** | **186** |

Under rule A, roots are excluded on 56 boxes. All 56 come from $H>0$; there were 0 boxes on which the upper bound of $H$ was negative. The remaining 130 boxes cannot be decided.

Under rule B, on the other hand, the crossing direction of a root, if one exists, can be decided on those 130 boxes as well. Of these, 67 boxes are decided by the radial curvature and 63 boxes by the tangential fourth derivative.

However, **it has not been shown that no root exists in the 130 boxes.** What was obtained is the condition that a root, if one exists, crosses downward. With that information, the lemma of Section 5.4 leads to an argument that bounds the number of roots. Also, since no box with $H<0$ is obtained from the record of these 186 boxes, the existence of a root cannot be derived from this tally. Existence rests on other inputs, such as the signs at the endpoints [4].

There are 12 terminal boxes touching $\rho=0$; 7 of them are decided by $H>0$ and 5 by the fourth derivative. The decision by curvature is not used on any box touching $\rho=0$, so the argument deriving $H_\rho<0$ from $E_{\rho\rho}=\rho H_\rho$ is always used in the range $\rho>0$. The 12 terminal boxes touching $\rho=1$ are all decided by curvature. $\rho=1$ corresponds to the surface of the ellipsoid, and quantities there are treated as limits from the interior [4].

This tally of 56, 67 and 63 comes from a rerun with the original kernel. It is not the result of recomputing the 186 boxes with an independent new kernel (Appendix A, G08).

## 6.3　What this comparison shows, and what it does not

**That rule B leaves 0 boxes undecided follows from the way the partition was made.** The 186 boxes were originally made by stopping the splitting as soon as one of the three decisions succeeded. So the fact itself that rule B can decide every box is not new information.

What this comparison shows is the following. For a shape on which $H$ actually has a zero, the enclosure of $H$ on a box containing the zero necessarily contains 0. On such a box, rule A never terminates, however finely the box is subdivided and however fine the quadrature grid. According to reference [4], for example, at $\lambda=3$ a stationary radius has been found numerically near $\rho\approx0.824$. In other words, the 130 boxes left undecided by rule A contain not only a lack of computation but **a limit of the very kind of decision, exclusion by sign**. Near a zero, a kind of guarantee different from exclusion (here, transversality) is needed in principle; this is the same situation as with uniqueness tests such as the interval Newton method [2, 7].

From the viewpoint of GeoEnclosure, the point is to anticipate this need at the stage of choosing the decided quantity, rather than to discover it after repeated subdivision has got stuck.

## 6.4　Relation to the breakdown of the original 186 boxes

In the original ledger of reference [4], the 186 boxes were divided into the following three groups.

| Decision adopted in the original ledger | Boxes |
| --- | ---: |
| $H>0$ | 39 |
| Radial curvature negative | 62 |
| Tangential fourth derivative negative | 85 |
| **Total** | **186** |

This breakdown and the 56, 67 and 63 of Section 6.2 do not contradict each other. In the original exploration, the last 85 boxes (all with $\rho\leq1/2$) were processed by a scheme that evaluated only the fourth derivative, and the ledger records no enclosures of $H$ or of the curvature for them. When $H$ and the curvature are evaluated afresh on these 85 boxes with the same quadrature grid, 17 boxes are decided by $H>0$, 5 boxes are decided by negative radial curvature, and the remaining 63 boxes use the fourth derivative. Hence

$$
39+17=56,\qquad 62+5=67,\qquad 85-17-5=63 .
$$

**Which decided quantities are used, and in which order, changes the conclusion attached to the same box.** For the 17 boxes, the stronger "there is no root" is obtained instead of "a root, if any, crosses downward".

## 6.5　Reading one box

Take one concrete box. Its shape range is $\lambda\in[2,\,9/4]$ and its radius range is $\rho\in[3/4,\,7/8]$. In ledger N3 it is branch x110 of E00.

The enclosure of $H$ on this box, with the ledger values rounded outward, is

$$
H\in[-0.151,\ 0.521] .
$$

It contains 0, so the sign of $H$ is not decided. But examining the radial curvature on the same box gives the negative enclosure

$$
E_{\rho\rho}\in[-1.227,\ -0.077] .
$$

If there is a point where $H=0$, then $E_{\rho\rho}=\rho H_\rho$ there. On this box $\rho>0$, so $H_\rho<0$ at such a point. That is, even though the sign of $H$ is not decided, one can conclude: **"if this box contains a root, that root crosses downward"**.

## 6.6　Limits of the comparison

From this comparison one cannot conclude that GeoEnclosure shortens computing time by a fixed ratio. What was measured is **the difference in mathematical information obtained from the same 186 boxes**. The number of boxes and the time required when splitting from the start by sign alone were not measured. Reference [4] also states explicitly that these box counts are not a comparison of computing times.

Also, the 31,340 boxes of Section 5.2 belong to a different exploration in which the height also varies. One cannot compare these 31,340 boxes with the 186 boxes to obtain a rate of reduction in computing time.

Further, this comparison is a tally that presupposes that the enclosures recorded in ledger N3 are correct. This ledger of 186 boxes is an early exploration record (a copy from a fixed original archive) for computational proposition C4 of reference [4], and the source code of the original kernel still carries the note that it is diagnostic and not evidence (`DIAGNOSTIC_ONLY / NOT_EVIDENCE`). Reference [4] has not changed these notes, and treats C4 not as a proven fact but as an assumption (level A1). Also, the radial monotonicity part of C4 rests not on these 186 boxes but on the 731 boxes of Section 7.4 and their re-evaluation by a separate implementation. So the comparison in this section is not a component of a proof; it is an illustration of the effect of the choice of the decided quantity.

---

# 7　Close with analysis, check independently

## 7.1　Finite computation and an infinite region

The shape parameter $\lambda$ ranges over the positive numbers. Laying out finitely many boxes in the original coordinate $\lambda$ does not necessarily cover every positive shape. For example, for the region of extremely thin ellipsoids, there is a method that treats the region all at once with inequalities that hold uniformly for $0<\lambda\leq1/32$ [4]. This is an example of handling, by analytic inequalities, a region that is hard to handle by finite computation alone.

However, when a region handled by analysis is combined with a region handled by numerical computation, one must confirm that there is no gap at the boundary. Also, a differential formula that holds in the interior does not necessarily hold on the boundary. For example, the boundary zeros treated in reference [4] are defined for the limit of the full gradient approached from the interior, which differs from a constrained extremum along the boundary.

## 7.2　Reproduction and independent checking

The verification of computational results has different stages. If the same code and the same input give the same result, the stored computation has been reproduced. Recomputing with different formulas or a different program is important for finding errors specific to the original implementation. But even that is not necessarily enough. If both programs rest on the same wrong definition, they may reproduce the same error. So a check that goes back to the original mathematical definition is also needed [3, §5].

The Standard v1.1 [3] sets conditions on rounding, remainders, covering of the region, independent checking and so on. Its main points are summarised in Appendix B.

## 7.3　A1 and A2

The Standard v1.1 [3, §7] divides the adoption of research results into two levels.

| Level | Content of the verification | Treatment in a paper |
| --- | --- | --- |
| A1 | A sampled independent audit under fixed conditions | Written as a theorem with the computational propositions stated explicitly as assumptions |
| A2 | Every terminal box re-evaluated with an independent kernel | The condition for writing an unconditional theorem (a computer-assisted proof) |

A result adopted at A1 is not written as an unconditional theorem as it stands. **It is stated as a theorem with the computational propositions stated explicitly as assumptions.** The research draft that classified the stationary points of the spheroid family [4] also states its global classification assuming six computational propositions C1–C6. This note does not reprove that global classification.

Also, the standard [3, §7.3] requires, as conditions for the stage of writing a paper, that the ledgers, code and checkers be made a public object with a DOI, and that the author personally make the final check. Their status for this note is given in Appendix A.4 and in the references.

## 7.4　Relation to a stronger result

Reference [4] also divides the same equatorial plane separately and examines whether the tangential fourth derivative is negative on the whole interior. For the shape range $2\leq\lambda\leq5$, a covering by 731 boxes is recorded. A separate implementation also subdivides those 731 boxes locally and re-evaluates them on 1,043 small pieces.

If this sign is guaranteed on the whole region, then $H_\rho<0$, and for each shape $H$ is strictly decreasing in the radius. This is a stronger claim than the decision "a root, if any, crosses downward" in the comparison on 186 boxes. The two are not to be confused. The comparison on 186 boxes shows that the information obtained changes with the choice of the decided quantity. The computation on 731 boxes is a separate computation that examines a stronger property: monotonicity on the whole equatorial plane.

---

# 8　Scope of GeoEnclosure

When GeoEnclosure is used on another problem, there is one thing to decide first.

**"If the sign of this quantity is known, how much of the desired conclusion is known?"**

For example, if several partial derivatives share a term, look for a combination that cancels it. If there is symmetry, group together points with the same property. If zeros cannot be excluded directly, consider whether the crossing direction or the number of zeros can be bounded. If the same function has several representations, compare their enclosures. Once the needed conclusion is obtained, no further subdivision is needed.

However, this note does not show a general rule that these operations reduce computation for every problem.

## 8.1　Extension to triaxial ellipsoids

Application to triaxial ellipsoids, which have no rotational symmetry, is currently being studied [5]. In the triaxial case, the rotational symmetry that collects a stationary circle into one radius is not available. So other directions or relations between partial derivatives must be chosen.

In this study, within the parameter rectangle $R=[1,16/5]\times[1,6]$ (below, the main rectangle), the classification of stationary points has been adopted at level A1 for a neighbourhood of the sphere and for narrow strips along the edges that correspond to spheroids. The structure of the zero curves of four quantities related to the centre and to the endpoints of the coordinate axes, and of their intersection, has also been adopted at level A1. On the other hand, the classification of stationary points over the whole interior of the main rectangle is not finished. A calibration computation for estimating the computing cost has been run, but at the time of writing it has not been accepted, and its results are not registered in the public repository. This note does not use those results for its conclusions.

In future, when different methods are compared, the starting region, the goal and the stopping criterion must be aligned, and then the number of boxes, the undecided region, the computing time and so on must be measured.

## 8.2　Limits as a methodology

GeoEnclosure puts weight on choosing a decided quantity suited to the structure of the problem. But an effective decided quantity cannot always be found. Nor does a smaller enclosure width necessarily make the whole computation faster. Changing the representation can increase the computation needed for one evaluation. Further, even if an interval is narrow, it cannot be used in a mathematical proof if the guarantees on rounding or remainders are insufficient.

The examples in this note come from one study (the spheroid family). The note gives no general procedure for choosing the decided quantity, and its effectiveness on other problems is unverified. So the effectiveness of GeoEnclosure must be assessed with the target problem and the computational conditions stated explicitly.

---

# 9　Conclusion

This note has organised, as GeoEnclosure, a methodology that traces back from the intended conclusion and chooses the quantity to be computed and the meaning of its sign. Its central operations are three: **Decide what to measure. Enclose values. Read signs.** They are supported by four principles: a representation that fits the shape, guaranteed enclosure, independent checking and analytic estimates.

In the concrete examples, merely taking the difference of partial derivatives showed that there is no stationary point, without subdividing the region. In another example, three enclosures of the same function were compared, confirming that the precision needed differs with the desired conclusion.

In the comparison on spheroids, on the same 186 boxes, the sign of $H$ alone excluded roots in 56 boxes. Further, using the curvature and the fourth derivative, the crossing direction of a root, if one exists, was decided on the remaining 130 boxes as well. On a box containing a zero, exclusion by sign cannot succeed in principle, so adding a decided quantity of this kind is not a substitute for subdivision but a necessary component.

However, no rate of reduction in computing time, and no performance advantage on general problems, has been shown.

**Before computing more, think about what is enough to compute.** State that policy explicitly as the quantity chosen, the conclusion that can be drawn from it, the guaranteed computation and the record of independent verification. This is the basic idea of GeoEnclosure proposed in this note.

---

# Appendix A　Table of claims and evidence

## A.1　Purpose of the table

For each claim of this note, the table records where in the text it is written, what it rests on, and who checked it by what method.

Three states of checking are used.

**Checked:** the stated claim has been checked by the stated method and over the stated range.

**Reproduced only:** the original record or computation has been reproduced, but no independent derivation or full independent check has been completed.

**Unchecked:** the needed check has not yet been completed.

These states are for managing the claims of this note, and are separate from the adoption levels A1 and A2 of the Standard v1.1. A "citation" introduces a result of other research material and does not mean that it is newly proved in this note.

The checkers are distinguished as follows.

- **Claude:** Claude (Anthropic, dialogue on claude.ai). It compared formulas, originals and ledgers.
- **ChatGPT:** ChatGPT (OpenAI). It took part in checking the run records on the research computer and in writing and re-running the code for the comparison.
- **Claude Code:** Claude Code (Anthropic). On 21 November 2026 it re-checked, using only fixed commits of the public repositories [3, 4, 5] as input. The scripts it used are attached to this note.
- **Author:** Katsushi Furuta. The researcher responsible for the final research content and for the decision to publish.

A check by an AI depends on the record of a dialogue and cannot itself be re-run by a third party. So checks that can be re-run (those for which the script and the location of the input are identified) are distinguished in the "re-check" column.

## A.2　Claims and evidence

| ID | Claim or citation of this note | Section | Evidence, range of check | Kind | Checker | State | Re-check from public material |
| --- | --- | --- | --- | --- | --- | --- | --- |
| G01 | If a quantity that must vanish at a stationary point is nonzero on the whole region, there is no stationary point | §2 | Definition of a stationary point and sign decision | Claim of this note | Claude | Checked | Complete in the text |
| G02 | In the two-variable example there is no stationary point | §3 | Algebra of $E_y-E_x=1$ | Claim of this note | Claude | Checked | Complete in the text |
| G03 | $x-x+1$ is always 1 | §4.1 | Algebraic identity | Claim of this note | Claude | Checked | Complete in the text |
| G04 | The mean-value form and the completed square give different enclosures | §4.2 | Rational arithmetic of the three intervals | Claim of this note | Claude | Checked | Recomputed in rational arithmetic; agrees |
| G05 | Whether the goal is "positive" or "greater than 0.99" changes the enclosure needed | §4.3 | The three lower bounds of G04 | Claim of this note | Claude | Checked | Complete in the text |
| G06a | From the coordinates in the first row of the angle field, a distance of about 0.702848 and an angle of about 0.389632 rad are obtained, and the point lies on the surface of the given ellipsoid | §5.1 | Computed independently from the coordinates, the surface condition and the normal | Numerical example | Claude | Checked | Recomputed; agrees to the displayed digits |
| G06b | The first row of the angle-field CSV holds recorded values that agree with G06a | §5.1 | Comparison with the first row of the original CSV on the research computer | Record comparison | ChatGPT | Reproduced only | Not possible (the CSV is not public) |
| G07 | The breakdown of the original ledger of 186 boxes is 39, 62, 85 | §6.4 | Direct comparison of reference [4] with ledger N3 | Comparison material of this note | Claude | Checked | Re-tallied from ledger N3; agrees |
| G08 | In the comparison on the same 186 boxes, 56 boxes are excluded and the crossing direction is decided on 130 boxes (67 + 63). The original 85 boxes are reclassified as 17, 5, 63 | §6.2, §6.4 | Rerun with the original kernel. Not a recomputation with an independent kernel | Comparison result of this note | ChatGPT | **Reproduced only** | The original kernel was compiled and rerun in another environment. All 186 enclosures in the ledger agree as integers, and 56, 67, 63 and 17, 5, 63 are reproduced. The kernel is the same, so the state remains "Reproduced only" |
| G09 | On branch x110 of E00, the curvature is negative although the sign of $H$ is undecided | §6.5 | Direct comparison of branch x110 of ledger N3 with the text | Concrete example of this note | Claude | Checked | Recomputed from the integer values of the ledger; agrees |
| G10 | If every interior root crosses downward, there is at most one root | §5.4 | One-variable analytic argument | Lemma used in this note | Claude | Checked | Complete in the proof in the text |
| G11 | Reference [4] examines the sign of the fourth derivative on 731 boxes and, in a separate implementation, on 1,043 small pieces | §7.4 | Comparison with reference [4], §6.4 | Citation | Claude | Checked | The statement confirmed in the source of reference [4] |
| G12 | The classification of the spheroid family in reference [4] is stated in a form that assumes C1–C6 | §7.3 | Comparison of reference [4] with the Standard v1.1 | Citation | Claude | Checked | Same as above |
| G13 | A1 and A2 have different audit conditions | §7.3 | Standard v1.1, §7 | Citation of the standard | Claude | Checked | Confirmed in the original text of the Standard v1.1 |
| G14 | For triaxial ellipsoids, four zero curves and some strips are adopted at A1, and the classification over the whole interior of the main rectangle is not finished | §8.1 | Adoption rulings of reference [5] and the triaxial research records | Citation of research status | Claude | Checked | Agrees with the statement in the repository README (the content of the ruling documents not checked) |
| G15 | In the early exploration, the sign was undecided on 21,254 of 31,340 boxes | §5.2 | Comparison of reference [4] with the ledger; arithmetic check of the breakdown by class | Citation | Claude | Checked | Only the statement in reference [4] confirmed (the ledger totals not checked) |
| G16 | The 186 terminal boxes of the 12 binary trees cover the target rectangle exactly | §6.1 | Integer checks of the initial boxes, the bisections and the terminal condition | Comparison condition of this note | Claude | Checked | Re-checked in integer arithmetic; agrees (174 splits, total area 3) |
| G17 | The run log of the calibration computation recorded the generation of 96 rows and the creation of the result archive | §8.1 | Confirmation of the run log and of the existence of the result files on the research computer | Run status | ChatGPT | Reproduced only | Not possible (the results are not public) |
| G18 | Of the 12 boxes touching $\rho=0$, 7 are decided by $H>0$ and 5 by the fourth derivative, and the decision by curvature is not used. The 12 boxes touching $\rho=1$ are all decided by curvature | §6.2 | Ledger N3 and the rerun results of G08 | Comparison condition of this note | Claude Code | Reproduced only | Same as the evidence column |

## A.3　How to read the table

**On G08:** the tally of 56, 67 and 63 is the result of a rerun with the original kernel. That the same result was reproduced in another environment shows that the stored computation is reproducible, but it does not show that the kernel itself is correct. No recomputation of the 186 boxes with an independent kernel has been done. So the state is "Reproduced only".

**On G06a and G06b:** computing the distance and the angle from the coordinates, and the agreement of the CSV record, are separate checks. The former has been checked as an independent mathematical computation. The latter is a comparison with the original on the research computer. The two are not merged into one state.

**On G11–G15:** "Checked" here means that agreement with what is stated in the cited material has been confirmed. It does not mean that the research results of the cited source have been newly and independently proved in this note.

**On G16:** that the covering of the region is correct and that the numerical enclosures of the boxes are correct are separate checks. The integer check confirms the former.

**On G17:** even if the run log records the generation of 96 rows, the mathematical correctness of all 96 rows has not been confirmed. Independent acceptance and the research decision to adopt or not are made separately.

## A.4　The author's final check

The checker column of this table shows the history of the work actually done. Before publication, the author checks at least the following.

1. What each claim means.
2. What can be concluded from that claim.
3. Whether the material cited as evidence is appropriate.
4. Whether the unchecked range is understated.
5. Whether the involvement of AI and the listing of checkers are accurate.

**Final check by the author:** date of check, 21 November 2026. Range of check, G01–G18.

---

# Appendix B　Technical conditions for rigorous verification

This appendix takes the Standard v1.1 [3] as the reference standard and lists its main points.

**B.1　Rounding.** In interval computation, rounding is handled so that the true value is certainly contained in the interval. Record the computing scheme used, the floating-point environment and the representation of constants.

**B.2　Quadrature and remainders.** Do not use an approximate value of numerical quadrature as it stands as a guaranteed value of the integral. Include the approximation error and the remainder of series through explicit upper bounds.

**B.3　Singularities and boundaries.** For contact points, axes of symmetry and derivatives at the boundary, state the representation used and the grounds for the limit. Distinguish the trace of the full gradient at the boundary from the constrained derivative along the boundary.

**B.4　Covering and computation records.** Confirm that the union of the computed boxes contains the target region. Do not delete undecided boxes or boxes on which the computation stopped.

**B.5　Independent audit.** Record separately: the check that goes back to the original definition, evaluation by independent formulas and implementations, the check of the boxes with the smallest margin, the check of randomly sampled boxes, and the recomputation of the covering.

**B.6　Correspondence between claims and evidence.** Match each computational claim in a paper with its inputs, ledgers, programs and check records. Agreement of SHA-256 shows that files are identical; it does not itself prove mathematical correctness.

---

# References and computational material

**[1]** R. E. Moore, *Interval Analysis*, Prentice-Hall, 1966.

**[2]** S. M. Rump, "Verification methods: Rigorous results using floating-point arithmetic," *Acta Numerica*, 19, 287–449, 2010. DOI: 10.1017/S096249291000005X.

**[3]** *GeoEnclosure Standard* v1.1, 20 November 2026. The audit standard of the GeoEnclosure research.
Repository: `https://github.com/cotaxxxx/bg-triaxial-family`
Commit: `67eb2afdd3ccc0bb976302dbb68548b256b3fc45` (`main`)
File: `evidence/chat-originals/2026-11-20/GEOENCLOSURE_STANDARD/GEOENCLOSURE_STANDARD_v1.1.md`
Record of adoption: `JUDGE_RULING_STANDARD_v1.1_20261120.md` in the same directory
A copy of the standard is included in the same Zenodo record as this note.

**[4]** Katsushi Furuta, *Counting stationary points and saddle circles of a cone-volume-weighted angle energy on spheroids*, Integrated Research Draft v0.4, 20 November 2026. A research draft on the structure of stationary points and stationary circles of the volume-preserving spheroid family.
Repository: `https://github.com/cotaxxxx/bg-spheroid-family`
Commit: `a5ab9b5016c8df9b7f94cbfd7cd0e82aeba8dd28` (branch `codex/paper-i-v0.4-20261120`)
Location: `manuscripts/2026-11-20/Paper_I_v0_4`
Accompanying archive: `Paper_I_v0_4_Manuscript_and_Verification.zip`
(SHA-256: `57ee540bb8f3679e1b5abfaf043d6c961d934a981bddfb9d0dba0bd32a4c4d91`)
Ledger of the 186 boxes: `audit/snapshots/ledgers/N3/E00.tsv.gz` to `E11.tsv.gz` in the archive
Original kernel: `audit/snapshots/kernel.cpp`, `interval.hpp` in the archive

**[5]** Research records of the stationary points of the volume-preserving triaxial ellipsoid family, 20–21 November 2026.
Repository: `https://github.com/cotaxxxx/bg-triaxial-family`; commit as in [3].
This research is ongoing, and the classification over the whole interior of the main rectangle is not finished.

**[6]** Exploration record of the angle field of the spheroid, `raw_angle_field/runs/coarse_raw.csv`.
SHA-256: `d745337c5a679d53f50cf41045e0871b0cbaa24e9274dfb07e445383a58cb50e`
This CSV is an unpublished record and is not included in the public repositories above. The numerical example of Section 5.1 is quoted from the first row of this record.

**[7]** R. E. Moore, R. B. Kearfott, M. J. Cloud, *Introduction to Interval Analysis*, SIAM, Philadelphia, 2009. ISBN 978-0-89871-669-6.

**[8]** W. Tucker, *Validated Numerics: A Short Introduction to Rigorous Computations*, Princeton University Press, 2011. ISBN 978-0-691-14781-9.

**[9]** E. Hansen, G. W. Walster, *Global Optimization Using Interval Analysis*, 2nd ed., revised and expanded, Marcel Dekker, New York, 2004. ISBN 978-0-8247-4059-7.

**[10]** H. Ratschek, J. Rokne, *Computer Methods for the Range of Functions*, Ellis Horwood, Chichester, 1984. ISBN 0-85312-703-4.

**[11]** J. Gómez-Serrano, "Computer-assisted proofs in PDE: a survey," *SeMA Journal*, 76(3), 459–484, 2019. DOI: 10.1007/s40324-019-00186-x.

**[12]** S. Oishi (ed.), *Seido hoshō tsuki sūchi keisan no kiso* [Foundations of Verified Numerical Computation], Corona Publishing, 2018 (in Japanese).

**Check scripts attached (placed in the same record as this note):**

- `check_n3_cover.py`: integer checks of the covering, the bisections, the terminal condition and the breakdown 39, 62, 85 of ledger N3 (G07, G16).
- `rerun_186_rules.py`: re-evaluates the 186 boxes with the original kernel and outputs the tallies of rules A and B (G08, G18).

---

# Use of AI and status of the manuscript

This research used **ChatGPT (OpenAI, GPT-6.2 Astra), Codex (OpenAI), Claude (Anthropic) and Claude Code (Anthropic)**. These AI systems took part in examining mathematical derivations, designing computational methods, writing programs, numerical computation, independent checking, auditing, structuring the manuscript and writing the text.

The idea of the method came from the author's dialogue with Claude. The GeoEnclosure Standard v1.1 was drafted and revised by Claude (dialogue on claude.ai), and v1.0 was reviewed by Claude Code. Claude (dialogue on claude.ai) took part in comparing the formulas, originals and ledgers of this note. The computations of reference [4] (including ledger N3 of the 186 boxes of Section 6 and the original kernel) were produced by ChatGPT (OpenAI, GPT-6.2 Astra) using Codex (OpenAI). ChatGPT (OpenAI) took part in checking the run records on the research computer, in writing and re-running the code for the comparison, and in revising the text. Claude Code was used for the revision to v1.0 and for the re-checks from the public repositories. The first Japanese draft was written by AI.

The "Judge" that appears in the standard and in the records of adoption is a role held by the researcher himself (the author). Whether a result is adopted as a research result is decided by the author; no AI decided any adoption.

What an AI proposed, what an AI checked and what the author personally checked are not treated as the same thing. The range of each check is given in Appendix A and in the related research records. The author has personally checked, and is responsible for, the final content of this note, its citations, the range of its mathematical claims and the disclosure of the use of AI.

**Status of this note:** research note v1.0 (Japanese original; this file is its English translation). For publication on Zenodo.

**Publication policy:** submitted to Zenodo as a research note presenting the methodology of GeoEnclosure, its conditions of application, its limits and its framework of verification.

---

# Revision history

*The revision history refers to the Japanese text.*

### v1.0, author's check (21 November 2026)

- Added "The idea of the method came from the author's dialogue with Claude" to the disclosure of the use of AI (the author's decision, 21 November 2026).
- Added to the disclosure of the use of AI that the computations of reference [4] were produced by ChatGPT (GPT-6.2 Astra) using Codex (fact confirmed by the author, 21 November 2026). The claims, numbers and states in the table are unchanged.
- Entered the author's final check in Appendix A.4 (date of check 21 November 2026, range of check G01–G18), and removed the note on the title page that it was awaiting entry. The claims, numbers and states in the table are unchanged.

### v1.0 (21 November 2026)

- Unified the version number, which differed between the title page and the end (v1.0 and v0.7), to v1.0.
- Unified formulas to `$...$` and `$$...$$`, and removed leftover escapes (`\_`, `\*\*`).
- Added Section 1.2, "Relation to existing work and contribution of this note", and references [7]–[12].
- Section 5.3: stated that the decision by the fourth derivative does not assume $H=0$.
- Section 5.4: rewrote the lemma and its proof in a form that does not assume the existence of adjacent roots.
- Section 6: called the starting boxes of the partition trees "initial boxes", distinguishing them from "roots", which refer to zeros of $H$. Stated that there are splits in the $\lambda$ direction.
- Added Section 6.3, stating that the 0 undecided boxes under rule B follow from the way the partition was made, and stating the limit in principle of exclusion by sign.
- Section 6.4: stated that the ledger records no $H$ or curvature for the original 85 boxes, and explained why the reclassification arises.
- Section 6.2 and Appendix A: added the breakdown of the boxes touching $\rho=0$ and $\rho=1$ (G18), and the column of re-checks from public material.
- Section 8.1: replaced internal terms (layer IV, V60, interior) with general expressions, and shortened the description of ongoing work.
- Replaced statements in the text such as "checked by Claude, the auditor" with references to IDs in Appendix A.
- Removed the closing slogan "The principle is simple; the verification is rigorous." (because the verification state of this note itself includes "Reproduced only" and "A1").
- Section 5.1: quoted the definitions of the ellipsoid family and of the energy from reference [4]. Stated that the angle-field CSV is an unpublished record.
- Section 6.6: stated the status of the ledger of 186 boxes (an early exploration record for C4, level A1, not a component of a proof).
- Checked the bibliographic data of references [7]–[12] against library catalogues and publisher information, and added ISBNs and DOIs.
- Use of AI: stated that the "Judge" is the researcher himself.
- No change to the numbers (the breakdown of the 186 boxes, 56, 67, 63, the endpoints of the enclosures).

### v0.7 (21 November 2026)

- Rewrote the abstract to centre on verification cost and the methodology of GeoEnclosure.
- Placed the motivation of the research at the start of Section 1 (not as a separate section).
- Began Section 1 with a problem setting from computational science in general, and moved the experimental records specific to geometry to Section 5.2.
- Distinguished existing theory from the methodological devices organised in this note.
- Unified the status notation for submission to Zenodo.
- No change to the results on the 186 boxes, the computational grounds or the audit status.

### v0.6, revision 3 (21 November 2026)

- Based on the author's corrected version, unified the delimiters for displayed formulas.
- Unified "零" used as a value to "0". Kept "零点" (zero), "零曲線" (zero curve) and "非零" (nonzero) as mathematical terms.
- Corrected a typo in the abstract, the listing of checkers, a missing character and Markdown escapes.
- The mathematical claims, numbers, comparison and audit status are unchanged.

### v0.6, revision 2 (21 November 2026)

- Removed from Section 1 a formula that only added up counts by class.
- Changed the internal name "Paper I" to "the spheroid research draft [4]" or "reference [4]".
- Stated the meaning of computation ledger N3 and where it is.
- Explained in the text the meaning of internal terms of the triaxial ellipsoid study.
- Tidied the references in the claim table for G07, G11, G12, G15 and others.
- The mathematical claims, the experimental results on the 186 boxes, the audit status and the content of the disclosure of the use of AI are kept.

### v0.6, revision 1 (21 November 2026)

- Stated that the drafting and revision of the GeoEnclosure Standard v1.1 were done by Claude (dialogue on claude.ai).
- Stated that the review of v1.0 was done by Claude Code.
- Made "chat" in Appendix A.1 explicit as Claude (Anthropic).
- Distinguished "chat" and "ChatGPT" as different systems.
- The formulas, numbers, comparison, adoption levels and states in the claim table are unchanged.
