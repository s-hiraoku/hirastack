# 解釈と検証の限界

このsessionは既存verify-habのsource reviewを分担して実施し、実動操作はcoordinatorが独立checkoutで行った。HAB本体・元の検証skillは編集していない。

## 矛盾と誤認しないscope差

- 基本Relay4 tool、HAB5 tool、任意`hab_discover`追加は異なるcatalog。全入口を「必ず5個」と判定しない。出典: [hab-relay-spec:434](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/hab-relay-spec.md#L434)、[mcp-agent-discovery:8](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/mcp-agent-discovery.md#L8)。
- 旧固定Task用Hermes Runsと共通MCP通信は別の任意経路。旧driverの存在だけで通信境界違反としない。出典: [common-mcp-connection:3](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/common-mcp-connection.md#L3)、[hermes-connection:3](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/hermes-connection.md#L3)。
- 元のaddress不変とopt-in v3 rename prototype、個体1対1互換とgroup共有mode、有限試験cleanupと常用設定保持はmode/版が違う。新しい実装の存在を本番採用の決定にしない。
- HubのJWKS fetch/cacheとRelayの公開鍵pinはsubsystem差。統合してどちらかを「誤り」としない。
- 歴史的exact-f19 delivery-labは現在compositeを意図的に拒否する。guardを緩めて現在sourceを合格させない。current P7選択は [publication.md](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/testing/publication.md) と実workflowで確認する。履歴を持たないshallow cloneのpin生成は別途未検証。
- 古いcapacity/fairness/attachment文書の「次の実装」には後発opt-in実装との時点差がある。「別層」という語は未実装の証明ではない。保守時は実際のsourceとversionを照合する。

## 確認した検証gap

- [receive-ack:24–33](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/.claude/skills/verify-hab/features/receive-ack.md#L24) はpoll JSONから直接ACKを送る。wireのlease/ACKを検証できるがreceiver durable commitの証拠を持たない。本適用のmcp-durable-liveは別SQLite接続で本文と元ACK journalを確認する。
- [restart-durability:29](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/.claude/skills/verify-hab/features/restart-durability.md#L29) のkill-9 claimに対し、選択suiteの [journey.restart:176–182](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/test/hab-journey-fixtures.js#L176) は正常close/reopen。crash proofに昇格できない。
- enrollment-terminalのtmux recipeは子shellで`$S`を使うがmain skillはexportしていない。単独copy/pasteでは`/_node.sh`へ解決し得る。既存featureのlive実行を行うときはexport済み絶対pathを使い、元recipe修正はHAB担当へ別報告する。
- WORKINGは [generic-agent-async-design:102–107](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/generic-agent-async-design.md#L102) の未実装profile案ではrecipient処理中。current [generic-nats-dispatch:7](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/implementation/generic-nats-dispatch.md#L7) はcoordinator開始。`src/store.ts:426` → `src/generic-jobs.ts:138–151` → `src/a2a/generic-handler.ts:66–90`でAPIへ投影される。両scopeの意味決定を自動では行わない。

## 偽陽性・見逃しの扱い

AST checkはimport/export/require/import typeを構文で読む。コメントと普通の文字列にある製品名は違反にしない。coreからの直接・間接HAB/Task/製品SDK依存は負例で拒否する。許可した共有module/packageを増やす場合は理由付きでreviewする。

計算したdynamic importは証明不能としてcheckを止めるため、合法な新しいloaderでも保守が必要になる。reflection、aliasされたrequire、生成コード、npm package内部、hostから注入したcallback内のmodel起動はASTだけでは検出できない。実製品のtool/承認経路も別の手動試験が必要。

Node TAPは非空のpass/fail/skip/cancel合計を確認する。exit 0だけ、skip、ゼロtestは成功にしない。ただし悪意ある出力や意味の弱いassertionは信頼できるソースレビューが必要。一般的な`exit` protocolはscript自身のassertion設計に依存する。

文書hashはdriftを止めるが、意図を自動抽出した証明ではない。対象のignoredファイル・依存物・runtime binaryはtree digest外。新たな外部仕様/PDF/wiki/非標準拡張子はcreate/maintainで再探索する。今回の外部A2A/NATS/製品API原典の現行版まで再検証したとは主張しない。
