# actions

`kryota-dev/actions` は再利用可能な GitHub Actions（Reusable Workflows および Composite Actions）を一元管理するリポジトリです。

## Overview

複数のリポジトリで共通して使用する GitHub Actions（Reusable Workflows および Composite Actions）を一元管理・公開することで、各リポジトリの CI/CD 設定の重複を排除し、品質と保守性を高めます。

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

### Composite Actions

他のリポジトリから Composite Action を参照する場合は以下の形式を使用します:

```yaml
steps:
  - uses: kryota-dev/actions/.github/composite/{action-name}@vX
    with:
      # inputs
```

バージョンはメジャータグ（例: `v1`）または完全なバージョンタグ（例: `v1.0.0`）で指定してください。

> **Reusable Workflows との違い**: Reusable Workflows は `jobs:` レベルで呼び出すのに対し、Composite Actions は `steps:` レベルで呼び出します。Composite Actions は呼び出し元ジョブ内でステップとして実行されるため、より細粒度な再利用が可能です。

## Available Workflows

### Reusable Workflows

#### codeql-analysis

CodeQL によるセキュリティスキャンを実行します。

| 入力名 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|
| `languages` | 任意 | `'["actions"]'` | スキャン対象言語の JSON 配列 |

```yaml
jobs:
  codeql:
    uses: kryota-dev/actions/.github/workflows/codeql-analysis.yml@v1

  # 言語を指定する場合
  codeql-js:
    uses: kryota-dev/actions/.github/workflows/codeql-analysis.yml@v1
    with:
      languages: '["javascript", "typescript"]'
```

---

#### tagpr-release

[tagpr](https://github.com/Songmu/tagpr) によるリリース管理とメジャータグ更新を実行します。

**前提条件:** リポジトリルートに `.tagpr` 設定ファイルが存在すること、`APP_TOKEN` シークレットが設定されていること

| シークレット名 | 必須 | 説明 |
|---|---|---|
| `app-token` | 必須 | tagpr 用 PAT（`repo` と `workflow` スコープが必要） |

| 出力名 | 説明 |
|---|---|
| `tag` | tagpr が生成したバージョンタグ（リリースなしの場合は空文字列） |

```yaml
jobs:
  release:
    uses: kryota-dev/actions/.github/workflows/tagpr-release.yml@v1
    secrets:
      app-token: ${{ secrets.APP_TOKEN }}
```

---

#### auto-assign-pr

PR 作成者を自動的に assignee に設定します。入力パラメータは不要です（`github` コンテキストから情報を取得します）。

```yaml
on:
  pull_request:
    types: [opened]

jobs:
  auto-assign:
    uses: kryota-dev/actions/.github/workflows/auto-assign-pr.yml@v1
```

---

#### actions-lint

GitHub Actions ワークフローの品質ゲート（actionlint / ls-lint / ghalint / zizmor）を実行します。

**前提条件:** リポジトリルートに `.ls-lint.yml` と `aqua.yaml`（ghalint 定義含む）が存在すること

| 入力名 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|
| `aqua-version` | 任意 | `v2.56.6` | aqua のバージョン |
| `reviewdog-reporter` | 任意 | `github-pr-review` | reviewdog のレポーター種別 |

```yaml
jobs:
  lint:
    uses: kryota-dev/actions/.github/workflows/actions-lint.yml@v1

  # パラメータをカスタマイズする場合
  lint-custom:
    uses: kryota-dev/actions/.github/workflows/actions-lint.yml@v1
    with:
      aqua-version: "v2.60.0"
      reviewdog-reporter: "github-check"
```

### Composite Actions

#### pnpm-setup

Node.js と pnpm のセットアップ、pnpm ストアキャッシュ、依存関係インストールを一括実行します。

**前提条件:** リポジトリルートに `.node-version`・`package.json`・`pnpm-lock.yaml` が存在すること

```yaml
steps:
  - uses: kryota-dev/actions/.github/composite/pnpm-setup@v1
```

---

#### playwright-setup

Playwright ブラウザをキャッシュ付きでインストールします。キャッシュヒット時はダウンロードをスキップします。

**前提条件:** `pnpm-setup` Action（または同等のセットアップ）が先に完了していること

```yaml
steps:
  - uses: kryota-dev/actions/.github/composite/pnpm-setup@v1
  - uses: kryota-dev/actions/.github/composite/playwright-setup@v1
```

---

#### slack-notify-success

ワークフロー成功時に Slack へ通知します。Slack Bot OAuth Token と `chat.postMessage` API を使用します。

| 入力名 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|
| `channel-id` | 必須 | - | Slack チャンネル ID |
| `bot-oauth-token` | 必須 | - | Slack Bot OAuth Token |
| `color` | 任意 | `good` | メッセージのカラーバー色 |
| `mention-user` | 任意 | `''` | メンション対象ユーザー |
| `title` | 任意 | `workflow execution completed` | メッセージタイトル |
| `message` | 任意 | 実行ログ URL | メッセージ本文 |
| `thread-ts` | 任意 | `'null'` | スレッド返信先 timestamp |
| `reply-broadcast` | 任意 | `'false'` | スレッド返信をチャンネルにもブロードキャストするか |

```yaml
steps:
  - uses: kryota-dev/actions/.github/composite/slack-notify-success@v1
    with:
      channel-id: ${{ vars.SLACK_CHANNEL_ID }}
      bot-oauth-token: ${{ secrets.SLACK_BOT_OAUTH_TOKEN }}
```

---

#### slack-notify-failure

ワークフロー失敗時に Slack へ通知します。Slack Incoming Webhook URL を使用します（`slack-notify-success` と異なり、チャンネル指定不要）。

| 入力名 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|
| `webhook-url` | 必須 | - | Slack Incoming Webhook URL |
| `color` | 任意 | `danger` | メッセージのカラーバー色 |
| `mention-user` | 任意 | `''` | メンション対象ユーザー |
| `title` | 任意 | `workflow failed` | メッセージタイトル |
| `message` | 任意 | 実行ログ URL | メッセージ本文 |

```yaml
steps:
  - uses: kryota-dev/actions/.github/composite/slack-notify-failure@v1
    with:
      webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### Internal CI Workflows

内部 CI ワークフロー（`my_` プレフィックス）はこのリポジトリ自身の品質管理に使用します。

| ワークフロー | トリガー | 説明 |
|---|---|---|
| `my-test.yml` | PR, merge_group | actionlint / ls-lint / ghalint / zizmor による品質ゲート |
| `my-setup-pr.yml` | PR opened | PR 作成者を自動で assignee に設定 |
| `my-release.yml` | push (main) | tagpr によるリリース管理とメジャータグ更新 |
| `my-codeql.yml` | PR, push (main), merge_group | CodeQL セキュリティスキャン |

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
