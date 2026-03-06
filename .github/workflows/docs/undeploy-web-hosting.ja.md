[English](undeploy-web-hosting.md) | **日本語**

# Undeploy from Web Hosting

Web ホスティングサーバー上のフィーチャー環境を FTP または rsync で削除するワークフロー

> Source: [`.github/workflows/undeploy-web-hosting.yml`](../undeploy-web-hosting.yml)

## Usage

```yaml
jobs:
  undeploy:
    permissions:
      contents: read
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/undeploy-web-hosting.yml@v0
    with:
      # deploy-type - デプロイ方法（'ftp' または 'rsync'）
      # Required
      deploy-type: 'ftp'

      # base-path-prefix - プロジェクト固有のパスプレフィックス（例: '/<your-project>'）
      # Optional (default: '')
      base-path-prefix: ''

      # production-branch - 本番ブランチ名
      # Optional (default: 'main')
      production-branch: 'main'

      # ref-name - ブランチ名の上書き（空の場合は github context から自動取得）
      # Optional (default: '')
      ref-name: ''

      # dry-run - ドライランモード
      # Optional (default: 'false')
      dry-run: 'false'
    secrets:
      # server-host - デプロイ先サーバーのホスト名
      # Required
      server-host: ${{ secrets.SERVER_HOST }}

      # server-user - デプロイ先サーバーのユーザー名
      # Required
      server-user: ${{ secrets.SERVER_USER }}

      # server-path - デプロイ先サーバーのパス
      # Required
      server-path: ${{ secrets.SERVER_PATH }}

      # server-password - デプロイ先サーバーのパスワード（FTP 使用時に必要）
      # Optional
      server-password: ${{ secrets.SERVER_PASSWORD }}

      # ssh-private-key - SSH 秘密鍵（rsync 使用時に必要）
      # Optional
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `deploy-type` | デプロイ方法（`'ftp'` または `'rsync'`） | Yes | - |
| `base-path-prefix` | プロジェクト固有のパスプレフィックス（例: `'/<your-project>'`） | No | `''` |
| `production-branch` | 本番ブランチ名 | No | `'main'` |
| `ref-name` | ブランチ名の上書き（空の場合は github context から自動取得） | No | `''` |
| `dry-run` | ドライランモード | No | `'false'` |

## Secrets

| Name | Description | Required |
|------|-------------|----------|
| `server-host` | デプロイ先サーバーのホスト名 | Yes |
| `server-user` | デプロイ先サーバーのユーザー名 | Yes |
| `server-path` | デプロイ先サーバーのパス | Yes |
| `server-password` | デプロイ先サーバーのパスワード（FTP 使用時に必要） | No |
| `ssh-private-key` | SSH 秘密鍵（rsync 使用時に必要） | No |

## Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| `contents` | `read` | リポジトリのチェックアウト |
| `pull-requests` | `write` | PR への削除結果コメント投稿 |

## Examples

### FTP でフィーチャー環境を削除する

```yaml
jobs:
  undeploy:
    permissions:
      contents: read
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/undeploy-web-hosting.yml@v0
    with:
      deploy-type: 'ftp'
    secrets:
      server-host: ${{ secrets.SERVER_HOST }}
      server-user: ${{ secrets.SERVER_USER }}
      server-path: ${{ secrets.SERVER_PATH }}
      server-password: ${{ secrets.SERVER_PASSWORD }}
```

### rsync でフィーチャー環境を削除する（パスプレフィックス付き）

```yaml
jobs:
  undeploy:
    permissions:
      contents: read
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/undeploy-web-hosting.yml@v0
    with:
      deploy-type: 'rsync'
      base-path-prefix: '/my-project'
    secrets:
      server-host: ${{ secrets.SERVER_HOST }}
      server-user: ${{ secrets.SERVER_USER }}
      server-path: ${{ secrets.SERVER_PATH }}
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
```

### ドライランで確認する

```yaml
jobs:
  undeploy:
    permissions:
      contents: read
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/undeploy-web-hosting.yml@v0
    with:
      deploy-type: 'rsync'
      dry-run: 'true'
    secrets:
      server-host: ${{ secrets.SERVER_HOST }}
      server-user: ${{ secrets.SERVER_USER }}
      server-path: ${{ secrets.SERVER_PATH }}
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
```

## Behavior

このワークフローは `delete` ジョブで構成され、以下の順序で実行されます。

1. `compute-web-hosting-deploy-path` Composite Action で削除対象パスを計算
2. `deploy-type` の値に応じて削除を実行
   - `'ftp'`: `undeploy-web-hosting-ftp` Composite Action を使用
   - `'rsync'`: `undeploy-web-hosting-rsync` Composite Action を使用
3. PR の場合: `marocchino/sticky-pull-request-comment` で成功/失敗コメントを投稿
4. 成功の場合: 過去の失敗コメントを非表示にし、過去のデプロイ成功コメントも非表示にする

## Prerequisites

- `deploy-type` が `'ftp'` の場合: `server-password` が必要
- `deploy-type` が `'rsync'` の場合: `ssh-private-key` が必要
