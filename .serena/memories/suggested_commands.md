# Suggested Commands

## Development Commands

```bash
# Create a new ADR (Architecture Decision Record)
npm run adr:new -- "ADR title"
```

## Linting Commands (CI runs these automatically)

```bash
# Workflow syntax check
aqua exec -- actionlint

# File naming convention check
ls-lint

# Workflow security policy verification (SHA pinning)
aqua exec -- ghalint run

# Composite Action security policy verification
aqua exec -- ghalint run-action

# Static security analysis (template injection, supply chain)
# zizmor is run in CI via npx, not locally
```

## Ruleset Management

```bash
# Apply local JSON rulesets to GitHub
bash .claude/skills/manage-rulesets/scripts/manage-rulesets.sh apply

# Show diff between local JSON and GitHub settings
bash .claude/skills/manage-rulesets/scripts/manage-rulesets.sh diff

# Export GitHub settings to local JSON
bash .claude/skills/manage-rulesets/scripts/manage-rulesets.sh export
```

## System Utilities (Darwin/macOS)

```bash
git       # Version control
ls        # List files
cd        # Change directory
grep      # Search text
find      # Find files
```

## Release Process
Releases are fully automated via tagpr:
1. tagpr creates a release PR with CHANGELOG updates
2. Merging to main auto-creates semantic version tags
3. `bump_major_tag` job updates major tags (v1, v2, etc.)
4. Requires `APP_TOKEN` (PAT) — `GITHUB_TOKEN` is insufficient
