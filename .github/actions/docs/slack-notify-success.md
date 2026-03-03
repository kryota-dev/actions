# slack-notify-success

ワークフロー成功時に Slack へメッセージを投稿する Composite Action。

> Source: [`.github/actions/slack-notify-success/action.yml`](../slack-notify-success/action.yml)

## Usage

```yaml
- uses: kryota-dev/actions/.github/actions/slack-notify-success@v1
  with:
    # channel-id - Slack Channel ID
    # Required
    channel-id: ''

    # bot-oauth-token - Slack Bot OAuth Token
    # Required
    bot-oauth-token: ''

    # color - メッセージの色
    # Optional (default: 'good')
    color: 'good'

    # mention-user - メンションするユーザー
    # Optional (default: '')
    mention-user: ''

    # title - メッセージタイトル
    # Optional (default: 'workflow execution completed')
    title: 'workflow execution completed'

    # message - メッセージ本文
    # Optional (default: 'Execution log: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}')
    message: 'Execution log: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}'

    # thread-ts - スレッド返信用のタイムスタンプ
    # Optional (default: 'null')
    thread-ts: 'null'

    # reply-broadcast - スレッド返信をチャンネルにもブロードキャストするかどうか
    # Optional (default: 'false')
    reply-broadcast: 'false'
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `channel-id` | Slack Channel ID | Yes | - |
| `bot-oauth-token` | Slack Bot OAuth Token | Yes | - |
| `color` | メッセージの色 | No | `'good'` |
| `mention-user` | メンションするユーザー | No | `''` |
| `title` | メッセージタイトル | No | `'workflow execution completed'` |
| `message` | メッセージ本文 | No | `'Execution log: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}'` |
| `thread-ts` | スレッド返信用のタイムスタンプ | No | `'null'` |
| `reply-broadcast` | スレッド返信をチャンネルにもブロードキャストするかどうか | No | `'false'` |

## Examples

### 基本的な使い方

必須パラメータのみを指定するシンプルな例。

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/slack-notify-success@v1
    with:
      channel-id: ${{ secrets.SLACK_CHANNEL_ID }}
      bot-oauth-token: ${{ secrets.SLACK_BOT_TOKEN }}
```

### メンション付き通知

特定のユーザーにメンションして通知する例。

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/slack-notify-success@v1
    with:
      channel-id: ${{ secrets.SLACK_CHANNEL_ID }}
      bot-oauth-token: ${{ secrets.SLACK_BOT_TOKEN }}
      mention-user: '<@U0123456789>'
      title: 'デプロイが完了しました'
```

### スレッド返信

既存のスレッドに返信として通知し、チャンネルにもブロードキャストする例。

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/slack-notify-success@v1
    with:
      channel-id: ${{ secrets.SLACK_CHANNEL_ID }}
      bot-oauth-token: ${{ secrets.SLACK_BOT_TOKEN }}
      thread-ts: ${{ steps.previous-step.outputs.thread-ts }}
      reply-broadcast: 'true'
```

## Behavior

1. `mention-user` が指定されている場合、タイトルにメンションを付与する（`*SUCCESS - {mention-user} {title}*`）
2. リポジトリ名と URL を取得する
3. `jq` で JSON ペイロードを構築する（channel, attachments with color/author/text）
4. `thread-ts` が `"null"` でない場合、スレッド返信として送信する（`reply_broadcast` 対応）
5. `curl` で `https://slack.com/api/chat.postMessage` に POST する（Bearer トークン認証）
6. レスポンスの `"ok":false` をチェックし、エラー時は exit 1 で失敗する

## Prerequisites

- Slack Bot OAuth Token が必要（`chat:write` スコープ）
- Slack Channel ID が必要

<!-- ## Migration Guide -->

<!-- Breaking Changes がある場合にコメントアウトを解除して記載する -->
