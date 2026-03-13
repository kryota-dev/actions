**English** | [日本語](deploy-web-hosting.ja.md)

# Deploy to Web Hosting

Workflow to deploy pre-built artifacts to a web hosting server via FTP or rsync

> Source: [`.github/workflows/deploy-web-hosting.yml`](../deploy-web-hosting.yml)

## Usage

```yaml
jobs:
  deploy:
    permissions:
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/deploy-web-hosting.yml@v0
    with:
      # environment - GitHub Environment name for secret access
      # Required
      environment: 'production'

      # deploy-type - Deployment method ('ftp' or 'rsync')
      # Required
      deploy-type: 'ftp'

      # artifact-name - Name of the build artifact to download
      # Required
      artifact-name: 'build-output'

      # output-dir - Build output directory name
      # Required
      output-dir: 'dist'

      # base-path-prefix - Project-specific path prefix (e.g., '/<your-project>')
      # Optional (default: '')
      base-path-prefix: ''

      # home-url - Site home URL
      # Optional (default: '')
      home-url: ''

      # dry-run - Dry-run mode
      # Optional (default: 'false')
      dry-run: 'false'

      # production-branch - Production branch name
      # Optional (default: 'main')
      production-branch: 'main'

      # ref-name - Branch name override (auto-detected from github context if empty)
      # Optional (default: '')
      ref-name: ''
    secrets:
      # server-host - Deployment server hostname
      # Required
      server-host: ${{ secrets.SERVER_HOST }}

      # server-user - Deployment server username
      # Required
      server-user: ${{ secrets.SERVER_USER }}

      # server-path - Deployment server path
      # Required
      server-path: ${{ secrets.SERVER_PATH }}

      # server-password - Deployment server password (required for FTP)
      # Optional
      server-password: ${{ secrets.SERVER_PASSWORD }}

      # ssh-private-key - SSH private key (required for rsync)
      # Optional
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}

      # slack-channel-id - Slack notification channel ID
      # Optional
      slack-channel-id: ${{ secrets.SLACK_CHANNEL_ID }}

      # slack-bot-oauth-token - Slack Bot OAuth token
      # Optional
      slack-bot-oauth-token: ${{ secrets.SLACK_BOT_OAUTH_TOKEN }}

      # slack-webhook-url - Slack Incoming Webhook URL
      # Optional
      slack-webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}

      # slack-mention-user - Slack user to mention on failure
      # Optional
      slack-mention-user: ${{ secrets.SLACK_MENTION_USER }}
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `environment` | GitHub Environment name for secret access | Yes | - |
| `deploy-type` | Deployment method (`'ftp'` or `'rsync'`) | Yes | - |
| `artifact-name` | Name of the build artifact to download | Yes | - |
| `output-dir` | Build output directory name | Yes | - |
| `base-path-prefix` | Project-specific path prefix (e.g., `'/<your-project>'`) | No | `''` |
| `home-url` | Site home URL | No | `''` |
| `dry-run` | Dry-run mode | No | `'false'` |
| `production-branch` | Production branch name | No | `'main'` |
| `ref-name` | Branch name override (auto-detected from github context if empty) | No | `''` |

## Secrets

| Name | Description | Required |
|------|-------------|----------|
| `server-host` | Deployment server hostname | Yes |
| `server-user` | Deployment server username | Yes |
| `server-path` | Deployment server path | Yes |
| `server-password` | Deployment server password (required for FTP) | No |
| `ssh-private-key` | SSH private key (required for rsync) | No |
| `slack-channel-id` | Slack notification channel ID | No |
| `slack-bot-oauth-token` | Slack Bot OAuth token | No |
| `slack-webhook-url` | Slack Incoming Webhook URL | No |
| `slack-mention-user` | Slack user to mention on failure | No |

## Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| `pull-requests` | `write` | Posting deployment result comments on PRs |

## Examples

### Deploy via FTP

```yaml
jobs:
  deploy:
    permissions:
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/deploy-web-hosting.yml@v0
    with:
      environment: 'production'
      deploy-type: 'ftp'
      artifact-name: 'build-output'
      output-dir: 'dist'
    secrets:
      server-host: ${{ secrets.SERVER_HOST }}
      server-user: ${{ secrets.SERVER_USER }}
      server-path: ${{ secrets.SERVER_PATH }}
      server-password: ${{ secrets.SERVER_PASSWORD }}
```

### Deploy via rsync (with Slack notifications)

```yaml
jobs:
  deploy:
    permissions:
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/deploy-web-hosting.yml@v0
    with:
      environment: 'production'
      deploy-type: 'rsync'
      artifact-name: 'build-output'
      output-dir: 'dist'
      base-path-prefix: '/my-project'
      home-url: 'https://example.com'
    secrets:
      server-host: ${{ secrets.SERVER_HOST }}
      server-user: ${{ secrets.SERVER_USER }}
      server-path: ${{ secrets.SERVER_PATH }}
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
      slack-channel-id: ${{ secrets.SLACK_CHANNEL_ID }}
      slack-bot-oauth-token: ${{ secrets.SLACK_BOT_OAUTH_TOKEN }}
      slack-webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
      slack-mention-user: ${{ secrets.SLACK_MENTION_USER }}
```

### Verify with dry-run

```yaml
jobs:
  deploy:
    permissions:
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/deploy-web-hosting.yml@v0
    with:
      environment: 'staging'
      deploy-type: 'rsync'
      artifact-name: 'build-output'
      output-dir: 'dist'
      dry-run: 'true'
    secrets:
      server-host: ${{ secrets.SERVER_HOST }}
      server-user: ${{ secrets.SERVER_USER }}
      server-path: ${{ secrets.SERVER_PATH }}
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
```

## Behavior

This workflow consists of a `deploy` job and executes in the following order:

1. Compute the deployment path using the `compute-web-hosting-deploy-path` Composite Action
2. Check Slack configuration (`slack-channel-id` + `slack-bot-oauth-token` enables success notifications, `slack-webhook-url` enables failure notifications)
3. Download build artifacts with `actions/download-artifact@v4.3.0`
4. Execute deployment based on the `deploy-type` value
   - `'ftp'`: Uses the `deploy-web-hosting-ftp` Composite Action
   - `'rsync'`: Uses the `deploy-web-hosting-rsync` Composite Action
5. For PRs: Post success/failure comments via `marocchino/sticky-pull-request-comment`
6. For non-PRs: Send Slack success notifications (`slack-notify-success`) / failure notifications (`slack-notify-failure`)
7. For PRs on success: Hide previous failure comments

## Prerequisites

- A GitHub Environment matching the `environment` input must exist in the caller's repository, with the required secrets configured at the environment level
- Build artifacts must have been uploaded via `actions/upload-artifact` in the calling workflow
- For `deploy-type` `'ftp'`: `server-password` is required
- For `deploy-type` `'rsync'`: `ssh-private-key` is required
