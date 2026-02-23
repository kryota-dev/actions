# Requirements Document

## Introduction

本ドキュメントは、`kryota-dev/actions` リポジトリの4つの内部 CI ワークフロー（`my-codeql.yml`、`my-release.yml`、`my-setup-pr.yml`、`my-test.yml`）を、外部リポジトリから呼び出し可能な Reusable Workflows として公開するための要件を定義する。

### 背景

現在、これらのワークフローは `kryota-dev/actions` リポジトリの内部 CI としてのみ機能している。しかし、CodeQL スキャン、tagpr リリース管理、PR assignee 自動設定、品質ゲート（actionlint / ls-lint / ghalint / zizmor）といった処理は、他のリポジトリでも共通的に必要とされるパターンである。

これらを Reusable Workflows として公開することで、各リポジトリの CI/CD 設定の重複を排除し、メンテナンスコストを削減する。

### スコープ

- **対象**: 4つの内部 CI ワークフローに対応する Reusable Workflow の新規作成
- **対象外**: 既存の内部 CI ワークフロー（`my-*`）のリファクタリング（Reusable Workflow 呼び出しへの変換は別途検討）

## Alignment with Product Vision

本リポジトリは「再利用可能な GitHub Actions を一元管理・公開する」ことを目的としている。現在 Composite Actions は4つ公開されているが、Reusable Workflows は "Coming soon." の状態であり、本対応によりリポジトリの主要目的の一つを実現する。

---

## Requirements

### Requirement 1: CodeQL Reusable Workflow の公開

**User Story:** As a 外部リポジトリの管理者, I want CodeQL セキュリティスキャンを Reusable Workflow として呼び出したい, so that 各リポジトリで CodeQL の設定を繰り返す必要がなくなる

#### Acceptance Criteria

1. WHEN 外部リポジトリが `workflow_call` で呼び出したとき THEN Reusable Workflow SHALL CodeQL の init と analyze を実行する
2. WHEN `languages` 入力が指定されたとき THEN Reusable Workflow SHALL 指定された言語でスキャンを実行する
3. IF `languages` 入力が省略されたとき THEN Reusable Workflow SHALL デフォルト値 `actions` でスキャンを実行する
4. WHEN スキャンが実行されたとき THEN Reusable Workflow SHALL `security-events: write` パーミッションで結果を SARIF として GitHub にアップロードする

---

### Requirement 2: Release Reusable Workflow の公開

**User Story:** As a 外部リポジトリの管理者, I want tagpr によるリリース管理を Reusable Workflow として呼び出したい, so that セマンティックバージョニングとメジャータグ更新を各リポジトリで再実装する必要がなくなる

#### Acceptance Criteria

1. WHEN 外部リポジトリが `workflow_call` で呼び出したとき THEN Reusable Workflow SHALL tagpr によるリリース PR の自動作成・管理を実行する
2. WHEN tagpr が新しいタグを生成したとき THEN Reusable Workflow SHALL メジャータグ（例: `v1`）を最新リリースに自動更新する
3. WHEN Reusable Workflow が呼び出されるとき THEN 呼び出し元 SHALL `app-token` シークレットを渡す必要がある
4. WHEN tagpr と bump_major_tag ジョブが実行されるとき THEN Reusable Workflow SHALL concurrency 制御によりリリースの競合を防止する

---

### Requirement 3: Setup PR Reusable Workflow の公開

**User Story:** As a 外部リポジトリの管理者, I want PR 作成時の assignee 自動設定を Reusable Workflow として呼び出したい, so that 各リポジトリで同じ自動化スクリプトを書く必要がなくなる

#### Acceptance Criteria

1. WHEN 外部リポジトリが `workflow_call` で呼び出したとき THEN Reusable Workflow SHALL PR 作成者を自動的に assignee に設定する
2. WHEN Reusable Workflow が呼び出されるとき THEN 呼び出し元 SHALL PR の URL と actor 情報を入力として渡す
3. WHEN assignee の設定が完了したとき THEN Reusable Workflow SHALL `pull-requests: write` パーミッションのみで動作する

---

### Requirement 4: Test (品質ゲート) Reusable Workflow の公開

**User Story:** As a 外部リポジトリの管理者, I want GitHub Actions ワークフローの品質ゲート（actionlint / ls-lint / ghalint / zizmor）を Reusable Workflow として呼び出したい, so that 品質チェックツールのセットアップを各リポジトリで繰り返す必要がなくなる

