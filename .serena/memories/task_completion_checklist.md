# Task Completion Checklist

When a task is completed, verify the following:

## Before Committing
1. **SHA Pinning**: All `uses:` directives use full 40-char SHA with tag comment
2. **Naming**: All new files follow kebab-case convention
3. **Composite Actions**: Placed in `.github/actions/{name}/action.yml`, NOT in workflows/
4. **ls-lint**: Run `ls-lint` to verify naming conventions
5. **actionlint**: Run `aqua exec -- actionlint` to verify workflow syntax
6. **ghalint**: Run `aqua exec -- ghalint run` and `aqua exec -- ghalint run-action` for security policy

## CI Quality Gates (automatically run on PR)
- actionlint (reviewdog integration)
- ls-lint
- ghalint (run + run-action)
- zizmor (security analysis)
- CodeQL

## If Adding a New Composite Action
1. Create directory: `.github/actions/{action-name}/`
2. Create file: `action.yml` inside that directory
3. Update README.md with usage documentation
4. Ensure ls-lint rules cover the new directory structure

## If Adding a New Reusable Workflow
1. Place in `.github/workflows/` with kebab-case name (no `my-` prefix)
2. Add `on: workflow_call:` trigger with typed inputs/secrets/outputs
3. Set `permissions: {}` at top level, declare job-level permissions
4. Set `timeout-minutes` on all jobs
5. Use `persist-credentials: false` on checkout
6. All `uses:` must be SHA-pinned
7. Create corresponding `my-*.yml` thin wrapper for internal CI usage
8. Update Ruleset required status checks if needed (check name format: `{caller_job} / {callee_job}`)
9. Update README.md with usage documentation

## If Adding a New Internal Workflow
1. Place in `.github/workflows/` with `my-` prefix and kebab-case name
2. Make it a thin wrapper calling the corresponding Reusable Workflow via `uses:`
3. Only define triggers, concurrency, and job-level permissions in the wrapper
4. Ensure all `uses:` are SHA-pinned
