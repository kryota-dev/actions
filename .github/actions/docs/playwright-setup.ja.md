[English](playwright-setup.md) | **日本語**

# playwright-setup

Playwright ブラウザのセットアップをキャッシュ付きで行う Composite Action。

> Source: [`.github/actions/playwright-setup/action.yml`](../playwright-setup/action.yml)

## Usage

```yaml
- uses: kryota-dev/actions/.github/actions/playwright-setup@v1
```

## Inputs

None

## Examples

### 基本的な使い方

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: kryota-dev/actions/.github/actions/pnpm-setup@v1
  - uses: kryota-dev/actions/.github/actions/playwright-setup@v1
```

## Behavior

1. `pnpm exec playwright --version` を実行して Playwright のバージョンを取得する（`sed 's/Version //'` でパース）
2. `actions/cache@v5.0.3` を使用して Playwright ブラウザをキャッシュする（パス: `~/.cache/ms-playwright`、キー: `{os}-playwright-{version}`）
3. キャッシュヒットしなかった場合のみ `pnpm exec playwright install --with-deps` を実行してブラウザをインストールする

## Prerequisites

- `pnpm-setup` アクションが事前に実行されていること（`pnpm exec` を使用するため）
- プロジェクトの依存関係に Playwright が含まれていること

<!-- ## Migration Guide -->

<!-- Breaking Changes がある場合にコメントアウトを解除して記載する -->
