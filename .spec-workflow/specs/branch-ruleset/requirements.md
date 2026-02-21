# Requirements Document

## Introduction

`kryota-dev/actions` リポジトリに GitHub Repository Rulesets を導入し、ブランチおよびタグを保護する。
このリポジトリは GitHub Actions の Reusable Workflow を一元管理・公開するものであり、外部リポジトリが `uses: kryota-dev/actions/.github/workflows/xxx.yml@vX.Y.Z` の形式で参照する。
そのため、リリースタグの信頼性とメインブランチの安定性を確保することが最重要課題である。

従来の Branch Protection Rules ではなく、より柔軟な **GitHub Repository Rulesets** を使用する。

### 背景

- **リリースフロー**: main へのマージ → tagpr がリリース PR 自動作成 → リリース PR マージで vX.Y.Z タグ付与 → `bump_major_tag` ジョブが vX メジャータグを force push で更新
- **自動化ボット**: tagpr（`github-actions[bot]` として動作）、Renovate Bot（PR 作成のみ）
- **内部 CI**: `my_test.yml`（PR, merge_group）、`my_codeql.yml`（PR, push to main, merge_group）、`my_release.yml`（push to main）、`my_setup_pr.yml`（PR opened）
- **セキュリティポリシー**: SHA ピン留め必須（ghalint, zizmor で CI 検証済み）、権限最小化

### スコープ

