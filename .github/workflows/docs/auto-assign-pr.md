# auto-assign-pr

> ソースファイル: [`.github/workflows/auto-assign-pr.yml`](../auto-assign-pr.yml)

PR 作成者を自動的に assignee に設定する Reusable Workflow です。通常ユーザーの場合は `gh pr edit` コマンドを使用して PR 作成者（`github.actor`）を assignee に追加します。Bot ユーザーの場合は `bot-assignees` で指定されたユーザーをアサインし、指定がなければスキップします。

## トリガー

`workflow_call`

## Inputs

| 名前 | 型 | 必須 | デフォルト | 説明 |
|---|---|---|---|---|
| `bot-assignees` | `string` | No | `''` | Bot PR 時にアサインするユーザー名（カンマ区切りで複数指定可） |

## Permissions

| 権限 | レベル | 用途 |
|---|---|---|
| `pull-requests` | `write` | PR の assignee 設定 |

## 動作フロー

1. **Bot 判定**: `github.actor` が `[bot]` で終わるかチェック
2. **通常ユーザーの場合**: PR 作成者を assignee に追加
3. **Bot ユーザーの場合**:
   - `bot-assignees` が指定されている → 指定ユーザーを assignee に追加
   - `bot-assignees` が未指定 → アサインをスキップし、ログに通知を出力

## 前提条件

- 呼び出し元ワークフローが `pull_request` イベントの `opened` タイプでトリガーされること

## 使用例

### 基本（Bot PR はスキップ）

```yaml
on:
  pull_request:
    types: [opened]

jobs:
  auto-assign:
    permissions:
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/auto-assign-pr.yml@v1
```

### Bot PR 時に特定ユーザーをアサイン

```yaml
on:
  pull_request:
    types: [opened]

jobs:
  auto-assign:
    permissions:
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/auto-assign-pr.yml@v1
    with:
      bot-assignees: 'your-username'
```

### Bot PR 時に複数ユーザーをアサイン

```yaml
on:
  pull_request:
    types: [opened]

jobs:
  auto-assign:
    permissions:
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/auto-assign-pr.yml@v1
    with:
      bot-assignees: 'user1, user2'
```
