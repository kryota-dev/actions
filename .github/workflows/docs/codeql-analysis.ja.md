[English](codeql-analysis.md) | **日本語**

# CodeQL Analysis

CodeQL によるセキュリティスキャンワークフロー

> Source: [`.github/workflows/codeql-analysis.yml`](../codeql-analysis.yml)

## Usage

```yaml
jobs:
  codeql:
    permissions:
      actions: read
      contents: read
      security-events: write
    uses: kryota-dev/actions/.github/workflows/codeql-analysis.yml@v0
    with:
      # languages - 分析対象の言語の JSON 配列
      # Optional (default: '["actions"]')
      languages: '["actions"]'
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `languages` | 分析対象の言語の JSON 配列（例: `'["javascript", "typescript"]'`） | No | `'["actions"]'` |

## Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| `actions` | `read` | CodeQL 分析の実行に必要 |
| `contents` | `read` | リポジトリのチェックアウト |
| `security-events` | `write` | CodeQL 分析結果のアップロード |

## Examples

### 基本的な使い方

```yaml
jobs:
  codeql:
    permissions:
      actions: read
      contents: read
      security-events: write
    uses: kryota-dev/actions/.github/workflows/codeql-analysis.yml@v0
```

### 応用例

```yaml
jobs:
  codeql:
    permissions:
      actions: read
      contents: read
      security-events: write
    uses: kryota-dev/actions/.github/workflows/codeql-analysis.yml@v0
    with:
      languages: '["javascript", "typescript"]'
```

## Behavior

1. `actions/checkout@v6` でリポジトリをチェックアウト（`persist-credentials: false`）
2. `github/codeql-action/init@v4.32.4` で CodeQL を初期化（`languages` は matrix の言語を使用）
3. `github/codeql-action/analyze@v4.32.4` で CodeQL 分析を実行

`languages` input の JSON 配列から matrix strategy により言語ごとにジョブを並列実行する。

<!-- ## Migration Guide -->

<!-- Breaking Changes がある場合にコメントアウトを解除して記載する -->
