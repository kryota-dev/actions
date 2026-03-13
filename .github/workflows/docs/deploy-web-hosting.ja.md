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
      # environment - シークレットアクセス用の GitHub Environment 名
      # Required
      environment: 'production'

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
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `environment` | シークレットアクセス用の GitHub Environment 名 | Yes | - |
| `deploy-type` | デプロイ方法（`'ftp'` または `'rsync'`） | Yes | - |
| `artifact-name` | ダウンロードするビルドアーティファクトの名前 | Yes | - |
| `output-dir` | ビルド出力ディレクトリ名 | Yes | - |
| `base-path-prefix` | プロジェクト固有のパスプレフィックス（例: `'/<your-project>'`） | No | `''` |
| `home-url` | サイトのホーム URL | No | `''` |
| `dry-run` | ドライランモード | No | `'false'` |
| `production-branch` | 本番ブランチ名 | No | `'main'` |
| `ref-name` | ブランチ名の上書き（空の場合は github context から自動取得） | No | `''` |

## Environment Secrets

`environment` input で指定した GitHub Environment に以下のシークレットを設定する必要があります:

| Name | Description | Required |
|------|-------------|----------|
| `SERVER_HOST` | デプロイ先サーバーのホスト名 | Yes |
| `SERVER_USER` | デプロイ先サーバーのユーザー名 | Yes |
| `SERVER_PATH` | デプロイ先サーバーのパス | Yes |
| `SERVER_PASSWORD` | デプロイ先サーバーのパスワード（FTP 使用時に必要） | Conditional |
| `SSH_PRIVATE_KEY` | SSH 秘密鍵（rsync 使用時に必要） | Conditional |
| `SLACK_CHANNEL_ID` | Slack 通知先チャンネル ID | No |
| `SLACK_BOT_OAUTH_TOKEN` | Slack Bot の OAuth トークン | No |
| `SLACK_WEBHOOK_URL` | Slack Incoming Webhook URL | No |
| `SLACK_MENTION_USER` | Slack で失敗時にメンションするユーザー | No |

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
      environment: 'production'
      deploy-type: 'ftp'
      artifact-name: 'build-output'
      output-dir: 'dist'
```

### rsync でデプロイする（Slack 通知付き）

```yaml
jobs:
  deploy:
    permissions:
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/deploy-web-hosting.yml@v0
    with:
      environment: 'production'
      deploy-type: 'rsync'
      artifact-name: 'build-output'
      output-dir: 'dist'
      base-path-prefix: '/my-project'
      home-url: 'https://example.com'
```

### ドライランで確認する

```yaml
jobs:
  deploy:
    permissions:
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/deploy-web-hosting.yml@v0
    with:
      environment: 'staging'
      deploy-type: 'rsync'
      artifact-name: 'build-output'
      output-dir: 'dist'
      dry-run: 'true'
```

## Behavior

このワークフローは `deploy` ジョブで構成され、以下の順序で実行されます。

1. `compute-web-hosting-deploy-path` Composite Action でデプロイ先パスを計算
2. Slack 設定チェック（`SLACK_CHANNEL_ID` + `SLACK_BOT_OAUTH_TOKEN` があれば成功通知可能、`SLACK_WEBHOOK_URL` があれば失敗通知可能）
3. `actions/download-artifact@v4.3.0` でビルドアーティファクトをダウンロード
4. `deploy-type` の値に応じてデプロイを実行
   - `'ftp'`: `deploy-web-hosting-ftp` Composite Action を使用
   - `'rsync'`: `deploy-web-hosting-rsync` Composite Action を使用
5. PR の場合: `marocchino/sticky-pull-request-comment` で成功/失敗コメントを投稿
6. PR 以外の場合: Slack で成功通知（`slack-notify-success`）/ 失敗通知（`slack-notify-failure`）を送信
7. PR かつ成功の場合: 過去の失敗コメントを非表示にする

## Prerequisites

- 呼び出し元リポジトリに `environment` input に対応する GitHub Environment が存在し、必要なシークレットが Environment レベルで設定されていること
- 呼び出し元ワークフローで `actions/upload-artifact` によるビルド成果物のアップロードが完了していること
- `deploy-type` が `'ftp'` の場合: `SERVER_PASSWORD` が必要
- `deploy-type` が `'rsync'` の場合: `SSH_PRIVATE_KEY` が必要
