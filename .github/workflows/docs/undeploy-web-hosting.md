**English** | [日本語](undeploy-web-hosting.ja.md)

# Undeploy from Web Hosting

Workflow to remove feature environments from a web hosting server via FTP or rsync

> Source: [`.github/workflows/undeploy-web-hosting.yml`](../undeploy-web-hosting.yml)

## Usage

```yaml
jobs:
  undeploy:
    permissions:
      contents: read
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/undeploy-web-hosting.yml@v0
    with:
      # environment - GitHub Environment name for secret access
      # Required
      environment: 'production'

      # deploy-type - Deployment method ('ftp' or 'rsync')
      # Required
      deploy-type: 'ftp'

      # base-path-prefix - Project-specific path prefix (e.g., '/<your-project>')
      # Optional (default: '')
      base-path-prefix: ''

      # production-branch - Production branch name
      # Optional (default: 'main')
      production-branch: 'main'

      # ref-name - Branch name override (auto-detected from github context if empty)
      # Optional (default: '')
      ref-name: ''

      # dry-run - Dry-run mode
      # Optional (default: 'false')
      dry-run: 'false'
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
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `environment` | GitHub Environment name for secret access | Yes | - |
| `deploy-type` | Deployment method (`'ftp'` or `'rsync'`) | Yes | - |
| `base-path-prefix` | Project-specific path prefix (e.g., `'/<your-project>'`) | No | `''` |
| `production-branch` | Production branch name | No | `'main'` |
| `ref-name` | Branch name override (auto-detected from github context if empty) | No | `''` |
| `dry-run` | Dry-run mode | No | `'false'` |

## Secrets

| Name | Description | Required |
|------|-------------|----------|
| `server-host` | Deployment server hostname | Yes |
| `server-user` | Deployment server username | Yes |
| `server-path` | Deployment server path | Yes |
| `server-password` | Deployment server password (required for FTP) | No |
| `ssh-private-key` | SSH private key (required for rsync) | No |

## Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| `contents` | `read` | Repository checkout |
| `pull-requests` | `write` | Posting removal result comments on PRs |

## Examples

### Remove feature environment via FTP

```yaml
jobs:
  undeploy:
    permissions:
      contents: read
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/undeploy-web-hosting.yml@v0
    with:
      environment: 'production'
      deploy-type: 'ftp'
    secrets:
      server-host: ${{ secrets.SERVER_HOST }}
      server-user: ${{ secrets.SERVER_USER }}
      server-path: ${{ secrets.SERVER_PATH }}
      server-password: ${{ secrets.SERVER_PASSWORD }}
```

### Remove feature environment via rsync (with path prefix)

```yaml
jobs:
  undeploy:
    permissions:
      contents: read
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/undeploy-web-hosting.yml@v0
    with:
      environment: 'production'
      deploy-type: 'rsync'
      base-path-prefix: '/my-project'
    secrets:
      server-host: ${{ secrets.SERVER_HOST }}
      server-user: ${{ secrets.SERVER_USER }}
      server-path: ${{ secrets.SERVER_PATH }}
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
```

### Verify with dry-run

```yaml
jobs:
  undeploy:
    permissions:
      contents: read
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/undeploy-web-hosting.yml@v0
    with:
      environment: 'staging'
      deploy-type: 'rsync'
      dry-run: 'true'
    secrets:
      server-host: ${{ secrets.SERVER_HOST }}
      server-user: ${{ secrets.SERVER_USER }}
      server-path: ${{ secrets.SERVER_PATH }}
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
```

## Behavior

This workflow consists of a `delete` job and executes in the following order:

1. Compute the target removal path using the `compute-web-hosting-deploy-path` Composite Action
2. Execute removal based on the `deploy-type` value
   - `'ftp'`: Uses the `undeploy-web-hosting-ftp` Composite Action
   - `'rsync'`: Uses the `undeploy-web-hosting-rsync` Composite Action
3. For PRs: Post success/failure comments via `marocchino/sticky-pull-request-comment`
4. On success: Hide previous failure comments and previous deploy success comments

## Prerequisites

- A GitHub Environment matching the `environment` input must exist in the caller's repository, with the required secrets configured at the environment level
- For `deploy-type` `'ftp'`: `server-password` is required
- For `deploy-type` `'rsync'`: `ssh-private-key` is required