#### Acceptance Criteria

1. WHEN 外部リポジトリが `workflow_call` で呼び出したとき THEN Reusable Workflow SHALL actionlint、ls-lint、ghalint、zizmor を実行する
2. WHEN actionlint がエラーを検出したとき THEN Reusable Workflow SHALL reviewdog 経由で PR にインラインコメントを付与する
3. WHEN ghalint がセキュリティポリシー違反を検出したとき THEN Reusable Workflow SHALL エラーを報告してチェックを失敗させる
4. WHEN zizmor が脆弱性を検出したとき THEN Reusable Workflow SHALL エラーを報告してチェックを失敗させる
5. WHEN `aqua-version` 入力が指定されたとき THEN Reusable Workflow SHALL 指定されたバージョンの aqua を使用する
6. IF `aqua-version` 入力が省略されたとき THEN Reusable Workflow SHALL デフォルトの aqua バージョンを使用する

---

### Requirement 5: Reusable Workflow の命名規則と配置

**User Story:** As a リポジトリ管理者, I want Reusable Workflow が既存の命名規則・配置ルールに従っていること, so that プロジェクトの一貫性が維持される

#### Acceptance Criteria

1. WHEN Reusable Workflow が作成されるとき THEN ファイル名 SHALL kebab-case で命名される（`my-` プレフィックスなし）
2. WHEN Reusable Workflow が配置されるとき THEN ファイル SHALL `.github/workflows/` ディレクトリに格納される
3. WHEN Reusable Workflow の `uses:` ディレクティブが記述されるとき THEN 全ての Action 参照 SHALL full commit SHA（40文字）でピン留めされ、タグをコメントで記載する
4. WHEN Reusable Workflow が作成されるとき THEN 各ジョブ SHALL `timeout-minutes` を設定する
5. WHEN Reusable Workflow が作成されるとき THEN トップレベル SHALL `permissions: {}` を設定し、各ジョブで最小権限のみ付与する

---

### Requirement 6: ドキュメントの更新

**User Story:** As a Reusable Workflow の利用者, I want README から利用可能な Reusable Workflow とその使い方を確認したい, so that 各ワークフローを迷わず使い始めることができる

#### Acceptance Criteria

1. WHEN Reusable Workflow が公開されたとき THEN README SHALL 各 Reusable Workflow の名前・用途・入力パラメータ・使用例を記載する
2. WHEN README の Reusable Workflows セクションが更新されるとき THEN "Coming soon." の記載 SHALL 実際のワークフロー一覧に置き換えられる

---

## Non-Functional Requirements

### Code Architecture and Modularity

- **Single Responsibility Principle**: 各 Reusable Workflow は単一の CI/CD 目的に特化する
- **Modular Design**: 内部 CI（`my-*`）と公開 Reusable Workflow は別ファイルとして分離する
- **Clear Interfaces**: `workflow_call` の `inputs` / `secrets` を明示的に定義し、必須・任意・デフォルト値を明確にする
- **Dependency Management**: Reusable Workflow 内の Action 参照も Renovate Bot による自動更新の対象とする

### Performance

- Reusable Workflow は呼び出し元のジョブとは別ジョブとして実行されるため、必要最小限のステップ構成とする
- `timeout-minutes` を全ジョブに設定し、異常実行の長時間化を防止する

### Security

- 全ての `uses:` は full commit SHA（40文字）でピン留めする
- `permissions: {}` をトップレベルに設定し、各ジョブで最小権限のみ付与する
- シークレットは `secrets:` キーワードで明示的に渡す（`secrets: inherit` は使用しない方針を推奨）
- テンプレートインジェクション対策として、`inputs` の値は `env:` 経由で環境変数として渡す

### Reliability

- Reusable Workflow は `kryota-dev/actions` リポジトリのバージョンタグ（例: `@v1`）で参照され、メジャータグは最新リリースに追従する
- concurrency 制御により、同一リファレンスに対する並列実行の競合を防止する

### Usability

- 全ての `inputs` と `secrets` に `description` を記載し、利用者が GitHub UI からパラメータの意味を把握できるようにする
- デフォルト値を適切に設定し、最小構成での呼び出しを可能にする

---

## Out of Scope

以下は本スコープ外とする:

- 既存の内部 CI ワークフロー（`my-*`）を Reusable Workflow 呼び出しにリファクタリングすること
- Reusable Workflow 以外の新機能追加
- 外部リポジトリでの E2E テスト
