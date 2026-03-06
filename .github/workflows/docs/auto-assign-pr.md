**English** | [日本語](auto-assign-pr.ja.md)

# Auto Assign PR

Workflow to automatically assign the PR creator as assignee

> Source: [`.github/workflows/auto-assign-pr.yml`](../auto-assign-pr.yml)

## Usage

```yaml
jobs:
  assign:
    permissions:
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/auto-assign-pr.yml@v0
    with:
      # bot-assignees - Comma-separated list of users/teams to assign for Bot PRs (empty = skip)
      # Optional (default: '')
      bot-assignees: ''
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `bot-assignees` | Comma-separated list of users/teams to assign for Bot PRs (empty = skip) | No | `''` |

## Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| `pull-requests` | `write` | Setting assignees via `gh pr edit --add-assignee` |

## Examples

### Basic Usage

```yaml
jobs:
  assign:
    permissions:
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/auto-assign-pr.yml@v0
```

### Advanced Usage

```yaml
jobs:
  assign:
    permissions:
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/auto-assign-pr.yml@v0
    with:
      bot-assignees: 'user1,user2'
```

## Behavior

1. Check if `github.actor` matches the `*[bot]` pattern to determine if it's a Bot
2. For humans: Set the PR creator as assignee via `gh pr edit --add-assignee`
3. For Bots with `bot-assignees` specified: Set each user from the comma-separated list as assignee
4. For Bots without `bot-assignees`: Skip (log output only)

<!-- ## Migration Guide -->

<!-- Uncomment and fill in when there are Breaking Changes -->
