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
    uses: kryota-dev/actions/.github/workflows/actions-lint.yml@v1
    with:
      # aqua-version - Version of aqua to install for ghalint
      # Optional (default: 'v2.56.6')
      aqua-version: 'v2.56.6'

      # reviewdog-reporter - Reporter type for reviewdog/actionlint
      # Optional (default: 'github-pr-review')
      reviewdog-reporter: 'github-pr-review'
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `aqua-version` | Version of aqua to install for ghalint | No | `'v2.56.6'` |
| `reviewdog-reporter` | Reporter type for reviewdog/actionlint (github-pr-review, github-check, etc.) | No | `'github-pr-review'` |

## Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| `contents` | `read` | Repository checkout and static analysis by zizmor |
| `pull-requests` | `write` | Posting PR review comments via reviewdog |

## Examples

### Basic Usage

```yaml
jobs:
  lint:
    permissions:
      contents: read
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/actions-lint.yml@v1
```

### Advanced Usage

```yaml
jobs:
  lint:
    permissions:
      contents: read
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/actions-lint.yml@v1
    with:
      aqua-version: 'v2.56.6'
      reviewdog-reporter: 'github-check'
```

## Behavior

1. Check out the repository with `actions/checkout@v6` (`persist-credentials: false`)
2. Run actionlint with `reviewdog/action-actionlint@v1.71.0` (reporter specified by the `reviewdog-reporter` input)
3. Check file naming conventions with `ls-lint/action@v2.3.1`
4. Install aqua with `aquaproj/aqua-installer@v4.0.4` (version specified by the `aqua-version` input)
5. Add aqua's bin path to `$GITHUB_PATH`
6. Run workflow lint with `ghalint run`
7. Run Composite Action lint with `ghalint run-action`
8. Set up uv with `astral-sh/setup-uv@v7.3.1`
9. Run static security analysis with `uvx zizmor --format=github .` (using `secrets.GITHUB_TOKEN` as `GH_TOKEN`)

<!-- ## Migration Guide -->

<!-- Uncomment and fill in when there are Breaking Changes -->
