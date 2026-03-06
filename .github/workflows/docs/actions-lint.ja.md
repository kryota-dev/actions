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
    uses: kryota-dev/actions/.github/workflows/actions-lint.yml@v0
    with:
      # reviewdog-reporter - actionlint のレポータータイプ
      # Optional (default: 'github-pr-review')
      reviewdog-reporter: 'github-pr-review'
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `reviewdog-reporter` | actionlint のレポータータイプ（github-pr-review, github-check 等） | No | `'github-pr-review'` |
| `actionlint-config` | actionlint 設定ファイルのパス（デフォルト: `.github/actionlint.yaml` または `.github/actionlint.yml`） | No | `''` |
| `ls-lint-config` | ls-lint 設定ファイルのパス（デフォルト: `.ls-lint.yml` があればそれを使用、なければ内蔵デフォルト） | No | `''` |
| `ghalint-config` | ghalint 設定ファイルのパス（デフォルト: `{.github/,.,}ghalint.{yaml,yml}`） | No | `''` |
| `zizmor-config` | zizmor 設定ファイルのパス（デフォルト: `.github/zizmor.yml` または `zizmor.yml`） | No | `''` |
| `skip-actionlint` | actionlint をスキップ | No | `false` |
| `skip-ls-lint` | ls-lint をスキップ | No | `false` |
| `skip-ghalint` | ghalint をスキップ | No | `false` |
| `skip-zizmor` | zizmor をスキップ | No | `false` |

## Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| `contents` | `read` | リポジトリのチェックアウトおよび zizmor による静的解析 |
| `pull-requests` | `write` | reviewdog による PR レビューコメントの投稿 |

## Examples

### 基本的な使い方（設定ファイル不要）

```yaml
jobs:
  lint:
    permissions:
      contents: read
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/actions-lint.yml@v0
```

### カスタマイズ例

```yaml
jobs:
  lint:
    permissions:
      contents: read
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/actions-lint.yml@v0
    with:
      reviewdog-reporter: 'github-check'
      ls-lint-config: '.custom-ls-lint.yml'
      ghalint-config: '.ghalint.yaml'
      skip-zizmor: true
```

## Behavior

1. `actions/checkout@v6` でリポジトリをチェックアウト（`persist-credentials: false`）
2. `aquaproj/aqua-installer@v4.0.4` で aqua をインストール
3. 動的に生成した aqua 設定で全 lint ツール（actionlint, reviewdog, ls-lint, ghalint, zizmor）をセットアップ — caller 側の `aqua.yaml` は不要
4. aqua の bin パスを `$GITHUB_PATH` に追加
5. actionlint を実行し、結果を reviewdog にパイプ（レポーターは `reviewdog-reporter` input で指定）。`actionlint-config` が指定されている場合は `-config-file` フラグで設定ファイルを使用、未指定時は `.github/actionlint.yaml` または `.github/actionlint.yml` を検索
6. ls-lint の設定を3段階フォールバックで準備: `ls-lint-config` input → caller の `.ls-lint.yml` → 内蔵デフォルト設定（`.github/workflows` と `.github/actions` の kebab-case ルール）
7. 解決された設定で ls-lint を実行
8. `ghalint run` でワークフロー lint を実行。`ghalint-config` が指定されている場合は `-c` フラグで設定ファイルを使用、未指定時は `ghalint.yaml`, `.ghalint.yaml`, `.github/ghalint.yaml`（および `.yml` 拡張子）を検索
9. `ghalint run-action` で Composite Action lint を実行
10. `zizmor --format github` で静的セキュリティ分析を実行（`github.token` を `GH_TOKEN` として使用）。`zizmor-config` が指定されている場合は `--config` フラグで設定ファイルを使用、未指定時は `.github/zizmor.yml` または `zizmor.yml` を検索

## Migration Guide

### 破壊的変更

| 変更 | 影響 | 移行方法 |
|------|------|---------|
| `aqua-version` input 削除 | この input を指定していた caller はエラーになる | ワークフローから `aqua-version` input を削除 |
| GitHub Actions → CLI 直接実行に変更 | 出力形式が微妙に変わる可能性 | 対応不要 — CLI で同等の出力を生成 |

### 移行手順

1. `aqua-version` input を指定している場合は削除
2. ghalint のためだけに配置していた caller 側の `aqua.yaml` を削除（不要になった）
3. デフォルトの kebab-case ルールのみ記述していた caller 側の `.ls-lint.yml` を削除（内蔵デフォルトで対応）
4. 必要に応じて skip や config の input を追加し、きめ細かな制御が可能
