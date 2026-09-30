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

    # apply-htaccess - Apply the artifact .htaccess on production deploys (opt-in)
    # Optional (default: 'false')
    apply-htaccess: 'false'

    # exclude-paths - Newline-separated paths to leave untouched on production deploys
    # Optional (default: '')
    exclude-paths: ''
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
| `apply-htaccess` | Apply the artifact `.htaccess` on production deploys (opt-in; only effective when `is-production` is `'true'`) | No | `'false'` |
| `exclude-paths` | Newline-separated paths relative to the target root to leave untouched (neither transferred nor deleted) on production deploys, in addition to `.htaccess` and `_feature/`. Allowed characters are `[A-Za-z0-9._-]` and `/`; a trailing `/` matches directories only (only effective when `is-production` is `'true'`) | No | `''` |

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

### Apply repository-managed `.htaccess` on production (opt-in)

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/deploy-web-hosting-ftp@v0
    with:
      output-dir: 'dist'
      ftp-server: ${{ secrets.FTP_SERVER }}
      ftp-username: ${{ secrets.FTP_USERNAME }}
      ftp-password: ${{ secrets.FTP_PASSWORD }}
      ftp-path: '/public_html'
      is-production: 'true'
      # Upload the artifact's .htaccess (e.g. redirects, ErrorDocument 404)
      # while still protecting the server's copy from deletion.
      apply-htaccess: 'true'
```

### Leave other content under the target root untouched on production

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/deploy-web-hosting-ftp@v0
    with:
      output-dir: 'dist'
      ftp-server: ${{ secrets.FTP_SERVER }}
      ftp-username: ${{ secrets.FTP_USERNAME }}
      ftp-password: ${{ secrets.FTP_PASSWORD }}
      ftp-path: '/public_html'
      is-production: 'true'
      # Another site placed under the same document root. These paths are
      # neither transferred nor deleted by the --delete mirror.
      exclude-paths: |
        other-site/
        shared/robots-extra.txt
```

## Behavior

1. Install lftp
2. Build the source path `./{output-dir}{base-path}`
3. In dry-run mode, test the connection to the FTP server and only display the file listing (both the mirror pass and the optional `.htaccess` upload are skipped — use the rsync action if you need a dry-run simulation of the `.htaccess` pass)
4. In normal mode, sync files from local to remote using the `mirror --reverse --delete` command
5. In production mode, exclude `.htaccess` and `_feature/` from the mirror so the server copies are never deleted (lftp `mirror` has no protect-only filter)
6. In production mode, each path listed in `exclude-paths` is added to the mirror as an extra `-x` regex anchored at the mirror root (`^`), with `.` escaped. A trailing `/` matches the directory only; otherwise the entry matches the file or a directory of that name. They are neither transferred nor deleted. Entries are validated up front (in every mode, including dry-run) and the step fails on disallowed characters or `.` / `..` segments. `exclude-paths` has no effect outside production
7. When `apply-htaccess: 'true'` (production only) and the artifact contains a `.htaccess`, upload it in a second pass via `put` — the artifact's `.htaccess` is transferred (overwriting the server copy) while the mirror still protects the server copy from deletion. If the artifact has no `.htaccess`, the second pass is skipped and the server copy is preserved. `apply-htaccess` has no effect outside production.
8. If `runner.debug` is enabled, enable the lftp debug flag `-d`

## Prerequisites

- Build artifacts must exist in the `output-dir`
- FTP server connection information (server address, username, password) must be configured

<!-- ## Migration Guide -->

<!-- Uncomment and fill in when there are Breaking Changes -->
