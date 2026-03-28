[English](cache-cleanup.md) | **日本語**

# Cache Cleanup

古くなった GitHub Actions キャッシュをスケジュール削除する Reusable Workflow

> Source: [`.github/workflows/cache-cleanup.yml`](../cache-cleanup.yml)

## Usage

```yaml
jobs:
  cleanup:
    permissions:
      actions: write
    uses: kryota-dev/actions/.github/workflows/cache-cleanup.yml@v0
    with:
      # max-age-days - キャッシュが削除されるまでの最終アクセスからの最大日数
      # Optional (default: 2)
      max-age-days: 2
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `max-age-days` | キャッシュが削除されるまでの最終アクセスからの最大日数 | No | `2` |

## Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| `actions` | `write` | リポジトリキャッシュの一覧取得と削除 |

## Examples

### 基本的な使い方（毎日スケジュール実行）

```yaml
name: Cache Cleanup
on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch: {}
jobs:
  cleanup:
    permissions:
      actions: write
    uses: kryota-dev/actions/.github/workflows/cache-cleanup.yml@v0
```

### 保持期間をカスタマイズする

```yaml
name: Cache Cleanup
on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch: {}
jobs:
  cleanup:
    permissions:
      actions: write
    uses: kryota-dev/actions/.github/workflows/cache-cleanup.yml@v0
    with:
      max-age-days: 7
```

## Behavior

1. GitHub REST API を使用して、呼び出し元リポジトリの全キャッシュをページネーションで取得する
2. 各キャッシュの `last_accessed_at` をしきい値（`現在時刻 - max-age-days`）と比較する
3. 最終アクセスがしきい値より古いキャッシュをすべて削除する
4. 削除したキャッシュ数をログに出力する

<!-- ## Migration Guide -->

<!-- Breaking Changes がある場合にコメントアウトを解除して記載する -->
