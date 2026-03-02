# deploy-web-hosting-ftp

> ソースファイル: [`.github/actions/deploy-web-hosting-ftp/action.yml`](../deploy-web-hosting-ftp/action.yml)

lftp を使用して Web ホスティングサーバーにアーティファクトをデプロイする Composite Action です。dry-run モードと本番モードをサポートしています。

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `base-path` | アーティファクトのベースパス | No | - |
| `output-dir` | ビルド出力ディレクトリ名 | Yes | - |
| `ftp-server` | FTP サーバーのアドレス | Yes | - |
| `ftp-username` | FTP サーバーのユーザー名 | Yes | - |
| `ftp-password` | FTP サーバーのパスワード | Yes | - |
| `ftp-path` | FTP サーバーのパス | Yes | - |
| `dry-run` | dry-run モードで実行するかどうか | No | `'false'` |
| `is-production` | 本番環境デプロイかどうか | No | `'false'` |

## 動作

- `dry-run: 'true'` の場合: ソースディレクトリの確認、FTP 接続テストを実行し、実際のデプロイは行わない
- `dry-run: 'false'` の場合: lftp の mirror コマンドでデプロイを実行
- `is-production: 'true'` の場合: `.htaccess` と `_feature/` を除外してデプロイ
- `runner.debug` が有効な場合: lftp のデバッグモードを有効化

## 前提条件

- デプロイ対象のビルド成果物が `./${output-dir}${base-path}` に存在すること
- FTP サーバーへのネットワークアクセスが可能であること

## 使用例

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/deploy-web-hosting-ftp@v1
    with:
      base-path: '/preview/pr-123'
      ftp-server: ${{ secrets.FTP_SERVER }}
      ftp-username: ${{ secrets.FTP_USERNAME }}
      ftp-password: ${{ secrets.FTP_PASSWORD }}
      ftp-path: '/public_html/preview/pr-123'
      dry-run: 'false'
      is-production: 'false'
```
