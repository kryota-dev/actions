# Requirements Document: actions-lint "No Config" Improvement

## Introduction

`actions-lint.yml` Reusable Workflow を改善し、caller 側に設定ファイル（`aqua.yaml`, `.ls-lint.yml`）不要で動作する "no config" な RW にする。併せて、全 lint ツール（actionlint, reviewdog, ls-lint, ghalint, zizmor）のバージョン管理を aqua に統一し、Renovate による自動更新を実現する。

現在のワークフローでは、各ツールの GitHub Action（`reviewdog/action-actionlint`, `ls-lint/action`）や `uvx`（zizmor）を個別に使用しており、バージョン管理が分散している。また、caller 側で `aqua.yaml` の設置が必要であり、導入の敷居が高い。

## Alignment with Product Vision

このリポジトリは再利用可能な GitHub Actions を一元管理・公開する場であり、caller 側の設定を最小限に抑えることが重要な設計方針。本改善により、caller は `uses:` 一行で包括的な lint チェックを利用でき、リポジトリの価値が向上する。

## Requirements

### Requirement 1: caller 側の設定ファイル不要化

**User Story:** As a caller workflow の管理者, I want actions-lint.yml を設定ファイルなしで呼び出したい, so that 導入コストを最小限に抑えられる

#### Acceptance Criteria

1. WHEN caller が `uses: kryota-dev/actions/.github/workflows/actions-lint.yml@v2` のみを指定 THEN actions-lint.yml SHALL `aqua.yaml` なしで全ツールをインストールし lint を実行する
2. WHEN caller のリポジトリに `.ls-lint.yml` が存在しない THEN actions-lint.yml SHALL 内蔵デフォルト設定（kebab-case ルール）で ls-lint を実行する
3. WHEN caller のリポジトリに `.ls-lint.yml` が存在する THEN actions-lint.yml SHALL caller の設定ファイルを優先して使用する
4. IF caller が `ls-lint-config` input を指定 THEN actions-lint.yml SHALL 指定されたパスの設定ファイルを使用する

### Requirement 2: 全ツールの aqua 統一管理

**User Story:** As a リポジトリメンテナー, I want 全 lint ツールを aqua で統一管理したい, so that バージョン管理が一元化され保守性が向上する

#### Acceptance Criteria

1. WHEN ワークフローが実行される THEN actionlint, reviewdog, ls-lint, ghalint, zizmor の 5 ツールが全て aqua 経由でインストールされる
2. WHEN aqua がインストールされる THEN aqua-installer は SHA ピン留め済みのバージョンで実行される
3. WHEN 各ツールのバージョンが定義される THEN バージョン文字列は `# renovate:` コメント注釈付きで YAML 内に記述される

### Requirement 3: 個別ツールのスキップ制御

**User Story:** As a caller workflow の管理者, I want 特定の lint ツールをスキップしたい, so that プロジェクトに不要なチェックを除外できる

#### Acceptance Criteria

1. WHEN `skip-actionlint: true` が指定される THEN actions-lint.yml SHALL actionlint ステップをスキップする
2. WHEN `skip-ls-lint: true` が指定される THEN actions-lint.yml SHALL ls-lint ステップをスキップする
3. WHEN `skip-ghalint: true` が指定される THEN actions-lint.yml SHALL ghalint run および ghalint run-action の両ステップをスキップする
4. WHEN `skip-zizmor: true` が指定される THEN actions-lint.yml SHALL zizmor ステップをスキップする
5. IF いずれの skip input も指定されない THEN actions-lint.yml SHALL 全ツールを実行する

### Requirement 4: 各ツールのカスタム設定サポート

**User Story:** As a caller workflow の管理者, I want 各ツールの設定ファイルパスを指定したい, so that プロジェクト固有の lint ルールを適用できる

#### Acceptance Criteria

1. WHEN `actionlint-config` input が指定される THEN actions-lint.yml SHALL 指定パスの設定ファイルで actionlint を実行する
2. WHEN `ghalint-config` input が指定される THEN actions-lint.yml SHALL 指定パスの設定ファイルで ghalint を実行する
3. WHEN `zizmor-config` input が指定される THEN actions-lint.yml SHALL 指定パスの設定ファイルで zizmor を実行する
4. IF 設定 input が空の場合 THEN actions-lint.yml SHALL 各ツールのデフォルト動作（自動検出）で実行する

### Requirement 5: Renovate による自動バージョン更新

**User Story:** As a リポジトリメンテナー, I want ツールバージョンが Renovate で自動更新されてほしい, so that 手動でのバージョン追従作業が不要になる

#### Acceptance Criteria

1. WHEN Renovate が実行される THEN actions-lint.yml 内の `# renovate:` 注釈付きバージョンを検出し更新 PR を作成する
2. WHEN `.github/renovate.json5` に customManagers が追加される THEN aqua-registry, actionlint, reviewdog, ls-lint, ghalint, zizmor の 6 つのバージョンが管理対象となる

### Requirement 6: 既存の出力互換性維持

**User Story:** As a PR レビュアー, I want lint 結果が既存と同等の形式で表示されてほしい, so that レビューワークフローに支障が出ない

#### Acceptance Criteria

1. WHEN actionlint がエラーを検出する THEN reviewdog が PR コメントとして結果を投稿する（既存の reviewdog/action-actionlint と同等）
2. WHEN zizmor がセキュリティ問題を検出する THEN GitHub Annotations として結果が表示される（`--format github` 出力）
3. WHEN ls-lint が命名規則違反を検出する THEN CLI のエラー出力でジョブが失敗する
4. WHEN ghalint がポリシー違反を検出する THEN CLI のエラー出力でジョブが失敗する

### Requirement 7: ドキュメント更新

**User Story:** As a actions ユーザー, I want 正確なドキュメントを参照したい, so that ワークフローの使い方を理解できる

#### Acceptance Criteria

1. WHEN actions-lint.yml が更新される THEN `.github/workflows/docs/actions-lint.md`（英語版）が更新される
2. WHEN actions-lint.yml が更新される THEN `.github/workflows/docs/actions-lint.ja.md`（日本語版）が更新される
3. WHEN ドキュメントが更新される THEN inputs テーブル、permissions テーブル、behavior ステップが最新の実装と一致する

## Non-Functional Requirements

### Reliability
- aqua インストール失敗時にワークフロー全体が明確なエラーで失敗すること
- 各 lint ステップは独立して実行され、一つの失敗が他のステップの実行を妨げないこと（ただし、全ステップ完了後にジョブは失敗とする）

### Performance
- aqua のキャッシュ機構により、2 回目以降の実行ではツールインストール時間が短縮されること
- ワークフロー全体の実行時間が現行と大きく変わらないこと（10 分以内のタイムアウト）

### Security
- aqua-installer は SHA ピン留め済みバージョンを使用すること
- aqua-registry のチェックサム検証によりツールの完全性が保証されること
- 最小権限の原則に従い、`permissions: {}` をトップレベルに設定すること

### Maintainability
- 全ツールバージョンが Renovate で自動更新可能であること
- バージョン定義が YAML 内の一箇所に集約されていること

### Backward Compatibility
- `aqua-version` input の削除はメジャーバージョンアップ（v1 → v2）として扱うこと
- 既存の caller は input を削除するだけで移行可能であること
