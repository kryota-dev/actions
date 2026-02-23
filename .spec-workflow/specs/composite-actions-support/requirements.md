# Requirements Document

## Introduction

本ドキュメントは、`kryota-dev/actions` リポジトリを Reusable Workflows に加えて **Composite Actions** も管理するリポジトリへ拡張するための要件を定義する。

**As-Is（現状）:**
- `kryota-dev/actions` は Reusable Workflows の管理リポジトリとして運用中
- `.github/workflows/` 配下に Reusable Workflows および内部 CI ワークフローを格納
- ls-lint により `.github/workflows/` 配下のファイルを snake_case に強制

**To-Be（目標）:**
- Reusable Workflows に加え、Composite Actions も同リポジトリで管理・公開
- 各 Composite Action は `.github/composite/{action-name}/action.yml` の構造で格納
- actionlint が Composite Actions 形式（`action.yml`）に未対応であるため、`.github/composite/` に分離することで actionlint の誤検知を回避する
- ghalint（`run-action` コマンド）と zizmor により Composite Actions のセキュリティ検証を実施
- ls-lint を `.github/composite/` ディレクトリに対応させる
- README に Composite Actions の利用方法と一覧を追記

**スコープの明確化:**
- 対象: Composite Actions サポートのためのリポジトリ構造・CI・ドキュメントの拡張
- 対象外: 個々の Composite Action の具体的な実装内容（本拡張は基盤整備のみ）

## Alignment with Product Vision

本リポジトリの目的は「再利用可能な GitHub Actions を一元管理・公開し、各リポジトリの CI/CD 設定の重複を排除する」ことである。Composite Actions は Reusable Workflows の補完的な存在であり、以下の価値を提供する:

- **単一ジョブ内で使用可能**: Reusable Workflows はジョブ単位でしか呼び出せないが、Composite Actions はステップ単位で呼び出せるため、より細粒度な再利用が可能
- **同一 SHA ピン留め**: 呼び出し元が指定した SHA により、Composite Action 内部のステップも同一バージョンに固定される

本拡張により、管理リポジトリとしての価値がさらに高まる。

---

## Requirements

### Requirement 1: Composite Actions のディレクトリ構造

**User Story:** As a リポジトリ管理者, I want Composite Actions を `.github/composite/` ディレクトリ配下に格納したい, so that 他リポジトリから `kryota-dev/actions/.github/composite/{action-name}@vX` の形式で参照でき、かつ actionlint の誤検知を回避できる

#### Acceptance Criteria

1. WHEN 新しい Composite Action を追加するとき THEN リポジトリ SHALL `.github/composite/{action-name}/action.yml` のディレクトリ構造で格納する
2. WHEN `.github/composite/{action-name}/action.yml` が存在する THEN その action.yml SHALL `using: "composite"` を `runs.using` フィールドに含む
3. WHEN 外部リポジトリから Composite Action を参照するとき THEN 参照形式は `kryota-dev/actions/.github/composite/{action-name}@{tag-or-sha}` とする
4. WHEN `.github/composite/` 配下にサブディレクトリを作成するとき THEN ディレクトリ名は kebab-case とする（例: `.github/composite/setup-node/`）
5. IF `action.yml` 内に `run` ステップが存在する THEN そのステップには `shell` フィールドを必ず明記する

---

### Requirement 2: ls-lint への Composite Actions ディレクトリの追加

**User Story:** As a リポジトリ管理者, I want Composite Actions のディレクトリ・ファイル命名規則を ls-lint で自動検証したい, so that 命名の一貫性を CI で強制できる

#### Acceptance Criteria

1. WHEN `.ls-lint.yml` を更新するとき THEN `.github/composite/` ディレクトリ配下の命名規則を追加する
2. WHEN `.github/composite/` 配下のサブディレクトリ名が kebab-case でない THEN CI SHALL ls-lint エラーを報告してチェックを失敗させる
3. WHEN `.github/composite/` 配下の `action.yml` ファイルが存在する THEN ls-lint SHALL そのファイルへの命名チェックを正常に通過させる
4. WHEN PR が作成・更新されたとき THEN CI SHALL 更新後の ls-lint 設定で `.github/composite/` ディレクトリを含む全対象ディレクトリを検証する

---

### Requirement 3: actionlint の検証対象から Composite Actions を除外する

