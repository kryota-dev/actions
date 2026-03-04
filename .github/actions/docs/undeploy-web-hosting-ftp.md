**English** | [日本語](undeploy-web-hosting-ftp.ja.md)

# undeploy-web-hosting-ftp

A Composite Action that removes a deployed directory from a web hosting server using lftp. Supports dry-run mode.

> Source: [`.github/actions/undeploy-web-hosting-ftp/action.yml`](../undeploy-web-hosting-ftp/action.yml)

## Usage

```yaml
- uses: kryota-dev/actions/.github/actions/undeploy-web-hosting-ftp@v1
  with:
    # ftp-server - FTP server address
    # Required
    ftp-server: ''

    # ftp-username - FTP server username
    # Required
    ftp-username: ''

    # ftp-password - FTP server password
    # Required
    ftp-password: ''

    # target-path - Target path to delete on the FTP server
    # Required
    target-path: ''

    # dry-run - Whether to run in dry-run mode
    # Optional (default: 'false')
    dry-run: 'false'
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `ftp-server` | FTP server address | Yes | - |
| `ftp-username` | FTP server username | Yes | - |
| `ftp-password` | FTP server password | Yes | - |
| `target-path` | Target path to delete on the FTP server | Yes | - |
| `dry-run` | Whether to run in dry-run mode | No | `'false'` |

## Examples

### Basic Usage

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/undeploy-web-hosting-ftp@v1
    with:
      ftp-server: ${{ secrets.FTP_SERVER }}
      ftp-username: ${{ secrets.FTP_USERNAME }}
      ftp-password: ${{ secrets.FTP_PASSWORD }}
      target-path: '/public_html/_feature/feat-awesome'
```

### Verify with Dry-run

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/undeploy-web-hosting-ftp@v1
    with:
      ftp-server: ${{ secrets.FTP_SERVER }}
      ftp-username: ${{ secrets.FTP_USERNAME }}
      ftp-password: ${{ secrets.FTP_PASSWORD }}
      target-path: '/public_html/_feature/feat-awesome'
      dry-run: 'true'
```

## Behavior

1. Install lftp
2. In dry-run mode, only check the directory contents with `ls -la {target-path}`
3. In normal mode, delete the target directory with `rm -rf {target-path}`

## Prerequisites

- FTP server connection information (server address, username, password) must be configured

<!-- ## Migration Guide -->

<!-- Uncomment and fill in when there are Breaking Changes -->
