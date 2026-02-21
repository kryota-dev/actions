# 3. Branch ruleset

Date: 2026-02-21

## Status

2026-02-21 accepted

## Context

Repository `kryota-dev/actions` manages reusable GitHub Actions workflows.
External repositories reference workflows via tags (e.g., `uses: kryota-dev/actions/.github/workflows/xxx.yml@v1.2.3`).
To maintain reliability of these references, the main branch and release tags must be protected from accidental deletion or modification.

The following automated tools operate in this repository:

- **tagpr**: Creates release PRs and pushes new version tags (e.g., `v1.2.3`) as `github-actions[bot]`
- **bump_major_tag**: Force-pushes major tags (e.g., `v1`) to point to the latest release, as `github-actions[bot]`
- **Renovate Bot**: Creates and updates dependency update PRs only

**Personal repository constraint**: GitHub's documentation states that "Actors may only be added to bypass lists when the repository belongs to an organization."
As a personal repository (`kryota-dev/actions`), bypass actors (Apps, Teams, etc.) cannot be added to ruleset bypass lists.
This means the initially intended design of registering `github-actions[bot]` as a bypass actor is not feasible.

The repository owner (human account) always bypasses rulesets as an administrator on personal repositories.
However, `github-actions[bot]` (used by tagpr and bump_major_tag) is a separate actor without administrator privileges and is subject to ruleset restrictions.

## Decision

Adopt three rulesets managed as JSON files in `.github/rulesets/`, applying a staged protection approach (Option C) that avoids blocking automated release tooling:

1. **protect-main** (`protect-main.json`):
   Targets the `main` branch. Prevents deletion (`deletion` rule) and force push (`non_fast_forward` rule).
   PR requirement is intentionally omitted because bypass actors cannot be configured on personal repositories,
   which would block tagpr's direct push to main during the release flow.

2. **protect-version-tags** (`protect-version-tags.json`):
   Targets tags matching `refs/tags/v*.*.*`. Prevents deletion and force push of version tags such as `v1.2.3`.
   New tag creation (used by tagpr) is not subject to `deletion` or `non_fast_forward` rules,
   so the release flow is unaffected.

3. **protect-major-tags** (`protect-major-tags.json`):
   Targets tags matching `refs/tags/v[0-9]*` (covers `v1`, `v2`, ..., `v10`, `v99`, and beyond).
   Prevents deletion only. The `non_fast_forward` rule is intentionally excluded to allow
   `bump_major_tag` workflow to force-push major tags without being blocked.

Ruleset JSON files are version-controlled in `.github/rulesets/` and applied via `gh api` or GitHub UI import
after merging to main. This enables IaC-style management with change history tracked in Git.

## Consequences

- The tagpr release flow (main push → release PR creation → merge → new vX.Y.Z tag) is unaffected.
- The `bump_major_tag` workflow force-pushing vX tags is permitted by the absence of `non_fast_forward` in protect-major-tags.
- Renovate Bot's PR-only workflow is unaffected.
- PR requirement for main is **NOT enforced**; this is a known limitation of personal repositories where bypass actors cannot be configured.
- Ruleset changes follow the flow: edit JSON file → PR review → merge to main → manual `gh api` import.
- If the repository is transferred to an organization, bypass actors (e.g., `github-actions[bot]`) can be added to ruleset bypass lists, enabling PR requirement enforcement for main while preserving the automated release flow.
