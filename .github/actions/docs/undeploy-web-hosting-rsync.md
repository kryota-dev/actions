# undeploy-web-hosting-rsync

> ソースファイル: [`.github/actions/undeploy-web-hosting-rsync/action.yml`](../undeploy-web-hosting-rsync/action.yml)

rsync over SSH を使用して Web ホスティングサーバー上のデプロイ済みディレクトリを削除する Composite Action です。空ディレクトリとの同期による削除方式で、dry-run モードをサポートし、SSH 秘密鍵のクリーンアップも自動実行します。

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `ssh-host` | SSH サーバーのホスト名 | Yes | - |
| `ssh-user` | SSH ユーザー名 | Yes | - |
| `ssh-private-key` | SSH 秘密鍵 | Yes | - |
| `target-path` | リモートサーバー上の削除対象パス | Yes | - |
| `dry-run` | dry-run モードで実行するかどうか | No | `'false'` |

## 動作

- SSH 秘密鍵のセットアップと `known_hosts` への登録を自動実行
- 空ディレクトリを作成し、rsync で同期することで対象ディレクトリの内容を削除
- `dry-run: 'true'` の場合: rsync `--dry-run` オプションで削除シミュレーション
- 削除成功後、空になった親ディレクトリの削除を試行（`rmdir`）
- ジョブの成否にかかわらず SSH 秘密鍵を必ず削除（`if: always()`）

## 前提条件

- SSH サーバーへのネットワークアクセスが可能であること

## 使用例

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/undeploy-web-hosting-rsync@v1
    with:
      ssh-host: ${{ secrets.SSH_HOST }}
      ssh-user: ${{ secrets.SSH_USER }}
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
      target-path: '/var/www/html/preview/pr-123'
      dry-run: 'false'
```
