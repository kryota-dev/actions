# deploy-web-hosting

> ソースファイル: [`.github/workflows/deploy-web-hosting.yml`](../deploy-web-hosting.yml)

ビルド済みアーティファクトを FTP または rsync で Web ホスティングサーバーにデプロイする Reusable Workflow です。ビルド処理は呼び出し元で行い、本ワークフローはデプロイと通知のみを担当します。PR プレビューデプロイ、本番/開発環境デプロイに対応し、PR コメントおよび Slack 通知を自動投稿します。

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `deploy-type` | デプロイ方式 (`'ftp'` or `'rsync'`) | Yes | - |
| `base-path` | デプロイ先のベースパス（呼び出し元で事前計算） | No | `''` |
| `is-pr` | PR プレビューデプロイかどうか | Yes | - |
| `home-url` | サイトのホーム URL | No | `''` |
| `dry-run` | dry-run モード | No | `'false'` |
| `is-production` | 本番デプロイかどうか | No | `'false'` |
| `artifact-name` | ダウンロードするビルドアーティファクト名 | Yes | - |
| `output-dir` | ビルド出力ディレクトリ名 | Yes | - |

## Secrets

| Name | Description | Required |
|------|-------------|----------|
| `server-host` | サーバーホスト | Yes |
| `server-user` | サーバーユーザー | Yes |
| `server-password` | FTP パスワード | No |
| `ssh-private-key` | SSH 秘密鍵 | No |
| `server-path` | サーバー上のパス | Yes |
| `slack-channel-id` | Slack チャンネル ID | No |
| `slack-bot-oauth-token` | Slack Bot OAuth トークン | No |
| `slack-webhook-url` | Slack Webhook URL | No |
| `slack-mention-user` | Slack メンションユーザー | No |

## 動作フロー

1. ビルドアーティファクトのダウンロード（`output-dir` で指定されたディレクトリに展開）
2. FTP/rsync でデプロイ（Composite Action 経由）
3. PR コメント投稿（成功/失敗）
4. Slack 通知（非 PR 時のみ、成功/失敗）
5. 過去の失敗コメント非表示

## 前提条件

呼び出し元ワークフローで以下を実施する必要があります：

1. プロジェクトのビルド
2. ビルド成果物を `actions/upload-artifact` でアップロード
3. 本ワークフローの `artifact-name` に一致するアーティファクト名を指定

## 使用例

```yaml
jobs:
  build:
    runs-on: ubuntu-24.04
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v6
      # ... ビルド処理 ...
      - uses: actions/upload-artifact@v4
        with:
          name: build-output
          path: out/

  deploy:
    needs: build
    permissions:
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/deploy-web-hosting.yml@v1
    with:
      deploy-type: ${{ vars.DEPLOY_TYPE }}
      base-path: ${{ needs.build.outputs.base-path }}
      is-pr: ${{ github.event_name == 'pull_request' }}
      home-url: ${{ vars.HOME_URL || '' }}
      dry-run: ${{ vars.SERVER_DRY_RUN || 'false' }}
      is-production: ${{ github.ref_name == 'main' && 'true' || 'false' }}
      artifact-name: build-output
    secrets:
      server-host: ${{ secrets.SERVER_HOST }}
      server-user: ${{ secrets.SERVER_USER }}
      server-password: ${{ secrets.SERVER_PASSWORD }}
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
      server-path: ${{ secrets.SERVER_PATH }}
      slack-channel-id: ${{ secrets.SLACK_CHANNEL_ID }}
      slack-bot-oauth-token: ${{ secrets.SLACK_BOT_OAUTH_TOKEN }}
      slack-webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
      slack-mention-user: ${{ secrets.SLACK_MENTION_USER }}
```
