**English** | [日本語](README.ja.md)

# actions

`kryota-dev/actions` is a repository that centrally manages reusable GitHub Actions (Reusable Workflows and Composite Actions).

## Overview

This repository centrally manages and publishes GitHub Actions (Reusable Workflows and Composite Actions) commonly used across multiple repositories, eliminating CI/CD configuration duplication and improving quality and maintainability.

## Usage

To reference a Reusable Workflow from another repository, use the following format:

```yaml
jobs:
  example:
    uses: kryota-dev/actions/.github/workflows/{workflow}.yml@vX
    with:
      # inputs
    secrets:
      # secrets
```

Specify the version using a major tag (e.g., `v1`) or a full version tag (e.g., `v1.0.0`).

### Composite Actions

To reference a Composite Action from another repository, use the following format:

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/{action-name}@vX
    with:
      # inputs
```

Specify the version using a major tag (e.g., `v1`) or a full version tag (e.g., `v1.0.0`).

> **Difference from Reusable Workflows**: Reusable Workflows are called at the `jobs:` level, while Composite Actions are called at the `steps:` level. Composite Actions run as steps within the calling job, enabling more fine-grained reuse.

## Available Workflows & Actions

- **[Reusable Workflows](.github/workflows/README.md)** — List and usage of publicly available workflows
- **[Composite Actions](.github/actions/README.md)** — List and usage of publicly available actions
- **[Internal CI Workflows](.github/workflows/README.md#internal-ci-workflows)** — Internal CI workflows for this repository

## Development

### ADR (Architecture Decision Records)

Design decisions are recorded as ADRs in `docs/adr/`.

To create a new ADR:

```bash
make adr title="ADR title"
```

See [docs/adr/](docs/adr/) for the list of ADRs.

### Workflow Security Policy

All `uses:` references are **pinned to full commit SHAs (40 characters)**:

```yaml
uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
```

SHA pinning is automatically verified in CI by [ghalint](https://github.com/suzuki-shunsuke/ghalint) and [zizmor](https://github.com/zizmorcore/zizmor), and automatically updated by [Renovate Bot](https://docs.renovatebot.com/).

## Manual Setup Required

The following settings must be configured separately via the repository's Web UI or external services:

1. **`APP_TOKEN` secret**: Add a PAT in Settings > Secrets and variables > Actions (requires `repo` and `workflow` scopes)
2. **Renovate Bot installation**: Install [Renovate GitHub App](https://github.com/apps/renovate) on the repository
3. **Enable Dependabot Alerts**: Enable in Settings > Security > Dependabot alerts
