# codeql-analysis

> ソースファイル: [`.github/workflows/codeql-analysis.yml`](../codeql-analysis.yml)

CodeQL によるセキュリティスキャンを実行する Reusable Workflow です。指定された言語に対して静的解析を行い、脆弱性を検出します。

## トリガー

`workflow_call`

## Inputs

| 入力名 | 型 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|---|
| `languages` | `string` | 任意 | `'["actions"]'` | スキャン対象言語の JSON 配列（例: `'["javascript", "typescript"]'`） |

## Permissions

| 権限 | レベル | 用途 |
|---|---|---|
| `actions` | `read` | ワークフロー情報の読み取り |
| `contents` | `read` | リポジトリのチェックアウト |
| `security-events` | `write` | セキュリティアラートの書き込み |

## 前提条件

- リポジトリで GitHub Advanced Security が有効であること（public リポジトリではデフォルトで有効）

## 使用例

```yaml
jobs:
  codeql:
    permissions:
      actions: read
      contents: read
      security-events: write
    uses: kryota-dev/actions/.github/workflows/codeql-analysis.yml@v1

  # 言語を指定する場合
  codeql-js:
    permissions:
      actions: read
      contents: read
      security-events: write
    uses: kryota-dev/actions/.github/workflows/codeql-analysis.yml@v1
    with:
      languages: '["javascript", "typescript"]'
```
