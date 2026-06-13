[English](claude-pr-review.md) | **日本語**

# Claude PR Review

[Claude Code GitHub Actions](https://github.com/anthropics/claude-code-action) を使って pull request をレビューする reusable workflow。メインエージェントがロール特化のレビューサブエージェントを動的にアサインして並列実行し、それらの結果と既存レビューを統合・重複排除したうえでバリデーションを行い、1 つのレビュー（インライン `critical`/`warning` コメント + 全指摘を列挙した body）および upsert 形式のナラティブサマリーコメントとして投稿する。

> Source: [`.github/workflows/claude-pr-review.yml`](../claude-pr-review.yml)

## Usage

```yaml
name: claude-pr-review
on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]
  issue_comment:
    types: [created]

concurrency:
  group: claude-pr-review-${{ github.event.pull_request.number || github.event.issue.number }}
  cancel-in-progress: true

permissions: {}

jobs:
  review:
    permissions:
      contents: read
      pull-requests: write
      issues: write
    uses: kryota-dev/actions/.github/workflows/claude-pr-review.yml@v0
    secrets:
      claude-code-oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `model` | `--model` フラグ経由で claude-code-action に渡す Claude モデル | No | `'claude-sonnet-4-6'` |
| `max-review-agents` | 並列実行するレビューサブエージェントの最大数 | No | `5` |
| `review-roles` | カンマ区切りで固定するレビュアーロール（空の場合はロールカタログから自動選択） | No | `''` |
| `role-prompts-dir` | 呼び出し元チェックアウト内のオーバーライド用プロンプトファイル（`role-catalog.md`）を格納するディレクトリ | No | `''` |
| `review-instructions-path` | 組み込みデフォルトを上書きする `review-rules.md` の、呼び出し元チェックアウト内のパス | No | `''` |
| `additional-instructions` | オーケストレーションプロンプトに追加するレビュアー向け補足指示 | No | `''` |
| `claude-args` | `claude_args` に追加する CLI 引数 | No | `''` |
| `paths` | レビュー対象に含めるカンマ／改行区切りの glob パターン（空の場合は diff 全体） | No | `''` |
| `exclude-paths` | レビューから除外するカンマ／改行区切りの glob パターン | No | `''` |
| `max-files` | diff が指定ファイル数を超えた場合に警告する閾値 | No | `200` |
| `max-diff-bytes` | diff がこのバイト数を超えた場合にレビューをスキップする閾値 | No | `500000` |
| `trigger-phrase` | `issue_comment` で再レビューをトリガーするフレーズ | No | `'/claude-review'` |
| `label-name` | `labeled` イベントでレビューをトリガーするラベル名 | No | `'claude-review'` |
| `submit` | レビューを送信する（`COMMENT`）。`false` の場合は pending のまま保留 | No | `true` |
| `review-event` | 送信時のレビューイベント（`COMMENT` / `APPROVE` / `REQUEST_CHANGES`） | No | `'COMMENT'` |
| `skip-draft` | draft pull request をスキップする | No | `true` |
| `skip-bots` | bot 作成の pull request（`*[bot]`）をスキップする | No | `true` |
| `allowed-bots` | `skip-bots` が有効でもレビュー対象とする bot ログインのカンマ区切りリスト | No | `''` |
| `timeout-minutes` | ジョブタイムアウト（分） | No | `30` |

## Secrets

| Name | Description | Required |
|------|-------------|----------|
| `claude-code-oauth-token` | Claude Pro/Max の OAuth トークン（`claude setup-token` で取得）。サブスクリプションを使用するため API 従量課金が発生しない優先オプション | No\* |
| `anthropic-api-key` | Anthropic API キー（従量課金）。OAuth トークンの代替 | No\* |
| `github-token` | diff の取得とレビュー／サマリーの投稿に使用するトークン。デフォルトはジョブの `github.token`；アプリトークンを指定するとコメント投稿者を変更できる | No |

\* `claude-code-oauth-token` または `anthropic-api-key` のいずれか **少なくとも 1 つ**を設定すること。両方とも未設定の場合はワークフローがフェイルファストする。

## Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| `contents` | `read` | PR の head をチェックアウトし、エージェントが関連コードを読めるようにする |
| `pull-requests` | `write` | diff／既存レビューの取得と、インラインコメント付きレビューの作成 |
| `issues` | `write` | マーカータグ付きのナラティブサマリーコメントを upsert する |

## 使用例

### 全 PR を自動レビュー（Claude Max を OAuth 経由で使用）

```yaml
jobs:
  review:
    permissions:
      contents: read
      pull-requests: write
      issues: write
    uses: kryota-dev/actions/.github/workflows/claude-pr-review.yml@v0
    secrets:
      claude-code-oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
```

### ラベルによるオプトイン（固定ロールセット + Opus）

```yaml
on:
  pull_request:
    types: [labeled]
jobs:
  review:
    if: github.event.label.name == 'ai-review'
    permissions:
      contents: read
      pull-requests: write
      issues: write
    uses: kryota-dev/actions/.github/workflows/claude-pr-review.yml@v0
    with:
      label-name: 'ai-review'
      model: 'claude-opus-4-8'
      review-roles: 'security,correctness,tests'
      submit: false
    secrets:
      anthropic-api-key: ${{ secrets.ANTHROPIC_API_KEY }}
```

## 動作

1. **ゲート** — `pull_request` または `issue_comment` イベントから PR 番号を解決する。コメントの場合は `trigger-phrase` の一致と OWNER/MEMBER/COLLABORATOR による投稿を要求し、`skip-draft`／`skip-bots`／`label-name` の設定も適用する。
2. **アノテーション** — diff を取得し `paths`／`exclude-paths` を適用する。diff が空または `max-diff-bytes` を超えた場合はスキップする。モデルが実際の行番号を引用できるよう、各行に絶対行番号をアノテーションする。
3. **既存レビュー取得** — 重複排除のため、既存のレビュー／コメント／スレッド（一般的な bot の定型文は除外）を収集する。
4. **レビュー** — メインエージェントが組み込みカタログ（または `review-roles`）からロールを選択し、最大 `max-review-agents` 数の並列サブエージェントを起動する。結果を統合・意味的重複排除・バリデーションして構造化された指摘 JSON を出力する。
5. **投稿** — 決定論的なステップが各指摘の行を diff に対してバリデーションし（マッピング不可の指摘は body のみに掲載）、機械的な重複排除ガードを適用したうえで、1 つのレビュー（インライン `critical`/`warning` + 全指摘のテーブル形式 body）を作成して送信する（`submit: true` の場合）。その後 `<!-- claude-pr-review -->` サマリーコメントを upsert する。

再実行時はサマリーコメントをその場で置き換える。インラインコメントは重複排除されるため積み重ならない。

## 前提条件

- `claude-code-oauth-token` **または** `anthropic-api-key` のシークレット。
- 呼び出し元ワークフローが受け取りたい GitHub イベント（`pull_request`、`issue_comment`、および／または `labeled`）をワイヤリングする。ワークフローは 3 つすべてを内部で解決・ゲーティングする。
