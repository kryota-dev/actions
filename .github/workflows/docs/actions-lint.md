**English** | [日本語](actions-lint.ja.md)

# Actions Lint

GitHub Actions quality gate workflow

> Source: [`.github/workflows/actions-lint.yml`](../actions-lint.yml)

## Usage

```yaml
jobs:
  lint:
    permissions:
      contents: read
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/actions-lint.yml@v0
    with:
      # reviewdog-reporter - Reporter type for actionlint
      # Optional (default: 'github-pr-review')
      reviewdog-reporter: 'github-pr-review'
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `reviewdog-reporter` | Reporter type for actionlint (github-pr-review, github-check, etc.) | No | `'github-pr-review'` |
| `actionlint-config` | Path to actionlint config file (default: `.github/actionlint.{yaml,yml}`) | No | `''` |
| `ls-lint-config` | Path to ls-lint config file (default: `.ls-lint.yml` if present, otherwise kebab-case rules for `.github/workflows` and `.github/actions`) | No | `''` |
| `ghalint-config` | Path to ghalint config file (default: `ghalint.{yaml,yml}` or `.ghalint.{yaml,yml}` or `.github/ghalint.{yaml,yml}`) | No | `''` |
| `zizmor-config` | Path to zizmor config file (default: `.github/zizmor.yml` or `zizmor.yml`) | No | `''` |
| `skip-actionlint` | Skip actionlint | No | `false` |
| `skip-ls-lint` | Skip ls-lint | No | `false` |
| `skip-ghalint` | Skip ghalint | No | `false` |
| `skip-zizmor` | Skip zizmor | No | `false` |

## Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| `contents` | `read` | Repository checkout and static analysis by zizmor |
| `pull-requests` | `write` | Posting PR review comments via reviewdog |

## Examples

### Basic Usage (No Config Required)

```yaml
jobs:
  lint:
    permissions:
      contents: read
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/actions-lint.yml@v0
```

### Customized Usage

```yaml
jobs:
  lint:
    permissions:
      contents: read
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/actions-lint.yml@v0
    with:
      reviewdog-reporter: 'github-check'
      ls-lint-config: '.custom-ls-lint.yml'
      ghalint-config: '.ghalint.yaml'
      skip-zizmor: true
```

## Behavior

1. Check out the repository with `actions/checkout@v6` (`persist-credentials: false`)
2. Install aqua with `aquaproj/aqua-installer@v4.0.4`
3. Set up all lint tools (actionlint, reviewdog, ls-lint, ghalint, zizmor) via a dynamically generated aqua configuration — no caller-side `aqua.yaml` required
4. Add aqua's bin path to `$GITHUB_PATH`
5. Run actionlint and pipe results through reviewdog (reporter specified by the `reviewdog-reporter` input). If `actionlint-config` is specified, the given config file is used via `-config-file` flag; otherwise actionlint looks for `.github/actionlint.{yaml,yml}`
6. Prepare ls-lint config with 3-tier fallback: `ls-lint-config` input → caller's `.ls-lint.yml` → default rules (`.github/workflows/*.yml`: kebab-case, `.github/actions/`: kebab-case directories and `action.yml` naming)
7. Run ls-lint with the resolved config
8. Run `ghalint run` for workflow lint. If `ghalint-config` is specified, the given config file is used via `-c` flag; otherwise ghalint looks for `ghalint.{yaml,yml}`, `.ghalint.{yaml,yml}`, or `.github/ghalint.{yaml,yml}`
9. Run `ghalint run-action` for Composite Action lint
10. Run `zizmor --format github` for static security analysis (using `github.token` as `GH_TOKEN`). If `zizmor-config` is specified, the given config file is used via `--config` flag; otherwise zizmor looks for `.github/zizmor.yml` or `zizmor.yml`

## Migration Guide

### Breaking Changes from Previous Version

| Change | Impact | Migration |
|--------|--------|-----------|
| `aqua-version` input removed | Callers specifying this input will get an error | Remove the `aqua-version` input from your workflow |
| GitHub Actions replaced with CLI | Output format may slightly differ | No action needed — CLI produces equivalent output |

### Migration Steps

1. Remove `aqua-version` input if present
2. Remove caller-side `aqua.yaml` if it was only used for ghalint (no longer needed)
3. Remove caller-side `.ls-lint.yml` if it only contained the default kebab-case rules (built-in default now covers this)
4. Optionally add skip or config inputs for fine-grained control
