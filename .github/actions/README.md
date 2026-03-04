**English** | [日本語](README.ja.md)

# Composite Actions

## Development Environment Setup

| Action | Description |
|--------|-------------|
| [pnpm-setup](docs/pnpm-setup.md) | Node.js + pnpm setup and dependency installation |
| [playwright-setup](docs/playwright-setup.md) | Playwright browser setup (with caching) |

## Notifications

| Action | Description |
|--------|-------------|
| [slack-notify-success](docs/slack-notify-success.md) | Slack success notification (using Bot OAuth Token) |
| [slack-notify-failure](docs/slack-notify-failure.md) | Slack failure notification (using Incoming Webhook) |

## Deploy

| Action | Description |
|--------|-------------|
| [compute-web-hosting-deploy-path](docs/compute-web-hosting-deploy-path.md) | Compute deploy path and production flag from GitHub context |
| [deploy-web-hosting-ftp](docs/deploy-web-hosting-ftp.md) | Deploy to web hosting server via FTP (lftp) |
| [deploy-web-hosting-rsync](docs/deploy-web-hosting-rsync.md) | Deploy to web hosting server via rsync (SSH) |
| [undeploy-web-hosting-ftp](docs/undeploy-web-hosting-ftp.md) | Remove directory from web hosting server via FTP (lftp) |
| [undeploy-web-hosting-rsync](docs/undeploy-web-hosting-rsync.md) | Remove directory from web hosting server via rsync (SSH) |

## Usage

To call a Composite Action from another repository:

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/{action-name}@v1
    with:
      # inputs
```

See the linked documentation above for details on each action's inputs.
