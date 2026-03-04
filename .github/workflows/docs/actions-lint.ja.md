[English](actions-lint.md) | **日本語**

# Actions Lint

GitHub Actions の品質ゲートワークフロー

> Source: [`.github/workflows/actions-lint.yml`](../actions-lint.yml)

## Usage

```yaml
jobs:
  lint:
    permissions:
      contents: read
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/actions-lint.yml@v1
    with:
      # aqua-version - ghalint 用にインストールする aqua のバージョン
      # Optional (default: 'v2.56.6')
      aqua-version: 'v2.56.6'

      # reviewdog-reporter - reviewdog/actionlint のレポータータイプ
      # Optional (default: 'github-pr-review')
      reviewdog-reporter: 'github-pr-review'
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `aqua-version` | ghalint 用にインストールする aqua のバージョン | No | `'v2.56.6'` |
| `reviewdog-reporter` | reviewdog/actionlint のレポータータイプ（github-pr-review, github-check 等） | No | `'github-pr-review'` |

## Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| `contents` | `read` | リポジトリのチェックアウトおよび zizmor による静的解析 |
| `pull-requests` | `write` | reviewdog による PR レビューコメントの投稿 |

## Examples

### 基本的な使い方

```yaml
jobs:
  lint:
    permissions:
      contents: read
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/actions-lint.yml@v1
```

### 応用例

```yaml
jobs:
  lint:
    permissions:
      contents: read
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/actions-lint.yml@v1
    with:
      aqua-version: 'v2.56.6'
      reviewdog-reporter: 'github-check'
```

## Behavior

1. `actions/checkout@v6` でリポジトリをチェックアウト（`persist-credentials: false`）
2. `reviewdog/action-actionlint@v1.71.0` で actionlint を実行（レポーターは `reviewdog-reporter` input で指定）
3. `ls-lint/action@v2.3.1` でファイル命名規則をチェック
4. `aquaproj/aqua-installer@v4.0.4` で aqua をインストール（バージョンは `aqua-version` input で指定）
5. aqua の bin パスを `$GITHUB_PATH` に追加
6. `ghalint run` でワークフロー lint を実行
7. `ghalint run-action` で Composite Action lint を実行
8. `astral-sh/setup-uv@v7.3.1` で uv をセットアップ
9. `uvx zizmor --format=github .` で静的セキュリティ分析を実行（`secrets.GITHUB_TOKEN` を `GH_TOKEN` として使用）

<!-- ## Migration Guide -->

<!-- Breaking Changes がある場合にコメントアウトを解除して記載する -->
