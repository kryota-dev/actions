# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## リポジトリ概要

再利用可能な GitHub Actions（Reusable Workflows および Composite Actions）を一元管理・公開するリポジトリ。TypeScript/JavaScript のソースコードは存在せず、GitHub Actions YAML ファイルが主な成果物。

## コマンド

```bash
# ADR（Architecture Decision Record）の新規作成
npm run adr:new -- "ADRのタイトル"

# Lint（CIで自動実行されるもの。ローカルでの実行は aqua 経由）
aqua exec -- actionlint           # ワークフロー構文チェック
ls-lint                           # ファイル命名規則チェック
aqua exec -- ghalint run          # ワークフロー セキュリティ検証
aqua exec -- ghalint run-action   # Composite Action セキュリティ検証

# Ruleset 管理（.github/rulesets/*.json ↔ GitHub API）
bash .claude/skills/manage-rulesets/scripts/manage-rulesets.sh apply   # ローカル JSON を GitHub に適用
bash .claude/skills/manage-rulesets/scripts/manage-rulesets.sh diff    # ローカルと GitHub の差分確認
bash .claude/skills/manage-rulesets/scripts/manage-rulesets.sh export  # GitHub 設定をローカルにエクスポート
```

## アーキテクチャ

### ディレクトリ構成

- `.github/workflows/` — 外部公開用 Reusable Workflows + 内部 CI ワークフロー（`my-` プレフィックス）
- `.github/actions/{action-name}/action.yml` — 外部公開用 Composite Actions
- `.github/rulesets/` — ブランチ・タグ保護ルール（JSON、`manage-rulesets` スクリプトで GitHub と同期）
- `docs/adr/` — Architecture Decision Records

### Reusable Workflows と Composite Actions の使い分け

- **Reusable Workflows**（`.github/workflows/`）: `jobs:` レベルで呼び出し。別ジョブとして実行される。`workflow_call` トリガーを持つ
- **Composite Actions**（`.github/actions/`）: `steps:` レベルで呼び出し。呼び出し元ジョブ内のステップとして実行される

### 内部 CI の薄いラッパーパターン

内部 CI（`my-*.yml`）は Reusable Workflows を `uses:` で呼び出す薄いラッパー。トリガー・concurrency・permissions のみ保持し、ロジックは Reusable Workflow に委譲する:

```yaml
# my-test.yml（ラッパー）→ actions-lint.yml（Reusable Workflow）
jobs:
  lint:
    permissions:
      contents: read
      pull-requests: write
    uses: ./.github/workflows/actions-lint.yml
```

**注意**: Reusable Workflow を `uses:` で呼び出すとチェック名が `{呼び出し元ジョブ名} / {呼び出し先ジョブ名}` になる（例: `lint / lint`）。Ruleset の required status checks 名もこの形式で設定する必要がある。

### permissions 継承

Reusable Workflow では呼び出し元のジョブレベル `permissions` が上限境界となる。呼び出し先はその範囲内でしか権限を持てない。トップレベルは必ず `permissions: {}` にし、ジョブレベルで必要最小限を宣言する。

### リリース管理

tagpr が CHANGELOG.md をベースにリリース PR を自動作成し、main マージ時にセマンティックバージョンタグを付与。`bump_major_tag` ジョブでメジャータグ（v1, v2 等）も更新される。`APP_TOKEN`（PAT）が必須（`GITHUB_TOKEN` では不可）。

## 厳守すべきルール

### SHA ピン留め

すべての `uses:` は **full commit SHA（40文字）** でピン留めし、タグをコメントで記載する:

```yaml
uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
```

ghalint と zizmor が CI で自動検証。Renovate Bot（`helpers:pinGitHubActionDigests` プリセット）が自動更新。

### 命名規則

- ワークフローファイル: **kebab-case**（例: `my-test.yml`, `actions-lint.yml`）
- 内部 CI: `my-` プレフィックス必須（例: `my-test.yml`）
- 外部公開 Reusable Workflows: プレフィックスなし、具体的な名前（例: `codeql-analysis.yml`, `tagpr-release.yml`）
- Composite Action ディレクトリ: **kebab-case**（例: `pnpm-setup/`）
- Composite Action ファイル名: `action.yml` 固定
- ls-lint が CI で自動検証

### actionlint と Composite Actions の非互換

actionlint は `action.yml` をサポートしない。Composite Actions は `.github/actions/` に配置することで actionlint の対象外となる。`.github/workflows/` には絶対に置かないこと。

### CI 品質ゲート

PR に対して以下が自動実行される:
- **actionlint**: ワークフロー構文チェック（reviewdog 統合）
- **ls-lint**: ファイル命名規則チェック
- **ghalint**: SHA ピン留め・セキュリティポリシー検証
- **zizmor**: 静的セキュリティ分析（テンプレートインジェクション等）
- **CodeQL**: セキュリティスキャン
