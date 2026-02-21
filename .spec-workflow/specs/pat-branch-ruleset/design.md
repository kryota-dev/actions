# Design Document

## Overview

本ドキュメントは、`kryota-dev/actions` リポジトリにおけるブランチ・タグ保護のルールセット設計を定義する。

PAT（`APP_TOKEN`）前提での再設計により、前回（GITHUB_TOKEN 前提）では実現できなかった PR 必須化・ステータスチェック必須化を含む強力な保護が可能となった。成果物は `.github/rulesets/` 配下の 3 つの JSON ファイル（IaC）と `docs/adr/003-pat-branch-ruleset.md` である。

## Steering Document Alignment

### Technical Standards

- **SHA ピン留め**: 本設計は Workflow ファイルを変更しないため SHA ピン留めポリシーの直接適用対象外。ただし設計判断を ADR として記録することで ADR 管理ポリシー（ADR 001）に準拠する。
- **権限最小化**: ルールセットの `bypass_actors` は空配列とし、明示的なバイパス設定を持たない（個人リポジトリのオーナーバイパスは GitHub 仕様として機能する）。

### Project Structure

- ルールセット JSON は `.github/rulesets/` に配置（`.github/` 配下の設定ファイルとして既存の `CODEOWNERS`, `release.yml` と同一レイヤー）
- ADR は `docs/adr/` に配置（`001-repository-environment-setup.md` と同一ディレクトリ）
- ファイル命名: `snake_case`（ls-lint ポリシー準拠、`protect-main.json` 等はハイフン区切りだが JSON ファイルは ls-lint の対象外）

## Code Reuse Analysis

### Existing Components to Leverage

- **`.github/workflows/my_test.yml`**: `lint` ジョブ（actionlint + ls-lint + ghalint + zizmor）がステータスチェック名 `lint` として機能。`required_status_checks` の `context` に直接参照する。
- **`.github/workflows/my_codeql.yml`**: `analyze` ジョブが `strategy.matrix` を使用するため、ステータスチェック名は `analyze (actions)` となる。`required_status_checks` の `context` に直接参照する。
- **`docs/adr/001-repository-environment-setup.md`**: ADR 003 の作成時にフォーマット（Date / Status / Context / Decision / Consequences）を踏襲する。

### Integration Points

- **tagpr（Songmu/tagpr）**: `my_release.yml` で PAT を使用して動作。ルールセット設定後も、個人リポジトリのオーナーバイパスにより main への直接 push（リリース PR 作成）が継続可能。
- **bump_major_tag**: PAT で `git push origin "$MAJOR" --force` を実行。`protect-major-tags.json` は `deletion` ルールのみ設定し、`non_fast_forward` は意図的に除外することで互換性を維持する。
- **Renovate Bot**: 依存関係更新 PR を作成し、CI（lint + analyze）のステータスチェックを通過した後にマージ可能となる。

## Architecture

### 設計の全体像

```mermaid
graph TD
    subgraph "GitHub Repository: kryota-dev/actions"
        subgraph "Rulesets (IaC)"
            PM[".github/rulesets/protect-main.json"]
            PVT[".github/rulesets/protect-version-tags.json"]
            PMT[".github/rulesets/protect-major-tags.json"]
        end

        subgraph "Protected Refs"
            MAIN["refs/heads/main"]
            VTAGS["refs/tags/v*.*.*"]
            MTAGS["refs/tags/v[0-9]*"]
        end

        subgraph "CI Workflows"
            LINT["my_test.yml → lint job"]
            ANALYZE["my_codeql.yml → analyze job"]
        end

        subgraph "Release Automation (PAT)"
            TAGPR["tagpr (APP_TOKEN)"]
            BUMP["bump_major_tag (APP_TOKEN)"]
        end

        PM --> MAIN
        PVT --> VTAGS
        PMT --> MTAGS

        LINT -->|"status: lint"| MAIN
        ANALYZE -->|"status: analyze (actions)"| MAIN

        TAGPR -->|"管理者バイパス"| MAIN
        TAGPR -->|"管理者バイパス"| VTAGS
        BUMP -->|"管理者バイパス"| MTAGS
    end

    subgraph "ADR"
        ADR["docs/adr/003-pat-branch-ruleset.md"]
    end
```

### 管理者バイパスの仕組み

