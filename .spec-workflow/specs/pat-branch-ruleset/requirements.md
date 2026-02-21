# Requirements Document

## Introduction

本ドキュメントは、`kryota-dev/actions` リポジトリにおけるブランチ・タグのルールセット設計について要件を定義する。

### 背景

PR #13（GITHUB_TOKEN 化）は PR #16 で revert された。これにより、リリースワークフロー（`my_release.yml`）は PAT（`APP_TOKEN`）使用に回帰した。

前回の設計（spec: branch-ruleset）は `github-actions[bot]`（GITHUB_TOKEN）前提だったため、個人リポジトリにおけるバイパスアクター制約により PR 必須化・ステータスチェック必須化が実現できず、削除/force push 防止のみの弱い保護に留まっていた。

**今回の前提（PAT 使用）における制約の解消:**

- PAT はリポジトリオーナーとして認証される
- 個人リポジトリでは、管理者（=オーナー）は GitHub の仕様により常にルールセットをバイパスできる
- tagpr（リリース PR 作成）・bump_major_tag（メジャータグ force push）はいずれも PAT で動作するため、ルールセット制限を受けない
- したがって、PR 必須化・ステータスチェック必須化・non_fast_forward 制限などの強力な保護が設定可能となった

### スコープの明確化

- **対象**: ブランチ・タグルールセットの JSON ファイル（IaC）、ADR 作成
- **対象外**: ルールセットの GitHub Web UI への適用手順（手動作業）、既存ワークフローの変更、Renovate Bot 設定の変更

## Alignment with Product Vision

本リポジトリは、Reusable GitHub Actions Workflow を一元管理・公開することで複数リポジトリの CI/CD 設定の重複を排除することを目的とする。

ブランチ・タグ保護により以下を実現する:

- 誤操作による main ブランチへの直接 push・削除を防止する
- PR を介したコードレビュープロセスを強制する
- CI ステータスチェックのパスを必須化し、品質ゲートを機能させる
- リリース済みバージョンタグの改ざんを防止し、外部利用者への信頼性を維持する

---

## Requirements

### Requirement 1: main ブランチの保護

**User Story:** As a リポジトリ管理者, I want main ブランチへの直接 push と誤削除を防ぎ、PR を必須化したい, so that コードレビューを経た変更のみが main に取り込まれることを保証できる

#### Acceptance Criteria

1. WHEN main ブランチに対して削除操作が実行されたとき THEN ルールセット SHALL `deletion` ルールにより削除をブロックする
2. WHEN main ブランチに対して non-fast-forward push（履歴書き換えを伴う push）が実行されたとき THEN ルールセット SHALL `non_fast_forward` ルールにより拒否する
3. WHEN main ブランチに対して push が実行されたとき THEN ルールセット SHALL `required_linear_history` ルールによりマージコミットを禁止し、squash または rebase マージのみを許可する
4. WHEN main ブランチへの変更が提案されたとき THEN ルールセット SHALL `pull_request` ルールにより PR の作成を必須とする（直接 push を禁止する）
5. WHEN pull_request ルールが有効のとき THEN システム SHALL 承認件数を `required_approving_review_count: 0` に設定する（GitHub の仕様上 PR 作成者は自分自身の PR を承認できないため、個人リポジトリでは 1 以上に設定するとマージブロックになる。PR 作成の必須化のみを目的とし、承認件数は 0 とする）
6. WHEN ステータスチェックが設定されているとき THEN ルールセット SHALL `required_status_checks` ルールにより指定チェックのパスを必須とする
7. WHEN `required_status_checks` が有効のとき THEN システム SHALL 以下のステータスチェックをブロッキング対象とする:
   - `lint`（`my_test.yml` の lint ジョブ）
   - `analyze (actions)`（`my_codeql.yml` の analyze ジョブ、matrix 使用により `analyze (actions)` がチェック名となる）