**User Story:** As a リポジトリ管理者, I want actionlint が Composite Actions の `action.yml` を誤検知しないようにしたい, so that CI が不必要なエラーで失敗しないようにできる

**背景:**
actionlint は Composite Actions 形式（`action.yml`）に未対応であり、`action.yml` を読み込むとエラーを報告する。`.github/composite/` ディレクトリに Composite Actions を分離配置することで、actionlint の検証対象（`.github/workflows/` 配下）から自然に除外できる。

#### Acceptance Criteria

1. WHEN actionlint が実行されるとき THEN actionlint SHALL `.github/workflows/` 配下の Workflow ファイルのみを検証対象とする
2. WHEN `.github/composite/` 配下の `action.yml` が存在するとき THEN actionlint SHALL それらのファイルを検証対象に含めない（誤検知を防ぐ）
3. WHEN PR が作成・更新されたとき THEN CI SHALL actionlint が `.github/composite/` 配下のファイルによってエラーを報告しないことを確認する

---

### Requirement 4: ghalint による Composite Actions のセキュリティポリシー準拠チェック

**User Story:** As a リポジトリ管理者, I want Composite Actions 内の `uses:` 指定を ghalint で検証したい, so that SHA ピン留めや credential 漏洩の違反を自動検出できる

**背景:**
ghalint の `run-action` コマンドは `^([^/]+/){0,3}action\.ya?ml$` パターンに一致するファイルを検証する。`.github/composite/{action-name}/action.yml` は3階層以内に収まるため検証対象となる。

#### Acceptance Criteria

1. WHEN PR が作成・更新されたとき THEN CI SHALL `ghalint run-action` を実行して `.github/composite/` 配下の `action.yml` を検証対象に含める
2. WHEN Composite Action 内の `uses:` がミュータブルタグ（例: `@v4`）で指定されているとき THEN ghalint SHALL エラーを報告する
3. WHEN Composite Action 内に credential 漏洩パターンが検出されたとき THEN ghalint SHALL エラーを報告する
4. WHEN `my_test.yml` を更新するとき THEN `ghalint run`（Workflow 検証）に加えて `ghalint run-action` ステップを追加する

---

### Requirement 5: zizmor による Composite Actions の静的セキュリティ分析

**User Story:** As a リポジトリ管理者, I want Composite Actions の `action.yml` を zizmor で静的セキュリティ分析したい, so that テンプレートインジェクションやサプライチェーンリスクを検出できる

**背景:**
zizmor は v1.0.0 からディレクトリをスキャンする際に `action.yml` を自動発見し、Composite Actions も検証対象に含める。現在の `uvx zizmor --format=github .` コマンドはリポジトリルートを指定しており、`.github/composite/` 配下の `action.yml` も自動的にスキャン対象となる。

#### Acceptance Criteria

1. WHEN PR が作成・更新されたとき THEN CI SHALL zizmor を実行して `.github/composite/` 配下の `action.yml` も検証対象に自動的に含める（追加設定不要）
2. WHEN テンプレートインジェクション脆弱性（例: `${{ inputs.xxx }}` の直接 `run` への埋め込み）が検出されたとき THEN zizmor SHALL エラーを報告する
3. WHEN サプライチェーンリスクのある Action 参照が検出されたとき THEN zizmor SHALL 警告を報告する
4. IF zizmor が `.github/composite/` 配下の `action.yml` をスキャン対象外とする場合 THEN CI の zizmor 実行コマンドにパスを明示的に追加する

---

### Requirement 6: Composite Actions の uses: full commit SHA ピン留め

**User Story:** As a リポジトリ管理者, I want Composite Actions 内の `uses:` も full commit SHA でピン留めしたい, so that サプライチェーン攻撃リスクを低減できる

#### Acceptance Criteria

1. WHEN `action.yml` 内に `uses:` ステップが存在する THEN その指定は full commit SHA（40文字）でピン留めする
2. WHEN Renovate Bot が設定済みのとき THEN Renovate SHALL `.github/composite/` 配下の `action.yml` 内の `uses:` も自動更新対象に含める
3. IF SHA ピン留めされていない `uses:` が `action.yml` 内に存在する THEN ghalint または zizmor SHALL CI でエラーを報告する

---

### Requirement 7: タグベースのリリース管理との整合

**User Story:** As a Composite Action の利用者, I want 既存の tagpr ベースのバージョニング（`v1`, `v1.0.0` 等）で Composite Actions を参照したい, so that Reusable Workflows と同じバージョン管理規則で一貫して利用できる

