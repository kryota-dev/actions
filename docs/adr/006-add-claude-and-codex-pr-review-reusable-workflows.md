# 6. Add Claude and Codex PR review reusable workflows

Date: 2026-06-13

## Status

2026-06-13 accepted

## Context

Automated AI-assisted PR review reduces the burden on human reviewers and catches issues earlier in the development cycle.
Two distinct AI backends are available—Claude (Anthropic) and Codex (OpenAI)—with different authentication models and
capabilities. A consistent posting strategy is needed so that multiple review passes on the same PR do not produce
duplicate or stacked comments.

Key constraints identified during design:

- A reusable workflow cannot version-consistently reference files or composite actions from its own repository at runtime,
  because `./` paths and the `github` context resolve to the **caller's** repository, not the callee's.
- ChatGPT (subscription) cannot be used in CI; Codex requires a metered `OPENAI_API_KEY`.
- Re-runs of the same workflow must not stack redundant summary comments.
- Security principle: the agent that performs analysis must not hold write access to the repository.

## Decision

1. **Two public reusable workflows are added**:
   - `claude-pr-review.yml`: multi-subagent review powered by Claude Code (claude.ai/code).
   - `codex-pr-review.yml`: single-pass review powered by OpenAI Codex CLI.

2. **Authentication**:
   - Claude: accepts either a Pro/Max OAuth token (`claude-code-oauth-token`) or an `anthropic-api-key` secret.
   - Codex: requires a metered `OPENAI_API_KEY`; ChatGPT subscription plans cannot authenticate in CI environments.

3. **Hybrid posting model**:
   - One formal GitHub review is submitted per run, containing inline comments for `critical` and `warning` findings
     only, plus a body table listing **all** findings across all severities.
   - A separate narrative summary comment is upserted via a stable marker tag, so re-runs overwrite the previous
     summary rather than appending a new one.

4. **Strict agent/engine separation (least-privilege)**:
   - The AI agent operates in analysis-only mode; it holds no write token and cannot push to the repository.
   - A deterministic Python engine (not the agent) is responsible for fetching the diff, retrieving prior reviews,
     and posting results to the GitHub API.
   - Required permissions: `contents: read`, `pull-requests: write`, `issues: write`. `id-token` is not requested.

5. **Severity model and de-duplication**:
   - Three severity levels: `critical`, `warning`, `suggestion`. Only `critical` and `warning` produce inline comments.
   - An ordered validity filter rejects out-of-range line numbers and malformed findings before posting.
   - Two-step de-duplication: a mechanical guard (source-tag matching + ±3-line proximity) in the Python engine,
     followed by semantic de-duplication performed by the agent itself. This approach is ported from the
     internal `ci-review` skill.

6. **Embedded engine and prompts via heredoc**:
   - Because of the GitHub Actions path-resolution limitation, the Python engine and system prompts are embedded
     directly inside the reusable workflow YAML as heredoc strings.
   - The canonical source lives in `scripts/pr-review/`; `scripts/pr-review/embed.py` regenerates the embedded
     content and must be run whenever the engine or prompts are updated to keep them in sync.

7. **Dogfooding policy**:
   - Only the Claude workflow is dogfooded via `my-claude-pr-review.yml`, using the OAuth/Max token (zero metered cost).
   - Codex usage in this repository is documented only; no `my-codex-pr-review.yml` wrapper is created to avoid
     metered API charges.
   - The advisory dogfood CI check is **not** added to required status checks, so it cannot block merges.

## Consequences

- **Embedded-engine duplication**: the Python engine and prompts exist in two locations (workflow YAML and
  `scripts/pr-review/`). Maintainers must run `embed.py` after every change to keep them in sync; this is a
  deliberate trade-off against the GitHub Actions path-resolution limitation.
- **Codex residual risks**: absolute line-number accuracy of Codex inline comments must be validated empirically.
  The `codex-version` input should be pinned and updated deliberately to avoid regressions from upstream Codex CLI
  changes.
- **Bedrock / Vertex auth out of scope for v1**: alternative Claude backends (Amazon Bedrock, Google Vertex AI)
  are not supported in this release. Adding them would require additional credential inputs and IAM configuration.
- **No increased blast radius from dogfood check**: because the dogfood job is advisory-only and excluded from
  required status checks, a broken AI review step cannot block legitimate PRs.
- **Cost transparency**: callers of `codex-pr-review.yml` must supply their own `OPENAI_API_KEY` and accept
  associated OpenAI usage charges. The workflow documentation must make this explicit.