8. WHEN PAT（`APP_TOKEN`）でリポジトリオーナーが操作するとき THEN ルールセット SHALL 管理者バイパス（GitHub 個人リポジトリのオーナーはルールセットを常にバイパス可能）により、tagpr・bump_major_tag の操作を妨げない
9. IF Renovate Bot が依存関係更新 PR を作成したとき THEN ルールセット SHALL `required_status_checks` の対象となり、CI が通過したものだけがマージ可能であることを保証する

**備考（管理者バイパスの仕組み）:** GitHub の個人リポジトリでは、オーナーが管理者権限を持つため、ルールセットの bypass_actors 設定に明示的なアクターを追加しなくとも、オーナーによる操作（PAT 使用を含む）はルールセットの制限をバイパスする。これにより tagpr（リリース PR 作成・main への直接操作）および bump_major_tag（メジャータグ force push）は制限されない。

---

### Requirement 2: バージョンタグ（`v*.*.*`）の保護

**User Story:** As a リリース管理者, I want 公開済みのバージョンタグ（vX.Y.Z 形式）の削除と変更を防ぎたい, so that 外部リポジトリが特定バージョンをピン留めして使用する際の信頼性を確保できる

#### Acceptance Criteria

1. WHEN `refs/tags/v*.*.*` パターンに合致するタグに対して削除操作が実行されたとき THEN ルールセット SHALL `deletion` ルールによりブロックする
2. WHEN `refs/tags/v*.*.*` パターンに合致するタグに対して force push が実行されたとき THEN ルールセット SHALL `non_fast_forward` ルールによりブロックする
3. IF tagpr がリリース PR マージ後に `vX.Y.Z` タグを付与するとき THEN ルールセット SHALL PAT（オーナー）バイパスにより tagpr の操作を妨げない
4. WHEN ルールセットの条件を設定するとき THEN システム SHALL `refs/tags/v*.*.*` の `*` が `.`（ドット）を含む任意の文字列にマッチする fnmatch 仕様を考慮した上で、`v1.2.3` 形式のタグに正しく適用されることを確認する

---

### Requirement 3: メジャータグ（`v[0-9]*`）の保護

**User Story:** As a リポジトリ管理者, I want メジャータグ（v1, v2 等）の誤削除を防ぎつつ、bump_major_tag による force push での更新を許可したい, so that 外部利用者は常に最新リリースをメジャータグで参照できる

#### Acceptance Criteria

1. WHEN `refs/tags/v[0-9]*` パターンに合致するタグに対して削除操作が実行されたとき THEN ルールセット SHALL `deletion` ルールによりブロックする
2. WHEN `refs/tags/v[0-9]*` パターンに合致するタグに対して force push が実行されたとき THEN ルールセット SHALL `non_fast_forward` ルールを**適用しない**（bump_major_tag による `--force` での更新を許容する）
3. WHEN bump_major_tag ジョブが PAT で `git push origin "$MAJOR" --force` を実行するとき THEN ルールセット SHALL PAT（オーナー）バイパスにより操作を妨げない
4. WHEN ルールセットの条件を設定するとき THEN システム SHALL `refs/tags/v[0-9]*` パターンが `v10`、`v11` 等の 2 桁以上のメジャーバージョンにも正しくマッチすることを確認する

---

### Requirement 4: ルールセットの JSON 管理（IaC）

**User Story:** As a リポジトリ管理者, I want ルールセット設定を JSON ファイルとしてバージョン管理したい, so that 設定変更の履歴を Git で追跡し、レビュープロセスを経て安全に適用できる

#### Acceptance Criteria

1. WHEN ルールセット設定ファイルを配置するとき THEN システム SHALL `.github/rulesets/` ディレクトリに JSON 形式で格納する
2. WHEN main ブランチ保護ルールセットを定義するとき THEN システム SHALL `.github/rulesets/protect-main.json` として管理する
3. WHEN バージョンタグ保護ルールセットを定義するとき THEN システム SHALL `.github/rulesets/protect-version-tags.json` として管理する
4. WHEN メジャータグ保護ルールセットを定義するとき THEN システム SHALL `.github/rulesets/protect-major-tags.json` として管理する
5. WHEN 各 JSON ファイルを作成するとき THEN システム SHALL GitHub API の Ruleset スキーマ（`name`, `target`, `enforcement`, `conditions`, `rules`, `bypass_actors`）に準拠した形式で定義する
6. WHEN ルールセットを GitHub に適用するとき THEN 作業者 SHALL GitHub Web UI または GitHub CLI を用いて JSON をインポートする（手動手順）

