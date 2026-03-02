# deploy-web-hosting

> ソースファイル: [`.github/workflows/deploy-web-hosting.yml`](../deploy-web-hosting.yml)

ビルド済みアーティファクトを FTP または rsync で Web ホスティングサーバーにデプロイする Reusable Workflow です。ビルド処理は呼び出し元で行い、本ワークフローはデプロイと通知のみを担当します。PR プレビューデプロイ、本番/開発環境デプロイに対応し、PR コメントおよび Slack 通知を自動投稿します。

デプロイパスと本番判定は `github` コンテキストから自動的に計算されます（内部で `compute-web-hosting-deploy-path` Composite Action を使用）。

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `deploy-type` | デプロイ方式 (`'ftp'` or `'rsync'`) | Yes | - |
| `artifact-name` | ダウンロードするビルドアーティファクト名 | Yes | - |
| `output-dir` | ビルド出力ディレクトリ名 | Yes | - |
| `base-path-prefix` | プロジェクト固有パスプレフィックス（例: `/<your-project>`） | No | `''` |
| `home-url` | サイトのホーム URL | No | `''` |
| `dry-run` | dry-run モード | No | `'false'` |
| `production-branch` | 本番ブランチ名 | No | `'main'` |
| `ref-name` | ブランチ名オーバーライド（未指定時は `github` コンテキストから自動導出） | No | `''` |

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

1. デプロイパスの計算（`compute-web-hosting-deploy-path` で `github` コンテキストから自動導出）
2. ビルドアーティファクトのダウンロード（`output-dir` で指定されたディレクトリに展開）
3. FTP/rsync でデプロイ（Composite Action 経由）
4. PR コメント投稿（成功/失敗）
5. Slack 通知（非 PR 時のみ、成功/失敗）
6. 過去の失敗コメント非表示

## 前提条件

呼び出し元ワークフローで以下を実施する必要があります：

1. プロジェクトのビルド
2. ビルド成果物を `actions/upload-artifact` でアップロード
3. 本ワークフローの `artifact-name` に一致するアーティファクト名を指定

## 使用例

### 基本的な使用例（PR / push）

```yaml
jobs:
  build:
    runs-on: ubuntu-24.04
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4
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
      base-path-prefix: ${{ vars.NEXT_PUBLIC_BASE_PATH || '' }}
      production-branch: 'main'
      home-url: ${{ vars.HOME_URL || '' }}
      dry-run: ${{ vars.SERVER_DRY_RUN || 'false' }}
      artifact-name: build-output
      output-dir: out
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

### repository_dispatch

`repository_dispatch` 時は `production-branch` の値が自動適用されるため、`ref-name` の指定は不要です。

```yaml
  deploy:
    needs: build
    permissions:
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/deploy-web-hosting.yml@v1
    with:
      deploy-type: ${{ vars.DEPLOY_TYPE }}
      base-path-prefix: ${{ vars.NEXT_PUBLIC_BASE_PATH || '' }}
      production-branch: 'main'
      artifact-name: build-output
      output-dir: out
    secrets:
      server-host: ${{ secrets.SERVER_HOST }}
      # ...
```

staging 環境等で `repository_dispatch` を使用する場合は、`ref-name` でオーバーライドできます:

```yaml
    with:
      ref-name: 'develop'  # production-branch ではなく develop を使用
```

## Migration Guide

### 削除された Inputs

| 旧 Input | 代替 |
|-----------|------|
| `is-pr` | 不要（`github.event_name` から自動判定） |
| `base-path` | `base-path-prefix` に置き換え（フルパスではなくプレフィックスのみ） |
| `is-production` | 不要（`production-branch` と ref-name から自動判定） |

### 変更例

```yaml
# Before
with:
  is-pr: ${{ github.event_name == 'pull_request' }}
  base-path: ${{ needs.build.outputs.base-path }}
  is-production: ${{ needs.build.outputs.is-production }}

# After
with:
  base-path-prefix: ${{ vars.NEXT_PUBLIC_BASE_PATH || '' }}
  production-branch: 'main'
```
