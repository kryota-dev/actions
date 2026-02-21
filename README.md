# actions

`kryota-dev/actions` は再利用可能な GitHub Actions Reusable Workflow を一元管理するリポジトリです。

## Overview

複数のリポジトリで共通して使用する GitHub Actions Workflow を一元管理・公開することで、各リポジトリの CI/CD 設定の重複を排除し、品質と保守性を高めます。

## Usage

他のリポジトリから Reusable Workflow を参照する場合は以下の形式を使用します:

```yaml
jobs:
  example:
    uses: kryota-dev/actions/.github/workflows/{workflow}.yml@vX
    with:
      # inputs
    secrets:
      # secrets
```

バージョンはメジャータグ（例: `v1`）または完全なバージョンタグ（例: `v1.0.0`）で指定してください。

## Available Workflows

### Reusable Workflows

Coming soon.

### Internal CI Workflows

内部 CI ワークフロー（`my_` プレフィックス）はこのリポジトリ自身の品質管理に使用します。

| ワークフロー | トリガー | 説明 |
|---|---|---|
| `my_test.yml` | PR, merge_group | actionlint / ls-lint / ghalint / zizmor による品質ゲート |
| `my_setup_pr.yml` | PR opened | PR 作成者を自動で assignee に設定 |
| `my_release.yml` | push (main) | tagpr によるリリース管理とメジャータグ更新 |
| `my_codeql.yml` | PR, push (main), merge_group | CodeQL セキュリティスキャン |

## Development

### ADR (Architecture Decision Records)

設計上の意思決定は ADR として `docs/adr/` に記録します。

新しい ADR を作成する場合:

```bash
npm run adr:new -- "ADR のタイトル"
```

ADR の一覧は [docs/adr/](docs/adr/) を参照してください。

### Workflow Security Policy

全ての `uses:` 指定は **full commit SHA（40文字）** でピン留めされます:

```yaml
uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
```

SHA のピン留めは [ghalint](https://github.com/suzuki-shunsuke/ghalint) と [zizmor](https://github.com/zizmorcore/zizmor) により CI で自動検証され、[Renovate Bot](https://docs.renovatebot.com/) により自動更新されます。

## Manual Setup Required

以下の設定はリポジトリの Web UI または外部サービスで別途対応が必要です:

1. **`APP_TOKEN` シークレットの設定**: Settings > Secrets and variables > Actions で PAT を追加（`repo` と `workflow` スコープが必要）
2. **Renovate Bot のインストール**: [Renovate GitHub App](https://github.com/apps/renovate) をリポジトリにインストール
3. **Dependabot Alerts の有効化**: Settings > Security > Dependabot alerts を有効化
