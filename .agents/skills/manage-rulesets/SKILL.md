---
name: manage-rulesets
description: Manage GitHub Repository Rulesets (create, update, delete, diff, export). Use when "rulesets" or "branch protection" is mentioned.
---

# GitHub Repository Rulesets Management

Manage GitHub Rulesets using `.github/rulesets/*.json` and the `gh` CLI.

## Prerequisites

- `gh` CLI authenticated with repository admin permissions
- Ruleset JSON files placed in `.github/rulesets/`

## Arguments → Subcommands

| Argument              | Action                                                    |
| --------------------- | --------------------------------------------------------- |
| `apply` / (no args)   | Apply all JSON to GitHub (update existing, create new)   |
| `list`                | Display list of rulesets                                  |
| `delete <name>`       | Delete the specified ruleset                              |
| `delete-all`          | Delete all rulesets                                       |
| `diff`                | Show diff between local JSON and GitHub settings          |
| `export`              | Export GitHub settings to local JSON                      |

## Execution

Run the script from the project root:

```bash
bash .agents/skills/manage-rulesets/scripts/manage-rulesets.sh <subcommand> [args]
```

Prompt the user for confirmation before executing `delete` and `delete-all`.

## API Notes

- `evaluate` enforcement is Enterprise plan only (returns 422 error on free/pro). Only `active` / `disabled` can be used
- Creating a ruleset with a duplicate name returns 422 `Name must be unique` error. The `apply` subcommand searches by name and automatically switches to update if a match is found
- If `diff` shows differences, it may be because the GitHub API adds default values (e.g., `allowed_merge_methods`). Focus on differences in `enforcement`, `rules[].type`, and `conditions`

## Output Format

After operation completion, report results in a table:

```
| Ruleset      | Action  | Result |
|------------- |---------|--------|
| protect-main | Created | OK     |
```
