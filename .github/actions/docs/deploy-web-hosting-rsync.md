# deploy-web-hosting-rsync

rsync over SSH でビルド成果物を Web ホスティングサーバーにデプロイする Composite Action。dry-run モードと本番モードに対応。

> Source: [`.github/actions/deploy-web-hosting-rsync/action.yml`](../deploy-web-hosting-rsync/action.yml)

## Usage

```yaml
- uses: kryota-dev/actions/.github/actions/deploy-web-hosting-rsync@v1
  with:
    # output-dir - ビルド出力ディレクトリ名
    # Required
    output-dir: ''

    # ssh-host - SSH サーバーのホスト名
    # Required
    ssh-host: ''

    # ssh-user - SSH ユーザー名
    # Required
    ssh-user: ''

    # ssh-private-key - SSH 秘密鍵
    # Required
    ssh-private-key: ''

    # ssh-path - SSH サーバー上のターゲットパス
    # Required
    ssh-path: ''

    # base-path - アーティファクトのベースパス
    # Optional
    base-path: ''

    # dry-run - dry-run モードで実行するかどうか
    # Optional (default: 'false')
    dry-run: 'false'

    # is-production - 本番デプロイかどうか
    # Optional (default: 'false')
    is-production: 'false'
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `output-dir` | ビルド出力ディレクトリ名 | Yes | - |
| `ssh-host` | SSH サーバーのホスト名 | Yes | - |
| `ssh-user` | SSH ユーザー名 | Yes | - |
| `ssh-private-key` | SSH 秘密鍵 | Yes | - |
| `ssh-path` | SSH サーバー上のターゲットパス | Yes | - |
| `base-path` | アーティファクトのベースパス | No | - |
| `dry-run` | dry-run モードで実行するかどうか | No | `'false'` |
| `is-production` | 本番デプロイかどうか | No | `'false'` |

## Examples

### 基本的な使い方

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/deploy-web-hosting-rsync@v1
    with:
      output-dir: 'dist'
      ssh-host: ${{ secrets.SSH_HOST }}
      ssh-user: ${{ secrets.SSH_USER }}
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
      ssh-path: '/home/user/public_html'
```

### dry-run モードでの確認

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/deploy-web-hosting-rsync@v1
    with:
      output-dir: 'dist'
      ssh-host: ${{ secrets.SSH_HOST }}
      ssh-user: ${{ secrets.SSH_USER }}
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
      ssh-path: '/home/user/public_html'
      dry-run: 'true'
```

### 本番デプロイ（base-path 指定あり）

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/deploy-web-hosting-rsync@v1
    with:
      output-dir: 'dist'
      ssh-host: ${{ secrets.SSH_HOST }}
      ssh-user: ${{ secrets.SSH_USER }}
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
      ssh-path: '/home/user/public_html'
      base-path: '/my-project'
      is-production: 'true'
```

## Behavior

1. SSH 鍵をセットアップする（`~/.ssh/id_rsa` に秘密鍵を書き込み、`ssh-keyscan` でホスト鍵を取得）
2. ソースパス `./{output-dir}{base-path}` を構築する
3. `rsync -az --delete` コマンドでローカルからリモートへファイルを同期する
4. production モードの場合、`.htaccess` と `_feature/` を `--exclude-from` で同期対象から除外する
5. dry-run モードの場合、`--dry-run` フラグを追加する
6. debug モードまたは dry-run モードの場合、`--verbose` フラグを追加する
7. 処理完了後（成功・失敗問わず）、SSH 鍵をクリーンアップする

## Prerequisites

- デプロイ対象のビルド成果物が `output-dir` に存在すること
- SSH サーバーへの接続情報（ホスト名、ユーザー名、秘密鍵）が設定されていること

<!-- ## Migration Guide -->

<!-- Breaking Changes がある場合にコメントアウトを解除して記載する -->
