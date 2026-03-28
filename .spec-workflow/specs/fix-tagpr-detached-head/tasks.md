# Tasks

## Task 1: Add `ref` input to `tagpr-release.yml`

- [x] Add optional `ref` input to `workflow_call` and use it in the `tagpr` job's checkout step
- **File:** `.github/workflows/tagpr-release.yml`
- **Purpose:** Allow callers to specify a git ref for checkout, fixing the detached HEAD issue when called from `pull_request` events
- **Leverage:** Existing `ref-name` input pattern in `deploy-web-hosting.yml`
- **Requirements:** Requirement 1 (tagpr succeeds on label-triggered re-run), Requirement 2 (existing flow unaffected)

## Task 2: Pass `ref` input from `my-update-release-pr.yml`

- [x] Add `with: ref:` parameter when calling `tagpr-release.yml` to pass the PR head branch
- **File:** `.github/workflows/my-update-release-pr.yml`
- **Purpose:** Provide the PR head branch ref to `tagpr-release.yml` so checkout targets the actual branch instead of the merge commit
- **Leverage:** Existing `my-update-release-pr.yml` structure
- **Requirements:** Requirement 1 (tagpr succeeds on label-triggered re-run)

## Task 3: Update workflow documentation

- [x] Update `tagpr-release.md` documentation to reflect the new `ref` input parameter
- **File:** `.github/workflows/docs/tagpr-release.md`
- **Purpose:** Keep documentation in sync with the workflow interface change
- **Leverage:** Existing docs structure in `.github/workflows/docs/`
- **Requirements:** Non-functional (maintainability)
