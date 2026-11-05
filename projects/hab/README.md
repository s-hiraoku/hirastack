# HAB への初回適用

対象は [s-hiraoku/hiraoku-agent-base](https://github.com/s-hiraoku/hiraoku-agent-base)、抽出基準は `c667095dcd3b0d7c672b522fe3dd45eaeade0c81`。並行修正から独立した参照checkoutを使用し、HABのtrackedファイルは編集していません。

| 資産 | 内容 |
| --- | --- |
| [design-principles.md](design-principles.md) | 目的・責務・不変条件19件と出典・scope |
| [document-review.md](document-review.md) | first-party90文書、verify9、第三者方法論16、補助asset4の台帳 |
| [contract.json](contract.json) | hash付き出典、要件、14自動check、5手動check、未解決5件 |
| [conflicts.md](conflicts.md) | 意味・scope・検証claimの差異と未決事項 |
| [review-notes.md](review-notes.md) | 差異の分類、偽陽性・残る限界 |
| [verify-hab-design](skills/verify-hab-design/SKILL.md) | この適用のLaunch/Doctor/Drive/Evidence/Cleanupとfeature map |
| [validation.md](validation.md) | 実行した結果・初回失敗・未検証範囲 |

HAB の核心は標準MCPによる共通通信、受信側のmodel-free poll・durable保存後ACK、受信側に残る判断・実行承認です。任意の旧固定Hermes Runs driverが存在することから、共通通信がそのdriverへ依存すると推定してはいけません。逆にgeneric通信へ製品実行依存が入り込むことは静的境界checkと実動proofで検出します。

HABの既存 `.claude/skills/verify-hab` は7つのpublic featureを持ちます。この適用の5featureは設計不変条件の追加検証で、既存7feature全体のlive maintenanceを完了したという主張ではありません。既存featureのsource照合は行いました。実製品接続・承認・本番認証・crash/power-loss・GUI parityは未検証のままです。

実行前提はNode >=24とlockfile通りの依存準備。隔離checkoutで `npm ci --no-audit --no-fund` を行ってください。NATS server、実credential、既存agent、常駐serviceは今回の14自動checkに不要です。実NATS brokerのsource-pinned P7試験は別scopeとして維持し、この小さなハーネスで置換しません。

```sh
# hirastack root
python3 -m hirastack audit --target "$HAB" --spec projects/hab/contract.json
python3 -m hirastack run --target "$HAB" --spec projects/hab/contract.json --out "$NEW_RUN" --execute
```

現契約の全体結果は、手動要件と未解決差異があるため `incomplete` になる設計です。自動checkが全て通ってもその事実を隠しません。並行修正後のcheckoutで設計文書が変わった場合は、maintain-design-verificationで出典とscopeを再読してから新しいrunを実行します。
