# AGENTS.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

GitHub Actions の Reusable Workflow を一元管理・公開するリポジトリ。複数リポジトリで共通利用する Workflow を集約し、CI/CD 設定の重複を排除する。

## コマンド

```bash
# ADR（Architecture Decision Record）の新規作成
npm run adr:new -- "タイトル"

# ghalint（GitHub Actions セキュリティポリシー検証）
ghalint run

# zizmor（静的セキュリティ分析）
uvx zizmor --format=github .

# aqua（CLI バージョン管理）でツールインストール
aqua install
```

ローカルに actionlint / ls-lint の単体実行コマンドはない。CI（`my_test.yml`）で reviewdog / ls-lint action 経由で実行される。

## アーキテクチャ

### Workflow の分類

- **`my_*.yml`**: 内部用 Workflow（このリポジトリ自体の CI/CD）
  - `my_test.yml` — 品質ゲート（actionlint, ls-lint, ghalint, zizmor）
  - `my_release.yml` — tagpr による自動リリース + メジャータグ更新
  - `my_setup_pr.yml` — PR 作成者を assignee に自動追加
  - `my_codeql.yml` — CodeQL セキュリティスキャン
- **`my_` プレフィックスなし**: 外部リポジトリから呼び出される Reusable Workflow（今後追加）

### リリースフロー

main へのマージ → tagpr がリリース PR 自動作成 → リリース PR マージで vX.Y.Z タグ付与 → vX メジャータグ自動更新

### 設計記録

ADR は `docs/adr/` に 3 桁ゼロ埋めプレフィックス（001, 002...）、英語で記録。

## 必須ルール

### SHA ピン留め

全ての `uses:` 指定は **full commit SHA（40文字）でピン留め必須**。ミュータブルタグ（`@v1`, `@main` 等）は禁止。ghalint と zizmor が CI で自動検証する。Renovate Bot が digest SHA を自動更新する。

```yaml
# OK
uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2

# NG
uses: actions/checkout@v4
```

### 権限最小化

各 Workflow はトップレベルで `permissions: {}` を宣言し、ジョブごとに必要最小限の権限のみ明示的に指定する。

### 命名規則

- Workflow ファイル: `snake_case.yml`（ls-lint で強制）
- 内部 Workflow: `my_` プレフィックス
- ADR: `NNN-kebab-case-title.md`

## ツールチェーン

| ツール | 用途 | バージョン管理 |
|--------|------|---------------|
| ghalint | Actions セキュリティポリシー検証 | aqua (`aqua.yaml`) |
| actionlint | YAML 構文チェック | CI で reviewdog action 経由 |
| ls-lint | ファイル命名規則チェック | CI で ls-lint action 経由 |
| zizmor | テンプレートインジェクション等の静的分析 | CI で `uvx` 経由 |
| tagpr | semantic versioning 自動リリース | `.tagpr` で設定 |
| Renovate Bot | 依存関係・SHA digest 自動更新 | `renovate.json5` |
| adr (npm) | ADR 管理 | `package.json` |

## シークレット

- リリースワークフロー（tagpr / メジャータグ更新）は `GITHUB_TOKEN` を使用（`github-actions[bot]` として動作）
