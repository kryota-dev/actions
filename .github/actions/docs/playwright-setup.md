**English** | [日本語](playwright-setup.ja.md)

# playwright-setup

A Composite Action for setting up Playwright browsers with caching.

> Source: [`.github/actions/playwright-setup/action.yml`](../playwright-setup/action.yml)

## Usage

```yaml
- uses: kryota-dev/actions/.github/actions/playwright-setup@v0
```

## Inputs

None

## Examples

### Basic Usage

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: kryota-dev/actions/.github/actions/pnpm-setup@v0
  - uses: kryota-dev/actions/.github/actions/playwright-setup@v0
```

## Behavior

1. Get the Playwright version by running `pnpm exec playwright --version` (parsed with `sed 's/Version //'`)
2. Cache Playwright browsers using `actions/cache@v5.0.3` (path: `~/.cache/ms-playwright`, key: `{os}-playwright-{version}`)
3. Only install browsers with `pnpm exec playwright install --with-deps` if the cache was not hit

## Prerequisites

- The `pnpm-setup` action must have been run beforehand (uses `pnpm exec`)
- Playwright must be included in the project's dependencies

<!-- ## Migration Guide -->

<!-- Uncomment and fill in when there are Breaking Changes -->
