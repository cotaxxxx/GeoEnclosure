# マクローリン列からヤコビ列へ｜GeoEnclosure の実例

2026-11-26 JST · DIAGNOSTIC_ONLY · chat の監査待ち

与えられた積分条件から、尺度に依存しない $F=af$ を作る。$F'(e)\ge44e/105>0$ により、箱の値域を両端の評価だけで包める。両端は剰余を付けた解析で閉じ、残る中間域を MPFR の符号で二分する。根を含む箱の全体で、$\omega=\Omega^2/(\pi G\rho)$ を評価する。[計画](PLAN.md) · [導出と剰余](DERIVATION.md)

| 段階 | 入力と成果物 |
|---|---|
| Measure | 相似正規化、$\arcsin$ への変形、単調性と両端の剰余 |
| Enclose | MPFR の値域、根の箱での $F'$ と $\omega$ の区間 |
| Read | 評価IDから復元する符号台帳と $(0,1)$ の被覆 |
| 確かめ直す | 別式・別コードの整数比級数による符号と区間の照合 |

## 作業機の確認

```sh
python3 -B smoke_checks.py
```

人工の一次関数で、中点が零になる場合の四分点処理と符号台帳を確認する。`--library PATH_TO_SO` を指定すれば、MPFR の基本演算の人工入力も確認できる。[作業機の記録](SMOKE_CHECKS.txt)

## 研究PCで実行する際の手順

1. chat の監査を受け、Judge の実行承認コミットを控える。候補B v2が終了した記録を確認する。**候補B v2の終了後かつ2026-11-26 18:14 JST以降**に Dig が実行する。
2. `MACLAURIN_JACOBI_PC_BUNDLE.tar.gz` と同名の `.sha256` を照合する。新しい実行用ディレクトリに展開後、`sha256sum -c SHA256SUMS.txt` を実行する。
3. 候補Bと同じ K1、コンパイルフラグ、MPFR/GMP の実ヘッダによるビルドを使う。`bash build.sh` は `libmpfr-dev`・`libgmp-dev` の導入状態と版、実 MPFR ヘッダ・リンク先の一致、GMPの64ビットlimbを確認する。パッケージが足りなければログと `apt-get -s install --no-install-recommends libmpfr-dev libgmp-dev` の予定を報告して停止し、Judge の導入承認を待つ。コンパイルは `-include mpfr.h -lmpfr -lgmp`、`-O2 -fno-fast-math -ffp-contract=off`。Python 3.10以降の標準ライブラリを使う。
4. 以下の大文字を実際の固定コミット、終了時刻、終了記録のパスまたはコミット、未使用の出力先に置き換える。終了時刻にはタイムゾーンのオフセットを含める。

```sh
bash build.sh
python3 -B run_case.py \
    --bundle-commit BUNDLE_GIT_SHA \
    --judge-execution JUDGE_EXECUTION_GIT_SHA \
    --candidate-b-v2-ended-at END_ISO_WITH_OFFSET \
    --candidate-b-v2-end-record END_RECORD \
    NEW_OUTPUT_DIRECTORY
```

出力には `EVALUATIONS.jsonl`、`STEPS.jsonl`、`SIGN_LEDGER.jsonl`、`RESULT.json`、`INDEPENDENT_CHECK.json`、`MANIFEST.json`、`RESULT_SHA256SUMS.txt`、K1・ビルドの記録を残す。開端は最初の箱の左側と最後の箱の右側だけである。MPFRの生の端点は整数の仮数と二の指数、区間形状は有理数文字列で保存する。

```sh
(cd NEW_OUTPUT_DIRECTORY && sha256sum -c RESULT_SHA256SUMS.txt)
python3 -I -B verify_certificate.py NEW_OUTPUT_DIRECTORY
```

独立検査は計算側を読み込まず、整数平方根と整数比の別式で包み直す。区間の符号と被覆、根幅、$F'$ と回転率の区間、実行時点の記録を点検する。数値の公表と採否はこの記録を監査した後の Judge の工程とする。

## 配置

`cotaxxxx/GeoEnclosure` の `examples/maclaurin-jacobi-bifurcation/` を、単独で展開できる実例の置き場所とする。実例コードと運用の固定版は Codex 専用ブランチで登録する。
