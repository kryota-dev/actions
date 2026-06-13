**English** | [日本語](claude-pr-review.ja.md)

# Claude PR Review

Reusable workflow that reviews a pull request with [Claude Code GitHub Actions](https://github.com/anthropics/claude-code-action). A main agent dynamically assigns role-specialized review subagents, runs them in parallel, integrates and de-duplicates their findings against prior reviews, validates each finding, and posts the result as a single review (inline `critical`/`warning` comments + a body listing every finding) plus an upserted narrative summary comment.

> Source: [`.github/workflows/claude-pr-review.yml`](../claude-pr-review.yml)

## Usage

```yaml
name: claude-pr-review
on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]
  issue_comment:
    types: [created]

concurrency:
  group: claude-pr-review-${{ github.event.pull_request.number || github.event.issue.number }}
  cancel-in-progress: true

permissions: {}

jobs:
  review:
    permissions:
      contents: read
      pull-requests: write
      issues: write
    uses: kryota-dev/actions/.github/workflows/claude-pr-review.yml@v0
    secrets:
      claude-code-oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `model` | Claude model passed to claude-code-action via `--model` | No | `'claude-sonnet-4-6'` |
| `max-review-agents` | Maximum number of parallel review subagents | No | `3` |
| `review-roles` | Comma-separated fixed reviewer roles (empty = auto-select from the role catalog) | No | `''` |
| `role-prompts-dir` | Directory in the caller checkout holding override prompt files (`role-catalog.md`) | No | `''` |
| `review-instructions-path` | Path in the caller checkout to a `review-rules.md` that overrides the embedded default | No | `''` |
| `additional-instructions` | Extra reviewer instructions appended to the orchestration prompt | No | `''` |
| `output-language` | Language for human-readable review text (problem/suggestion/summary); code and identifiers stay unchanged | No | `'English'` |
| `claude-args` | Extra CLI args appended to `claude_args` | No | `''` |
| `paths` | Comma/newline-separated globs to include (empty = whole diff) | No | `''` |
| `exclude-paths` | Comma/newline-separated globs to exclude from review | No | `''` |
| `max-files` | Warn when the diff touches more than this many files | No | `200` |
| `max-diff-bytes` | Skip the review when the diff is larger than this many bytes | No | `500000` |
| `trigger-phrase` | Phrase required in an `issue_comment` to trigger a re-review | No | `'/claude-review'` |
| `label-name` | Label name that triggers a review on a `labeled` event | No | `'claude-review'` |
| `submit` | Submit the review (`COMMENT`). `false` = leave it pending | No | `true` |
| `review-event` | Review event when submitting (`COMMENT` / `APPROVE` / `REQUEST_CHANGES`) | No | `'COMMENT'` |
| `skip-draft` | Skip draft pull requests | No | `true` |
| `skip-bots` | Skip pull requests authored by bots (`*[bot]`) | No | `true` |
| `allowed-bots` | Comma-separated bot logins to review despite `skip-bots` | No | `''` |
| `timeout-minutes` | Job timeout in minutes | No | `30` |
| `debug` | Show full agent output and pass `--debug` to Claude (for troubleshooting) | No | `false` |

## Secrets

| Name | Description | Required |
|------|-------------|----------|
| `claude-code-oauth-token` | Claude Pro/Max OAuth token (`claude setup-token`). Preferred — uses the subscription, no metered API cost | No\* |
| `anthropic-api-key` | Anthropic API key (metered). Alternative to the OAuth token | No\* |
| `github-token` | Token used to read the diff and post the review/summary. Defaults to the job's `github.token`; supply an app token for a custom comment author | No |

\* Provide **at least one** of `claude-code-oauth-token` or `anthropic-api-key`; the workflow fails fast if neither is set.

## Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| `contents` | `read` | Check out the PR head and let the agent read related code |
| `pull-requests` | `write` | Read the diff/prior reviews and create the review with inline comments |
| `issues` | `write` | Upsert the marker-tagged narrative summary comment |

## Examples

### Auto-review on every PR (Claude Max via OAuth)

```yaml
jobs:
  review:
    permissions:
      contents: read
      pull-requests: write
      issues: write
    uses: kryota-dev/actions/.github/workflows/claude-pr-review.yml@v0
    secrets:
      claude-code-oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
```

### Opt-in via a label, with a fixed role set and Opus

```yaml
on:
  pull_request:
    types: [labeled]
jobs:
  review:
    if: github.event.label.name == 'ai-review'
    permissions:
      contents: read
      pull-requests: write
      issues: write
    uses: kryota-dev/actions/.github/workflows/claude-pr-review.yml@v0
    with:
      label-name: 'ai-review'
      model: 'claude-opus-4-8'
      review-roles: 'security,correctness,tests'
      submit: false
    secrets:
      anthropic-api-key: ${{ secrets.ANTHROPIC_API_KEY }}
```

## Behavior

1. **Gate** — resolves the PR number from `pull_request` or `issue_comment` events; for comments it requires the `trigger-phrase` and an OWNER/MEMBER/COLLABORATOR author; honors `skip-draft`/`skip-bots`/`label-name`.
2. **Annotate** — fetches the diff, applies `paths`/`exclude-paths`, skips when empty or larger than `max-diff-bytes`, and annotates every line with its absolute number so the model cites real lines.
3. **Prior reviews** — collects existing reviews/comments/threads (excluding common bot boilerplate) for de-duplication.
4. **Review** — the main agent selects roles from the embedded catalog (or `review-roles`), spawns up to `max-review-agents` parallel subagents, integrates, semantically de-duplicates, validates, and emits a structured findings JSON.
5. **Post** — a deterministic step validates each finding's line against the diff (non-mappable findings become body-only), applies a mechanical dedup guard, creates one review (inline `critical`/`warning` + a body table of all findings) and submits it (when `submit: true`), then upserts a `<!-- claude-pr-review -->` summary comment.

Re-runs replace the summary comment in place; inline comments are de-duplicated so they do not stack.

## Prerequisites

- A `claude-code-oauth-token` **or** `anthropic-api-key` secret.
- The caller wires the GitHub events it wants (`pull_request`, `issue_comment`, and/or `labeled`); the workflow resolves and gates all three internally.
