# Codebase Structure

```
.github/
├── workflows/           # Reusable Workflows + Internal CI (my-* prefix thin wrappers)
│   ├── actions-lint.yml       # [Reusable] Quality gate (actionlint/ls-lint/ghalint/zizmor)
│   ├── auto-assign-pr.yml    # [Reusable] Auto-assign PR creator
│   ├── codeql-analysis.yml   # [Reusable] CodeQL security scanning
│   ├── tagpr-release.yml     # [Reusable] tagpr release + major tag bump
│   ├── my-test.yml            # [Internal] Thin wrapper → actions-lint.yml
│   ├── my-release.yml         # [Internal] Thin wrapper → tagpr-release.yml
│   ├── my-setup-pr.yml        # [Internal] Thin wrapper → auto-assign-pr.yml
│   └── my-codeql.yml          # [Internal] Thin wrapper → codeql-analysis.yml
├── composite/           # Composite Actions (externally consumable)
│   ├── pnpm-setup/action.yml
│   ├── playwright-setup/action.yml
│   ├── slack-notify-success/action.yml
│   └── slack-notify-failure/action.yml
├── rulesets/            # Branch/tag protection rules (JSON)
│   ├── protect-main.json
│   ├── protect-version-tags.json
│   └── protect-major-tags.json
└── CODEOWNERS

docs/adr/               # Architecture Decision Records
.spec-workflow/          # Spec Workflow specifications and approvals
```

## Key Directories
- `.github/workflows/` — Reusable Workflows (workflow_call) + Internal CI thin wrappers (my-* prefix). actionlint scans this
- `.github/actions/` — Composite Actions (actionlint does NOT scan this, by design)
- `.github/rulesets/` — Repository protection rules as JSON
- `docs/adr/` — Architecture Decision Records (English)
