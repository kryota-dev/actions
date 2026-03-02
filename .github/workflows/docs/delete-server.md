# delete-server

> ソースファイル: [`.github/workflows/delete-server.yml`](../delete-server.yml)

PR プレビュー環境を FTP または rsync で削除する Reusable Workflow です。PR コメントで削除結果を通知し、デプロイ済みコメントの非表示も自動実行します。

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `deploy-type` | デプロイ方式 (`'ftp'` or `'rsync'`) | Yes | - |
| `base-path` | 削除対象のベースパス | Yes | - |
| `is-pr` | PR イベントかどうか | Yes | - |
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

1. FTP/rsync で対象ディレクトリを削除（inline steps）
2. PR コメント投稿（成功/失敗）
3. 過去の失敗コメント非表示
4. デプロイ済みコメント非表示

## 使用例

```yaml
jobs:
  delete:
    permissions:
      contents: read
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/delete-server.yml@v1
    with:
      deploy-type: ${{ vars.DEPLOY_TYPE }}
      base-path: ${{ format('{0}/_feature/pr-{1}', vars.BASE_PATH || '', github.event.pull_request.number) }}
      is-pr: ${{ github.event_name == 'pull_request' }}
      dry-run: ${{ vars.SERVER_DRY_RUN || 'false' }}
    secrets:
      server-host: ${{ secrets.SERVER_HOST }}
      server-user: ${{ secrets.SERVER_USER }}
      server-password: ${{ secrets.SERVER_PASSWORD }}
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
      server-path: ${{ secrets.SERVER_PATH }}
```
