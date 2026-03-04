**English** | [日本語](slack-notify-success.ja.md)

# slack-notify-success

A Composite Action for posting a message to Slack on workflow success.

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

    # color - Message color
    # Optional (default: 'good')
    color: 'good'

    # mention-user - User to mention
    # Optional (default: '')
    mention-user: ''

    # title - Message title
    # Optional (default: 'workflow execution completed')
    title: 'workflow execution completed'

    # message - Message body
    # Optional (default: 'Execution log: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}')
    message: 'Execution log: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}'

    # thread-ts - Thread timestamp for replies
    # Optional (default: 'null')
    thread-ts: 'null'

    # reply-broadcast - Whether to broadcast thread replies to the channel
    # Optional (default: 'false')
    reply-broadcast: 'false'
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `channel-id` | Slack Channel ID | Yes | - |
| `bot-oauth-token` | Slack Bot OAuth Token | Yes | - |
| `color` | Message color | No | `'good'` |
| `mention-user` | User to mention | No | `''` |
| `title` | Message title | No | `'workflow execution completed'` |
| `message` | Message body | No | `'Execution log: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}'` |
| `thread-ts` | Thread timestamp for replies | No | `'null'` |
| `reply-broadcast` | Whether to broadcast thread replies to the channel | No | `'false'` |

## Examples

### Basic Usage

A simple example specifying only required parameters.

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/slack-notify-success@v1
    with:
      channel-id: ${{ secrets.SLACK_CHANNEL_ID }}
      bot-oauth-token: ${{ secrets.SLACK_BOT_TOKEN }}
```

### Notification with Mention

An example of notifying with a mention to a specific user.

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/slack-notify-success@v1
    with:
      channel-id: ${{ secrets.SLACK_CHANNEL_ID }}
      bot-oauth-token: ${{ secrets.SLACK_BOT_TOKEN }}
      mention-user: '<@U0123456789>'
      title: 'Deployment completed'
```

### Thread Reply

An example of replying to an existing thread and broadcasting to the channel.

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

1. If `mention-user` is specified, prepend the mention to the title (`*SUCCESS - {mention-user} {title}*`)
2. Retrieve the repository name and URL
3. Build the JSON payload with `jq` (channel, attachments with color/author/text)
4. If `thread-ts` is not `"null"`, send as a thread reply (with `reply_broadcast` support)
5. POST to `https://slack.com/api/chat.postMessage` via `curl` (Bearer token authentication)
6. Check the response for `"ok":false` and exit 1 on error

## Prerequisites

- Slack Bot OAuth Token is required (`chat:write` scope)
- Slack Channel ID is required

<!-- ## Migration Guide -->

<!-- Uncomment and fill in when there are Breaking Changes -->
