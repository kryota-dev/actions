# Requirements Document

## Introduction

本ドキュメントは、GitHub Actions の Reusable Workflow を管理するリポジトリ（以下「本リポジトリ」）の基盤環境を構築するための要件を定義する。

参考リポジトリ: [route06/actions](https://github.com/route06/actions)

本リポジトリは、個人または組織が複数のリポジトリにまたがって利用する Reusable Workflow を一元管理・公開することを目的とする。現時点では基本ファイル（README.md, LICENSE, .gitignore, .envrc）のみが存在しており、CI/CD パイプライン、品質管理ツール、リリース管理、ドキュメント管理の基盤整備が必要な状態である。

**スコープの明確化:**
- 対象: リポジトリの基盤インフラ（CI/CD パイプライン、品質管理ツール、リリース管理、依存関係管理、ADR 管理、CODEOWNERS 設定）
- 対象外: 個々の Reusable Workflow の実装内容（今回は環境構築のみ）

## Alignment with Product Vision

本リポジトリは、再利用可能な GitHub Actions Workflow を一元管理・公開することで、各リポジトリの CI/CD 設定の重複を排除し、品質と保守性を高めることを目的とする。

本環境構築により以下を実現する:
- Workflow ファイルの品質を CI で自動検証できる状態にする
- セマンティックバージョニングに基づくリリース管理ができる状態にする
- 設計決定を ADR として記録・参照できる状態にする
- 依存する Actions と npm パッケージのバージョンを Renovate Bot で自動追跡できる状態にする

---

## Requirements

### Requirement 1: Workflow ファイルの命名規則 Lint（ls-lint）

**User Story:** As a リポジトリ管理者, I want Workflow ファイル名を snake_case に強制する Lint を導入したい, so that ファイル名の表記ゆれをなくし一貫性を維持できる

#### Acceptance Criteria

1. WHEN `.github/workflows/` 配下のファイルが追加・変更されたとき THEN CI SHALL ls-lint による命名規則チェックを実行する
2. WHEN ファイル名が snake_case に違反している THEN CI SHALL エラーを報告してチェックを失敗させる
3. WHEN `.ls-lint.yml` が存在する THEN システム SHALL `.github/workflows/` ディレクトリに対して `snake_case.yml` ルールを適用する

---

### Requirement 2: Workflow 構文・セキュリティチェック（actionlint / ghalint / zizmor）

**User Story:** As a リポジトリ管理者, I want Workflow の構文エラーとセキュリティ上の問題を自動検出したい, so that 文法ミスや脆弱な設定を早期に発見・修正できる

#### Acceptance Criteria

**actionlint（構文チェック）**

1. WHEN PR が作成・更新されたとき THEN CI SHALL actionlint を実行して全 Workflow ファイルを検証する
2. WHEN actionlint がエラーを検出したとき THEN CI SHALL reviewdog 経由で PR にインラインコメントを付与する
3. IF actionlint の実行に成功した THEN CI SHALL ゼロエラーであることを確認してステータスチェックを通過させる

**ghalint（セキュリティポリシー準拠チェック）**

4. WHEN PR が作成・更新されたとき THEN CI SHALL ghalint（suzuki-shunsuke/ghalint）を実行して全 Workflow ファイルのセキュリティポリシー準拠を検証する
5. WHEN Actions のバージョン指定がミュータブルタグ（例: `@v4`）のとき THEN ghalint SHALL エラーを報告する（full commit SHA ピン留めを強制）
6. WHEN Workflow の `permissions` 宣言が不足または過剰なとき THEN ghalint SHALL エラーを報告する
7. WHEN credential 漏洩パターンが検出されたとき THEN ghalint SHALL エラーを報告してチェックを失敗させる

**zizmor（静的セキュリティ分析）**

8. WHEN PR が作成・更新されたとき THEN CI SHALL zizmor（zizmorcore/zizmor）を実行して全 Workflow ファイルの静的セキュリティ分析を行う
9. WHEN テンプレートインジェクション脆弱性が検出されたとき THEN zizmor SHALL エラーを報告する
10. WHEN サプライチェーンリスクのある Action 参照が検出されたとき THEN zizmor SHALL 警告を報告する
11. WHEN permission 問題が検出されたとき THEN zizmor SHALL エラーを報告してチェックを失敗させる

---

### Requirement 3: 内部 CI ワークフロー群

**User Story:** As a リポジトリ管理者, I want リポジトリ自身の CI/CD を自動化したい, so that 品質チェックとリリースを人手を介さずに実行できる

#### Acceptance Criteria

1. WHEN PR が作成・更新されたとき THEN システム SHALL `my_test.yml`（actionlint + ls-lint + ghalint + zizmor）を実行する
2. WHEN PR が作成されたとき THEN システム SHALL `my_setup_pr.yml` により PR 作成者を自動的に assignee へ追加する
3. WHEN tagpr がリリース PR をマージしたとき THEN システム SHALL `my_release.yml` によりタグ付けとメジャータグの更新を行う
4. WHEN メインブランチでコードが変更されたとき THEN システム SHALL `my_codeql.yml` により CodeQL セキュリティスキャンを実行する
5. WHEN 内部 CI ワークフローを識別するとき THEN システム SHALL `my_` プレフィックスを持つファイル名で管理する

---

### Requirement 4: タグベースのリリース管理（tagpr）

**User Story:** As a リポジトリ管理者, I want tagpr を使ってセマンティックバージョニングに基づくリリースを自動化したい, so that 手動でのタグ付けや CHANGELOG 更新の手間を省ける

#### Acceptance Criteria

1. WHEN メインブランチにコミットがプッシュされたとき THEN tagpr SHALL 次のバージョン番号を計算してリリース PR を自動作成・更新する
2. WHEN リリース PR がマージされたとき THEN システム SHALL `vX.Y.Z` 形式のタグを自動付与する
3. WHEN 新しいリリースタグが作成されたとき THEN システム SHALL メジャーバージョンタグ（例: `v1`）を最新リリースに自動更新する
4. WHEN `.tagpr` 設定ファイルが存在する THEN システム SHALL `vPrefix=true`、`releaseBranch=main`、`versionFile=-` の設定で動作する
5. IF リリースに通常の `GITHUB_TOKEN` では権限が不足する場合 THEN システム SHALL PAT（Personal Access Token）を `APP_TOKEN` シークレットとして使用する

---

### Requirement 5: リリースノートのカテゴリ設定

**User Story:** As a リポジトリ管理者, I want GitHub の自動リリースノートをカテゴリ別に整理したい, so that 変更内容を分かりやすく利用者へ伝えられる

#### Acceptance Criteria

1. WHEN リリースが作成されるとき THEN `.github/release.yml` SHALL 以下のカテゴリでリリースノートを自動生成する: `Breaking Changes` / `New Features` / `Fix bug` / `Maintenance` / `Other Changes`
2. WHEN PR に付与されたラベルに基づき THEN システム SHALL 対応するカテゴリに PR を分類する

---

### Requirement 6: 依存関係管理（Renovate Bot + Dependabot Alerts）

**User Story:** As a リポジトリ管理者, I want 依存する Actions と npm パッケージのバージョンを自動追跡し、脆弱性を早期に検知したい, so that セキュリティパッチや機能改善を見逃さずに適用できる

#### Acceptance Criteria

**Renovate Bot（バージョン更新 PR の自動作成）**

1. WHEN Renovate Bot が設定済みのとき THEN Renovate SHALL `github-actions` の依存関係を更新する PR を自動作成する
2. WHEN Renovate Bot が設定済みのとき THEN Renovate SHALL `npm` の依存関係を更新する PR を自動作成する
3. WHEN Dependabot Alerts がセキュリティ脆弱性を検知したとき THEN Renovate SHALL `[SECURITY]` プレフィックスを付与したタイトルで優先度の高いセキュリティ更新 PR を作成する
4. WHEN `renovate.json5` が存在する THEN Renovate SHALL スケジュール、パッチグルーピング等の設定に従って動作する

**Dependabot Alerts（脆弱性検出通知のみ）**

5. WHEN Dependabot Alerts が有効のとき THEN Dependabot SHALL 依存関係の既知の脆弱性（CVE）をリポジトリの Security タブに通知する
6. WHEN Dependabot Alerts が有効のとき THEN Dependabot SHALL Version Updates（PR 自動作成）および Security Updates（PR 自動作成）を無効にする（Renovate で管理するため二重 PR を避ける）

**Note:** Dependabot Alerts はリポジトリの Security 設定で有効化するのみで、`.github/dependabot.yml` による Version Updates / Security Updates の PR 作成は設定しない。

---

### Requirement 7: ADR（Architecture Decision Records）の管理

**User Story:** As a リポジトリ管理者, I want 設計上の意思決定を ADR として記録・管理したい, so that 将来の自分や貢献者が決定の経緯を理解できる

#### Acceptance Criteria

1. WHEN `.adr.json` が存在する THEN システム SHALL `docs/adr/` ディレクトリに ADR を保存し、英語・3桁のゼロ埋めプレフィックスの命名規則を適用する
2. WHEN 新しい ADR を作成するとき THEN `npm run adr:new` コマンド SHALL ADR スケルトンファイルを生成する
3. WHEN `package.json` が存在する THEN システム SHALL `adr` を devDependency として管理する

---

### Requirement 8: CODEOWNERS の設定

**User Story:** As a リポジトリ管理者, I want リポジトリのコードオーナーを設定したい, so that PR レビューの担当者が自動的にアサインされる

#### Acceptance Criteria

1. WHEN `.github/CODEOWNERS` が存在する THEN システム SHALL `@kryota-dev` をデフォルトのコードオーナーとして設定する
2. WHEN PR が作成されたとき THEN GitHub SHALL CODEOWNERS 設定に基づいてレビュアーを自動アサインする

---

### Requirement 9: README とドキュメント構造

**User Story:** As a Reusable Workflow の利用者, I want リポジトリの README から利用可能なワークフローと使い方をすぐに把握したい, so that 目的のワークフローを迷わず使い始めることができる

#### Acceptance Criteria

1. WHEN `README.md` が存在する THEN ドキュメント SHALL リポジトリの目的・概要を冒頭に記載する
2. WHEN `README.md` にワークフロー一覧セクションが存在する THEN ドキュメント SHALL 利用可能な各 Reusable Workflow の名前・用途・参照方法を記載する（現時点では空のプレースホルダーでよい）
3. WHEN `docs/` ディレクトリが存在する THEN システム SHALL ADR および設計ドキュメントを `docs/adr/` 配下に格納する

---

## Non-Functional Requirements

### Code Architecture and Modularity

- **Single Responsibility Principle**: 各 Workflow ファイルは単一の目的に特化する（例: テスト、リリース、セキュリティスキャンを分離）
- **Modular Design**: Reusable Workflow と内部 CI Workflow を明確に分離し、`my_` プレフィックスで識別可能にする
- **Dependency Management**: Renovate Bot による依存関係の定期的な自動更新で最新状態を維持し、Dependabot Alerts で脆弱性通知を受け取る
- **Clear Interfaces**: Reusable Workflow は `workflow_call` トリガーと明示的な `inputs`/`secrets` 定義で外部インターフェースを明確化する（個別 Workflow 実装時に適用）

### Performance

- CI の各ジョブは独立して実行可能とし、並列化による高速化を考慮する
- actionlint と ls-lint は同一 Workflow 内のステップとして実行し、不要なジョブ分割を避ける

### Security

- シークレット（`APP_TOKEN` 等）はリポジトリのシークレット設定で管理し、Workflow ファイルにハードコードしない
- CodeQL による静的解析を継続的に実行し、セキュリティ脆弱性を早期発見する
- Renovate Bot によりセキュリティパッチを含む依存関係の更新を自動追跡し、Dependabot Alerts で脆弱性を通知する
- Actions のバージョンは **full commit SHA ピン留め**（例: `actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683`）を基本とし、ghalint および zizmor によりミュータブルタグ参照を CI で強制検出する（2025年の tj-actions/changed-files サプライチェーン攻撃等を教訓とした対策）
- ghalint によるセキュリティポリシー準拠チェック（SHA ピン留め強制・permission 検証・credential 漏洩検出）と zizmor による静的セキュリティ分析（テンプレートインジェクション・サプライチェーンリスク）を多層的に実施する

### Reliability

- 内部 CI（`my_test.yml`）は PR の品質ゲートとして機能し、テスト失敗時はマージをブロックする
- tagpr によるリリース管理で、手動操作ミスによるリリース失敗を防止する

### Usability

- `my_` プレフィックスにより、内部 CI と公開 Reusable Workflow を直感的に区別できる
- 全ての設定ファイル（`.tagpr`, `.adr.json`, `.ls-lint.yml` 等）はリポジトリルートに配置し、設定の所在を明確にする
- README にリポジトリの目的・使用方法・利用可能な Reusable Workflow の一覧を記載する

---

## Out of Scope

以下は今回の環境構築スコープ外とする:

- 個々の Reusable Workflow（`add_assignee_to_pr.yml`, `codeql.yml` 等）の実装
- GitHub リポジトリの Web UI 設定（Branch Protection Rules、Required Status Checks 等）
- README の詳細なドキュメント整備（Reusable Workflow が揃ってから実施）