個人リポジトリ（`kryota-dev/actions`）では、リポジトリオーナーは GitHub の仕様上、常に管理者権限を持つ。PAT（`APP_TOKEN`）はリポジトリオーナーとして認証されるため、ルールセットの `bypass_actors` に明示的な設定をしなくとも、PAT を用いた操作はルールセットの制限をバイパスする。

これにより:
- tagpr の main への直接 push（リリース PR 作成・タグ付け）はバイパス
- bump_major_tag の force push もバイパス
- オーナー自身が行う操作は `pull_request` ルール・`required_status_checks` に縛られない

### required_approving_review_count の設計上の考慮

要件 1-5 では `required_approving_review_count: 1` を定義したが、個人リポジトリでの PR 運用に際して以下の制約がある:

**制約**: GitHub の仕様上、PR の作成者は自分自身の PR を承認できない。オーナーが唯一の貢献者である個人リポジトリでは、`required_approving_review_count: 1` が事実上マージブロックとなる可能性がある。

**設計判断**: `required_approving_review_count: 0` に設定する。PR の作成自体は必須化（`pull_request` ルール）し、コードレビューの強制は 0 件とすることで、個人リポジトリでの運用可能性を確保する。オーナーは管理者バイパスによりルールセット適用対象外で操作できるが、通常の PR ワークフローを通すことでコミット履歴の可視性を確保する。

**将来の拡張**: 協力者が増えた場合は `required_approving_review_count` を 1 以上に変更する。

### required_linear_history の設計上の考慮

`required_linear_history` は squash マージまたは rebase マージのみを許可する。tagpr はリリース PR を作成し、GitHub の PR マージ機能（squash または merge commit）を通じてマージされる。

- GitHub の PR マージで「Squash and merge」または「Rebase and merge」を使用する限り、`required_linear_history` との互換性は問題ない。
- tagpr が main へ直接 push する場合は管理者バイパスが適用されるため、`required_linear_history` の制約を受けない。

**設計判断**: `required_linear_history` を有効化する。リポジトリのマージ設定で「Squash and merge」または「Rebase and merge」のみを許可する設定（Web UI）と組み合わせることを推奨するが、ルールセット JSON の設定範囲外とする。

## Components and Interfaces

### Component 1: protect-main.json

- **Purpose:** main ブランチへの直接 push 防止、PR 必須化、CI ステータスチェック必須化
- **対象ref:** `refs/heads/main`
- **適用ルール:**
  - `deletion`: main ブランチの削除禁止
  - `non_fast_forward`: 履歴書き換えを伴う push の禁止
  - `required_linear_history`: マージコミット禁止（squash/rebase のみ許可）
  - `pull_request`: PR 必須化（`required_approving_review_count: 0`）
  - `required_status_checks`: CI パス必須化（`lint`, `analyze (actions)`）
- **Dependencies:** `my_test.yml`（lint）、`my_codeql.yml`（analyze (actions)）がステータスチェックを提供すること
- **Reuses:** 既存の CI ワークフローのジョブ名をそのまま `context` として参照

### Component 2: protect-version-tags.json

- **Purpose:** 公開済みバージョンタグ（vX.Y.Z）の削除・改ざん防止
- **対象ref:** `refs/tags/v*.*.*`（fnmatch: `*` はドットを含む任意文字列にマッチ）
- **適用ルール:**
  - `deletion`: タグ削除禁止
  - `non_fast_forward`: タグへの force push 禁止
- **Dependencies:** なし（管理者バイパスにより tagpr の操作は妨げない）
- **Reuses:** 前回設計（spec: branch-ruleset）の `protect-version-tags.json` の基本構造を踏襲

### Component 3: protect-major-tags.json

- **Purpose:** メジャータグ（v1, v2 等）の誤削除防止。force push は bump_major_tag のため許可。
- **対象ref:** `refs/tags/v[0-9]*`（`v10`、`v11` 等の 2 桁以上にも対応）
- **適用ルール:**
  - `deletion`: タグ削除禁止のみ
  - `non_fast_forward`: **意図的に除外**（bump_major_tag の `--force` を許容）
- **Dependencies:** なし（管理者バイパスにより bump_major_tag の操作は妨げない）
- **Reuses:** 前回設計（spec: branch-ruleset）の `protect-major-tags.json` の基本構造を踏襲

