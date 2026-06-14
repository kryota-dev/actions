[English](codex-pr-review.md) | **日本語**

# Codex PR Review

[openai/codex-action](https://github.com/openai/codex-action) を使って pull request をレビューする reusable workflow。Claude バリアントとは異なり、**単一の Codex エージェント**がエンドツーエンドで包括的なレビューを実行する — サブエージェントへの分割は行わない。既存レビューとの重複排除・各指摘のバリデーションを行い、1 つのレビュー（インライン `critical`/`warning` コメント + 全指摘を列挙した body）および upsert 形式のマーカータグ付きサマリーコメントとして投稿する。投稿モデル・重複排除ロジック・重要度ルール（`critical`/`warning`/`suggestion`）は Claude バリアントと同一だが、Codex action 自体は投稿を行わない — このワークフロー内の決定論的なステップが GitHub API 呼び出しをすべて処理する点が重要な違いである。

> Source: [`.github/workflows/codex-pr-review.yml`](../codex-pr-review.yml)

## Usage

```yaml
name: codex-pr-review
on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]
  issue_comment:
    types: [created]

concurrency:
  group: codex-pr-review-${{ github.event.pull_request.number || github.event.issue.number }}
  cancel-in-progress: true

permissions: {}

jobs:
  review:
    permissions:
      contents: read
      pull-requests: write
      issues: write
    uses: kryota-dev/actions/.github/workflows/codex-pr-review.yml@v0
    secrets:
      openai-api-key: ${{ secrets.OPENAI_API_KEY }}
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `model` | Codex モデル（空の場合は action のデフォルト；例: gpt-5.3-codex / gpt-5.5） | No | `'gpt-5.3-codex'` |
| `effort` | codex-action に渡す推論エフォート（例: low / medium / high） | No | `'medium'` |
| `sandbox` | codex-action のサンドボックスモード（read-only / workspace-write / danger-full-access） | No | `'read-only'` |
| `codex-version` | 再現性のため `@openai/codex` バージョンをピン留めする（空の場合は latest） | No | `''` |
| `codex-args` | codex exec に転送する追加 CLI 引数 | No | `''` |
| `review-instructions-path` | 組み込みデフォルトを上書きする `review-rules.md` の、呼び出し元チェックアウト内のパス | No | `''` |
| `additional-instructions` | Codex プロンプトに追加するレビュアー向け補足指示 | No | `''` |
| `output-language` | レビューの可読テキスト（problem/suggestion/サマリー）の言語。コードや識別子はそのまま | No | `'English'` |
| `paths` | レビュー対象に含めるカンマ／改行区切りの glob パターン（空の場合は diff 全体） | No | `''` |
| `exclude-paths` | レビューから除外するカンマ／改行区切りの glob パターン | No | `''` |
| `max-files` | diff が指定ファイル数を超えた場合に警告する閾値 | No | `200` |
| `max-diff-bytes` | diff がこのバイト数を超えた場合にレビューをスキップする閾値 | No | `500000` |
| `trigger-phrase` | `issue_comment` で再レビューをトリガーするフレーズ | No | `'/codex-review'` |
| `label-name` | `labeled` イベントでレビューをトリガーするラベル名 | No | `'codex-review'` |
| `submit` | レビューを送信する（`COMMENT`）。`false` の場合は pending のまま保留 | No | `true` |
| `review-event` | 送信時のレビューイベント（`COMMENT` / `APPROVE` / `REQUEST_CHANGES`） | No | `'COMMENT'` |
| `resolve-addressed` | コードが変更され、レビュアーが対応済みと判断した自分の過去インラインスレッドを resolve する。`false` = 自動 resolve しない | No | `true` |
| `skip-draft` | draft pull request をスキップする | No | `true` |
| `skip-bots` | bot 作成の pull request（`*[bot]`）をスキップする | No | `true` |
| `allowed-bots` | `skip-bots` が有効でもレビュー対象とする bot ログインのカンマ区切りリスト | No | `''` |
| `timeout-minutes` | ジョブタイムアウト（分） | No | `20` |

## Secrets

| Name | Description | Required |
|------|-------------|----------|
| `openai-api-key` | codex-action がモデルを呼び出すために使用する OpenAI API キー | Yes |
| `github-token` | diff の取得とレビュー／サマリーの投稿に使用するトークン。デフォルトはジョブの `github.token`；アプリトークンを指定するとコメント投稿者を変更できる | No |

> **ChatGPT サブスクリプションは CI で使用できない。従量課金の `OPENAI_API_KEY` が必須である。**

## Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| `contents` | `read` | PR の head をチェックアウトし、エージェントが関連コードを読めるようにする |
| `pull-requests` | `write` | diff／既存レビューの取得、インラインコメント付きレビューの作成、対応済みスレッドの resolve |
| `issues` | `write` | マーカータグ付きのナラティブサマリーコメントを upsert する |

自動 resolve は各スレッドの `viewerCanResolve` でゲーティングされるため、呼び出し元が指定した `github-token` にスレッドを resolve する権限がない場合でも安全に劣化する（警告をログ出力し、ジョブ自体は成功する）。

## 使用例

### OPENAI_API_KEY を使用して全 PR を自動レビュー

```yaml
jobs:
  review:
    permissions:
      contents: read
      pull-requests: write
      issues: write
    uses: kryota-dev/actions/.github/workflows/codex-pr-review.yml@v0
    secrets:
      openai-api-key: ${{ secrets.OPENAI_API_KEY }}
```

### コメントトリガー `/codex-review` によるオプトイン（effort high）

```yaml
on:
  issue_comment:
    types: [created]
jobs:
  review:
    permissions:
      contents: read
      pull-requests: write
      issues: write
    uses: kryota-dev/actions/.github/workflows/codex-pr-review.yml@v0
    with:
      trigger-phrase: '/codex-review'
      effort: 'high'
    secrets:
      openai-api-key: ${{ secrets.OPENAI_API_KEY }}
```

## 動作

1. **ゲート** — `pull_request` または `issue_comment` イベントから PR 番号を解決する。コメントの場合は `trigger-phrase` の一致と OWNER/MEMBER/COLLABORATOR による投稿を要求し、`skip-draft`／`skip-bots`／`label-name` の設定も適用する。
2. **アノテーション** — diff を取得し `paths`／`exclude-paths` を適用する。diff が空または `max-diff-bytes` を超えた場合はスキップする。モデルが実際の行番号を引用できるよう、各行に絶対行番号をアノテーションする。
3. **既存レビュー取得** — 重複排除のため、既存のレビュー／コメント／スレッド（一般的な bot の定型文は除外）を収集する。
4. **Codex 単一レビュー** — 単一のプロンプト（レビュールール + 既存レビュー JSON + アノテーション付き diff）を組み立て、`--output-schema` と `--output-file` を指定して `openai/codex-action` を呼び出す。エージェントは構造化された指摘 JSON を直接出力する。サブエージェントは生成されず、1 つの Codex エージェントがレビュー全体を処理する。
5. **投稿** — 決定論的なステップ（Codex action 自体は投稿しない）が各指摘の行を diff に対してバリデーションし（マッピング不可の指摘は body のみに掲載）、機械的な重複排除ガードを適用したうえで、1 つのレビュー（インライン `critical`/`warning` + 全指摘のテーブル形式 body）を作成して送信する（`submit: true` の場合）。その後 `<!-- codex-pr-review -->` サマリーコメントを upsert する。
6. **自動 resolve**（`resolve-addressed: true` の場合）— このワークフロー自身が過去に投稿したインラインスレッドのうち、**機械的ゲート**（自分のスレッドで、未 resolve・行アンカー・resolve 可能、かつ GitHub が `isOutdated`＝指摘行が変更済みと報告）**と** レビュアーの判断（対応済みとして列挙）の**両方**を満たすものを無言で resolve する。ハイブリッドな AND により未解決の問題を誤って閉じることを防ぐ。問題が実際に残っている場合は Codex が新規に再投稿する。各 resolve はベストエフォート（失敗しても警告を出すだけでジョブは失敗しない）。

再実行時はサマリーコメントをその場で置き換える。インラインコメントは重複排除されるため積み重ならず、対応済みスレッドは再投稿されず resolve される。

> **注記:** 再現性のため `codex-version` をピン留めすること。action のバージョンによっては tools が有効な場合に `--output-schema` が無視されることがあり、既知の動作バージョンにピン留めすることで予期しない出力フォーマットの変更を防止できる。

## 前提条件

- `openai-api-key` シークレットは**必須**である。ChatGPT サブスクリプションは CI で使用できない — [platform.openai.com](https://platform.openai.com/) の従量課金 API キーを指定する必要がある。
- 再現性のある一貫したレビューのため、`codex-version` を特定リリースにピン留めすること。空のままにすると最新バージョンが使用され、実行をまたいで動作が変わる可能性がある。
- 呼び出し元ワークフローが受け取りたい GitHub イベント（`pull_request`、`issue_comment`、および／または `labeled`）をワイヤリングする。ワークフローは 3 つすべてを内部で解決・ゲーティングする。
