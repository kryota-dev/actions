**English** | [日本語](undeploy-web-hosting-rsync.ja.md)

# undeploy-web-hosting-rsync

A Composite Action that removes a deployed directory from a web hosting server via rsync over SSH. Supports dry-run mode.

> Source: [`.github/actions/undeploy-web-hosting-rsync/action.yml`](../undeploy-web-hosting-rsync/action.yml)

## Usage

```yaml
- uses: kryota-dev/actions/.github/actions/undeploy-web-hosting-rsync@v1
  with:
    # ssh-host - SSH server hostname
    # Required
    ssh-host: ''

    # ssh-user - SSH username
    # Required
    ssh-user: ''

    # ssh-private-key - SSH private key
    # Required
    ssh-private-key: ''

    # target-path - Target path to delete on the remote server
    # Required
    target-path: ''

    # dry-run - Whether to run in dry-run mode
    # Optional (default: 'false')
    dry-run: 'false'
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `ssh-host` | SSH server hostname | Yes | - |
| `ssh-user` | SSH username | Yes | - |
| `ssh-private-key` | SSH private key | Yes | - |
| `target-path` | Target path to delete on the remote server | Yes | - |
| `dry-run` | Whether to run in dry-run mode | No | `'false'` |

## Examples

### Basic Usage

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/undeploy-web-hosting-rsync@v1
    with:
      ssh-host: ${{ secrets.SSH_HOST }}
      ssh-user: ${{ secrets.SSH_USER }}
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
      target-path: '/home/user/public_html/_feature/feat-awesome'
```

### Verify with Dry-run

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/undeploy-web-hosting-rsync@v1
    with:
      ssh-host: ${{ secrets.SSH_HOST }}
      ssh-user: ${{ secrets.SSH_USER }}
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
      target-path: '/home/user/public_html/_feature/feat-awesome'
      dry-run: 'true'
```

## Behavior

1. Set up the SSH key (write private key to `~/.ssh/id_rsa`, retrieve host key with `ssh-keyscan`)
2. Create an empty directory `./empty_dir`
3. Sync the empty directory to the target path using `rsync -az --delete` (effectively deleting all files in the target)
4. In normal mode, attempt to remove the emptied parent directory with `rmdir`
5. In dry-run mode, add the `--dry-run` and `--verbose` flags
6. In debug mode, add the `--verbose` flag
7. Clean up SSH keys and `empty_dir` after completion (regardless of success or failure)

## Prerequisites

- SSH server connection information (hostname, username, private key) must be configured

<!-- ## Migration Guide -->

<!-- Uncomment and fill in when there are Breaking Changes -->
