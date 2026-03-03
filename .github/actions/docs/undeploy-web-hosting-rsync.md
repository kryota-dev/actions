# undeploy-web-hosting-rsync

rsync over SSH で Web ホスティングサーバーからデプロイ済みディレクトリを削除する Composite Action。dry-run モードに対応。

> Source: [`.github/actions/undeploy-web-hosting-rsync/action.yml`](../undeploy-web-hosting-rsync/action.yml)

## Usage

```yaml
- uses: kryota-dev/actions/.github/actions/undeploy-web-hosting-rsync@v1
  with:
    # ssh-host - SSH サーバーのホスト名
    # Required
    ssh-host: ''

    # ssh-user - SSH ユーザー名
    # Required
    ssh-user: ''

    # ssh-private-key - SSH 秘密鍵
    # Required
    ssh-private-key: ''

    # target-path - リモートサーバー上の削除対象パス
    # Required
    target-path: ''

    # dry-run - dry-run モードで実行するかどうか
    # Optional (default: 'false')
    dry-run: 'false'
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `ssh-host` | SSH サーバーのホスト名 | Yes | - |
| `ssh-user` | SSH ユーザー名 | Yes | - |
| `ssh-private-key` | SSH 秘密鍵 | Yes | - |
| `target-path` | リモートサーバー上の削除対象パス | Yes | - |
| `dry-run` | dry-run モードで実行するかどうか | No | `'false'` |

## Examples

### 基本的な使い方

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/undeploy-web-hosting-rsync@v1
    with:
      ssh-host: ${{ secrets.SSH_HOST }}
      ssh-user: ${{ secrets.SSH_USER }}
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
      target-path: '/home/user/public_html/_feature/feat-awesome'
```

### dry-run モードでの確認

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/undeploy-web-hosting-rsync@v1
    with:
      ssh-host: ${{ secrets.SSH_HOST }}
      ssh-user: ${{ secrets.SSH_USER }}
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
      target-path: '/home/user/public_html/_feature/feat-awesome'
      dry-run: 'true'
```

## Behavior

1. SSH 鍵をセットアップする（`~/.ssh/id_rsa` に秘密鍵を書き込み、`ssh-keyscan` でホスト鍵を取得）
2. 空ディレクトリ `./empty_dir` を作成する
3. `rsync -az --delete` で空ディレクトリをターゲットパスに同期する（実質的にターゲット内の全ファイルを削除）
4. 通常モードの場合、`rmdir` で空になった親ディレクトリの削除を試行する
5. dry-run モードの場合、`--dry-run` と `--verbose` フラグを追加する
6. debug モードの場合、`--verbose` フラグを追加する
7. 処理完了後（成功・失敗問わず）、SSH 鍵と `empty_dir` をクリーンアップする

## Prerequisites

- SSH サーバーへの接続情報（ホスト名、ユーザー名、秘密鍵）が設定されていること

<!-- ## Migration Guide -->

<!-- Breaking Changes がある場合にコメントアウトを解除して記載する -->
