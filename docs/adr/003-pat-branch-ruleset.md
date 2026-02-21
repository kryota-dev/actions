# 3. PAT-based branch ruleset

Date: 2026-02-21

## Status

2026-02-21 accepted

## Context

This repository (`kryota-dev/actions`) manages reusable GitHub Actions workflows and requires strong branch and tag protection to ensure code quality and release integrity.

### Background: GITHUB_TOKEN Approach and Its Limitations

PR #13 attempted to migrate the release workflow (`my_release.yml`) from PAT (`APP_TOKEN`) to `GITHUB_TOKEN` (`github-actions[bot]`). However, this was reverted in PR #16 due to the following constraints in the branch ruleset design:

- **Personal repository bypass actor limitation**: GitHub's ruleset `bypass_actors` configuration for personal repositories does not support `github-actions[bot]` as a bypass actor in a way that allows it to bypass `pull_request` and `required_status_checks` rules.
- **Consequence**: With `GITHUB_TOKEN`, it was impossible to enforce both:
  - PR-required pushes to `main` (tagpr needs direct push access)
  - Required status checks (tagpr and `bump_major_tag` would be blocked)
- As a result, the previous design (spec: `branch-ruleset`) was limited to weak protection: only `deletion` and `non_fast_forward` rules without PR enforcement or status checks.

### PAT-based Approach

With the revert to PAT (`APP_TOKEN`) in PR #16, the following constraint is resolved:

- **PAT authenticates as the repository owner**: In a personal repository, the owner always has administrator privileges by GitHub's specification.
- **Administrator bypass**: Repository owners (including operations using PAT) can bypass all ruleset restrictions without explicit `bypass_actors` configuration.
- **Result**: Strong protection is now achievable — PR enforcement, required status checks, and history protection — while still allowing automated release workflows (tagpr, `bump_major_tag`) to operate without restriction.

## Decision

Design three rulesets as JSON files under `.github/rulesets/` (IaC):

### 1. `protect-main.json` — Main Branch Protection

- **Target**: `refs/heads/main`
- **Rules**:
  - `deletion`: Prevent branch deletion
  - `non_fast_forward`: Prevent force pushes and history rewrites
  - `required_linear_history`: Allow only squash or rebase merges (no merge commits)
  - `pull_request`: Require PR for all changes (direct push prohibited)
  - `required_status_checks`: Require CI checks to pass before merge
    - `lint` — from `my_test.yml` (actionlint + ls-lint + ghalint + zizmor)
    - `analyze (actions)` — from `my_codeql.yml` (matrix job, hence the `(actions)` suffix)
- **`required_approving_review_count: 0`**: GitHub's specification prevents PR authors from approving their own PRs. In a personal repository where the owner is the sole contributor, setting this to 1 or more would permanently block merges. Setting to 0 enforces the PR workflow (visible history, CI checks) without requiring self-approval.
- **`bypass_actors: []`**: Explicit bypass actors are not needed. The repository owner (PAT) bypasses rulesets by GitHub's administrator privilege specification.

### 2. `protect-version-tags.json` — Version Tag Protection

- **Target**: `refs/tags/v*.*.*` (fnmatch: `*` matches any string including dots, covering `v1.2.3`, `v10.0.0`, etc.)
- **Rules**:
  - `deletion`: Prevent tag deletion
  - `non_fast_forward`: Prevent force pushes to version tags
- **Rationale**: Published version tags (`vX.Y.Z`) must be immutable to ensure reliability for external repositories that pin to specific versions.

### 3. `protect-major-tags.json` — Major Tag Protection

- **Target**: `refs/tags/v[0-9]*` (covers `v1`, `v2`, `v10`, `v11`, etc.)
- **Rules**:
  - `deletion`: Prevent tag deletion only
  - `non_fast_forward`: **Intentionally excluded** to allow `bump_major_tag` to update major tags via `git push origin "$MAJOR" --force`
- **Pattern overlap**: `v1.0.0` matches both `v*.*.*` and `v[0-9]*`. GitHub applies all matching rulesets with logical OR (most restrictive wins). The `non_fast_forward` rule from `protect-version-tags` blocks force pushes on `v1.0.0`-style tags, which is the intended behavior. Major tags (`v1`, without patch version) only match `protect-major-tags`, allowing force push for updates.

## Consequences

- Direct pushes to `main` are blocked for non-owner contributors; PRs are required
- CI checks (`lint`, `analyze (actions)`) must pass before any PR can be merged into `main`
- Published version tags (`vX.Y.Z`) cannot be deleted or modified by anyone except the repository owner
- Major tags (`v1`, `v2`, etc.) cannot be deleted but can be force-pushed (required for `bump_major_tag`)
- Release automation (tagpr, `bump_major_tag`) continues to function without modification, as PAT operations bypass ruleset restrictions via administrator privileges
- Renovate Bot dependency update PRs are subject to required status checks, ensuring only CI-passing updates are merged
- The ruleset JSON files serve as IaC documentation; applying them to GitHub requires manual import via Web UI or GitHub CLI (`gh api --input`)