### Component 4: docs/adr/003-pat-branch-ruleset.md

- **Purpose:** PAT 前提での再設計判断の記録
- **Interfaces:** ADR 形式（Date / Status / Context / Decision / Consequences）
- **Dependencies:** なし
- **Reuses:** `docs/adr/001-repository-environment-setup.md` のフォーマット

## Data Models

### GitHub Ruleset JSON スキーマ

```
{
  "name": string,              // ルールセット名（Web UI での表示名）
  "target": "branch" | "tag", // 保護対象の種別
  "enforcement": "active" | "disabled" | "evaluate",
  "conditions": {
    "ref_name": {
      "include": string[],     // 適用対象の ref パターン（例: ["refs/heads/main"]）
      "exclude": string[]      // 除外パターン（通常は空配列）
    }
  },
  "rules": [
    {
      "type": string           // ルール種別（下記参照）
      // "parameters" フィールドはルール種別によって異なる
    }
  ],
  "bypass_actors": []          // 個人リポジトリでは空配列
}
```

### protect-main.json の完全スキーマ

```json
{
  "name": "protect-main",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "include": ["refs/heads/main"],
      "exclude": []
    }
  },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "required_linear_history" },
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": false,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": false,
        "do_not_enforce_on_create": false,
        "required_status_checks": [
          { "context": "lint" },
          { "context": "analyze (actions)" }
        ]
      }
    }
  ],
  "bypass_actors": []
}
```

**`strict_required_status_checks_policy: false` の理由:** `true` にすると「PR のベースブランチが最新の状態でなければマージ不可」となり、Renovate Bot 等の更新 PR で追加の操作が必要になる。個人リポジトリでの運用負荷を考慮して `false` とする。

**`integration_id` の省略:** `required_status_checks` の `context` に `integration_id`（GitHub App ID）を指定することで特定の App のチェックに限定できるが、`my_test.yml` および `my_codeql.yml` は `github-actions` App（統合 ID: 15368）を使用する。Web UI からインポートする際、`integration_id` は省略可能（省略時は任意の App のチェックを受け付ける）。JSON での管理を簡素化するため省略する。

### protect-version-tags.json の完全スキーマ

```json
{
  "name": "protect-version-tags",
  "target": "tag",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "include": ["refs/tags/v*.*.*"],
      "exclude": []
    }
  },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" }
  ],
  "bypass_actors": []
}
```

**fnmatch 仕様の注記:** `refs/tags/v*.*.*` の `*` は fnmatch の仕様により `.`（ドット）を含む任意の文字列にマッチする。これにより `v1.2.3`、`v10.0.0` 等に正しく適用される。

### protect-major-tags.json の完全スキーマ

```json
{
  "name": "protect-major-tags",
  "target": "tag",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "include": ["refs/tags/v[0-9]*"],
      "exclude": []
    }
  },
  "rules": [
    { "type": "deletion" }
  ],
  "bypass_actors": []
}
```

**`non_fast_forward` を含めない理由:** bump_major_tag が `git push origin "$MAJOR" --force` で実行するため、force push を許容する必要がある。管理者バイパスにより制限されないが、ルールとして設定した場合、非管理者による force push も意図せず許可することになる。`deletion` のみに絞ることで、削除防止のみを強制する最小限の保護とする。

### パターン重複時の GitHub Rulesets 動作

`refs/tags/v*.*.*`（protect-version-tags）と `refs/tags/v[0-9]*`（protect-major-tags）は、バージョンタグ `v1.0.0` のような ref に対して両方マッチする。

**GitHub の動作仕様:** 複数のルールセットが同一の ref にマッチした場合、GitHub はすべてのルールセットのルールを評価し、論理 OR（最も厳しい制約）を適用する。

**具体例（`v1.0.0` タグへの操作）:**

| 操作 | protect-version-tags | protect-major-tags | 結果 |
|------|---------------------|-------------------|------|
| 削除 | `deletion` でブロック | `deletion` でブロック | ブロック |
| force push | `non_fast_forward` でブロック | ルールなし（許可） | ブロック |

`v1.0.0` のような ref は `protect-version-tags` の `non_fast_forward` によって force push がブロックされる。これは意図した動作である（バージョンタグ `vX.Y.Z` は不変であるべきで、force push は禁止すべき）。

