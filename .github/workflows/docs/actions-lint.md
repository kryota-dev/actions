# actions-lint

> ソースファイル: [`.github/workflows/actions-lint.yml`](../actions-lint.yml)

GitHub Actions ワークフローの品質ゲートを実行する Reusable Workflow です。actionlint、ls-lint、ghalint、zizmor による静的解析を一括で実行します。

## トリガー

`workflow_call`

## Inputs

| 入力名 | 型 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|---|
| `aqua-version` | `string` | 任意 | `v2.56.6` | ghalint 用の aqua バージョン |
| `reviewdog-reporter` | `string` | 任意 | `github-pr-review` | reviewdog/actionlint のレポーター種別（`github-pr-review`, `github-check` 等） |

## Permissions

| 権限 | レベル | 用途 |
|---|---|---|
| `contents` | `read` | リポジトリのチェックアウト |
| `pull-requests` | `write` | reviewdog による PR レビューコメント |

## 前提条件

- リポジトリルートに `.ls-lint.yml` が存在すること（ls-lint の命名規則定義）
- リポジトリルートに `aqua.yaml` が存在すること（ghalint の定義を含む）

## 使用例

```yaml
jobs:
  lint:
    permissions:
      contents: read
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/actions-lint.yml@v1

  # パラメータをカスタマイズする場合
  lint-custom:
    permissions:
      contents: read
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/actions-lint.yml@v1
    with:
      aqua-version: "v2.60.0"
      reviewdog-reporter: "github-check"
```
