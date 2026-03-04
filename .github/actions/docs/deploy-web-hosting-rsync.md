**English** | [日本語](deploy-web-hosting-rsync.ja.md)

# deploy-web-hosting-rsync

A Composite Action that deploys build artifacts to a web hosting server via rsync over SSH. Supports dry-run and production modes.

> Source: [`.github/actions/deploy-web-hosting-rsync/action.yml`](../deploy-web-hosting-rsync/action.yml)

## Usage

```yaml
- uses: kryota-dev/actions/.github/actions/deploy-web-hosting-rsync@v1
  with:
    # output-dir - Build output directory name
    # Required
    output-dir: ''

    # ssh-host - SSH server hostname
    # Required
    ssh-host: ''

    # ssh-user - SSH username
    # Required
    ssh-user: ''

    # ssh-private-key - SSH private key
    # Required
    ssh-private-key: ''

    # ssh-path - Target path on the SSH server
    # Required
    ssh-path: ''

    # base-path - Base path for artifacts
    # Optional
    base-path: ''

    # dry-run - Whether to run in dry-run mode
    # Optional (default: 'false')
    dry-run: 'false'

    # is-production - Whether this is a production deploy
    # Optional (default: 'false')
    is-production: 'false'
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `output-dir` | Build output directory name | Yes | - |
| `ssh-host` | SSH server hostname | Yes | - |
| `ssh-user` | SSH username | Yes | - |
| `ssh-private-key` | SSH private key | Yes | - |
| `ssh-path` | Target path on the SSH server | Yes | - |
| `base-path` | Base path for artifacts | No | - |
| `dry-run` | Whether to run in dry-run mode | No | `'false'` |
| `is-production` | Whether this is a production deploy | No | `'false'` |

## Examples

### Basic Usage

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/deploy-web-hosting-rsync@v1
    with:
      output-dir: 'dist'
      ssh-host: ${{ secrets.SSH_HOST }}
      ssh-user: ${{ secrets.SSH_USER }}
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
      ssh-path: '/home/user/public_html'
```

### Verify with Dry-run

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/deploy-web-hosting-rsync@v1
    with:
      output-dir: 'dist'
      ssh-host: ${{ secrets.SSH_HOST }}
      ssh-user: ${{ secrets.SSH_USER }}
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
      ssh-path: '/home/user/public_html'
      dry-run: 'true'
```

### Production Deploy (with base-path)

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/deploy-web-hosting-rsync@v1
    with:
      output-dir: 'dist'
      ssh-host: ${{ secrets.SSH_HOST }}
      ssh-user: ${{ secrets.SSH_USER }}
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
      ssh-path: '/home/user/public_html'
      base-path: '/my-project'
      is-production: 'true'
```

## Behavior

1. Set up the SSH key (write private key to `~/.ssh/id_rsa`, retrieve host key with `ssh-keyscan`)
2. Build the source path `./{output-dir}{base-path}`
3. Sync files from local to remote using the `rsync -az --delete` command
4. In production mode, exclude `.htaccess` and `_feature/` from sync targets via `--exclude-from`
5. In dry-run mode, add the `--dry-run` flag
6. In debug mode or dry-run mode, add the `--verbose` flag
7. Clean up SSH keys after completion (regardless of success or failure)

## Prerequisites

- Build artifacts must exist in the `output-dir`
- SSH server connection information (hostname, username, private key) must be configured

<!-- ## Migration Guide -->

<!-- Uncomment and fill in when there are Breaking Changes -->
