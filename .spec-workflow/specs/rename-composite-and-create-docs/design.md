# Design Document

## Overview

`.github/composite/` → `.github/actions/` へのディレクトリリネームと、Reusable Workflows / Composite Actions のドキュメント体系を構築する。ドキュメントは3層構造（ルート README → 一覧 README → 個別詳細ドキュメント）とし、情報の参照性と保守性を両立する。

## Architecture

### ドキュメント3層構造

```
README.md（ルート）
├── 概要 + 参照リンク
├── → .github/workflows/README.md
├── → .github/actions/README.md
└── Development / Security Policy 等（既存セクション維持）

.github/workflows/README.md（一覧）
├── Reusable Workflows 一覧（簡単な説明 + 詳細リンク）
├── Internal CI Workflows 一覧（簡単な説明）
└── → docs/*.md

.github/actions/README.md（一覧）
├── Composite Actions 一覧（簡単な説明 + 詳細リンク）
└── → docs/*.md

.github/workflows/docs/*.md（個別詳細）
.github/actions/docs/*.md（個別詳細）
```

### リネーム後のディレクトリ構造

```
.github/
├── actions/                          # ← .github/composite/ からリネーム
│   ├── README.md                     # 新規: Composite Actions 一覧
│   ├── docs/                         # 新規: 詳細ドキュメント
│   │   ├── pnpm-setup.md
│   │   ├── playwright-setup.md
│   │   ├── slack-notify-success.md
│   │   └── slack-notify-failure.md
│   ├── pnpm-setup/action.yml
│   ├── playwright-setup/action.yml
│   ├── slack-notify-success/action.yml
│   └── slack-notify-failure/action.yml
├── workflows/
│   ├── README.md                     # 新規: Workflows 一覧 + Internal CI 説明
│   ├── docs/                         # 新規: 詳細ドキュメント
│   │   ├── actions-lint.md
│   │   ├── auto-assign-pr.md
│   │   ├── codeql-analysis.md
│   │   └── tagpr-release.md
│   ├── actions-lint.yml
│   ├── auto-assign-pr.yml
│   ├── codeql-analysis.yml
│   ├── tagpr-release.yml
│   ├── my-test.yml
│   ├── my-setup-pr.yml
│   ├── my-release.yml
│   └── my-codeql.yml
└── ...
```

## Components and Interfaces

### Component 1: ディレクトリリネーム

- **Purpose:** `.github/composite/` を `.github/actions/` にリネームし、全参照を更新
- **操作:**
  1. `git mv .github/composite .github/actions`
  2. 以下のファイル内の参照を `.github/composite` → `.github/actions` に一括置換:
     - `.ls-lint.yml`
     - `CLAUDE.md`
     - `README.md`
     - `docs/adr/004-composite-actions-support.md`
  3. Serena memories の更新（`codebase_structure`, `style_and_conventions`, `task_completion_checklist`）

### Component 2: `.github/workflows/README.md`（一覧）

- **Purpose:** Reusable Workflows と Internal CI Workflows の一覧ページ
- **構造:**

```markdown
# Workflows

## Reusable Workflows

| ワークフロー | 説明 |
|---|---|
| [actions-lint](docs/actions-lint.md) | GitHub Actions の品質ゲート |
| [auto-assign-pr](docs/auto-assign-pr.md) | PR 作成者の自動 assignee 設定 |
| [codeql-analysis](docs/codeql-analysis.md) | CodeQL セキュリティスキャン |
| [tagpr-release](docs/tagpr-release.md) | tagpr リリース管理 |

## 使い方

{簡潔な uses: の書式説明}

## Internal CI Workflows

| ワークフロー | トリガー | 呼び出し先 | 説明 |
|---|---|---|---|
| my-test.yml | PR, merge_group | actions-lint.yml | 品質ゲート |
| my-setup-pr.yml | PR opened | auto-assign-pr.yml | 自動 assignee |
| my-release.yml | push (main) | tagpr-release.yml | リリース管理 |
| my-codeql.yml | PR, push, merge_group | codeql-analysis.yml | セキュリティスキャン |
```

