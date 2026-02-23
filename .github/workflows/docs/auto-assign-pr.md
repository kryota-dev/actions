# auto-assign-pr

> ソースファイル: [`.github/workflows/auto-assign-pr.yml`](../auto-assign-pr.yml)

PR 作成者を自動的に assignee に設定する Reusable Workflow です。`gh pr edit` コマンドを使用して PR 作成者（`github.actor`）を assignee に追加します。

## トリガー

`workflow_call`

## Inputs

なし

## Permissions

| 権限 | レベル | 用途 |
|---|---|---|
| `pull-requests` | `write` | PR の assignee 設定 |

## 前提条件

- 呼び出し元ワークフローが `pull_request` イベントの `opened` タイプでトリガーされること

## 使用例

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
