# Actions

## Composite Actions

| アクション | 説明 |
|---|---|
| [pnpm-setup](docs/pnpm-setup.md) | Node.js + pnpm セットアップ |
| [playwright-setup](docs/playwright-setup.md) | Playwright ブラウザセットアップ |
| [slack-notify-success](docs/slack-notify-success.md) | Slack 成功通知（Bot OAuth Token） |
| [slack-notify-failure](docs/slack-notify-failure.md) | Slack 失敗通知（Incoming Webhook） |

## 使い方

他のリポジトリから Composite Action を呼び出す場合:

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/{action-name}@v1
    with:
      # inputs
```

各アクションの inputs の詳細は上記リンク先のドキュメントを参照してください。
