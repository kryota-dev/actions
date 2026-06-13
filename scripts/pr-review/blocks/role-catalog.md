# Reviewer role catalog (single source of truth for Claude)

Select roles by evaluating each `trigger` against the PR's changed files. Launch
only the matching roles (plus an ad-hoc role for a PR-specific concern not
covered below), capped at the configured maximum. Each role becomes one parallel
subagent.

| role | trigger | primary responsibility |
|------|---------|------------------------|
| `correctness` | `always` | logic / runtime / data-consistency bugs |
| `security` | `always` | vulnerabilities, secret leakage, authz, unsafe defaults |
| `performance` | `extensions=.ts,.tsx,.js,.jsx,.go,.rb,.py,.rs,.java,.kt,.sql` | hot paths, N+1, allocations, blocking I/O |
| `tests` | `paths=**/*test*,**/*spec*,**/tests/**,**/__tests__/**` | coverage of new paths, edge/error cases, flakiness |
| `api-interface` | `paths=**/api/**,**/*.proto,**/*.graphql,**/openapi*; extensions=.d.ts` | breaking changes, contract / backward compatibility |
| `docs` | `paths=**/*.md,**/*.mdx; exclude_paths=**/CHANGELOG.md` | documentation accuracy vs. code |
| `github-actions` | `paths=.github/workflows/**,.github/actions/**` | SHA pinning, least-privilege permissions, template injection |

Trigger syntax: `always` | `paths=<glob,...>` | `extensions=<.ext,...>`, with an
optional `; exclude_paths=<glob,...>`. A `paths`/`extensions` trigger fires when
any changed file matches and none match `exclude_paths`.

Add a new perspective by adding a row here (this table is the only place role
selection is defined).
