**English** | [日本語](pnpm-setup.ja.md)

# pnpm-setup

A Composite Action for setting up Node.js and pnpm, and installing dependencies.

> Source: [`.github/actions/pnpm-setup/action.yml`](../pnpm-setup/action.yml)

## Usage

```yaml
- uses: kryota-dev/actions/.github/actions/pnpm-setup@v0
```

## Inputs

| Name      | Required | Default | Description                                                                                                                                                                                                                |
| --------- | -------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `version` | No       | `''`    | pnpm version to install. Leave empty to use the `packageManager` field in `package.json` (recommended). Required only when `package.json` has no `packageManager` field, since pnpm/action-setup v6 makes the version mandatory in that case. |

## Examples

### Basic Usage

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: kryota-dev/actions/.github/actions/pnpm-setup@v0
```

### Pinning an explicit pnpm version

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: kryota-dev/actions/.github/actions/pnpm-setup@v0
    with:
      version: 10
```

## Behavior

1. Install pnpm using `pnpm/action-setup@v6.0.8`. The pnpm version is resolved from the `version` input when provided, otherwise from the `packageManager` field in `package.json` (`run_install: false`)
2. Install Node.js using `actions/setup-node@v6.4.0` (reads version from `.node-version` file)
3. Get the pnpm store path by running `pnpm store path --silent`
4. Cache the pnpm store using `actions/cache@v5.0.5` (key: `{os}-pnpm-store-{hash(pnpm-lock.yaml)}`)
5. Install dependencies by running `pnpm install`

## Prerequisites

- `package.json` must exist in the repository
- `package.json` must contain a `packageManager` field (e.g. `"packageManager": "pnpm@10.0.0"`), or the `version` input must be set. pnpm/action-setup v6 requires the version to be resolvable from one of these sources
- `.node-version` file must exist in the repository
- `pnpm-lock.yaml` must exist in the repository

## Migration Guide

### Upgrading the underlying `pnpm/action-setup` from v5 to v6

pnpm/action-setup v6 changed how the pnpm version is resolved:

- When `package.json` contains a `packageManager` field, the version is read from it and no further action is needed
- When `package.json` does **not** contain a `packageManager` field, a version must be specified explicitly. Set the `version` input (e.g. `version: 10`)

If your pnpm setup starts failing after this upgrade with a missing-version error, add a `packageManager` field to `package.json` or pass the `version` input.
