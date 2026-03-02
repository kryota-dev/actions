# undeploy-web-hosting

> ソースファイル: [`.github/workflows/undeploy-web-hosting.yml`](../undeploy-web-hosting.yml)

Web ホスティングサーバー上のフィーチャー環境を FTP または rsync で削除する Reusable Workflow です。PR コメントで削除結果を通知し、デプロイ済みコメントの非表示も自動実行します。

削除対象パスは `github` コンテキストから自動的に計算されます（内部で `compute-web-hosting-deploy-path` Composite Action を使用）。

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `deploy-type` | デプロイ方式 (`'ftp'` or `'rsync'`) | Yes | - |
| `base-path-prefix` | プロジェクト固有パスプレフィックス（例: `/<your-project>`） | No | `''` |
| `ref-name` | ブランチ名オーバーライド（未指定時は `github` コンテキストから自動導出） | No | `''` |
| `dry-run` | dry-run モード | No | `'false'` |

## Secrets

| Name | Description | Required |
|------|-------------|----------|
| `server-host` | サーバーホスト | Yes |
| `server-user` | サーバーユーザー | Yes |
| `server-password` | FTP パスワード | No |
| `ssh-private-key` | SSH 秘密鍵 | No |
| `server-path` | サーバー上のパス | Yes |

## 動作フロー

1. 削除対象パスの計算（`compute-web-hosting-deploy-path` で `github` コンテキストから自動導出）
2. FTP/rsync で対象ディレクトリを削除（Composite Action 経由）
3. PR コメント投稿（成功/失敗）
4. 過去の失敗コメント非表示
5. デプロイ済みコメント非表示

## 使用例

### PR クローズ時の自動削除

```yaml
jobs:
  undeploy:
    permissions:
      contents: read
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/undeploy-web-hosting.yml@v1
    with:
      deploy-type: ${{ vars.DEPLOY_TYPE }}
      base-path-prefix: ${{ vars.NEXT_PUBLIC_BASE_PATH || '' }}
      dry-run: ${{ vars.SERVER_DRY_RUN || 'false' }}
    secrets:
      server-host: ${{ secrets.SERVER_HOST }}
      server-user: ${{ secrets.SERVER_USER }}
      server-password: ${{ secrets.SERVER_PASSWORD }}
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
      server-path: ${{ secrets.SERVER_PATH }}
```

### workflow_dispatch による手動削除

```yaml
on:
  workflow_dispatch:
    inputs:
      branch_name:
        description: '削除対象のブランチ名'
        required: true

jobs:
  undeploy:
    permissions:
      contents: read
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/undeploy-web-hosting.yml@v1
    with:
      deploy-type: ${{ vars.DEPLOY_TYPE }}
      base-path-prefix: ${{ vars.NEXT_PUBLIC_BASE_PATH || '' }}
      ref-name: ${{ github.event.inputs.branch_name }}
    secrets:
      server-host: ${{ secrets.SERVER_HOST }}
      server-user: ${{ secrets.SERVER_USER }}
      server-password: ${{ secrets.SERVER_PASSWORD }}
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
      server-path: ${{ secrets.SERVER_PATH }}
```

## Migration Guide

### 削除された Inputs

| 旧 Input | 代替 |
|-----------|------|
| `base-path` | `base-path-prefix` に置き換え（フルパスではなくプレフィックスのみ） |
| `is-pr` | 不要（`github.event_name` から自動判定） |

### 変更例

```yaml
# Before
with:
  base-path: ${{ format('{0}/_feature/pr-{1}', vars.BASE_PATH || '', github.event.pull_request.number) }}
  is-pr: ${{ github.event_name == 'pull_request' }}

# After
with:
  base-path-prefix: ${{ vars.NEXT_PUBLIC_BASE_PATH || '' }}
```