#### Acceptance Criteria

1. WHEN tagpr が新しいリリースタグ（例: `v1.2.0`）を作成するとき THEN そのタグは Composite Actions にも適用される
2. WHEN メジャーバージョンタグ（例: `v1`）が更新されるとき THEN Composite Actions への参照も自動的に最新バージョンに追従する
3. WHEN 外部リポジトリが `kryota-dev/actions/.github/composite/{action-name}@v1` の形式で参照するとき THEN 最新のメジャーバージョンに対応した Composite Action が提供される
4. WHEN 既存の tagpr・リリース設定（`.tagpr`, `my_release.yml`, `.github/release.yml`）が存在する THEN それらの設定変更は不要とする（既存設定でリポジトリ全体のリリースが管理される）

---

### Requirement 8: README の更新

**User Story:** As a Composite Action の利用者, I want README から利用可能な Composite Actions と使い方をすぐに把握したい, so that 目的の Action を迷わず使い始めることができる

#### Acceptance Criteria

1. WHEN `README.md` を更新するとき THEN 「Available Workflows」セクションに「Composite Actions」サブセクションを追加する
2. WHEN Composite Action のサブセクションが存在する THEN 外部リポジトリからの参照方法のサンプルを以下の形式で含める:
   ```yaml
   steps:
     - uses: kryota-dev/actions/.github/composite/{action-name}@vX
       with:
         # inputs
   ```
3. WHEN 現時点で公開済みの Composite Action が存在しない THEN 「Coming soon.」または空の一覧プレースホルダーを記載する（将来の Action 追加時に更新する）
4. WHEN `README.md` に Reusable Workflows の参照方法（`uses:` + `jobs:` 構文）が記載されている THEN Composite Actions の参照方法（`uses:` + `steps:` 構文）との違いも明記する

---

## Non-Functional Requirements

### Code Architecture and Modularity

- **Single Responsibility Principle**: 各 Composite Action は単一の目的に特化し、複数の責務を持たせない
- **Modular Design**: `.github/composite/` ディレクトリ配下に Action ごとのサブディレクトリを設け、Reusable Workflows（`.github/workflows/`）と明確に分離する
- **Dependency Management**: Composite Action 内の `uses:` は Renovate Bot により自動更新管理する
- **Clear Interfaces**: `action.yml` には `inputs`・`outputs`・`description` を明示的に定義し、利用者への明確なインターフェースを提供する

### Performance

- Composite Actions は Reusable Workflows と異なり呼び出し元ジョブ内で実行されるため、ジョブ起動オーバーヘッドが発生しない
- CI の lint ジョブ（`my_test.yml`）は既存の単一ジョブ構成を維持し、不要なジョブ分割を避ける

### Security

- Composite Action 内の全 `uses:` は **full commit SHA（40文字）でピン留め**する
- ghalint（`run-action` コマンド）と zizmor により Composite Actions のセキュリティポリシー違反を CI で自動検出する
- Composite Action への入力値（`inputs`）は `run` ステップへの直接埋め込みを避け、環境変数経由で渡すことでテンプレートインジェクションリスクを排除する
- `action.yml` にシークレットをハードコードしない

### Reliability

- `my_test.yml` の CI パイプラインに `ghalint run-action` ステップを追加し、Composite Actions も品質ゲートの対象に含める
- actionlint の誤検知を防ぐため、Composite Actions は `.github/composite/` に配置し、`.github/workflows/` と分離する
- 既存の Reusable Workflows への影響を与えないこと（後方互換性の維持）

### Usability

- Composite Actions のディレクトリ名は kebab-case で命名し、Action の目的が名前から直感的に分かるようにする
- `action.yml` には `name` と `description` を必ず記載し、GitHub UI での視認性を確保する

---

## Out of Scope

以下は今回のスコープ外とする:

- 個々の Composite Action（例: `.github/composite/setup-node/action.yml` 等）の具体的な実装内容（本拡張は基盤整備のみ）
- Reusable Workflows の新規追加・変更
- 既存の内部 CI ワークフロー（`my_test.yml`, `my_release.yml` 等）の動作変更（`ghalint run-action` ステップの追加を除く）
- GitHub リポジトリの Web UI 設定の変更（Branch Protection Rules 等）
- Docker Action や JavaScript Action のサポート（Composite Actions のみ対象）
