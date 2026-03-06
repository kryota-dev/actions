[English](undeploy-web-hosting-ftp.md) | **日本語**

# undeploy-web-hosting-ftp

lftp を使用して Web ホスティングサーバーからデプロイ済みディレクトリを削除する Composite Action。dry-run モードに対応。

> Source: [`.github/actions/undeploy-web-hosting-ftp/action.yml`](../undeploy-web-hosting-ftp/action.yml)

## Usage

```yaml
- uses: kryota-dev/actions/.github/actions/undeploy-web-hosting-ftp@v0
  with:
    # ftp-server - FTP サーバーのアドレス
    # Required
    ftp-server: ''

    # ftp-username - FTP サーバーのユーザー名
    # Required
    ftp-username: ''

    # ftp-password - FTP サーバーのパスワード
    # Required
    ftp-password: ''

    # target-path - FTP サーバー上の削除対象パス
    # Required
    target-path: ''

    # dry-run - dry-run モードで実行するかどうか
    # Optional (default: 'false')
    dry-run: 'false'
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `ftp-server` | FTP サーバーのアドレス | Yes | - |
| `ftp-username` | FTP サーバーのユーザー名 | Yes | - |
| `ftp-password` | FTP サーバーのパスワード | Yes | - |
| `target-path` | FTP サーバー上の削除対象パス | Yes | - |
| `dry-run` | dry-run モードで実行するかどうか | No | `'false'` |

## Examples

### 基本的な使い方

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/undeploy-web-hosting-ftp@v0
    with:
      ftp-server: ${{ secrets.FTP_SERVER }}
      ftp-username: ${{ secrets.FTP_USERNAME }}
      ftp-password: ${{ secrets.FTP_PASSWORD }}
      target-path: '/public_html/_feature/feat-awesome'
```

### dry-run モードでの確認

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/undeploy-web-hosting-ftp@v0
    with:
      ftp-server: ${{ secrets.FTP_SERVER }}
      ftp-username: ${{ secrets.FTP_USERNAME }}
      ftp-password: ${{ secrets.FTP_PASSWORD }}
      target-path: '/public_html/_feature/feat-awesome'
      dry-run: 'true'
```

## Behavior

1. lftp をインストールする
2. dry-run モードの場合、`ls -la {target-path}` でディレクトリの内容を確認のみ行う
3. 通常モードの場合、`rm -rf {target-path}` で対象ディレクトリを削除する

## Prerequisites

- FTP サーバーへの接続情報（サーバーアドレス、ユーザー名、パスワード）が設定されていること

<!-- ## Migration Guide -->

<!-- Breaking Changes がある場合にコメントアウトを解除して記載する -->
