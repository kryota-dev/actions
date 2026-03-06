[English](deploy-web-hosting.md) | **日本語**

# Deploy to Web Hosting

ビルド済みアーティファクトを FTP または rsync で Web ホスティングサーバーにデプロイするワークフロー

> Source: [`.github/workflows/deploy-web-hosting.yml`](../deploy-web-hosting.yml)

## Usage

```yaml
jobs:
  deploy:
    permissions:
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/deploy-web-hosting.yml@v0
    with:
      # deploy-type - デプロイ方法（'ftp' または 'rsync'）
      # Required
      deploy-type: 'ftp'

      # artifact-name - ダウンロードするビルドアーティファクトの名前
      # Required
      artifact-name: 'build-output'

      # output-dir - ビルド出力ディレクトリ名
      # Required
      output-dir: 'dist'

      # base-path-prefix - プロジェクト固有のパスプレフィックス（例: '/<your-project>'）
      # Optional (default: '')
      base-path-prefix: ''

      # home-url - サイトのホーム URL
      # Optional (default: '')
      home-url: ''

      # dry-run - ドライランモード
      # Optional (default: 'false')
      dry-run: 'false'

      # production-branch - 本番ブランチ名
      # Optional (default: 'main')
      production-branch: 'main'

      # ref-name - ブランチ名の上書き（空の場合は github context から自動取得）
      # Optional (default: '')
      ref-name: ''
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

      # slack-channel-id - Slack 通知先チャンネル ID
      # Optional
      slack-channel-id: ${{ secrets.SLACK_CHANNEL_ID }}

      # slack-bot-oauth-token - Slack Bot の OAuth トークン
      # Optional
      slack-bot-oauth-token: ${{ secrets.SLACK_BOT_OAUTH_TOKEN }}

      # slack-webhook-url - Slack Incoming Webhook URL
      # Optional
      slack-webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}

      # slack-mention-user - Slack で失敗時にメンションするユーザー
      # Optional
      slack-mention-user: ${{ secrets.SLACK_MENTION_USER }}
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `deploy-type` | デプロイ方法（`'ftp'` または `'rsync'`） | Yes | - |
| `artifact-name` | ダウンロードするビルドアーティファクトの名前 | Yes | - |
| `output-dir` | ビルド出力ディレクトリ名 | Yes | - |
| `base-path-prefix` | プロジェクト固有のパスプレフィックス（例: `'/<your-project>'`） | No | `''` |
| `home-url` | サイトのホーム URL | No | `''` |
| `dry-run` | ドライランモード | No | `'false'` |
| `production-branch` | 本番ブランチ名 | No | `'main'` |
| `ref-name` | ブランチ名の上書き（空の場合は github context から自動取得） | No | `''` |

## Secrets

| Name | Description | Required |
|------|-------------|----------|
| `server-host` | デプロイ先サーバーのホスト名 | Yes |
| `server-user` | デプロイ先サーバーのユーザー名 | Yes |
| `server-path` | デプロイ先サーバーのパス | Yes |
| `server-password` | デプロイ先サーバーのパスワード（FTP 使用時に必要） | No |
| `ssh-private-key` | SSH 秘密鍵（rsync 使用時に必要） | No |
| `slack-channel-id` | Slack 通知先チャンネル ID | No |
| `slack-bot-oauth-token` | Slack Bot の OAuth トークン | No |
| `slack-webhook-url` | Slack Incoming Webhook URL | No |
| `slack-mention-user` | Slack で失敗時にメンションするユーザー | No |

## Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| `pull-requests` | `write` | PR へのデプロイ結果コメント投稿 |

## Examples

### FTP でデプロイする

```yaml
jobs:
  deploy:
    permissions:
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/deploy-web-hosting.yml@v0
    with:
      deploy-type: 'ftp'
      artifact-name: 'build-output'
      output-dir: 'dist'
    secrets:
      server-host: ${{ secrets.SERVER_HOST }}
      server-user: ${{ secrets.SERVER_USER }}
      server-path: ${{ secrets.SERVER_PATH }}
      server-password: ${{ secrets.SERVER_PASSWORD }}
```

### rsync でデプロイする（Slack 通知付き）

```yaml
jobs:
  deploy:
    permissions:
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/deploy-web-hosting.yml@v0
    with:
      deploy-type: 'rsync'
      artifact-name: 'build-output'
      output-dir: 'dist'
      base-path-prefix: '/my-project'
      home-url: 'https://example.com'
    secrets:
      server-host: ${{ secrets.SERVER_HOST }}
      server-user: ${{ secrets.SERVER_USER }}
      server-path: ${{ secrets.SERVER_PATH }}
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
      slack-channel-id: ${{ secrets.SLACK_CHANNEL_ID }}
      slack-bot-oauth-token: ${{ secrets.SLACK_BOT_OAUTH_TOKEN }}
      slack-webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
      slack-mention-user: ${{ secrets.SLACK_MENTION_USER }}
```

### ドライランで確認する

```yaml
jobs:
  deploy:
    permissions:
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/deploy-web-hosting.yml@v0
    with:
      deploy-type: 'rsync'
      artifact-name: 'build-output'
      output-dir: 'dist'
      dry-run: 'true'
    secrets:
      server-host: ${{ secrets.SERVER_HOST }}
      server-user: ${{ secrets.SERVER_USER }}
      server-path: ${{ secrets.SERVER_PATH }}
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
```

## Behavior

このワークフローは `deploy` ジョブで構成され、以下の順序で実行されます。

1. `compute-web-hosting-deploy-path` Composite Action でデプロイ先パスを計算
2. Slack 設定チェック（`slack-channel-id` + `slack-bot-oauth-token` があれば成功通知可能、`slack-webhook-url` があれば失敗通知可能）
3. `actions/download-artifact@v4.3.0` でビルドアーティファクトをダウンロード
4. `deploy-type` の値に応じてデプロイを実行
   - `'ftp'`: `deploy-web-hosting-ftp` Composite Action を使用
   - `'rsync'`: `deploy-web-hosting-rsync` Composite Action を使用
5. PR の場合: `marocchino/sticky-pull-request-comment` で成功/失敗コメントを投稿
6. PR 以外の場合: Slack で成功通知（`slack-notify-success`）/ 失敗通知（`slack-notify-failure`）を送信
7. PR かつ成功の場合: 過去の失敗コメントを非表示にする

## Prerequisites

- 呼び出し元ワークフローで `actions/upload-artifact` によるビルド成果物のアップロードが完了していること
- `deploy-type` が `'ftp'` の場合: `server-password` が必要
- `deploy-type` が `'rsync'` の場合: `ssh-private-key` が必要
