# 4. Composite Actions support

Date: 2026-02-21

## Status

2026-02-21 accepted

## Context

This repository (`kryota-dev/actions`) was initially designed to manage only Reusable Workflows under `.github/workflows/`. However, Reusable Workflows have a limitation: they can only be called at the `jobs:` level, meaning each call creates a separate job.

Composite Actions complement Reusable Workflows by enabling reuse at the `steps:` level within a single job. This provides finer-grained reusability without the overhead of additional job execution.

### Key considerations

- **actionlint incompatibility**: actionlint does not support Composite Action files (`action.yml`). Placing `action.yml` under `.github/workflows/` would cause false lint errors.
- **Directory separation**: Composite Actions must be stored outside `.github/workflows/` to avoid actionlint interference.
- **CI tool coverage**: ghalint (`run-action` command, available since v1.5.1) and zizmor natively support `action.yml` scanning without additional configuration.
- **Renovate compatibility**: Renovate's `github-actions` manager automatically discovers `action.yml` files matching `/(^|/)action\.ya?ml$/`, so `.github/actions/` files are covered by default.
- **ls-lint configuration key bug**: The existing `.ls-lint.yml` used `ls-lint:` as the top-level key, but ls-lint (all versions) requires `ls:`. This was corrected as part of this change.

### Reference

- [Composite Actions directory structure approach](https://zenn.dev/moaikids/articles/32363c5386978e)

## Decision

1. **Directory structure**: Store Composite Actions under `.github/actions/{action-name}/action.yml` (kebab-case naming enforced by ls-lint)
2. **External reference format**: `kryota-dev/actions/.github/actions/{action-name}@{tag-or-sha}`
3. **CI pipeline extension**: Add `ghalint run-action` step to `my-test.yml` for SHA pinning and security policy verification of `action.yml` files
4. **Naming convention unification**: Unify all workflow file naming from snake_case to kebab-case (e.g., `my_test.yml` → `my-test.yml`)
5. **ls-lint configuration fix**: Correct the top-level key from `ls-lint:` to `ls:` and add `.github/actions/` rules (`.dir: kebab-case`, `.yml: regex:action`)
6. **No changes required** for: zizmor (auto-discovers `action.yml`), Renovate (auto-discovers `action.yml`), tagpr/release management (tags apply repository-wide), actionlint (naturally excludes `.github/actions/`)

## Consequences

- Composite Actions are stored under `.github/actions/` with kebab-case directory names
- All workflow files under `.github/workflows/` now use kebab-case naming (breaking change from previous snake_case convention)
- `ghalint run-action` enforces SHA pinning on all `action.yml` files in CI
- ls-lint now correctly validates naming conventions (previous `ls-lint:` key bug is fixed)
- External repositories can reference Composite Actions via `kryota-dev/actions/.github/actions/{action-name}@vX`
- Composite Actions share the same versioning scheme (tagpr) as Reusable Workflows
- ADR 001 is partially superseded: workflow naming convention changed from snake_case to kebab-case