一方、`v1`（メジャータグのみ、`v1.0.0` 形式ではない）は `protect-major-tags` のみにマッチするため、`deletion` のみがブロックされ force push は許容される。bump_major_tag が更新するのは `v1` 形式のタグであり、`v1.0.0` 形式ではないため、パターン重複は bump_major_tag の動作に影響しない。

**結論:** パターン重複は意図的に許容する。設計の一貫性として、`vX.Y.Z` タグへの force push はどちらのルールセットからも（直接または間接的に）ブロックされることが望ましい。

## Error Handling

### Error Scenarios

1. **インポート時の JSON スキーマ不正**
   - **Handling:** GitHub Web UI または GitHub CLI がスキーマエラーを返す。JSON の `rules[].type` やパラメータのネストを確認する。
   - **Impact:** ルールセットが適用されない。既存の保護に影響なし。

2. **`required_status_checks` のコンテキスト名不一致**
   - **Handling:** ステータスチェック名（`lint`, `analyze (actions)`）が Workflow の実際のチェック名と一致しているか確認する。`my_test.yml` の `jobs.lint`（チェック名: `lint`）、`my_codeql.yml` の `jobs.analyze`（matrix 使用のためチェック名: `analyze (actions)`）を参照。
   - **Impact:** 存在しないコンテキスト名を指定した場合、ステータスチェックが永遠に pending となり PR がマージ不可になる。

3. **tagpr / bump_major_tag がルールセットにブロックされる**
   - **原因:** 個人リポジトリのオーナーバイパスが期待通りに機能しない場合（アカウント設定変更等）
   - **Handling:** `bypass_actors` に明示的なアクター追加を検討するか、ルールセットの `enforcement` を一時的に `evaluate` に変更して確認する。
   - **Impact:** リリース自動化が停止する。

4. **PR が `required_approving_review_count` によりブロックされる**
   - **本設計では `required_approving_review_count: 0` を採用するため発生しない。**
   - 将来、値を 1 以上に変更した場合は、オーナーが自分の PR をマージするために管理者バイパス（「Merge without waiting for requirements」）を使用する必要がある。

## Testing Strategy

### ルールセット動作確認（手動）

本設計は Workflow ファイルではなく GitHub のルールセット設定であるため、自動テストは適用できない。以下の手動確認手順を実施する。

#### 確認 1: main ブランチへの直接 push のブロック

```bash
# テスト用ブランチを作成してマージ
git checkout -b test/ruleset-verify
echo "test" >> README.md
git add README.md && git commit -m "test: verify ruleset"
# 直接 main への push を試みる（ブロックされることを確認）
git push origin main  # → blocked
# PR 経由でのマージ（成功することを確認）
git push origin test/ruleset-verify
gh pr create --title "test: verify ruleset" --base main
```

#### 確認 2: ステータスチェックの必須化

- PR 作成後、`lint` および `analyze (actions)` のステータスチェックが pending → pass になることを確認する
- 意図的に lint を失敗させた場合、PR がマージ不可になることを確認する

#### 確認 3: tagpr の動作継続

- main にコミットを push し、tagpr がリリース PR を作成できることを確認する
- リリース PR のマージ後、tagpr が `vX.Y.Z` タグを付与できることを確認する

#### 確認 4: bump_major_tag の動作継続

- タグ作成後、`bump_major_tag` ジョブが `git push origin "$MAJOR" --force` を成功させることを確認する

#### 確認 5: バージョンタグの保護

```bash
# 削除禁止の確認（ブロックされることを確認）
git tag -d v0.0.1 && git push origin :v0.0.1  # → blocked
# force push 禁止の確認
git tag -f v0.0.1 && git push origin v0.0.1 --force  # → blocked
```

#### 確認 6: メジャータグの削除禁止

```bash
# 削除禁止の確認（ブロックされることを確認）
git push origin :v0  # → blocked
# force push は許可（bump_major_tag と同じ操作）
git tag -f v0 && git push origin v0 --force  # → 成功（管理者バイパス）
```

### JSON 検証

```bash
# JSON 構文チェック
jq . .github/rulesets/protect-main.json
jq . .github/rulesets/protect-version-tags.json
jq . .github/rulesets/protect-major-tags.json
```
