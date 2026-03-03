[English](README.md) | **日本語**

# Composite Actions

## 開発環境セットアップ

| Action | Description |
|--------|-------------|
| [pnpm-setup](docs/pnpm-setup.ja.md) | Node.js + pnpm セットアップと依存関係インストール |
| [playwright-setup](docs/playwright-setup.ja.md) | Playwright ブラウザのセットアップ（キャッシュ対応） |

## 通知

| Action | Description |
|--------|-------------|
| [slack-notify-success](docs/slack-notify-success.ja.md) | Slack 成功通知（Bot OAuth Token 使用） |
| [slack-notify-failure](docs/slack-notify-failure.ja.md) | Slack 失敗通知（Incoming Webhook 使用） |

## デプロイ

| Action | Description |
|--------|-------------|
| [compute-web-hosting-deploy-path](docs/compute-web-hosting-deploy-path.ja.md) | GitHub コンテキストからデプロイパスと本番フラグを計算 |
| [deploy-web-hosting-ftp](docs/deploy-web-hosting-ftp.ja.md) | FTP（lftp）で Web ホスティングサーバーにデプロイ |
| [deploy-web-hosting-rsync](docs/deploy-web-hosting-rsync.ja.md) | rsync（SSH）で Web ホスティングサーバーにデプロイ |
| [undeploy-web-hosting-ftp](docs/undeploy-web-hosting-ftp.ja.md) | FTP（lftp）で Web ホスティングサーバーからディレクトリを削除 |
| [undeploy-web-hosting-rsync](docs/undeploy-web-hosting-rsync.ja.md) | rsync（SSH）で Web ホスティングサーバーからディレクトリを削除 |

## Usage

他のリポジトリから Composite Action を呼び出す場合:

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/{action-name}@v1
    with:
      # inputs
```

各アクションの inputs の詳細は上記リンク先のドキュメントを参照してください。