### Component 3: `.github/actions/README.md`（一覧）

- **Purpose:** Composite Actions の一覧ページ
- **構造:**

```markdown
# Actions

## Composite Actions

| アクション | 説明 |
|---|---|
| [pnpm-setup](docs/pnpm-setup.md) | Node.js + pnpm セットアップ |
| [playwright-setup](docs/playwright-setup.md) | Playwright ブラウザセットアップ |
| [slack-notify-success](docs/slack-notify-success.md) | Slack 成功通知 |
| [slack-notify-failure](docs/slack-notify-failure.md) | Slack 失敗通知 |

## 使い方

{簡潔な uses: の書式説明}
```

### Component 4: Reusable Workflow 詳細ドキュメント（4ファイル）

- **Purpose:** 各 Reusable Workflow の詳細リファレンス
- **共通構造:**

```markdown
# {workflow-name}

{概要説明}

## トリガー

`workflow_call`

## Inputs

| 入力名 | 型 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|---|

## Secrets（該当する場合）

| シークレット名 | 必須 | 説明 |
|---|---|---|

## Outputs（該当する場合）

| 出力名 | 説明 |
|---|---|

## Permissions

{必要な permissions の表}

## 前提条件

{前提条件の箇条書き}

## 使用例

{YAML コードブロック}
```

### Component 5: Composite Action 詳細ドキュメント（4ファイル）

- **Purpose:** 各 Composite Action の詳細リファレンス
- **共通構造:**

```markdown
# {action-name}

{概要説明}

## Inputs

| 入力名 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|

## 前提条件

{前提条件の箇条書き}

## 使用例

{YAML コードブロック}
```

### Component 6: ルート `README.md` のリファクタリング

- **Purpose:** 詳細情報を各一覧 README に委譲し、簡潔なトップページにする
- **削除対象:** `Available Workflows` セクション内の:
  - Reusable Workflows の詳細（inputs テーブル、コード例）
  - Composite Actions の詳細（inputs テーブル、コード例）
  - Internal CI Workflows テーブル
- **追加内容:** 各一覧 README への参照リンク
- **維持するセクション:** Overview, Usage（簡潔な形式説明のみ）, Development, Workflow Security Policy, Manual Setup Required

## 参照更新の全一覧

### `.github/composite` → `.github/actions` の文字列置換が必要なファイル

| ファイル | 更新箇所 |
|---|---|
| `.ls-lint.yml` | `.github/composite:` → `.github/actions:` |
| `CLAUDE.md` | 3箇所（ディレクトリ構成、使い分け、actionlint非互換）|
| `README.md` | 使用例の `uses:` パス（複数箇所）|
| `docs/adr/004-composite-actions-support.md` | 決定事項・結果の記述（複数箇所）|
| `.serena/memories/codebase_structure` | ディレクトリ構造説明 |
| `.serena/memories/style_and_conventions` | ファイル配置ルール |
| `.serena/memories/task_completion_checklist` | Composite Actions 配置ルール |

## actionlint との互換性

actionlint は `.github/workflows/` ディレクトリのみをスキャン対象とする。`.github/actions/` は `.github/workflows/` の外にあるため、`composite/` と同様に自然に無視される。追加設定は不要。

## Testing Strategy

### CI 整合性確認

- `ls-lint` が `.github/actions/` 配下の命名規則を正しく検証すること（`.ls-lint.yml` の更新後）
- `ghalint run-action` が `.github/actions/` 配下の `action.yml` をスキャンすること
- `actionlint` が `.github/actions/` を無視すること

### ドキュメントリンク整合性

- 各一覧 README 内のリンクが正しい詳細ドキュメントを指していること
- ルート README 内のリンクが正しい一覧 README を指していること
- 使用例の `uses:` パスが `.github/actions/` を使用していること
