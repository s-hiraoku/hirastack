# hirastack

設計書にある目的・責務・不変条件を、出典付きの検証契約として維持するメタスキルと実行ハーネスです。

設計から検証への対応は agent がコードと文書を読んで作ります。CLI は意味や優先順位を決定しません。設計書の追加・変更・削除、引用位置のずれ、未確認の検証、未解決の設計差異を見える形で残します。

| スキル | 役割 |
| --- | --- |
| [create-design-verification](skills/create-design-verification/SKILL.md) | 全文書を調査し、設計原則・仕様・検証スキルを生成して実証する |
| [maintain-design-verification](skills/maintain-design-verification/SKILL.md) | 設計・実装・検証の変化を分類し、検証資産を保守する |
| [verify-design](skills/verify-design/SKILL.md) | 対象の契約と既存 verify スキルを解決し、実行して証拠・不足を報告する |

Python 3.11 以上とGit、POSIX `ps`。汎用 CLI に追加Python packageは不要です。対象プロジェクトの実動検証に必要な runtime は契約に記載します。現在のプロセス管理は macOS/Linux 用で、自分のprocess groupの終了を観測できる実行環境が必要です。観測が拒否された場合は成功とせずscratchを保持します。

```sh
# hirastack のルートから。HAB は別の独立 checkout を使う。
HAB=/absolute/path/to/hiraoku-agent-base
python3 -m hirastack audit --target "$HAB" --spec projects/hab/contract.json
# まず plan。検証コマンドは起動しない。新しい保存先を毎回指定する。
python3 -m hirastack run --target "$HAB" --spec projects/hab/contract.json --out /tmp/hirastack-plan-001
# contract.json の argv と副作用・前提を読んだ後に実行。
python3 -m hirastack run --target "$HAB" --spec projects/hab/contract.json --out /tmp/hirastack-run-001 --execute
```

終了コードは `0=記録された必須scopeをすべて検証`、`1=検証した動作に失敗`、`2=仕様不備・drift・未検証・環境不足・未解決`。`audit: current` は文書の同一性と形式の検査結果で、設計適合の合格ではありません。手動検証は常に未検証として残ります。この版は人の申告だけで合格へ昇格させる機能を持ちません。

初回適用は [HAB](projects/hab/README.md)。90件の first-party 文書、既存 verify スキル9件、第三者方法論16件、補助asset4件を索引化しました。主張は元commitに固定し、汎用コードに HAB や製品名の判定を持ち込みません。HABのコードは変更しません。

第2適用先は [Python CLIのhirastack自身](projects/hirastack/README.md)。同じengineを別契約で実行し、HABやNodeに依存しない再利用を確認します。[再利用の手順と証拠範囲](docs/reuse.md)も参照してください。

別プロジェクトでは `init` が未レビューの文書索引を作ります。空の requirements は意図的に監査失敗になります。

```sh
python3 -m hirastack init --target /path/to/app --name example --repository https://github.com/owner/example --spec /path/to/verification/contract.json
python3 -m hirastack inventory --target /path/to/app
python3 -m unittest discover -s tests -v
```

スキルの利用は、各 `skills/<name>` を利用環境のスキルディレクトリへコピーまたはリンクします。Codex の repo-local は `.agents/skills/`、Claude Code は `.claude/skills/`、Cursor は `.cursor/skills/`。CLI は hirastack のルートから起動し、生成物は別リポジトリに置けます。インストールや既存グローバル設定の変更は自動では行いません。

契約の形式と限界は [contract-format.md](docs/contract-format.md)、設計は [architecture.md](docs/architecture.md)、参考元は [THIRD_PARTY.md](THIRD_PARTY.md) を参照してください。