| 対象 | 内容 |
|------|------|
| In Scope | main ブランチの保護、バージョンタグ（vX.Y.Z）の保護、メジャータグ（vX）の保護ポリシー検討、ルールセット定義の JSON ファイルによるバージョン管理、ADR の作成 |
| Out of Scope | 他ブランチ（feature/*, renovate/* 等）の制限、Workflow ファイルの変更、外部リポジトリの設定 |

## Alignment with Product Vision

外部リポジトリが安全に Reusable Workflow を参照できる環境を維持するため、以下を達成する:

1. main ブランチへの意図しない直接 push を防止する
2. リリースタグが改ざん・削除されないよう保護する
3. CI が必ず通過した変更のみが main に入ることを保証する
4. tagpr / Renovate Bot 等の自動化ツールが適切に動作できるバイパス設定を提供する
5. ルールセット定義を JSON ファイルとしてリポジトリ内でバージョン管理し、IaC 的な運用を実現する
6. 設計判断を ADR として記録し、将来の意思決定を支援する

## Requirements

### Requirement 1: main ブランチへの直接 push の制限

**User Story:** リポジトリ管理者として、main ブランチへの直接 push を防ぎたい。そうすることで、すべての変更が PR レビューと CI チェックを経由することを保証できる。

#### Acceptance Criteria

1. WHEN 任意のユーザー（管理者を含む）が main ブランチに直接 push しようとする THEN GitHub SHALL その push を拒否する
2. WHEN `github-actions[bot]`（tagpr）が main ブランチに push しようとする THEN GitHub SHALL バイパスリストの設定に従い push を許可する
3. IF バイパスアクターが設定されている THEN そのアクターは Pull Request を経由せずに main へ push できる（バイパスモード: always）

### Requirement 2: Pull Request の必須化

**User Story:** リポジトリ管理者として、main ブランチへのすべての変更に PR を必須化したい。そうすることで、変更の追跡可能性とレビュー機会を確保できる。

#### Acceptance Criteria

1. WHEN 一般ユーザーが main ブランチへ変更をマージしようとする THEN GitHub SHALL Pull Request の作成を要求する
2. WHEN Pull Request が作成される THEN GitHub SHALL 最低 1 名のレビュー承認（`required_approving_review_count: 1`）を要求する
3. WHEN PR 作成者自身が唯一のレビュアーである THEN GitHub SHALL その承認を無効とする（dismiss_stale_reviews は任意）
4. WHEN `github-actions[bot]`（tagpr のリリース PR）がバイパスアクターとして動作する THEN GitHub SHALL PR なしでの直接 push を許可する
5. WHEN Renovate Bot が PR を作成する THEN Renovate Bot の PR は通常の PR フローを経由し、レビューが必要である

### Requirement 3: 必須ステータスチェックの設定

**User Story:** リポジトリ管理者として、CI が通過した変更のみが main にマージされることを保証したい。そうすることで、コードの品質と安全性を維持できる。

#### Acceptance Criteria

1. WHEN Pull Request が main ブランチをターゲットとする THEN GitHub SHALL 以下のステータスチェックを必須とする:
   - `lint`（`my_test.yml` の lint ジョブ）
   - `analyze`（`my_codeql.yml` の analyze ジョブ）
2. WHEN 上記のいずれかのステータスチェックが未完了または失敗している THEN GitHub SHALL マージを拒否する
3. WHEN ステータスチェックが通過している AND レビュー承認が揃っている THEN GitHub SHALL マージを許可する
4. IF Merge Queue を使用する場合 THEN バイパスアクターであっても merge queue をバイパスすることはできない（GitHub の仕様上の制約）

### Requirement 4: バージョンタグ（vX.Y.Z）の保護

**User Story:** リポジトリ管理者として、リリースタグが削除・改ざんされないよう保護したい。そうすることで、外部リポジトリが参照する Workflow のバージョンを安定して保てる。

#### Acceptance Criteria

1. WHEN 任意のユーザーが `v*.*.*` パターンに一致するタグを削除しようとする THEN GitHub SHALL その操作を拒否する
2. WHEN 任意のユーザーが既存の `v*.*.*` タグに force push しようとする THEN GitHub SHALL その操作を拒否する
3. WHEN tagpr が新規バージョンタグ（例: `v1.2.3`）を作成しようとする THEN GitHub SHALL その作成を許可する（新規作成は保護対象外）
4. IF バイパスアクターがバージョンタグを削除・force push する場合 THEN GitHub SHALL 監査ログに記録する

### Requirement 5: メジャータグ（vX）の保護と force push 許可

**User Story:** リポジトリ管理者として、メジャータグ（v1, v2 等）の管理ポリシーを明確に定義したい。そうすることで、`bump_major_tag` ワークフローが正常に動作しつつ、不正な更新を防止できる。

#### Acceptance Criteria

1. WHEN `bump_major_tag` ジョブ（`github-actions[bot]`）が `vX` 形式のタグを force push しようとする THEN GitHub SHALL その操作を許可する
2. WHEN 一般ユーザーが `vX` 形式のタグを削除・force push しようとする THEN GitHub SHALL その操作を拒否する
3. WHEN メジャータグのルールセットを設定する THEN `github-actions[bot]` をバイパスアクターとして登録する
4. IF `vX` タグのルールセットでは force push を許可するオプションを設ける THEN そのオプションはバイパスアクター（`github-actions[bot]`）のみに適用される

### Requirement 6: ルールセット定義の JSON ファイルによるバージョン管理

**User Story:** リポジトリ管理者として、ルールセットの定義を JSON ファイルとしてリポジトリ内でバージョン管理したい。そうすることで、設定変更の履歴追跡・レビュー・IaC 的な管理を実現できる。

#### Acceptance Criteria

1. WHEN ルールセットを定義する THEN GitHub Settings > Rules > Rulesets の Export 機能で出力した JSON 形式のファイルをリポジトリ内の `.github/rulesets/` ディレクトリに格納する
2. WHEN ルールセットの JSON ファイルを作成する THEN ファイル名はルールセット名と一致した `kebab-case.json` 形式とする（例: `protect-main.json`, `protect-version-tags.json`, `protect-major-tags.json`）
3. WHEN ルールセットの設定を変更する THEN 対応する JSON ファイルを修正し、Pull Request を作成してレビューを受けてからマージする
4. WHEN JSON ファイルへの変更が main にマージされる THEN 管理者は以下のいずれかの方法でルールセットを適用する:
   - **GitHub UI**: Settings > Rules > Rulesets > Import ruleset から JSON ファイルをアップロード（新規作成時）
   - **`gh api` コマンド**: 既存ルールセットの更新時は `gh api` を使って REST API 経由で適用する
     ```bash
     # 新規作成
     gh api repos/{owner}/{repo}/rulesets \
       --method POST \
       --input .github/rulesets/protect-main.json

     # 既存ルールセットの更新（ruleset_id を指定）
     gh api repos/{owner}/{repo}/rulesets/{ruleset_id} \
       --method PUT \
       --input .github/rulesets/protect-main.json
     ```
5. WHEN ルールセットをインポートする THEN インポート元の JSON ファイルと実際に適用されたルールセットが一致していることを確認する
6. IF ルールセットの初回作成時 THEN GitHub Settings > Rules > Rulesets > New ruleset で作成した後、Export 機能で JSON を出力し `.github/rulesets/` に格納する
7. WHEN 既存ルールセットを `gh api` で更新する THEN `gh api repos/{owner}/{repo}/rulesets` で ruleset_id を事前に確認してから実行する

#### 変更管理フロー

**初回セットアップ**:
```
GitHub UI でルールセットを新規作成
    ↓
Export 機能で JSON をダウンロード
    ↓
.github/rulesets/ に格納して PR 作成
    ↓
レビュー承認 + CI 通過 → main にマージ
```

**設定変更時**:
```
.github/rulesets/{name}.json を修正
    ↓
Pull Request を作成
    ↓
レビュー承認 + CI 通過
    ↓
main にマージ
    ↓
管理者が gh api または GitHub UI でインポートを実行
    ↓
適用されたルールセットを GitHub UI で確認
```

### Requirement 7: ADR の作成

**User Story:** リポジトリ管理者として、ブランチルールセットの設計判断を ADR として記録したい。そうすることで、将来のメンテナンス時に判断根拠を参照できる。

#### Acceptance Criteria

1. WHEN ブランチルールセットが実装される THEN `docs/adr/` に ADR ファイルが作成される
2. WHEN ADR を作成する THEN ファイル名は `NNN-kebab-case-title.md` の命名規則に従う（例: `003-branch-ruleset.md`）
3. WHEN ADR を作成する THEN 英語で記述し、Context・Decision・Consequences の構造を含む
4. WHEN ADR に Decision を記述する THEN 各ルールセットの名前、対象パターン、適用ルール、バイパス設定を明記する
5. WHEN ADR に Consequences を記述する THEN tagpr・Renovate Bot・`github-actions[bot]` への影響を説明する

## Non-Functional Requirements

### セキュリティ

- **権限最小化**: ルールセットのバイパスアクターは必要最小限に限定する
- **監査可能性**: すべてのバイパス操作は GitHub の監査ログに記録される
- **自動化との両立**: tagpr（`github-actions[bot]`）および `bump_major_tag` ジョブが正常動作できるよう、バイパス設定を適切に構成する
- **ルールセット数の最適化**: 保護対象ごとに独立したルールセットを作成し、管理の明確化を図る

### 信頼性

- **リリースフローの継続性**: ブランチルールセット導入後も、tagpr によるリリースフローが中断なく動作すること
- **Renovate Bot の継続動作**: Renovate Bot が SHA digest 更新 PR を作成・更新できること
- **CI/CD の継続性**: `my_test.yml`、`my_codeql.yml`、`my_release.yml`、`my_setup_pr.yml` が正常に動作すること

### 保守性

- **設定の透明性**: ルールセット設定は ADR で文書化し、理由を明確にする
- **IaC 的な管理**: ルールセット定義を JSON ファイルとしてリポジトリ内で管理することで、設定の変更履歴を Git で追跡できる
- **変更の追跡**: ルールセット設定の変更は Git の commit 履歴と GitHub の監査ログの両方で追跡可能にする
- **レビュー可能性**: ルールセットの変更は PR を通じてレビューされるため、意図しない設定変更を防止できる

### 可用性

- **マージのブロック回避**: 適切なバイパス設定により、自動化ボットがデッドロック状態に陥らないようにする
- **緊急時対応**: バイパスアクターの設定により、緊急修正時に管理者がバイパス可能な仕組みを用意する（ただし、バイパスは監査ログに記録される）

## 補足: ルールセット設計の考察

### 作成するルールセットの構成案

| ルールセット名 | 対象パターン | 主なルール | バイパスアクター |
|--------------|------------|----------|--------------|
| `protect-main` | `main` ブランチ | PR 必須、必須ステータスチェック、force push 禁止、削除禁止 | `github-actions[bot]`（always） |
| `protect-version-tags` | `v*.*.*` タグ | 削除禁止、force push 禁止 | なし（または管理者のみ） |
| `protect-major-tags` | `v[0-9]` タグ | 削除禁止、force push 禁止（バイパスあり） | `github-actions[bot]`（always） |

### JSON ファイルによるバージョン管理

ルールセットの定義は `.github/rulesets/` ディレクトリに JSON ファイルとして格納し、Git でバージョン管理する。

| ファイル名 | 対応するルールセット |
|----------|------------------|
| `protect-main.json` | `protect-main` ルールセット |
| `protect-version-tags.json` | `protect-version-tags` ルールセット |
| `protect-major-tags.json` | `protect-major-tags` ルールセット |

**運用フロー**:
- **初回**: GitHub UI でルールセットを新規作成 → Export で JSON 出力 → `.github/rulesets/` に格納 → PR でマージ
- **変更時**: JSON ファイルを修正 → PR でレビュー → マージ → 管理者が `gh api` または GitHub UI で適用
- **確認**: 適用後にルールセットの設定が JSON と一致しているかを GitHub UI で確認する

**適用コマンド例**:
```bash
# ルールセット一覧（ruleset_id の確認）
gh api repos/kryota-dev/actions/rulesets

# 新規作成
gh api repos/kryota-dev/actions/rulesets \
  --method POST \
  --input .github/rulesets/protect-main.json

# 既存ルールセットの更新
gh api repos/kryota-dev/actions/rulesets/{ruleset_id} \
  --method PUT \
  --input .github/rulesets/protect-main.json
```

**メリット**:
- ルールセット設定の変更履歴を Git commit として追跡可能
- 変更の意図を PR の説明文として記録できる
- レビュープロセスにより、意図しない設定変更を防止
- `gh api` による CLI 操作で手順を自動化・再現可能にできる
- 他のリポジトリへの展開時に JSON を再利用可能

### バイパスアクターの注意事項

- GitHub Repository Rulesets のバイパスアクターは、リポジトリがオーナーである場合（個人リポジトリ）は `github-actions[bot]` のような GitHub App を直接バイパスリストに追加することが**制限される場合がある**
- 個人リポジトリ（`kryota-dev/actions`）では Organization リポジトリと異なり、バイパスアクターに App を追加できない制約がある可能性を考慮し、設計フェーズで実現可能性を検証する
- 設計フェーズでは、GitHub Rulesets の実際の制約を確認し、代替手段（管理者権限での bypass 等）を含む設計を提案する
