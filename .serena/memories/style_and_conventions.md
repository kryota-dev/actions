# Style and Conventions

## SHA Pinning (Critical)
ALL `uses:` directives MUST use full 40-character commit SHA with tag as comment:
```yaml
uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
```
Enforced by ghalint and zizmor in CI. Renovate Bot auto-updates SHA pins.

## Naming Conventions
- Workflow files: **kebab-case** (e.g., `my-test.yml`, `actions-lint.yml`)
- Internal workflow prefix: `my-` (e.g., `my-test.yml`, `my-release.yml`)
- External Reusable Workflows: no prefix, descriptive names (e.g., `codeql-analysis.yml`, `tagpr-release.yml`)
- Composite Action directories: **kebab-case** (e.g., `pnpm-setup/`)
- Composite Action file name: always `action.yml`
- Enforced by ls-lint in CI

## File Placement
- Workflows → `.github/workflows/`
- Composite Actions → `.github/actions/{action-name}/action.yml`
- NEVER place `action.yml` under `.github/workflows/` (actionlint incompatibility)

## ADR
- Written in English
- Stored in `docs/adr/` with 3-digit numbering (001, 003, 004, ...)
- Created via `npm run adr:new -- "title"`

## Language
- README, CHANGELOG, commit messages: Japanese
- ADR: English
- Workflow comments: English
