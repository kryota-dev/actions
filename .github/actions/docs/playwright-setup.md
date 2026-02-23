# playwright-setup

> ソースファイル: [`.github/actions/playwright-setup/action.yml`](../playwright-setup/action.yml)

Playwright ブラウザをキャッシュ付きでインストールする Composite Action です。Playwright のバージョンに基づいてキャッシュキーを生成し、キャッシュヒット時はダウンロードをスキップします。

## Inputs

なし

## 前提条件

- `pnpm-setup` Action（または同等のセットアップ）が先に完了していること
- `pnpm exec playwright --version` が実行可能な状態であること

## 使用例

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: kryota-dev/actions/.github/actions/pnpm-setup@v1
  - uses: kryota-dev/actions/.github/actions/playwright-setup@v1
```
