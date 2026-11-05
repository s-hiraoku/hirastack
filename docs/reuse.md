# 他プロジェクトへの再利用

hirastackの汎用部分は`hirastack/`と`skills/`。プロジェクト名・製品名・model実行APIへの分岐は持たない。入力は出典付きcontract、対象Git checkout、証拠の新規保存先である。

プロジェクト固有の契約は対象リポジトリ側に置き、hirastackには入れない。hirastack内の唯一の契約はPython CLIのhirastack自身で、[projects/hirastack](../projects/hirastack/README.md) にある。他プロジェクトのprinciples/helper/runtime依存を読み込まず、同じCLIでPython unittestの結果と文書driftを検証する。coreを編集せず契約と検証コマンドだけを変えることを実証する。

さらにgeneric-cliの回帰試験は、`example/app`という別originの一時Gitプロジェクトを作り、initでの索引生成→未レビューdraftの拒否→出典付き契約のaudit→planは未実行→実行成功→設計書変更後のaudit拒否を実CLI経由で行う。このfixtureは他の実サービスの品質や配備の証明ではなく、汎用workflowの再利用証拠である。

新しいプロジェクトに必要なのは次の資産だけである。

1. 全設計資料の台帳とレビュー、目的・責務・不変条件の説明。
2. 適用scope、根拠行とhash、検証への対応を持つ`contract.json`。
3. そのプロジェクト固有の実動recipeと必要なhelper、既存verify skillへの連携。
4. 議論中の設計判断と未検証範囲を残すreport。

```sh
# hirastack root。同じrunner、異なる入力。
python3 -m hirastack run --target "$TARGET" --spec "$TARGET/path/to/design-verification/contract.json" --out "$TARGET_NEW_RUN" --execute
python3 -m hirastack run --target "$HIRASTACK" --spec projects/hirastack/contract.json --out "$SELF_NEW_RUN" --execute
```

スキルはagentの判断を伴うworkflowで、コード生成器が文書の思想を自動確定する仕組みではない。別プロジェクトの規約・実行方法・外部権限はその対象から調査する。ある対象プロジェクトの通信方式や不変条件を、別プロジェクトの必須要件として持ち込まない。
