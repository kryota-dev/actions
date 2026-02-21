# 2. Replace PAT with GITHUB_TOKEN for release workflow

Date: 2026-02-21

## Status

2026-02-21 accepted

Supersedes the PAT (`APP_TOKEN`) decision in [ADR-001](001-repository-environment-setup.md).

## Context

The release workflow (`my_release.yml`) previously used a Personal Access Token (`APP_TOKEN`) for tagpr and major tag updates. This caused release PRs and commits to be attributed to the PAT owner's personal account rather than a bot account.

Additionally, the use of `APP_TOKEN` caused tagpr-triggered events to re-trigger workflows, leading to duplicate release PRs being created due to race conditions.

## Decision

Replace `APP_TOKEN` (PAT) with the built-in `GITHUB_TOKEN` (`secrets.GITHUB_TOKEN`) for all operations in `my_release.yml`.

- tagpr PR creation, tagging, and release operations use `GITHUB_TOKEN`
- Major tag update (`bump_major_tag`) uses `GITHUB_TOKEN`
- Checkout steps no longer require explicit `token` parameter

## Consequences

- Release PRs and commits are attributed to `github-actions[bot]` instead of a personal account
- `APP_TOKEN` secret is no longer required for the release workflow
- Events triggered by `GITHUB_TOKEN` do not re-trigger workflows, eliminating the duplicate release PR issue
- CI (`my_test.yml`) will not automatically run on tagpr-created release PRs, since `GITHUB_TOKEN`-triggered events do not trigger other workflows. This is acceptable because release PRs only contain changelog updates, not code changes
