# 第2適用先: hirastack自身

Python製の検証CLIを別の対象プロジェクトとして検証する。HABの通信や製品固有helperは使わない。入力契約だけを変え、同じengine/skillで別の言語・責務のプロジェクトへ適用できることを示す。

[contract.json](contract.json) は汎用性、出典drift、未検証の正直な判定、証拠/provenance/owned cleanupの4原則を、汎用runnerの回帰試験へ対応させる。実行時はPython unittestの非空成功とskip/expected failureなしを要求する。実際のCLI create/audit/plan/execute/driftは独立した一時Git repoでも試験する。

```sh
# hirastack root
python3 -m hirastack audit --target "$PWD" --spec projects/hirastack/contract.json
python3 -m hirastack run --target "$PWD" --spec projects/hirastack/contract.json --out "$NEW_RUN_OUTSIDE_CHECKOUT" --execute
```

前提はPython>=3.11、Git、POSIX psと自分のprocess groupを観測できる環境。sandboxがpsを拒否した場合はcleanupを確認できないためblockedになる。これは抑制せず、許可された実行環境で試す。pip install、Node、HAB checkout、NATS、外部サービス、credentialは不要。

このself適用は汎用機構の局所的な契約を検証する。将来の全projectの設計抽出が正しいこと、あらゆるOS、外部toolの副作用や悪意ある任意コードをsandbox化できることは主張しない。原則の意味と検証scopeのレビュー責務は残る。
