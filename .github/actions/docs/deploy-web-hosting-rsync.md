# deploy-web-hosting-rsync

> ソースファイル: [`.github/actions/deploy-web-hosting-rsync/action.yml`](../deploy-web-hosting-rsync/action.yml)

rsync over SSH を使用してアーティファクトを Web ホスティングサーバーにデプロイする Composite Action です。dry-run モードと本番モードをサポートし、SSH 秘密鍵のクリーンアップも自動実行します。

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `base-path` | アーティファクトのベースパス | No | - |
| `output-dir` | ビルド出力ディレクトリ名 | Yes | - |
| `ssh-host` | SSH サーバーのホスト名 | Yes | - |
| `ssh-user` | SSH ユーザー名 | Yes | - |
| `ssh-private-key` | SSH 秘密鍵 | Yes | - |
| `ssh-path` | SSH サーバー上のターゲットパス | Yes | - |
| `dry-run` | dry-run モードで実行するかどうか | No | `'false'` |
| `is-production` | 本番環境デプロイかどうか | No | `'false'` |

## 動作

- SSH 秘密鍵のセットアップと `known_hosts` への登録を自動実行
- `dry-run: 'true'` の場合: rsync `--dry-run` オプションで転送シミュレーション
- `is-production: 'true'` の場合: `.htaccess` と `_feature/` を除外してデプロイ
- `runner.debug` が有効、または `dry-run` の場合: rsync `--verbose` オプションを有効化
- ジョブの成否にかかわらず SSH 秘密鍵を必ず削除（`if: always()`）

## 前提条件

- デプロイ対象のビルド成果物が `./${output-dir}${base-path}` に存在すること
- SSH サーバーへのネットワークアクセスが可能であること

## 使用例

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/deploy-web-hosting-rsync@v1
    with:
      base-path: '/preview/pr-123'
      ssh-host: ${{ secrets.SSH_HOST }}
      ssh-user: ${{ secrets.SSH_USER }}
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
      ssh-path: '/var/www/html/preview/pr-123'
      dry-run: 'false'
      is-production: 'false'
```
