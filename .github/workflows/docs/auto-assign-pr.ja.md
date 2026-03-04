[English](auto-assign-pr.md) | **日本語**

# Auto Assign PR

PR 作成者を自動的に assignee として設定するワークフロー

> Source: [`.github/workflows/auto-assign-pr.yml`](../auto-assign-pr.yml)

## Usage

```yaml
jobs:
  assign:
    permissions:
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/auto-assign-pr.yml@v1
    with:
      # bot-assignees - Bot PR 時に割り当てるユーザー/チームのカンマ区切りリスト（空 = スキップ）
      # Optional (default: '')
      bot-assignees: ''
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `bot-assignees` | Bot PR 時に割り当てるユーザー/チームのカンマ区切りリスト（空 = スキップ） | No | `''` |

## Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| `pull-requests` | `write` | `gh pr edit --add-assignee` による assignee の設定 |

## Examples

### 基本的な使い方

```yaml
jobs:
  assign:
    permissions:
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/auto-assign-pr.yml@v1
```

### 応用例

```yaml
jobs:
  assign:
    permissions:
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/auto-assign-pr.yml@v1
    with:
      bot-assignees: 'user1,user2'
```

## Behavior

1. `github.actor` が `*[bot]` パターンに一致するかチェックし、Bot かどうかを判定
2. 人間の場合: `gh pr edit --add-assignee` で PR 作成者を assignee に設定
3. Bot かつ `bot-assignees` が指定されている場合: カンマ区切りで各ユーザーを assignee に設定
4. Bot かつ `bot-assignees` が未指定の場合: スキップ（ログ出力のみ）

<!-- ## Migration Guide -->

<!-- Breaking Changes がある場合にコメントアウトを解除して記載する -->
