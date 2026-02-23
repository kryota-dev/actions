# slack-notify-success

> ソースファイル: [`.github/actions/slack-notify-success/action.yml`](../slack-notify-success/action.yml)

ワークフロー成功時に Slack へ通知する Composite Action です。Slack Bot OAuth Token と `chat.postMessage` API を使用してメッセージを送信します。スレッド返信やブロードキャストにも対応しています。

## Inputs

| 入力名 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|
| `channel-id` | 必須 | - | Slack チャンネル ID |
| `bot-oauth-token` | 必須 | - | Slack Bot OAuth Token |
| `color` | 任意 | `good` | メッセージのカラーバー色 |
| `mention-user` | 任意 | `''` | メンション対象ユーザー |
| `title` | 任意 | `workflow execution completed` | メッセージタイトル |
| `message` | 任意 | 実行ログ URL | メッセージ本文 |
| `thread-ts` | 任意 | `null` | スレッド返信先 timestamp |
| `reply-broadcast` | 任意 | `false` | スレッド返信をチャンネルにもブロードキャストするか |

## 前提条件

- Slack Bot が対象チャンネルに招待されていること
- Bot に `chat:write` スコープが付与されていること

## 使用例

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/slack-notify-success@v1
    with:
      channel-id: ${{ vars.SLACK_CHANNEL_ID }}
      bot-oauth-token: ${{ secrets.SLACK_BOT_OAUTH_TOKEN }}

  # メンション付き・スレッド返信の場合
  - uses: kryota-dev/actions/.github/actions/slack-notify-success@v1
    with:
      channel-id: ${{ vars.SLACK_CHANNEL_ID }}
      bot-oauth-token: ${{ secrets.SLACK_BOT_OAUTH_TOKEN }}
      mention-user: "<@U01234567>"
      title: "デプロイ完了"
      thread-ts: ${{ steps.initial-post.outputs.ts }}
      reply-broadcast: "true"
```
