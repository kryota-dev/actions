**English** | [日本語](pnpm-setup.ja.md)

# pnpm-setup

A Composite Action for setting up Node.js and pnpm, and installing dependencies.

> Source: [`.github/actions/pnpm-setup/action.yml`](../pnpm-setup/action.yml)

## Usage

```yaml
- uses: kryota-dev/actions/.github/actions/pnpm-setup@v0
```

## Inputs

None

## Examples

### Basic Usage

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: kryota-dev/actions/.github/actions/pnpm-setup@v0
```

## Behavior

1. Install pnpm using `pnpm/action-setup@v4.2.0` (references `package.json`, `run_install: false`)
2. Install Node.js using `actions/setup-node@v6.3.0` (reads version from `.node-version` file)
3. Get the pnpm store path by running `pnpm store path --silent`
4. Cache the pnpm store using `actions/cache@v5.0.3` (key: `{os}-pnpm-store-{hash(pnpm-lock.yaml)}`)
5. Install dependencies by running `pnpm install`

## Prerequisites

- `package.json` must exist in the repository
- `.node-version` file must exist in the repository
- `pnpm-lock.yaml` must exist in the repository

<!-- ## Migration Guide -->

<!-- Uncomment and fill in when there are Breaking Changes -->
