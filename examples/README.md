# GeoEnclosure 実例（Worked Examples）

2026-11-26 JST · Judge 決定：各実例は次の **3点セット** で構成する。

| 3点 | 中身 | 必須ファイル（例） |
|---|---|---|
| **1. 検証方法** | 何を測るか（Measure）、どう包むか（Enclose）、どう符号を読むか（Read）、端の解析的な閉じ方、合否基準。**実行前に固定**する | `PLAN.md`、`DERIVATION.md`、`PLAN_INPUTS.json` |
| **2. 検証結果** | 符号台帳と被覆、得られた保証区間、独立検査の判定、監査記録。古典値との照合。数学的主張と到達状態を分けて書く | `SIGN_LEDGER.jsonl`、`RESULT.json`、`INDEPENDENT_CHECK.json`、監査記録へのリンク |
| **3. 再現コード** | 第三者が同じ結果を出し直せる一式。ビルド、実行、別系統の独立検査、ハッシュ | `build.sh`、`run_case.py`、`verify_certificate.py`、`src/`、`SHA256SUMS.txt` |

## 順序

検証方法の固定（事前登録）→ chat 監査 → Judge 実行承認 → 研究PCで実行 → 検証結果の登録 → chat 監査 → Judge 採否 → 公開。

## 一覧

| # | 実例 | 検証方法 | 検証結果 | 再現コード |
|---|---|---|---|---|
| 1 | マクローリン→ヤコビ分かれ目 | 固定済（4e52466、ブランチ `codex/macl-jacobi-interval-20261126`） | **採用**（53319d8、chat 監査 4e0a884、Judge 採用 2026-11-26）：e* ∈ [0.8126700106117429, 0.8126700106117432]、Ω²/(πGρ) ∈ [0.3742296747861903, 0.3742296747862011] | 固定済（束 SHA-256 da6a37be…7038） |

候補（未着手）：マクローリン列の目印、ヤコビ→洋梨形、楕円への法線の本数、ラグランジュ点、3軸楕円体のへそ点。記録は experimental-mathematics-ai-collaboration `docs/GEOENCLOSURE_WORKED_EXAMPLE_CANDIDATES_20261126.md`（e812e00）。
