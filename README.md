# hirastack

設計書に書いた目的・責務・不変条件を、出典付きの検証契約として残し、変更のたびに確かめるためのスキルです。

agent は設計書を読んで実装を進めますが、しばらくすると設計と実装がずれ、検証は古くなり、「テストは通った」がどの設計を証明したのか分からなくなります。hirastack は、設計書の行と検証を結び付けた契約を対象リポジトリに置き、そのずれを見える形で残します。CLI は意味や優先順位を決めません。設計の解釈は agent と利用者が行います。

[mattpocock/skills](https://github.com/mattpocock/skills) と [pstack](https://github.com/cursor/plugins/tree/main/pstack) と組み合わせて使う前提で作っています。

## 導入（30秒）

plugin は自動で更新されます。skills.sh（`npx skills`）は編集可能なファイルをプロジェクトにコピーし、更新は手で行います。両方入れると同じスキルが二重になるので、agent ごとに一つ選んでください。

### 1. スキルを入れる

<details>
<summary><strong>Claude Code</strong></summary>

```bash
claude plugin marketplace add s-hiraoku/hirastack
claude plugin install hirastack@hirastack
```

公式以外の marketplace は自動更新がオフで始まります。一度だけ `/plugin` の **Marketplaces** タブで `hirastack` を選び、**Enable auto-update** を選んでください。手動なら `claude plugin marketplace update hirastack` のあと `claude plugin update hirastack@hirastack` です。

</details>

<details>
<summary><strong>Codex</strong></summary>

```bash
codex plugin marketplace add s-hiraoku/hirastack
codex plugin add hirastack@hirastack
```

起動時に自動で更新されます。

</details>

<details>
<summary><strong>GitHub Copilot</strong>（CLI と VS Code）</summary>

```bash
copilot plugin marketplace add s-hiraoku/hirastack
copilot plugin install hirastack@hirastack
```

一度だけ、`~/.copilot/settings.json` に次を追加します。

```json
{
  "extraKnownMarketplaces": {
    "hirastack": { "source": { "source": "github", "repo": "s-hiraoku/hirastack" }, "autoUpdate": true }
  }
}
```

VS Code では **Chat: Install Plugin From Source** を実行し、`https://github.com/s-hiraoku/hirastack` を入力します。毎日更新されます。

</details>

<details>
<summary><strong>Gemini CLI</strong>（手動更新）</summary>

```bash
gemini skills install https://github.com/s-hiraoku/hirastack.git --path skills
```

更新するときは同じコマンドを再実行します。

</details>

<details>
<summary><strong>そのほかの agent、または編集可能なファイル</strong>（手動更新）</summary>

```bash
npx skills@latest add s-hiraoku/hirastack -a <agent>  # cursor, opencode, codex など。-a を省くと選択
```

どのスキルを入れるか聞かれたら `setup-hirastack` も含めてください。更新は `npx skills@latest update`、新しいスキルを取り込むには `add` を再実行します。

</details>

plugin は CLI と docs も一緒に入れます。Gemini CLI と skills.sh はスキルのフォルダだけをコピーするので、CLI は `uv`（または `pipx`）経由で commit を固定して起動します。どの方法でも、既存のグローバル設定は変更しません。

### 2. `/setup-hirastack` を実行する

agent の中で、リポジトリごとに一度だけ実行します。次のことをします。

- `hirastack doctor` で Python・Git・`ps` と、open-verified-pr が使う Node・Java・pstack のスキルを確認する（何もインストールしない）
- 既存の検証契約、プロジェクト用 verify スキル、形式検証スキルを探す
- 検証契約を置く場所（既定は `docs/design-verification/`）と CLI の起動方法を聞き、`CLAUDE.md` か `AGENTS.md` の `## hirastack` 節に書く

### 3. これで準備完了

「create-design-verification で、このリポジトリの設計書から検証契約を作って」と頼めば始められます。全設計書を読むので、大きなリポジトリでは時間がかかります。

## なぜこのスキルがあるのか

agent と一緒に開発していて、繰り返し見た失敗を防ぐために作りました。

### #1: 設計書と実装がいつの間にかずれている

**問題**: 設計書には「保存してから ACK を返す」と書いてあるのに、実装はいつの間にか逆になっている。テストは通っているので誰も気付きません。テストが設計書のどの行を確かめているのか、どこにも書かれていないからです。

**解決**: 設計書の目的・責務・不変条件を、行範囲とハッシュ付きの要件として契約にし、それぞれを実際に動かす検証に結び付けます。

- [`create-design-verification`](skills/create-design-verification/SKILL.md): 全設計書を読み、出典付きの契約とプロジェクト用 verify スキルを作って、実際の動作と負例で実証する
- [`verify-design`](skills/verify-design/SKILL.md): 契約の検証を実行し、証拠・失敗・未検証の範囲を報告する

### #2: 設計を変えたのに、検証は古いまま

**問題**: 設計書が更新されても、検証は前の設計を確かめ続けます。逆に、テストを通すために要件のほうを弱めてしまうこともあります。

**解決**: CLI の `audit` は、設計書の追加・削除・引用行の変化を検出し、契約が古いうちは検証を実行しません。ハッシュだけを更新して通す方法はありません。

- [`maintain-design-verification`](skills/maintain-design-verification/SKILL.md): 設計・実装・依存の変化を分類し、要件を弱めずに契約を直す

### #3: PR レビューで状態遷移のバグを見落とす

**問題**: 並行処理や再試行の変更は、差分を読むだけではどの順番で壊れるのか分かりません。形式検証があっても、その結果はレビュアーに届きません。

**解決**: PR が触れる形式検証を最新化して実行し、状態遷移図と、図から見つけたバグ、検証できていない範囲を PR 本文に載せます。

- [`/open-verified-pr`](skills/open-verified-pr/SKILL.md): pstack の statechart で図を描き、TLA+ は [tla-ts](https://github.com/aidenybai/tla-ts) で検査して PR を出す

### #4: 「検証は通った」が何を証明したのか分からない

**問題**: 終了コード 0 は偽装できますし、スキップされたテストも成功に見えます。手動確認が自動の合格に混ざることもあります。

**解決**: CLI はテストランナー自身の集計を読み、空の成功・スキップ・TODO を合格にしません。合格は記録した scope の中だけで、手動の確認は常に未検証として残ります。

### まとめ

hirastack が受け持つのは「設計の意図が、今のコードでも守られているか」を、出典と証拠付きで答えられる状態に保つことです。設計を詰める・実装する・形式モデルを作る作業は、mattpocock/skills と pstack に任せます。段階ごとの使い分けは [docs/workflow.md](docs/workflow.md) にあります。

## リファレンス

スキルは、誰が呼べるかで二つに分かれます。**利用者が呼ぶ**スキルは名前を入力したときだけ動きます。**モデルも呼ぶ**スキルは、作業に合えば agent が自分で使います。

**利用者が呼ぶ**

- **[setup-hirastack](skills/setup-hirastack/SKILL.md)**: リポジトリごとに一度、前提を確認し、検証契約の置き場所と CLI の起動方法を記録する。
- **[open-verified-pr](skills/open-verified-pr/SKILL.md)**: 変更が触れる形式検証を最新化・実行し、状態遷移図とバグレビュー・検証範囲を PR 本文に載せて PR を出す。

**モデルも呼ぶ**

- **[create-design-verification](skills/create-design-verification/SKILL.md)**: 全文書を調査し、設計原則・仕様・検証スキルを生成して実証する。
- **[maintain-design-verification](skills/maintain-design-verification/SKILL.md)**: 設計・実装・検証の変化を分類し、検証資産を保守する。
- **[verify-design](skills/verify-design/SKILL.md)**: 対象の契約と既存 verify スキルを解決し、実行して証拠・不足を報告する。

### 前提

| スキル | 必須 | 場合により必要 |
| --- | --- | --- |
| setup-hirastack、create / maintain-design-verification、verify-design | Python 3.11 以上、Git、POSIX `ps`。plugin 以外で入れた場合は `uv` か `pipx` | 対象の実動検証に必要な runtime とサービス（契約に記載） |
| open-verified-pr | Git、対象プロジェクトが PR 前に求めるチェック、push と PR 作成の権限 | 形式検証がある場合は pstack の statechart と create/maintain-formal-verification-skill（Claude Code では `claude plugin marketplace add cursor/plugins` → `claude plugin install pstack@cursor-plugins`）。TLA+ は Node（tla-ts）、statechart が Java TLC を使う版では Java |

汎用 CLI に追加の Python package は不要です。現在のプロセス管理は macOS/Linux 用で、自分の process group の終了を観測できる実行環境が必要です。観測が拒否された場合は成功とせず scratch を保持します。

### リリース

plugin は `version` が変わったときだけ再インストールされます。利用者に届けたい変更をマージしたら、`.claude-plugin/plugin.json` と `pyproject.toml` の `version` を一緒に上げてください。

### CLI

```sh
# hirastack のルートから。plugin 以外で入れた場合は `python3 -m hirastack` を `uvx --from git+https://github.com/s-hiraoku/hirastack@<commit> hirastack` に置き換える。
# 対象は別の独立 checkout、契約は対象リポジトリ側に置く。
TARGET=/absolute/path/to/project
SPEC="$TARGET/path/to/design-verification/contract.json"
python3 -m hirastack audit --target "$TARGET" --spec "$SPEC"
# まず plan。検証コマンドは起動しない。新しい保存先を毎回指定する。
python3 -m hirastack run --target "$TARGET" --spec "$SPEC" --out /tmp/hirastack-plan-001
# contract.json の argv と副作用・前提を読んだ後に実行。
python3 -m hirastack run --target "$TARGET" --spec "$SPEC" --out /tmp/hirastack-run-001 --execute
```

終了コードは `0=記録された必須scopeをすべて検証`、`1=検証した動作に失敗`、`2=仕様不備・drift・未検証・環境不足・未解決`。`audit: current` は文書の同一性と形式の検査結果で、設計適合の合格ではありません。手動検証は常に未検証として残ります。この版は人の申告だけで合格へ昇格させる機能を持ちません。

プロジェクト固有の原則・文書台帳・契約・helperは、対象リポジトリ（または利用者が選んだ検証用リポジトリ）に置きます。hirastackには対象プロジェクトの文書を持ち込みません。汎用コードに製品名の判定も持ち込みません。

hirastack内の契約は [Python CLIのhirastack自身](projects/hirastack/README.md) だけです。同じengineを自分自身に適用し、特定の対象に依存しない再利用を確認します。[再利用の手順と証拠範囲](docs/reuse.md)も参照してください。

別プロジェクトでは `init` が未レビューの文書索引を作ります。空の requirements は意図的に監査失敗になります。

```sh
python3 -m hirastack init --target /path/to/app --name example --repository https://github.com/owner/example --spec /path/to/verification/contract.json
python3 -m hirastack inventory --target /path/to/app
python3 -m hirastack doctor --target /path/to/app   # 必須ツールが欠けていれば終了コード 2。何もインストールしない
python3 -m unittest discover -s tests -v
```

契約の形式と限界は [contract-format.md](docs/contract-format.md)、設計は [architecture.md](docs/architecture.md)、参考元は [THIRD_PARTY.md](THIRD_PARTY.md) を参照してください。
