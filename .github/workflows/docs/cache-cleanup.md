**English** | [日本語](cache-cleanup.ja.md)

# Cache Cleanup

Reusable workflow for proactively deleting stale GitHub Actions caches

> Source: [`.github/workflows/cache-cleanup.yml`](../cache-cleanup.yml)

## Usage

```yaml
jobs:
  cleanup:
    permissions:
      actions: write
    uses: kryota-dev/actions/.github/workflows/cache-cleanup.yml@v0
    with:
      # max-age-days - Maximum number of days since last access before a cache is deleted
      # Optional (default: 2)
      max-age-days: 2
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `max-age-days` | Maximum number of days since last access before a cache is deleted | No | `2` |

## Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| `actions` | `write` | Listing and deleting repository caches |

## Examples

### Basic Usage (Scheduled Daily)

```yaml
name: Cache Cleanup
on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch: {}
jobs:
  cleanup:
    permissions:
      actions: write
    uses: kryota-dev/actions/.github/workflows/cache-cleanup.yml@v0
```

### Custom Retention Period

```yaml
name: Cache Cleanup
on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch: {}
jobs:
  cleanup:
    permissions:
      actions: write
    uses: kryota-dev/actions/.github/workflows/cache-cleanup.yml@v0
    with:
      max-age-days: 7
```

## Behavior

1. Paginate through all caches in the calling repository via the GitHub REST API
2. For each cache, compare `last_accessed_at` against the threshold (`now - max-age-days`)
3. Delete every cache whose last access is older than the threshold
4. Log the number of deleted caches

<!-- ## Migration Guide -->

<!-- Uncomment and fill in when there are Breaking Changes -->
