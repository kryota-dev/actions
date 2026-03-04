[English](pnpm-setup.md) | **日本語**

# pnpm-setup

Node.js と pnpm のセットアップ、および依存関係のインストールを行う Composite Action。

> Source: [`.github/actions/pnpm-setup/action.yml`](../pnpm-setup/action.yml)

## Usage

```yaml
- uses: kryota-dev/actions/.github/actions/pnpm-setup@v1
```

## Inputs

None

## Examples

### 基本的な使い方

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: kryota-dev/actions/.github/actions/pnpm-setup@v1
```

## Behavior

1. `pnpm/action-setup@v4.2.0` を使用して pnpm をインストールする（`package.json` を参照、`run_install: false`）
2. `actions/setup-node@v6.2.0` を使用して Node.js をインストールする（`.node-version` ファイルからバージョンを取得、`cache: 'pnpm'`）
3. `pnpm store path --silent` を実行して pnpm ストアのパスを取得する
4. `actions/cache@v5.0.3` を使用して pnpm ストアをキャッシュする（キー: `{os}-pnpm-store-{hash(pnpm-lock.yaml)}`）
5. `pnpm install` を実行して依存関係をインストールする

## Prerequisites

- リポジトリに `package.json` が存在すること
- リポジトリに `.node-version` ファイルが存在すること
- リポジトリに `pnpm-lock.yaml` が存在すること

<!-- ## Migration Guide -->

<!-- Breaking Changes がある場合にコメントアウトを解除して記載する -->
