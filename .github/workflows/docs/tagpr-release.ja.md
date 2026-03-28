[English](tagpr-release.md) | **日本語**

# tagpr Release

tagpr によるリリース管理とメジャータグ更新ワークフロー

> Source: [`.github/workflows/tagpr-release.yml`](../tagpr-release.yml)

## Usage

```yaml
jobs:
  release:
    permissions:
      contents: write
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/tagpr-release.yml@v0
    secrets:
      # app-token - tagpr 用の Personal Access Token（'repo' と 'workflow' スコープが必要）
      # Required
      app-token: ${{ secrets.APP_TOKEN }}
```

## Inputs

None

## Secrets

| Name | Description | Required |
|------|-------------|----------|
| `app-token` | tagpr 用の Personal Access Token（`repo` と `workflow` スコープが必要） | Yes |

## Outputs

| Name | Description |
|------|-------------|
| `tag` | tagpr が作成したバージョンタグ（リリースがない場合は空） |

## Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| `contents` | `write` | tagpr によるタグ作成・プッシュおよびメジャータグの強制更新 |
| `pull-requests` | `write` | tagpr によるリリース PR の作成・更新 |

## Examples

### 基本的な使い方

```yaml
jobs:
  release:
    permissions:
      contents: write
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/tagpr-release.yml@v0
    secrets:
      app-token: ${{ secrets.APP_TOKEN }}
```

### リリース後に後続ジョブを実行する

```yaml
jobs:
  release:
    permissions:
      contents: write
      pull-requests: write
    uses: kryota-dev/actions/.github/workflows/tagpr-release.yml@v0
    secrets:
      app-token: ${{ secrets.APP_TOKEN }}

  post-release:
    needs: release
    if: needs.release.outputs.tag != ''
    runs-on: ubuntu-latest
    steps:
      - run: echo "Released ${{ needs.release.outputs.tag }}"
```

## Behavior

このワークフローは `tagpr` ジョブと `bump_major_tag` ジョブの2つで構成されます。

**Concurrency**: `group: {workflow}-release` / `cancel-in-progress: false`

### tagpr ジョブ

1. `actions/checkout@v6` でリポジトリをチェックアウト（ref: `pull_request` イベント時は `github.head_ref`、それ以外はデフォルト、token: `app-token`、`persist-credentials: false`）
2. `Songmu/tagpr@v1.17.1` を実行してリリース PR の作成・マージ・タグ付けを行う（`GITHUB_TOKEN: app-token`）
3. リリースされた場合はバージョンタグを `tag` output として出力（リリースがなければ空）

### bump_major_tag ジョブ

`tagpr` ジョブの完了後、タグが作成された場合（`tag != ''`）のみ実行されます。

1. `actions/checkout@v6` でリポジトリをチェックアウト（token: `app-token`、`persist-credentials: false`）
2. タグからメジャーバージョンを抽出（例: `v1.2.3` → `v1`）
3. `git tag -f` でメジャータグを更新し、`git push --force` でリモートに反映

## Prerequisites

- GitHub App Token または Personal Access Token（`repo` + `workflow` スコープ）が必要
- `.tagpr` 設定ファイルがリポジトリに存在すること
