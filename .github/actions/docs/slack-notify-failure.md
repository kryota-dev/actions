# slack-notify-failure

ワークフロー失敗時に Slack へメッセージを投稿する Composite Action。

> Source: [`.github/actions/slack-notify-failure/action.yml`](../slack-notify-failure/action.yml)

## Usage

```yaml
- uses: kryota-dev/actions/.github/actions/slack-notify-failure@v1
  with:
    # webhook-url - Slack Incoming Webhook URL
    # Required
    webhook-url: ''

    # color - メッセージの色
    # Optional (default: 'danger')
    color: 'danger'

    # mention-user - メンションするユーザー
    # Optional (default: '')
    mention-user: ''

    # title - メッセージタイトル
    # Optional (default: 'workflow failed')
    title: 'workflow failed'

    # message - メッセージ本文
    # Optional (default: 'Execution log: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}')
    message: 'Execution log: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}'
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `webhook-url` | Slack Incoming Webhook URL | Yes | - |
| `color` | メッセージの色 | No | `'danger'` |
| `mention-user` | メンションするユーザー | No | `''` |
| `title` | メッセージタイトル | No | `'workflow failed'` |
| `message` | メッセージ本文 | No | `'Execution log: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}'` |

## Examples

### 基本的な使い方

必須パラメータのみを指定するシンプルな例。

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/slack-notify-failure@v1
    with:
      webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### メンション付き通知

特定のユーザーにメンションして通知する例。

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/slack-notify-failure@v1
    with:
      webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
      mention-user: '<@U0123456789>'
      title: 'デプロイが失敗しました'
```

### カスタムメッセージ

メッセージ本文をカスタマイズする例。

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/slack-notify-failure@v1
    with:
      webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
      title: 'CI テストが失敗しました'
      message: 'ブランチ: ${{ github.ref_name }} / コミット: ${{ github.sha }}'
```

## Behavior

1. `mention-user` が指定されている場合、タイトルにメンションを付与する（`*FAILURE - {mention-user} {title}*`）
2. リポジトリ名と URL を取得する
3. `jq` で JSON ペイロードを構築する（attachments with color/author/text）
4. `curl --fail` で Webhook URL に POST する
5. 失敗時は exit 1 で失敗する

## Prerequisites

- Slack Incoming Webhook URL が必要

<!-- ## Migration Guide -->

<!-- Breaking Changes がある場合にコメントアウトを解除して記載する -->
