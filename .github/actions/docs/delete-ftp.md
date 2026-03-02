# delete-ftp

> ソースファイル: [`.github/actions/delete-ftp/action.yml`](../delete-ftp/action.yml)

lftp を使用して FTP サーバー上のディレクトリを削除する Composite Action です。dry-run モードをサポートしています。

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `ftp-server` | FTP サーバーのアドレス | Yes | - |
| `ftp-username` | FTP サーバーのユーザー名 | Yes | - |
| `ftp-password` | FTP サーバーのパスワード | Yes | - |
| `target-path` | FTP サーバー上の削除対象パス | Yes | - |
| `dry-run` | dry-run モードで実行するかどうか | No | `'false'` |

## 動作

- `dry-run: 'true'` の場合: 削除対象ディレクトリの存在確認と接続テストを実行し、実際の削除は行わない
- `dry-run: 'false'` の場合: lftp の `rm -rf` で対象ディレクトリを削除

## 前提条件

- FTP サーバーへのネットワークアクセスが可能であること

## 使用例

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/delete-ftp@v1
    with:
      ftp-server: ${{ secrets.FTP_SERVER }}
      ftp-username: ${{ secrets.FTP_USERNAME }}
      ftp-password: ${{ secrets.FTP_PASSWORD }}
      target-path: '/public_html/preview/pr-123'
      dry-run: 'false'
```
