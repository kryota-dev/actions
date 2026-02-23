# Workflows

## Reusable Workflows

| ワークフロー | 説明 |
|---|---|
| [actions-lint](docs/actions-lint.md) | GitHub Actions の品質ゲート（actionlint / ls-lint / ghalint / zizmor） |
| [auto-assign-pr](docs/auto-assign-pr.md) | PR 作成者の自動 assignee 設定 |
| [codeql-analysis](docs/codeql-analysis.md) | CodeQL セキュリティスキャン |
| [tagpr-release](docs/tagpr-release.md) | tagpr リリース管理とメジャータグ更新 |

## 使い方

他のリポジトリから Reusable Workflow を呼び出す場合:

```yaml
jobs:
  example:
    uses: kryota-dev/actions/.github/workflows/{workflow}.yml@v1
    with:
      # inputs
    secrets:
      # secrets
```

各ワークフローの inputs / secrets / permissions の詳細は上記リンク先のドキュメントを参照してください。

## Internal CI Workflows

このリポジトリ自身の品質管理に使用する内部 CI ワークフロー（`my-` プレフィックス）です。各 Reusable Workflow を呼び出す薄いラッパーとして実装されています。

| ワークフロー | トリガー | 呼び出し先 | 説明 |
|---|---|---|---|
| my-test.yml | PR, merge_group | actions-lint.yml | 品質ゲート |
| my-setup-pr.yml | PR opened | auto-assign-pr.yml | 自動 assignee |
| my-release.yml | push (main) | tagpr-release.yml | リリース管理 |
| my-codeql.yml | PR, push (main), merge_group | codeql-analysis.yml | セキュリティスキャン |
