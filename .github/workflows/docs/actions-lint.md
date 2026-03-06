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
    uses: kryota-dev/actions/.github/workflows/actions-lint.yml@v2
    with:
      # reviewdog-reporter - Reporter type for actionlint
      # Optional (default: 'github-pr-review')
      reviewdog-reporter: 'github-pr-review'
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `reviewdog-reporter` | Reporter type for actionlint (github-pr-review, github-check, etc.) | No | `'github-pr-review'` |
| `actionlint-config` | Path to actionlint config file (default: auto-detect) | No | `''` |
| `ls-lint-config` | Path to ls-lint config file (default: `.ls-lint.yml` if present, otherwise built-in default) | No | `''` |
| `ghalint-config` | Path to ghalint config file (default: auto-detect) | No | `''` |
| `zizmor-config` | Path to zizmor config file (default: auto-detect) | No | `''` |
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
    uses: kryota-dev/actions/.github/workflows/actions-lint.yml@v2
```

### Customized Usage

```yaml
jobs:
  lint:
    permissions:
      contents: read
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/actions-lint.yml@v2
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
5. Run actionlint and pipe results through reviewdog (reporter specified by the `reviewdog-reporter` input). If `actionlint-config` is specified, the given config file is used via `-config-file` flag; otherwise actionlint auto-detects `.github/actionlint.{yaml,yml}`
6. Prepare ls-lint config with 3-tier fallback: `ls-lint-config` input → caller's `.ls-lint.yml` → built-in default config (kebab-case rules for `.github/workflows` and `.github/actions`)
7. Run ls-lint with the resolved config
8. Run `ghalint run` for workflow lint. If `ghalint-config` is specified, the given config file is used via `-c` flag; otherwise ghalint auto-detects from standard locations
9. Run `ghalint run-action` for Composite Action lint
10. Run `zizmor --format github` for static security analysis (using `github.token` as `GH_TOKEN`). If `zizmor-config` is specified, the given config file is used via `--config` flag; otherwise zizmor auto-detects from standard locations

## Migration Guide (v1 → v2)

### Breaking Changes

| Change | Impact | Migration |
|--------|--------|-----------|
| `aqua-version` input removed | Callers specifying this input will get an error | Remove the `aqua-version` input from your workflow |
| GitHub Actions replaced with CLI | Output format may slightly differ | No action needed — CLI produces equivalent output |

### Migration Steps

1. Update the version tag from `@v1` to `@v2`
2. Remove `aqua-version` input if present
3. Remove caller-side `aqua.yaml` if it was only used for ghalint (no longer needed)
4. Remove caller-side `.ls-lint.yml` if it only contained the default kebab-case rules (built-in default now covers this)
5. Optionally add skip or config inputs for fine-grained control
