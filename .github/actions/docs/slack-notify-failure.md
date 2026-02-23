# slack-notify-failure

> ソースファイル: [`.github/actions/slack-notify-failure/action.yml`](../slack-notify-failure/action.yml)

ワークフロー失敗時に Slack へ通知する Composite Action です。Slack Incoming Webhook URL を使用してメッセージを送信します（`slack-notify-success` と異なり、チャンネル指定は不要です）。

## Inputs

| 入力名 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|
| `webhook-url` | 必須 | - | Slack Incoming Webhook URL |
| `color` | 任意 | `danger` | メッセージのカラーバー色 |
| `mention-user` | 任意 | `''` | メンション対象ユーザー |
| `title` | 任意 | `workflow failed` | メッセージタイトル |
| `message` | 任意 | 実行ログ URL | メッセージ本文 |

## 前提条件

- Slack Incoming Webhook URL が設定されていること

## 使用例

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/slack-notify-failure@v1
    with:
      webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}

  # メンション付きの場合
  - uses: kryota-dev/actions/.github/actions/slack-notify-failure@v1
    with:
      webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
      mention-user: "<@U01234567>"
      title: "デプロイ失敗"
```
