# tagpr-release

> ソースファイル: [`.github/workflows/tagpr-release.yml`](../tagpr-release.yml)

[tagpr](https://github.com/Songmu/tagpr) によるリリース管理とメジャータグ更新を実行する Reusable Workflow です。CHANGELOG.md をベースにリリース PR を自動作成し、main マージ時にセマンティックバージョンタグを付与します。メジャータグ（例: `v1`）も自動更新されます。

## トリガー

`workflow_call`

## Secrets

| シークレット名 | 必須 | 説明 |
|---|---|---|
| `app-token` | 必須 | tagpr 用 Personal Access Token（`repo` と `workflow` スコープが必要） |

## Outputs

| 出力名 | 説明 |
|---|---|
| `tag` | tagpr が生成したバージョンタグ（リリースなしの場合は空文字列） |

## Permissions

| 権限 | レベル | 用途 |
|---|---|---|
| `contents` | `write` | タグの作成・プッシュ |
| `pull-requests` | `write` | リリース PR の作成・更新 |

## 前提条件

- リポジトリルートに `.tagpr` 設定ファイルが存在すること
- `APP_TOKEN` シークレット（PAT）がリポジトリに設定されていること（`repo` と `workflow` スコープ）
- `GITHUB_TOKEN` では権限が不足するため PAT が必須

## 使用例

```yaml
on:
  push:
    branches: [main]

jobs:
  release:
    permissions:
      contents: write
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/tagpr-release.yml@v1
    secrets:
      app-token: ${{ secrets.APP_TOKEN }}
```
