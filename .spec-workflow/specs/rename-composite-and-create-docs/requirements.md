# Requirements Document

## Introduction

`.github/composite/` ディレクトリを `.github/actions/` へリネームし、全ての Reusable Workflows および Composite Actions の個別 README ドキュメントを作成する。

GitHub Actions エコシステムでは `actions/` ディレクトリが Composite Actions の標準的な配置先として広く採用されており、より直感的なパス名への移行と、各 Action/Workflow の利用方法ドキュメント整備を同時に行う。

## Requirements

### Requirement 1: ディレクトリリネーム

**User Story:** リポジトリ利用者として、`.github/composite/` を `.github/actions/` にリネームしたい。パスがより直感的になり、GitHub Actions の慣習に沿ったものにするため。

#### Acceptance Criteria

1. WHEN `git mv` でリネームを実行 THEN `.github/composite/` が `.github/actions/` に移動し、Git 履歴が保持される
2. WHEN リネーム後 THEN 以下の 4 つの Composite Actions がすべて `.github/actions/` 配下に存在する:
   - `pnpm-setup/action.yml`
   - `playwright-setup/action.yml`
   - `slack-notify-success/action.yml`
   - `slack-notify-failure/action.yml`
3. WHEN リネーム後 THEN `.ls-lint.yml` のパス設定が `.github/actions` に更新される
4. WHEN リネーム後 THEN `CLAUDE.md` 内の `.github/composite` への全参照が `.github/actions` に更新される
5. WHEN リネーム後 THEN `README.md` 内の `.github/composite` への全参照が `.github/actions` に更新される
6. WHEN リネーム後 THEN `docs/adr/004-composite-actions-support.md` 内の参照が更新される
7. WHEN リネーム後 THEN `.serena/memories/` 内の参照が更新される
8. WHEN リネーム後 THEN actionlint が `.github/actions/` を無視する（`.github/workflows/` のみスキャン対象）

### Requirement 2: ディレクトリ直下の一覧 README 作成

**User Story:** リポジトリ利用者として、`.github/workflows/` と `.github/actions/` の直下に一覧 README を配置したい。各 Workflow/Action の概要を一目で把握し、詳細ドキュメントへ素早くアクセスするため。

#### Acceptance Criteria

1. WHEN ドキュメント作成後 THEN `.github/workflows/README.md` が存在し、以下を含む:
   - 各 Reusable Workflow（`my-*` を除く）の簡単な説明文
   - 各 Workflow の詳細ドキュメント（`docs/*.md`）への相対リンク
   - 内部 CI ワークフロー（`my-*`）の一覧と簡単な説明
2. WHEN ドキュメント作成後 THEN `.github/actions/README.md` が存在し、以下を含む:
   - 各 Composite Action の簡単な説明文
   - 各 Action の詳細ドキュメント（`docs/*.md`）への相対リンク
3. WHEN ルート `README.md` を参照 THEN 以下が削除されている:
   - Reusable Workflows の詳細な使用方法（inputs テーブル、コード例等）
   - Composite Actions の詳細な使用方法（inputs テーブル、コード例等）
   - Internal CI Workflows の一覧テーブルと説明
4. WHEN ルート `README.md` を参照 THEN 以下の参照リンクが記載されている:
   - `.github/workflows/README.md` への参照リンク（Reusable Workflows 一覧）
   - `.github/actions/README.md` への参照リンク（Composite Actions 一覧）
   - `.github/workflows/README.md` 内の Internal CI Workflows セクションへの参照リンク

### Requirement 3: Reusable Workflows の詳細ドキュメント作成

**User Story:** リポジトリ利用者として、各 Reusable Workflow の詳細ドキュメントを参照したい。使い方・inputs・outputs・permissions・前提条件を素早く把握するため。

#### Acceptance Criteria

1. WHEN ドキュメント作成後 THEN 以下のファイルが存在する:
   - `.github/workflows/docs/actions-lint.md`
   - `.github/workflows/docs/auto-assign-pr.md`
   - `.github/workflows/docs/codeql-analysis.md`
   - `.github/workflows/docs/tagpr-release.md`
2. WHEN 各ドキュメントを参照 THEN 以下のセクションが含まれる:
   - 概要説明
   - トリガー（`workflow_call`）
   - inputs（名前・型・必須/任意・デフォルト値・説明）
   - secrets（ある場合）
   - outputs（ある場合）
   - 必要な permissions
   - 前提条件
   - 使用例（YAML コードブロック）
3. IF 内部 CI ワークフロー（`my-*`）THEN ドキュメントは作成しない（薄いラッパーのため）

### Requirement 4: Composite Actions の詳細ドキュメント作成

**User Story:** リポジトリ利用者として、各 Composite Action の詳細ドキュメントを参照したい。使い方・inputs・前提条件を素早く把握するため。

#### Acceptance Criteria

1. WHEN ドキュメント作成後 THEN 以下のファイルが存在する:
   - `.github/actions/docs/pnpm-setup.md`（リネーム後のパス）
   - `.github/actions/docs/playwright-setup.md`
   - `.github/actions/docs/slack-notify-success.md`
   - `.github/actions/docs/slack-notify-failure.md`
2. WHEN 各ドキュメントを参照 THEN 以下のセクションが含まれる:
   - 概要説明
   - inputs（名前・必須/任意・デフォルト値・説明）
   - 前提条件
   - 使用例（YAML コードブロック）
3. WHEN 使用例内の参照パス THEN `.github/actions/` パスが使用される（リネーム後のパス）

## Non-Functional Requirements

### 後方互換性

- **破壊的変更**: `.github/composite/` → `.github/actions/` のリネームは破壊的変更。外部リポジトリからの参照パスが変更される
- **リリース対応**: メジャーバージョンアップ（v1 → v2 等）として扱うべきか、CHANGELOG に明記するかは別途判断

### Git 履歴の保持

- `git mv` コマンドでリネームし、ファイルの Git 履歴を維持する
- 削除→新規作成によるリネームは禁止

### ドキュメント品質

- README は日本語で記述する（コードサンプル・技術用語は英語のまま）
- 各ドキュメントは自己完結的で、単体で理解可能であること
- `uses:` パスの例示は SHA ピン留めではなくメジャータグ（`@v1`）で記載する（簡潔さのため）

### CI 整合性

- リネーム後も ls-lint、ghalint、actionlint の全テストがパスすること
- actionlint は `.github/actions/` ディレクトリを自然に無視するか確認が必要
