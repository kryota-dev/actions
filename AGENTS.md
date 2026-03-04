# AGENTS.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

A repository for centrally managing and publishing reusable GitHub Actions (Reusable Workflows and Composite Actions). There is no TypeScript/JavaScript source code; GitHub Actions YAML files are the primary artifacts.

## Commands

```bash
# Create a new ADR (Architecture Decision Record)
npm run adr:new -- "ADR title"

# Lint (auto-run in CI; run locally via aqua)
aqua exec -- actionlint           # Workflow syntax check
ls-lint                           # File naming convention check
aqua exec -- ghalint run          # Workflow security verification
aqua exec -- ghalint run-action   # Composite Action security verification

# Ruleset management (.github/rulesets/*.json ↔ GitHub API)
bash .agents/skills/manage-rulesets/scripts/manage-rulesets.sh apply   # Apply local JSON to GitHub
bash .agents/skills/manage-rulesets/scripts/manage-rulesets.sh diff    # Diff between local and GitHub
bash .agents/skills/manage-rulesets/scripts/manage-rulesets.sh export  # Export GitHub settings to local
```

## Architecture

### Directory Structure

- `.github/workflows/` — Publicly available Reusable Workflows + internal CI workflows (`my-` prefix)
- `.github/actions/{action-name}/action.yml` — Publicly available Composite Actions
- `.github/rulesets/` — Branch and tag protection rules (JSON, synced with GitHub via `manage-rulesets` script)
- `docs/adr/` — Architecture Decision Records

### Reusable Workflows vs Composite Actions

- **Reusable Workflows** (`.github/workflows/`): Called at the `jobs:` level. Runs as a separate job. Has a `workflow_call` trigger
- **Composite Actions** (`.github/actions/`): Called at the `steps:` level. Runs as a step within the calling job

### Internal CI Thin Wrapper Pattern

Internal CI workflows (`my-*.yml`) are thin wrappers that call Reusable Workflows via `uses:`. They only contain triggers, concurrency, and permissions; logic is delegated to the Reusable Workflow:

```yaml
# my-test.yml (wrapper) → actions-lint.yml (Reusable Workflow)
jobs:
  lint:
    permissions:
      contents: read
      pull-requests: write
    uses: ./.github/workflows/actions-lint.yml
```

**Note**: When calling a Reusable Workflow via `uses:`, the check name becomes `{caller job name} / {callee job name}` (e.g., `lint / lint`). Required status check names in Rulesets must also use this format.

### Permissions Inheritance

In Reusable Workflows, the caller's job-level `permissions` serve as the upper boundary. The callee can only have permissions within that scope. The top level must always be `permissions: {}`, with minimum required permissions declared at the job level.

### Release Management

tagpr automatically creates release PRs based on CHANGELOG.md and assigns semantic version tags upon merging to main. The `bump_major_tag` job also updates major tags (v1, v2, etc.). `APP_TOKEN` (PAT) is required (`GITHUB_TOKEN` is insufficient).

## Mandatory Rules

### SHA Pinning

All `uses:` references must be **pinned to full commit SHAs (40 characters)** with the tag noted in a comment:

```yaml
uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
```

ghalint and zizmor automatically verify in CI. Renovate Bot (`helpers:pinGitHubActionDigests` preset) handles automatic updates.

### Naming Conventions

- Workflow files: **kebab-case** (e.g., `my-test.yml`, `actions-lint.yml`)
- Internal CI: `my-` prefix required (e.g., `my-test.yml`)
- Public Reusable Workflows: No prefix, descriptive names (e.g., `codeql-analysis.yml`, `tagpr-release.yml`)
- Composite Action directories: **kebab-case** (e.g., `pnpm-setup/`)
- Composite Action filename: Fixed as `action.yml`
- ls-lint automatically verifies in CI

### actionlint and Composite Actions Incompatibility

actionlint does not support `action.yml`. Composite Actions are placed in `.github/actions/` to be excluded from actionlint's scope. Never place them in `.github/workflows/`.

### CI Quality Gates

The following are automatically run on PRs:

- **actionlint**: Workflow syntax check (reviewdog integration)
- **ls-lint**: File naming convention check
- **ghalint**: SHA pinning and security policy verification
- **zizmor**: Static security analysis (template injection, etc.)
- **CodeQL**: Security scanning
