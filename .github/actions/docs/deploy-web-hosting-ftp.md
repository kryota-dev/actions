**English** | [日本語](deploy-web-hosting-ftp.ja.md)

# deploy-web-hosting-ftp

A Composite Action that deploys build artifacts to a web hosting server via FTP using lftp. Supports dry-run and production modes.

> Source: [`.github/actions/deploy-web-hosting-ftp/action.yml`](../deploy-web-hosting-ftp/action.yml)

## Usage

```yaml
- uses: kryota-dev/actions/.github/actions/deploy-web-hosting-ftp@v0
  with:
    # output-dir - Build output directory name
    # Required
    output-dir: ''

    # ftp-server - FTP server address
    # Required
    ftp-server: ''

    # ftp-username - FTP server username
    # Required
    ftp-username: ''

    # ftp-password - FTP server password
    # Required
    ftp-password: ''

    # ftp-path - FTP server path
    # Required
    ftp-path: ''

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
| `ftp-server` | FTP server address | Yes | - |
| `ftp-username` | FTP server username | Yes | - |
| `ftp-password` | FTP server password | Yes | - |
| `ftp-path` | FTP server path | Yes | - |
| `base-path` | Base path for artifacts | No | - |
| `dry-run` | Whether to run in dry-run mode | No | `'false'` |
| `is-production` | Whether this is a production deploy | No | `'false'` |

## Examples

### Basic Usage

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/deploy-web-hosting-ftp@v0
    with:
      output-dir: 'dist'
      ftp-server: ${{ secrets.FTP_SERVER }}
      ftp-username: ${{ secrets.FTP_USERNAME }}
      ftp-password: ${{ secrets.FTP_PASSWORD }}
      ftp-path: '/public_html'
```

### Verify with Dry-run

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/deploy-web-hosting-ftp@v0
    with:
      output-dir: 'dist'
      ftp-server: ${{ secrets.FTP_SERVER }}
      ftp-username: ${{ secrets.FTP_USERNAME }}
      ftp-password: ${{ secrets.FTP_PASSWORD }}
      ftp-path: '/public_html'
      dry-run: 'true'
```

### Production Deploy (with base-path)

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/deploy-web-hosting-ftp@v0
    with:
      output-dir: 'dist'
      ftp-server: ${{ secrets.FTP_SERVER }}
      ftp-username: ${{ secrets.FTP_USERNAME }}
      ftp-password: ${{ secrets.FTP_PASSWORD }}
      ftp-path: '/public_html'
      base-path: '/my-project'
      is-production: 'true'
```

## Behavior

1. Install lftp
2. Build the source path `./{output-dir}{base-path}`
3. In dry-run mode, test the connection to the FTP server and only display the file listing
4. In normal mode, sync files from local to remote using the `mirror --reverse --delete` command
5. In production mode, exclude `.htaccess` and `_feature/` from sync targets
6. If `runner.debug` is enabled, enable the lftp debug flag `-d`

## Prerequisites

- Build artifacts must exist in the `output-dir`
- FTP server connection information (server address, username, password) must be configured

<!-- ## Migration Guide -->

<!-- Uncomment and fill in when there are Breaking Changes -->
