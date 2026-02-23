# pnpm-setup

> ソースファイル: [`.github/actions/pnpm-setup/action.yml`](../pnpm-setup/action.yml)

Node.js と pnpm のセットアップ、pnpm ストアキャッシュの設定、依存関係のインストールを一括実行する Composite Action です。

## Inputs

なし

## 前提条件

- リポジトリルートに `.node-version` ファイルが存在すること
- リポジトリルートに `package.json` が存在すること
- リポジトリルートに `pnpm-lock.yaml` が存在すること

## 使用例

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: kryota-dev/actions/.github/actions/pnpm-setup@v1
```
