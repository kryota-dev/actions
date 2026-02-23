# Project Overview

## Purpose
`kryota-dev/actions` is a repository that centrally manages and publishes reusable GitHub Actions (Reusable Workflows and Composite Actions) for use across multiple repositories.

## Tech Stack
- **Primary language**: YAML (GitHub Actions workflow/action definitions)
- **Package manager**: pnpm (for development tooling only)
- **Version management**: tagpr (semantic versioning, auto-release)
- **Dependency updates**: Renovate Bot (with SHA pinning preset)
- **Tool management**: aqua (for ghalint)
- **ADR tool**: adr (npm package)

## No Application Code
This repository does not contain TypeScript/JavaScript application code. The deliverables are GitHub Actions YAML files.

## Architecture Pattern
Internal CI workflows (`my-*`) are thin wrappers that call Reusable Workflows via `uses:`. This avoids code duplication — logic lives in the Reusable Workflow, wrappers only define triggers/concurrency/permissions.

**Important**: When calling a Reusable Workflow via `uses:`, the check name becomes `{caller_job} / {callee_job}` (e.g., `lint / lint`). Rulesets must use this format for required status checks.

## Current Version
v0.0.5 (as of 2026-02-24)

## License
MIT
