# 初回検証の記録

HAB対象commitは`c667095dcd3b0d7c672b522fe3dd45eaeade0c81`。Nodeは対象`.node-version`と同じ24.12.0。lockfile通りに独立checkoutへ依存準備し、trackedファイルは編集していない。実credential、実agent/model、NATS broker、公開・配備を使用していない。

## 実証した範囲

14自動checkが成功。既存Nodeテストは403件、fail/skip/cancel/TODOは0。共通MCP/HTTPの実動proofでは、受信側の別SQLite接続から本文と元ACK journalのcommitを観測してからnetwork ACKを送った。送信側status、同ID再送、inbox再読、owned process停止と証拠存続まで確認した。

| Check | 成功テスト数 / 証拠 |
| --- | --- |
| dependency-boundary | RelayのAST依存graph |
| boundary-controls | 6負例の拒否、comment/stringの偽陽性control |
| mcp-durable-live | trace、独立pre-ACK read、proof、cleanup |
| durable-receive | 19 |
| model-free-supervisor | 8 |
| explicit-task-boundary | 60 |
| current-authorization | 46 |
| immutable-delivery | 37 |
| bounded-replies | 80 |
| attachment-integrity | 61 |
| capacity-fairness | 60 |
| logical-snapshot | 27 |
| shared-application | 5 |
| diagram-source | 正本/画像manifest一致 |

全体は意図どおり`incomplete`（exit2）。手動check5件と未解決差異5件を隠さず、独立して成功した自動checkとは分けている。実受信owner承認、WORKINGの意味決定、kill-9/電断/実認証復旧、実接続/費用、GUIを含む全入口parityは未検証。

## 初回失敗と修正

最初のlive helperは`relay_resolve`の戻りを`agent_id`と誤読した。実APIは`recipient_id`でありhelperだけ修正、再実行した。失敗時もowned scaffoldは正常終了しcleanup証拠が残った。

最初の全runではcurrent-authorizationが1件失敗、logical-snapshotが23件失敗した。前者はCLI stderr完全一致にNodeのExperimentalWarningが混入したため。後者はmacOSの`TMPDIR=/var/...`のsymlink表現を、canonical/private pathを要求するsnapshot契約が拒否したため。製品codeとassertionを変えず、runnerの専用canonical TMPDIRと、該当check限定のExperimentalWarning種別全体の明示抑制で再検証した。全初回ログを保存し、環境条件をreportへ記録する。

独立レビューではTODOを合格にし得るparser、cleanup後のprocess group確認不足、実行後だけのhelper hash取得を指摘・照合した。TODO/不整合countの拒否、group終了確認不能時のscratch保持、runner/helperの実行前後hash比較を実装し、対応する回帰試験を追加した。ps観測を拒否する通常sandboxでの試験はblockedになることを確認し、観測可能な実行環境で再実行した。

## 証拠の保存

生ログは公開しない`.evidence/`配下へ保持する。live初回失敗、初回全run、再実行、最終source版のrunを別dirに保存する。各reportはtarget commit/tree、spec hash、runner/helper前後hash、check log hash、環境上書きとcleanupを記録する。最終runの実パス・commit・hashは引継ぎ結果に記載する。

この結果はHABの旧7feature map全体のlive maintenance、実NATSのP7再受入れ、全製品の承認境界、物理別故障domainの証明ではない。source reviewは119文書/assetすべてを分類して実施したが、外部規格と製品APIの現行版全体まで再確認したとは主張しない。
