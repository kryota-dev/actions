[English](pnpm-setup.md) | **日本語**

# pnpm-setup

Node.js と pnpm のセットアップ、および依存関係のインストールを行う Composite Action。

> Source: [`.github/actions/pnpm-setup/action.yml`](../pnpm-setup/action.yml)

## Usage

```yaml
- uses: kryota-dev/actions/.github/actions/pnpm-setup@v0
```

## Inputs

| 名前      | 必須 | デフォルト | 説明                                                                                                                                                                                       |
| --------- | ---- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `version` | No   | `''`       | インストールする pnpm のバージョン。空のままにすると `package.json` の `packageManager` フィールドを使用する（推奨）。`packageManager` フィールドがない場合のみ必須（pnpm/action-setup v6 ではその場合バージョン指定が必須となるため）。 |

## Examples

### 基本的な使い方

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: kryota-dev/actions/.github/actions/pnpm-setup@v0
```

### pnpm バージョンを明示的に指定する

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: kryota-dev/actions/.github/actions/pnpm-setup@v0
    with:
      version: 10
```

## Behavior

1. `pnpm/action-setup@v6.0.8` を使用して pnpm をインストールする。pnpm のバージョンは `version` 入力が指定されていればそれを、なければ `package.json` の `packageManager` フィールドから解決する（`run_install: false`）
2. `actions/setup-node@v6.4.0` を使用して Node.js をインストールする（`.node-version` ファイルからバージョンを取得）
3. `pnpm store path --silent` を実行して pnpm ストアのパスを取得する
4. `actions/cache@v5.0.5` を使用して pnpm ストアをキャッシュする（キー: `{os}-pnpm-store-{hash(pnpm-lock.yaml)}`）
5. `pnpm install` を実行して依存関係をインストールする

## Prerequisites

- リポジトリに `package.json` が存在すること
- `package.json` に `packageManager` フィールド（例: `"packageManager": "pnpm@10.0.0"`）が含まれているか、`version` 入力が指定されていること。pnpm/action-setup v6 ではいずれかからバージョンを解決できる必要がある
- リポジトリに `.node-version` ファイルが存在すること
- リポジトリに `pnpm-lock.yaml` が存在すること

## Migration Guide

### 内部で使用する `pnpm/action-setup` の v5 から v6 へのアップグレード

pnpm/action-setup v6 では pnpm バージョンの解決方法が変更された。

- `package.json` に `packageManager` フィールドがある場合、そこからバージョンが読み取られるため追加対応は不要
- `package.json` に `packageManager` フィールドがない場合、バージョンを明示的に指定する必要がある。`version` 入力を設定する（例: `version: 10`）

このアップグレード後に pnpm のセットアップがバージョン未指定エラーで失敗するようになった場合は、`package.json` に `packageManager` フィールドを追加するか、`version` 入力を渡すこと。
