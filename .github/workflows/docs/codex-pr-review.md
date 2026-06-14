**English** | [日本語](codex-pr-review.ja.md)

# Codex PR Review

Reusable workflow that reviews a pull request with [openai/codex-action](https://github.com/openai/codex-action). Unlike the Claude variant, a **single Codex agent** performs the comprehensive review end-to-end — no subagent splitting. It de-duplicates findings against prior reviews, validates each finding, and posts the result as a single review (inline `critical`/`warning` comments + a body listing every finding) plus an upserted marker-tagged summary comment. The posting model, dedup logic, and severity rules (`critical`/`warning`/`suggestion`) are identical to the Claude variant; the key difference is that the Codex action itself does not post — a deterministic step in this workflow handles all GitHub API calls.

> Source: [`.github/workflows/codex-pr-review.yml`](../codex-pr-review.yml)

## Usage

```yaml
name: codex-pr-review
on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]
  issue_comment:
    types: [created]

concurrency:
  group: codex-pr-review-${{ github.event.pull_request.number || github.event.issue.number }}
  cancel-in-progress: true

permissions: {}

jobs:
  review:
    permissions:
      contents: read
      pull-requests: write
      issues: write
    uses: kryota-dev/actions/.github/workflows/codex-pr-review.yml@v0
    secrets:
      openai-api-key: ${{ secrets.OPENAI_API_KEY }}
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `model` | Codex model (empty = action default; e.g. gpt-5.3-codex / gpt-5.5) | No | `'gpt-5.3-codex'` |
| `effort` | Reasoning effort passed to codex-action (e.g. low / medium / high) | No | `'medium'` |
| `sandbox` | codex-action sandbox mode (read-only / workspace-write / danger-full-access) | No | `'read-only'` |
| `codex-version` | Pin `@openai/codex` version for reproducibility (empty = latest) | No | `''` |
| `codex-args` | Extra CLI args forwarded to codex exec | No | `''` |
| `review-instructions-path` | Path in the caller checkout to a `review-rules.md` that overrides the embedded default | No | `''` |
| `additional-instructions` | Extra reviewer instructions appended to the Codex prompt | No | `''` |
| `output-language` | Language for human-readable review text (problem/suggestion/summary); code and identifiers stay unchanged | No | `'English'` |
| `paths` | Comma/newline-separated globs to include (empty = whole diff) | No | `''` |
| `exclude-paths` | Comma/newline-separated globs to exclude from review | No | `''` |
| `max-files` | Warn when the diff touches more than this many files | No | `200` |
| `max-diff-bytes` | Skip the review when the diff is larger than this many bytes | No | `500000` |
| `trigger-phrase` | Phrase required in an `issue_comment` to trigger a re-review | No | `'/codex-review'` |
| `label-name` | Label name that triggers a review on a `labeled` event | No | `'codex-review'` |
| `submit` | Submit the review (`COMMENT`). `false` = leave it pending | No | `true` |
| `review-event` | Review event when submitting (`COMMENT` / `APPROVE` / `REQUEST_CHANGES`) | No | `'COMMENT'` |
| `resolve-addressed` | Resolve our prior inline threads whose code changed and that the reviewer judged addressed. `false` = never auto-resolve | No | `true` |
| `skip-draft` | Skip draft pull requests | No | `true` |
| `skip-bots` | Skip pull requests authored by bots (`*[bot]`) | No | `true` |
| `allowed-bots` | Comma-separated bot logins to review despite `skip-bots` | No | `''` |
| `timeout-minutes` | Job timeout in minutes | No | `20` |

## Secrets

| Name | Description | Required |
|------|-------------|----------|
| `openai-api-key` | OpenAI API key used by codex-action to call the model | Yes |
| `github-token` | Token used to read the diff and post the review/summary. Defaults to the job's `github.token`; supply an app token for a custom comment author | No |

> **A ChatGPT subscription cannot be used in CI; a metered `OPENAI_API_KEY` is required.**

## Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| `contents` | `read` | Check out the PR head and let the agent read related code |
| `pull-requests` | `write` | Read the diff/prior reviews, create the review with inline comments, and resolve addressed threads |
| `issues` | `write` | Upsert the marker-tagged narrative summary comment |

Auto-resolve is gated on each thread's `viewerCanResolve`, so it degrades gracefully if a caller-supplied `github-token` lacks the scope to resolve threads (a warning is logged; the job still succeeds).

## Examples

### Auto-review on every PR with OPENAI_API_KEY

```yaml
jobs:
  review:
    permissions:
      contents: read
      pull-requests: write
      issues: write
    uses: kryota-dev/actions/.github/workflows/codex-pr-review.yml@v0
    secrets:
      openai-api-key: ${{ secrets.OPENAI_API_KEY }}
```

### Opt-in via comment trigger `/codex-review` with effort high

```yaml
on:
  issue_comment:
    types: [created]
jobs:
  review:
    permissions:
      contents: read
      pull-requests: write
      issues: write
    uses: kryota-dev/actions/.github/workflows/codex-pr-review.yml@v0
    with:
      trigger-phrase: '/codex-review'
      effort: 'high'
    secrets:
      openai-api-key: ${{ secrets.OPENAI_API_KEY }}
```

## Behavior

1. **Gate** — resolves the PR number from `pull_request` or `issue_comment` events; for comments it requires the `trigger-phrase` and an OWNER/MEMBER/COLLABORATOR author; honors `skip-draft`/`skip-bots`/`label-name`.
2. **Annotate** — fetches the diff, applies `paths`/`exclude-paths`, skips when empty or larger than `max-diff-bytes`, and annotates every line with its absolute number so the model cites real lines.
3. **Prior reviews** — collects existing reviews/comments/threads (excluding common bot boilerplate) for de-duplication.
4. **Codex single review** — assembles a single prompt (review rules + prior reviews JSON + annotated diff) and invokes `openai/codex-action` with `--output-schema` and `--output-file` so the agent emits a structured findings JSON directly. No subagents are spawned; one Codex agent handles the full review.
5. **Post** — a deterministic step (the Codex action itself does not post) validates each finding's line against the diff (non-mappable findings become body-only), applies a mechanical dedup guard, creates one review (inline `critical`/`warning` + a body table of all findings) and submits it (when `submit: true`), then upserts a `<!-- codex-pr-review -->` summary comment.
6. **Auto-resolve** (when `resolve-addressed: true`) — silently resolves the workflow's own prior inline threads that pass **both** a mechanical gate (the thread is ours, unresolved, line-anchored, resolvable, and GitHub reports it `isOutdated` — i.e. the flagged lines changed) **and** the reviewer's judgment (it listed the thread as addressed). The hybrid AND avoids closing still-valid issues; if an issue actually persists Codex re-posts it fresh. Each resolve is best-effort (a failure logs a warning and never fails the job).

Re-runs replace the summary comment in place; inline comments are de-duplicated so they do not stack, and addressed threads are resolved instead of re-posted.

> **Note:** Pin `codex-version` for reproducibility. Some versions of the action ignore `--output-schema` when tools are active; pinning to a known-good version avoids unexpected output format changes.

## Prerequisites

- An `openai-api-key` secret is **required**. A ChatGPT subscription cannot be used in CI — you must supply a metered API key from [platform.openai.com](https://platform.openai.com/).
- Pin `codex-version` to a specific release for reproducible reviews; leaving it empty uses the latest version, which may change behavior across runs.
- The caller wires the GitHub events it wants (`pull_request`, `issue_comment`, and/or `labeled`); the workflow resolves and gates all three internally.
