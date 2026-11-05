# HAB 設計原則

抽出対象commit: `c667095dcd3b0d7c672b522fe3dd45eaeade0c81`。全first-party文書をsource reviewした結果。採用・提案・未決を混同せず、検証範囲は各scopeに限定する。

## 根本の目的

異なるagentが標準MCPを使って通信でき、各agentが判断・記憶・実行権限を保持する。HABは配送の永続性と相関・認可を担う。製品固有model実行を通信の必須条件にしない。

## HAB-001 共通MCPと製品非依存の通信

Relay core/clientはTask engineや製品のモデル実行APIに依存せず、各agentの標準MCPから通信できる。

理由: 配送のために受信製品の実行を中央へ移すことを防ぐ。

決定区分: `accepted`。検証scope: src/relayの静的module境界と合成MCP/HTTP通信

出典: [docs/common-mcp-connection.md:3](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/common-mcp-connection.md#L3-L6), [docs/hab-relay-spec.md:76](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/hab-relay-spec.md#L76-L97)

検証: `dependency-boundary`, `boundary-controls`, `mcp-durable-live`

## HAB-002 保存・dedup・元ACK journalがACKより先

受信側は本文とdedup、再送用ACK要求を永続commitしてからACKし、応答消失時も元ACKを照合する。

理由: Relay本文解放後の消失や二重受信を防ぐ。

決定区分: `accepted`。検証scope: common SQLiteInbox/DurableReceiverとreal loopback MCP

出典: [docs/common-mcp-connection.md:47](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/common-mcp-connection.md#L47-L61), [docs/hab-relay-spec.md:263](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/hab-relay-spec.md#L263-L269)

検証: `mcp-durable-live`, `durable-receive`

## HAB-003 model-free定期受信

receive supervisorはpoll・保存・ACKだけを担い、判断・返信・Task引受け・model起動は受信側の別処理にする。

理由: 継続通信にLLM起動やTask engineを必須としない。

決定区分: `accepted`。検証scope: 合成waitを用いたReceiveSupervisorとdurable host

出典: [docs/receive-supervisor.md:5](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/receive-supervisor.md#L5-L15), [docs/receive-supervisor.md:36](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/receive-supervisor.md#L36-L52)

検証: `model-free-supervisor`

## HAB-004 通信許可と実行引受けの分離

ACKや本文を根拠にTaskを作らず、任意bridgeは別の明示accept/submitと認可を必要とする。

理由: 普通のmessage配送を自動仕事実行へ昇格させない。

決定区分: `accepted`。検証scope: 固定Task bridge/AdapterHostの合成storageとHTTP

出典: [docs/task-bridge.md:5](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/task-bridge.md#L5-L17), [docs/hab-product-spec.md:43](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/hab-product-spec.md#L43-L47)

検証: `explicit-task-boundary`

## HAB-005 実受信側に判断とowner承認を残す

外部本文・ROLE_USER・同group・送信者の承認を受信ownerの保護対象操作承認に代用しない。

理由: 通信の認証がshell/個人データ/外部送信の包括権限になることを防ぐ。

決定区分: `accepted`。検証scope: 実製品の実効tool/owner approval経路（未検証）

出典: [docs/generic-agent-async-design.md:75](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/generic-agent-async-design.md#L75-L86), [docs/hab-principles.md:7](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/hab-principles.md#L7-L15)

検証: `real-recipient-policy`

## HAB-006 現在の認証・group・名義scope

権限は検証済み主体と現在policyで決まり、引数の名前では得られない。同group共有とforeign-group拒否を区別する。

理由: 認証・登録・Bot名・実Bot本人性を混同しない。

決定区分: `accepted`。検証scope: Registry/group opt-inと合成MCP/admin。旧個体専有文言のscopeは未整理。

出典: [docs/relay-auth-groups.md:23](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/relay-auth-groups.md#L23-L29), [docs/relay-auth-groups.md:52](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/relay-auth-groups.md#L52-L60), [docs/local-mvp.md:97](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/local-mvp.md#L97-L103)

検証: `current-authorization`

## HAB-007 元intentと期限の維持

宛先ID/本文/message ID/初回期限を再送前に保存し、不明応答で別ID再送や期限延長をしない。

理由: at-least-once配送を二重依頼や別宛先転送にしない。

決定区分: `accepted`。検証scope: Relay contract/store/senderの合成故障注入

出典: [docs/hab-relay-spec.md:233](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/hab-relay-spec.md#L233-L239), [docs/hab-relay-spec.md:378](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/hab-relay-spec.md#L378-L386), [docs/generic-agent-async-design.md:141](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/generic-agent-async-design.md#L141-L153)

検証: `immutable-delivery`

## HAB-008 配送・表示・作業・停止の証拠を分ける

保存ACKを既読/実行/完了にせず、workingや取消状態はそのscopeの確認済み証拠に対応させる。

理由: transport handleやcoordinator開始を受信runtime処理の証拠へ誤昇格しない。

決定区分: `unresolved`。検証scope: WORKING proposalとcurrent projectionの意味差異は未解決。

出典: [docs/generic-agent-async-design.md:94](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/generic-agent-async-design.md#L94-L107), [docs/implementation/generic-nats-dispatch.md:3](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/implementation/generic-nats-dispatch.md#L3-L11), [docs/profiles/async-text-v1.md:38](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/profiles/async-text-v1.md#L38-L42)

検証: `state-semantics`

## HAB-009 未知結果と未終了実行の保守的保持

timeout/local abort/cancel要求でremote停止や副作用ゼロを推定せず、receipt/slot/元identityを保持し照合する。

理由: 応答消失からの二重副作用と不正slot解放を防ぐ。

決定区分: `accepted`。検証scope: AdapterHost/bridge/senderの合成境界

出典: [docs/adapter-host.md:51](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/adapter-host.md#L51-L59), [docs/hab-workflow.md:42](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/hab-workflow.md#L42-L48), [docs/generic-agent-async-design.md:157](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/generic-agent-async-design.md#L157-L165)

検証: `explicit-task-boundary`, `immutable-delivery`

## HAB-010 有限返信と連鎖抑止

返信は受信側の明示判断と永続intent/budgetに従い、ACK/結果/通知から新Taskや無制限返信を自動生成しない。

理由: 別ID/threadによるloop/費用増殖を防ぐ。

決定区分: `accepted`。検証scope: 回答intentとreply budgetの合成呼出し。全実adapter入口は未確認。

出典: [docs/adapter-reply-budget.md:15](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/adapter-reply-budget.md#L15-L36), [docs/answer-intents.md:20](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/answer-intents.md#L20-L34), [docs/answer-intents.md:46](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/answer-intents.md#L46-L46)

検証: `bounded-replies`, `explicit-task-boundary`

## HAB-011 添付の検証と受信durability

添付はboundedな全長/digest確認を終えてからbody/ACKを保存し、server削除とreceiver copy管理を分ける。

理由: 不完全byteや未検証contentで保存ACKを返さない。

決定区分: `accepted`。検証scope: 任意添付layerの合成SQLite/checkpoint

出典: [docs/attachment-inbox.md:17](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/attachment-inbox.md#L17-L35), [docs/attachment-receiver.md:14](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/attachment-receiver.md#L14-L36)

検証: `attachment-integrity`

## HAB-012 有限容量と公平性の限定

宣言byteとrecordを原子的に予約し、受理済み状態を追い出さず有限retry/選択機会/slotを管理する。

理由: 過負荷から権限緩和・データ喪失・無制限workを起こさない。

決定区分: `accepted`。検証scope: 同一policy下の合成capacity/fair-poll/writer admission。SLOは対象外。

出典: [docs/attachment-capacity.md:12](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/attachment-capacity.md#L12-L24), [docs/relay-agent-capacity.md:11](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/relay-agent-capacity.md#L11-L25), [docs/writer-admission.md:17](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/writer-admission.md#L17-L31)

検証: `attachment-integrity`, `capacity-fairness`

## HAB-013 正本と復旧receiptを分ける

単一Task正本とtransactional mutation/audit/outboxを維持し、通信・Mac journalを第二Task engineにしない。

理由: 不整合な重複state machineと権限の二重管理を防ぐ。

決定区分: `accepted`。検証scope: 既存Task bridge/共通TaskServiceの合成integration

出典: [docs/architecture.md:17](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/architecture.md#L17-L21), [docs/implementation/generic-job-application.md:3](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/implementation/generic-job-application.md#L3-L9)

検証: `shared-application`, `explicit-task-boundary`

## HAB-014 論理snapshotと権限の分離

snapshotは明示した完全profileとwriter lockで作り、fresh offline restore後も現在権限・外部結果の照合を要する。

理由: 古いbackupで承認や副作用を未実行へ巻き戻さない。

決定区分: `accepted`。検証scope: helperの限定profileによる論理snapshot/restore

出典: [docs/sqlite-snapshot-bundle.md:7](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/sqlite-snapshot-bundle.md#L7-L17), [docs/sqlite-snapshot-bundle.md:33](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/sqlite-snapshot-bundle.md#L33-L43)

検証: `logical-snapshot`

## HAB-015 crashと実運用復旧は別証拠

clean close/reopenをkill-9/電断/実認証復元/別故障domain restoreの証明として報告しない。

理由: 検証範囲を越えた耐障害性の主張を防ぐ。

決定区分: `accepted`。検証scope: crash/実運用復旧は未実行。既存feature mapの過大claimを記録。

出典: [docs/testing/p7-lab.md:38](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/testing/p7-lab.md#L38-L46), [.claude/skills/verify-hab/features/restart-durability.md:25](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/.claude/skills/verify-hab/features/restart-durability.md#L25-L29)

検証: `crash-and-production-recovery`

## HAB-016 共通application serviceと入口同等性

同じ主体・権限・対象・入力は入口に依存せず同じ認可/冪等/状態を使う。GUIの直接DB別経路を作らない。

理由: UIごとの実行権限や状態の分岐を防ぐ。

決定区分: `accepted`。検証scope: A2A/MCP合成境界は自動確認。GUIと全入口同等性は未検証。

出典: [docs/hab-product-spec.md:11](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/hab-product-spec.md#L11-L17), [docs/profiles/async-text-v1.md:28](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/profiles/async-text-v1.md#L28-L38)

検証: `shared-application`, `full-surface-parity`

## HAB-017 証拠範囲と配備・費用の分離

設計採用/source成功/local fixtureを本番接続・owner承認・課金・常駐・公開成功へ昇格しない。

理由: 利用者が未確認の接続能力や費用を信頼してしまうことを防ぐ。

決定区分: `accepted`。検証scope: 実接続/本番/費用/常駐はこの適用の対象外で未検証。

出典: [docs/hab-decisions.md:5](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/hab-decisions.md#L5-L5), [docs/common-mcp-connection.md:106](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/common-mcp-connection.md#L106-L122), [docs/hab-security.md:35](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/hab-security.md#L35-L37)

検証: `deployment-and-cost`

## HAB-018 図の単一正本

Markdown Mermaidを正本とし、生成画像とmanifestを一致させる。

理由: 図ごとの独立管理による設計statusの分岐を防ぐ。

決定区分: `accepted`。検証scope: 既存source/image manifest整合性

出典: [docs/hab-topology.md:5](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/hab-topology.md#L5-L5), [docs/hab-topology.md:65](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/hab-topology.md#L65-L75)

検証: `diagram-source`

## HAB-019 受信owner承認profileの将来拡張

受信owner承認は独立した認証経路・操作hash・期限・現在権限に結び付ける。

理由: 送信者へowner承認を委譲せず古い承認の再利用を防ぐ。

決定区分: `proposed`。検証scope: 未実装HAB profile案。現在実装済みとは扱わない。

出典: [docs/generic-agent-async-design.md:102](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/generic-agent-async-design.md#L102-L117), [docs/generic-agent-async-design.md:226](https://github.com/s-hiraoku/hiraoku-agent-base/blob/c667095dcd3b0d7c672b522fe3dd45eaeade0c81/docs/generic-agent-async-design.md#L226-L231)

検証: `real-recipient-policy`

