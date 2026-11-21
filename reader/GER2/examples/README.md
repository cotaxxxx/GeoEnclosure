# GeoEnclosure の例題集（examples/）

研究ノート『GeoEnclosure』の §3〜§4 の数と、基準 v1.1 §6 の「根の主張」を、自分の計算機で確かめるための例題です。Python 3.9 以上の標準ライブラリだけで動き、numpy などは要りません。

```bash
python ex1_gradient_difference.py
python ex2_three_enclosures.py
python ex3_root_by_bisection.py
python selftest_examples.py        # 最後に FAILURES 0
```

| 例題 | 内容 | 体験できること |
|---|---|---|
| `ex1_gradient_difference.py` | E(x, y) ＝ (x＋y)²/2 − x の [0, 1]² での停留点 | 箱に分けると 9 箱を評価して決まる。先に E_y − E_x ＝ 1 を測れば、箱は要らない。式を整理せずに差を包むと [−1, 3] になる（§4.1 の依存性） |
| `ex2_three_enclosures.py` | F(x) ＝ x² − 2x ＋ 2 の [0.9, 1.1] での三つの包み | 三つとも正しい。目標が「F > 0」なら一つ目で足り、「F > 0.99」なら三つ目が要る。有理数で厳密に計算する |
| `ex3_root_by_bisection.py` | x³ − 2x − 5 の [2, 3] の根 | 「根がちょうど一つ」を、存在（端の符号）、一意性（f′ > 0）、位置（二分）の三つに分けて示す |
| `iv.py` | 外向き丸めの区間（約 40 行） | 基準 v1.1 §2.1 (b)：IEEE の +、−、× は正しく丸められるので、端を 1 ulp 外へ動かせば真の値を必ず含む |

## 読むときの注意

- **`iv.py` は、計算がたまたま厳密なときも端を 1 ulp 広げます。** そのため、0 ＋ 0 が [−5e−324, 5e−324] のように表示されます。規則を単純にした代わりの、小さな損です。
- **`iv.py` に渡す値は、二進でちょうど表せる数に限ります。** 整数や、0.5、0.25 などです。0.1 は二進でちょうど表せないので、`ex2` は有理数（`fractions.Fraction`）を使っています。
- **箱の区間が 0 を含んでも、そこに根があるという証明にはなりません。** `ex3` では、根の存在は端の符号と連続性で示しています。箱は場所を狭めるためだけに使います。

---

**English.** Small runnable examples for the GeoEnclosure research note (§3–§4) and for Standard v1.1 §6 (claims about roots). Pure Python 3.9+. `iv.py` is a 40-line outward-rounded interval type. Run `selftest_examples.py`; it ends with `FAILURES 0`.
