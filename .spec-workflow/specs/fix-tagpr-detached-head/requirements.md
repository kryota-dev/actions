# Requirements Document

## Introduction

Fix the `my-update-release-pr.yml` workflow so that tagpr can successfully re-run when a `tagpr:minor` or `tagpr:major` label is added to a tagpr release PR. Currently, tagpr fails with `fatal: ref HEAD is not a symbolic ref` because the `pull_request` event checks out a merge commit in detached HEAD state.

This blocks the minor/major version bump flow, which is a core part of the release management process.

## Requirements

### Requirement 1: tagpr succeeds on label-triggered re-run

**User Story:** As a repository maintainer, I want tagpr to successfully update the version when I add a `tagpr:minor` or `tagpr:major` label to a release PR, so that the release PR reflects the correct version bump.

#### Acceptance Criteria

1. WHEN `tagpr:minor` label is added to a tagpr release PR THEN the `update-release-pr` workflow SHALL run tagpr successfully without detached HEAD errors
2. WHEN `tagpr:major` label is added to a tagpr release PR THEN the `update-release-pr` workflow SHALL run tagpr successfully without detached HEAD errors
3. WHEN the workflow completes successfully THEN the release PR title and CHANGELOG.md SHALL reflect the correct minor/major version bump

### Requirement 2: Existing release flow remains unaffected

**User Story:** As a repository maintainer, I want the existing `push`-to-`main` release flow (`my-release.yml`) to continue working correctly, so that normal releases are not broken by this fix.

#### Acceptance Criteria

1. WHEN a PR is merged to `main` THEN `my-release.yml` SHALL trigger `tagpr-release.yml` and tagpr SHALL create tags and releases as before
2. WHEN `tagpr-release.yml` is called from `my-release.yml` (push event) THEN `actions/checkout` SHALL check out the `main` branch (default behavior, unchanged)

## Non-Functional Requirements

### Security
- The fix must not weaken the existing permissions model (`permissions: {}` at top level, minimal job-level permissions)
- `APP_TOKEN` secret handling must remain unchanged

### Reliability
- The fix must handle edge cases where the PR head ref might not exist or is stale

### Maintainability
- The fix should follow the existing thin wrapper pattern and not add unnecessary complexity to `tagpr-release.yml`
- SHA pinning conventions must be maintained for any new or modified `uses:` references

## Out of Scope
- Changes to tagpr itself (upstream Songmu/tagpr)
- Changes to the `my-release.yml` workflow (push-to-main trigger)
- Changes to the `bump_major_tag` job
