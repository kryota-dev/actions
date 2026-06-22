[English](deploy-web-hosting-ftp.md) | **日本語**

# deploy-web-hosting-ftp

lftp を使用してビルド成果物を Web ホスティングサーバーに FTP デプロイする Composite Action。dry-run モードと本番モードに対応。

> Source: [`.github/actions/deploy-web-hosting-ftp/action.yml`](../deploy-web-hosting-ftp/action.yml)

## Usage

```yaml
- uses: kryota-dev/actions/.github/actions/deploy-web-hosting-ftp@v0
  with:
    # output-dir - ビルド出力ディレクトリ名
    # Required
    output-dir: ''

    # ftp-server - FTP サーバーのアドレス
    # Required
    ftp-server: ''

    # ftp-username - FTP サーバーのユーザー名
    # Required
    ftp-username: ''

    # ftp-password - FTP サーバーのパスワード
    # Required
    ftp-password: ''

    # ftp-path - FTP サーバーのパス
    # Required
    ftp-path: ''

    # base-path - アーティファクトのベースパス
    # Optional
    base-path: ''

    # dry-run - dry-run モードで実行するかどうか
    # Optional (default: 'false')
    dry-run: 'false'

    # is-production - 本番デプロイかどうか
    # Optional (default: 'false')
    is-production: 'false'

    # apply-htaccess - 本番デプロイで成果物の .htaccess を適用するか（opt-in）
    # Optional (default: 'false')
    apply-htaccess: 'false'
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `output-dir` | ビルド出力ディレクトリ名 | Yes | - |
| `ftp-server` | FTP サーバーのアドレス | Yes | - |
| `ftp-username` | FTP サーバーのユーザー名 | Yes | - |
| `ftp-password` | FTP サーバーのパスワード | Yes | - |
| `ftp-path` | FTP サーバーのパス | Yes | - |
| `base-path` | アーティファクトのベースパス | No | - |
| `dry-run` | dry-run モードで実行するかどうか | No | `'false'` |
| `is-production` | 本番デプロイかどうか | No | `'false'` |
| `apply-htaccess` | 本番デプロイで成果物の `.htaccess` を適用するか（opt-in。`is-production` が `'true'` のときのみ有効） | No | `'false'` |

## Examples

### 基本的な使い方

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/deploy-web-hosting-ftp@v0
    with:
      output-dir: 'dist'
      ftp-server: ${{ secrets.FTP_SERVER }}
      ftp-username: ${{ secrets.FTP_USERNAME }}
      ftp-password: ${{ secrets.FTP_PASSWORD }}
      ftp-path: '/public_html'
```

### dry-run モードでの確認

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/deploy-web-hosting-ftp@v0
    with:
      output-dir: 'dist'
      ftp-server: ${{ secrets.FTP_SERVER }}
      ftp-username: ${{ secrets.FTP_USERNAME }}
      ftp-password: ${{ secrets.FTP_PASSWORD }}
      ftp-path: '/public_html'
      dry-run: 'true'
```

### 本番デプロイ（base-path 指定あり）

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/deploy-web-hosting-ftp@v0
    with:
      output-dir: 'dist'
      ftp-server: ${{ secrets.FTP_SERVER }}
      ftp-username: ${{ secrets.FTP_USERNAME }}
      ftp-password: ${{ secrets.FTP_PASSWORD }}
      ftp-path: '/public_html'
      base-path: '/my-project'
      is-production: 'true'
```

### リポジトリ管理の `.htaccess` を本番へ適用する（opt-in）

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/deploy-web-hosting-ftp@v0
    with:
      output-dir: 'dist'
      ftp-server: ${{ secrets.FTP_SERVER }}
      ftp-username: ${{ secrets.FTP_USERNAME }}
      ftp-password: ${{ secrets.FTP_PASSWORD }}
      ftp-path: '/public_html'
      is-production: 'true'
      # 成果物の .htaccess（リダイレクトや ErrorDocument 404 など）をアップロードしつつ、
      # サーバー側のコピーを削除から保護する。
      apply-htaccess: 'true'
```

## Behavior

1. lftp をインストールする
2. ソースパス `./{output-dir}{base-path}` を構築する
3. dry-run モードの場合、FTP サーバーへの接続テストを実行し、ファイル一覧のみを表示する
4. 通常モードの場合、`mirror --reverse --delete` コマンドでローカルからリモートへファイルを同期する
5. production モードの場合、`.htaccess` と `_feature/` を mirror から除外し、サーバー側のコピーが削除されないようにする（lftp の `mirror` には protect 専用フィルタがないため）
6. `apply-htaccess: 'true'`（production のみ）かつ成果物に `.htaccess` が含まれる場合、2 パス目で `put` によりアップロードする。成果物の `.htaccess` を転送（サーバー側を上書き）しつつ、mirror 側ではサーバー側コピーを削除から保護する。成果物に `.htaccess` がない場合は 2 パス目をスキップし、サーバー側コピーを保持する。`apply-htaccess` は production 以外では効果がない。
7. `runner.debug` が有効な場合、lftp のデバッグフラグ `-d` を有効化する

## Prerequisites

- デプロイ対象のビルド成果物が `output-dir` に存在すること
- FTP サーバーへの接続情報（サーバーアドレス、ユーザー名、パスワード）が設定されていること

<!-- ## Migration Guide -->

<!-- Breaking Changes がある場合にコメントアウトを解除して記載する -->
