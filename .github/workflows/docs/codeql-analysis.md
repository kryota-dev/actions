**English** | [日本語](codeql-analysis.ja.md)

# CodeQL Analysis

Security scanning workflow using CodeQL

> Source: [`.github/workflows/codeql-analysis.yml`](../codeql-analysis.yml)

## Usage

```yaml
jobs:
  codeql:
    permissions:
      actions: read
      contents: read
      security-events: write
    uses: kryota-dev/actions/.github/workflows/codeql-analysis.yml@v1
    with:
      # languages - JSON array of languages to analyze
      # Optional (default: '["actions"]')
      languages: '["actions"]'
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `languages` | JSON array of languages to analyze (e.g., `'["javascript", "typescript"]'`) | No | `'["actions"]'` |

## Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| `actions` | `read` | Required for CodeQL analysis execution |
| `contents` | `read` | Repository checkout |
| `security-events` | `write` | Uploading CodeQL analysis results |

## Examples

### Basic Usage

```yaml
jobs:
  codeql:
    permissions:
      actions: read
      contents: read
      security-events: write
    uses: kryota-dev/actions/.github/workflows/codeql-analysis.yml@v1
```

### Advanced Usage

```yaml
jobs:
  codeql:
    permissions:
      actions: read
      contents: read
      security-events: write
    uses: kryota-dev/actions/.github/workflows/codeql-analysis.yml@v1
    with:
      languages: '["javascript", "typescript"]'
```

## Behavior

1. Check out the repository with `actions/checkout@v6` (`persist-credentials: false`)
2. Initialize CodeQL with `github/codeql-action/init@v4.32.4` (using the language from the matrix)
3. Run CodeQL analysis with `github/codeql-action/analyze@v4.32.4`

Jobs run in parallel per language via matrix strategy from the `languages` input JSON array.

<!-- ## Migration Guide -->

<!-- Uncomment and fill in when there are Breaking Changes -->