---

### Requirement 5: ADR の作成

**User Story:** As a リポジトリ管理者, I want PAT 前提のブランチルールセット設計の意思決定を ADR として記録したい, so that 将来の自分や貢献者が設計経緯（特に GITHUB_TOKEN からの回帰理由）を理解できる

#### Acceptance Criteria

1. WHEN ADR を作成するとき THEN システム SHALL `docs/adr/003-pat-branch-ruleset.md` として英語で記録する
2. WHEN ADR 003 を作成するとき THEN ドキュメント SHALL 以下の内容を含む:
   - PR #13（GITHUB_TOKEN 化）が revert（PR #16）された背景と理由
   - PAT（`APP_TOKEN`）前提での設計再考の決定
   - 個人リポジトリにおける管理者バイパスの仕組みとその活用
   - PR 必須化・ステータスチェック必須化が実現可能になった理由
3. WHEN ADR 003 を作成するとき THEN ドキュメント SHALL 既存 ADR（001）のフォーマット（Date / Status / Context / Decision / Consequences）に準拠する
4. WHEN `docs/adr/README.md` を更新するとき THEN ドキュメント SHALL ADR 003 のエントリを追加する

---

## Non-Functional Requirements

### Code Architecture and Modularity

- **Single Responsibility Principle**: 各ルールセット JSON は保護対象（main / version-tags / major-tags）ごとに独立したファイルとして管理する
- **Modular Design**: ルールセットは対象・目的ごとに分離し、一つのファイルに複数の保護対象を混在させない
- **Clear Interfaces**: 各 JSON ファイルは GitHub API スキーマに準拠し、Web UI または CLI から直接インポート可能な形式とする

### Security

- ルールセットの `enforcement` は `active`（有効）に設定し、`disabled` や `evaluate` では運用しない
- `bypass_actors` は空配列とする（個人リポジトリのオーナーバイパスは GitHub 仕様として機能するため、明示的な設定は不要）
- PR 必須化による強制的なコードレビュープロセスを確立し、main への直接 push による意図しない変更を防止する
- ステータスチェック（`lint`, `analyze (actions)`）の必須化により、セキュリティ検査（zizmor, ghalint, CodeQL）を通過しない変更のマージを防止する

### Reliability

- ルールセット JSON は GitHub API スキーマへの準拠を維持し、インポート時のエラーを防止する
- tagpr・bump_major_tag の自動化フローがルールセットにより妨げられないことを設計レベルで保証する
- Renovate Bot の依存関係更新 PR も CI ステータスチェックの適用対象となることを設計に反映する

### Usability

- ルールセット JSON はコメントなしで Git で管理し、変更意図は ADR と commit message で記録する
- 各 JSON ファイル名は保護対象が一目でわかる命名とする（`protect-main.json`, `protect-version-tags.json`, `protect-major-tags.json`）
- GitHub Web UI からのインポート手順は ADR または tasks.md の手動手順セクションに記載する

---

## Out of Scope

以下は本スペックのスコープ外とする:

- ルールセットを GitHub Web UI に適用する具体的な手動操作（tasks.md の手動手順として別途記載）
- 既存 Workflow ファイル（`my_release.yml` 等）の変更
- tagpr の設定（`.tagpr`）の変更
- ADR 002 の廃止記録（PR #13 の GITHUB_TOKEN 化に関する ADR 002 は PR #16 の revert 前に削除済みのため、ADR 003 で経緯を説明するにとどめる）
- 個人リポジトリ以外の組織リポジトリへの適用（bypass_actors の設定方法が異なるため、本スペックは個人リポジトリを前提とする）
- AGENTS.md / CLAUDE.md の再作成（別途対応）
