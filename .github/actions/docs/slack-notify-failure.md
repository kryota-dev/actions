**English** | [日本語](slack-notify-failure.ja.md)

# slack-notify-failure

A Composite Action for posting a message to Slack on workflow failure.

> Source: [`.github/actions/slack-notify-failure/action.yml`](../slack-notify-failure/action.yml)

## Usage

```yaml
- uses: kryota-dev/actions/.github/actions/slack-notify-failure@v1
  with:
    # webhook-url - Slack Incoming Webhook URL
    # Required
    webhook-url: ''

    # color - Message color
    # Optional (default: 'danger')
    color: 'danger'

    # mention-user - User to mention
    # Optional (default: '')
    mention-user: ''

    # title - Message title
    # Optional (default: 'workflow failed')
    title: 'workflow failed'

    # message - Message body
    # Optional (default: 'Execution log: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}')
    message: 'Execution log: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}'
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `webhook-url` | Slack Incoming Webhook URL | Yes | - |
| `color` | Message color | No | `'danger'` |
| `mention-user` | User to mention | No | `''` |
| `title` | Message title | No | `'workflow failed'` |
| `message` | Message body | No | `'Execution log: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}'` |

## Examples

### Basic Usage

A simple example specifying only required parameters.

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/slack-notify-failure@v1
    with:
      webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### Notification with Mention

An example of notifying with a mention to a specific user.

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/slack-notify-failure@v1
    with:
      webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
      mention-user: '<@U0123456789>'
      title: 'Deployment failed'
```

### Custom Message

An example of customizing the message body.

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/slack-notify-failure@v1
    with:
      webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
      title: 'CI tests failed'
      message: 'Branch: ${{ github.ref_name }} / Commit: ${{ github.sha }}'
```

## Behavior

1. If `mention-user` is specified, prepend the mention to the title (`*FAILURE - {mention-user} {title}*`)
2. Retrieve the repository name and URL
3. Build the JSON payload with `jq` (attachments with color/author/text)
4. POST to the Webhook URL via `curl --fail`
5. Exit 1 on failure

## Prerequisites

- Slack Incoming Webhook URL is required

<!-- ## Migration Guide -->

<!-- Uncomment and fill in when there are Breaking Changes -->
