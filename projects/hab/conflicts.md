# 差異・優先順位・未決事項

自動的な文書の優先順位は設定していない。以下のopen項目は、検証結果が緑でも影響要件を合格へ昇格させない。HABコードや既存skillをこの作業で書き換えない。

## C-STATE / open

generic-agent-async-design:107/122はrecipient処理開始、generic-nats-dispatch:7とcurrent APIはcoordinator開始。前者は未実装profile案。どのprofile/scopeでどの意味を公開するかは明示決定が必要。

影響: HAB-008

## C-IDENTITY / open

local-mvp:101/local-relay-host:56の個体専有gateと、relay-auth-groups:52-60の採用済みgroup共有の適用scopeを文書上で整理する必要がある。共有group内のBot本人性は推定しない。

影響: HAB-006

## C-ACK-PROOF / open

既存verify-hab/receive-ack:24-33とSKILLのraw poll→ACKはreceiver commitを観測しない。新しいdurable-live/helperはこのgapを検証するがHAB側の既存recipeはこのsessionで編集していない。

影響: HAB-002

## C-CRASH-CLAIM / open

既存restart-durability:29はkill-9をtest:hab-integrationの範囲とするが、選択testのjourney.restartは同processで正常listener/DB close/reopen。crash proofのsourceとの不一致が残る。

影響: HAB-015

## C-STATUS / open

architecture:7/55などのcurrent固定Task/Relay未実装という記載と後発opt-in Relay/generic実装の時点・subsystemを明示整理する必要がある。古いscopeの設計まで自動廃止しない。

影響: HAB-013

