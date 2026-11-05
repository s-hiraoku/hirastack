# Contract v1

契約はUTF-8 JSON。実例は [hirastack自身の契約](../projects/hirastack/contract.json)。`python3 -m hirastack audit` が形式と出典を検査します。必須fieldは CLI の `validate()` が正本です。

| Field | 内容 |
| --- | --- |
| `version` | `1` |
| `project` | `name`, `repository`（originとの一致）, `baseline`（抽出時commit） |
| `documents` | `path`, `sha256`, `role`, `review`, `summary`。excludedには`exclusion_reason`必須 |
| `requirements` | `id`, `title`, `statement`, `rationale`, `scope`, `decision`, `citations`, `checks` |
| `citations[]` | 文書`path`、1始まりinclusiveの`start/end`、その行範囲のUTF-8 bytesの`excerpt_sha256` |
| `checks` | 一意ID、`kind`（command/manual）、`tier`、`proves`、`limitations` |
| command | `argv`配列、target相対`cwd`、`timeout_seconds`（1–3600）、`protocol`（下の表）。`junit-xml`/`jest-json`は`report`（`{evidence}/`配下のpath）が必須。任意`env`は明示的な環境変数上書きmap |
| manual | `instructions`。runnerは実行済みと推測せずunverifiedを返す |
| `conflicts` | 一意ID、`status`（open/resolved）、`question`、影響する`requirements`。resolvedは`resolution`必須 |

`role` はnormative/context/evidence/excluded。`review`はpending/reviewed。文書の主張をnormativeと認める判断はagentのレビュー責務です。全fileにsummaryを要求しますが、要約の妥当性をCLIが証明するわけではありません。

`decision` はaccepted/proposed/unresolved/historical。acceptedとunresolvedを必須範囲に含めます。unresolvedはcheckが緑でもblocked。proposed/historicalはnot-enforcedと表示します。この除外は意味のある決定なので、変更時は根拠とレビューを残します。

argvの `{target}` はtarget root、`{bundle}`はcontract所在dir、`{evidence}`は今回の新規run dirへ置換します。shell展開や環境変数展開はしません。`cwd`はtarget内に限定します。対象の追跡対象と衝突しないよう、evidenceはtarget外に置きます。

commandごとにcanonicalな専用scratch dirを作り、`TMPDIR`として渡して終了後に削除します。macOSの`/var`等のsymlink表現を厳密なstorageが拒否する問題を避けます。`env`の上書きもreportへ記録します。警告の抑制などで環境を上書きする場合は、その範囲を`limitations`に書き、元の未抑制失敗も証拠として保存します。

文書探索はGit管理下およびignoreされていないuntrackedのMarkdown/MDX/RST/AsciiDoc/txtと、`docs/`配下の非画像・非PDF assetを含みます。PDF/画像、wiki、issue、外部参照、別名の設計ディレクトリにある非text assetは自動では読みません。create/maintainで追加調査し、必要なら明示的にdocumentsへ登録する前に探索policyを対応させます。重要設計をignoreしたり別拡張子へ隠したりしてscopeを狭めてはいけません。

source変更はaudit失敗→再読・再分類・引用修正→再検証の順に扱います。hashは変更検知であり、承認・署名や文書の真実性の証明ではありません。runnerはcheck間・全体の依存環境snapshotや秘密のredactionを自動では行いません。report/logは公開前に確認してください。

## Assertion protocol

テストランナー自身の集計を読むprotocolを優先します。exit 0だけでは「0件実行」や「全件skip」を見抜けません。

| protocol | 読む結果 | 代表的な使い方 |
| --- | --- | --- |
| `node-tap` | 出力のTAP合計 | `node --test --test-reporter=tap` |
| `python-unittest` | `Ran N tests`と単独の`OK` | `python -m unittest` |
| `junit-xml` | `report`のXML（ファイル、またはその配下の`*.xml`全部）の`testcase`要素 | pytest `--junitxml={evidence}/r.xml`、Maven `-Dsurefire.reportsDirectory={evidence}/r`、PHPUnit `--log-junit`、Vitestのjunit reporter、Go `gotestsum --junitfile`、Rust `cargo nextest`のJUnit出力、.NETのJUnit logger |
| `jest-json` | `report`のJSONの`assertionResults` | Jest `--json --outputFile={evidence}/r.json`、Vitest `--reporter=json --outputFile={evidence}/r.json` |
| `go-test-json` | 出力の`go test -json`イベント（サブテストも1件と数える） | `go test -json ./...` |
| `cargo-test` | 出力の`test result:`行（test binaryとdoctestを合算） | `cargo test` |
| `exit` | 終了コードのみ | 上記で読めない場合だけ。scriptのassertion設計に依存する |

全protocol共通の判定: 失敗が1件でもあれば`fail`（exit 0でも）。成功0件・集計なし・集計の不整合・レポート未生成は`blocked`。skip/pending/todo/ignored、Goのtest fileなしpackage、unittestのskip/expected failureは`unverified`。cargoの`filtered out`はargvでの明示的な選択として扱い、減点しない。

`report`は毎回新規の`{evidence}`配下に限定し、前回のレポートや対象checkout内の古いファイルを読まないようにします。JUnit XMLはsuiteの集計属性ではなく`testcase`要素を数え、suite直下の`error`/`failure`（収集・setup失敗）も失敗に数えます。Jest/VitestはnumTotalTestsと個別結果の一致を要求し、読み込みに失敗したsuiteを失敗に数えます。いずれも「そのテストが要件を証明するか」は判定しません。
