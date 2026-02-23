# Tasks Document

## 概要

本タスクドキュメントは、`kryota-dev/actions` リポジトリに Composite Actions サポートを追加するための実装タスクを定義する。

変更対象ファイルは以下の4つのみ:

| ファイル | 変更種別 | 対応タスク |
|---|---|---|
| `.ls-lint.yml` | 修正 | タスク 1 |
| `.github/workflows/my_test.yml` | 修正 | タスク 2 |
| `.github/composite/` | 新規作成 | タスク 3 |
| `README.md` | 修正 | タスク 4 |

---

## Phase 1: 設定ファイルの修正

- [ ] 1. `.ls-lint.yml` の修正（既存バグ修正 + Composite Actions ルール追加）
  - File: `.ls-lint.yml`
  - トップレベルキーを `ls-lint:` から `ls:` に修正する（ls-lint 全バージョンで正式なキーは `ls:`。現行の `ls-lint:` キーは認識されないため CI のチェックが機能していない）
  - `.github/composite/` ディレクトリの命名規則ルールを追加する
  - _Leverage: 既存の `.ls-lint.yml`（現在は `ls-lint:` キーで `.github/workflows` の snake_case ルールのみ記述）_
  - _Requirements: Requirement 2_
  - _Prompt: Role: リポジトリ管理者 | Task: `.ls-lint.yml` を以下の内容に書き換える。変更点は2つ: (1) トップレベルキーを `ls-lint:` → `ls:` に修正（ls-lint の正式なキー。現行の `ls-lint:` は認識されないバグがある）, (2) `.github/composite:` セクションを追加して Composite Actions の命名規則を設定する。\n\n変更前:\n```yaml\nls-lint:\n  .github/workflows:\n    .yml: snake_case\n```\n\n変更後:\n```yaml\nls:\n  .github/workflows:\n    .yml: snake_case\n  .github/composite:\n    .dir: kebab-case\n    .yml: regex:action\n```\n\n設定の意味: `.dir: kebab-case` は `.github/composite/` 配下のサブディレクトリ名（Action 名）を kebab-case に強制する。`.yml: regex:action` は `action.yml` というファイル名のみを許可する（`action.yml` 以外の `.yml` ファイルをエラーにする）。 | Restrictions: `.github/workflows` の既存ルール（`snake_case`）は変更しない。インデントは2スペースを使用すること | Success: `.ls-lint.yml` が上記の内容で保存されており、`ls` キーが使用されていること。`.github/composite/kebab-case-action/action.yml` のような構造に対して ls-lint がエラーを報告しないこと_

---

## Phase 2: CI パイプラインの拡張

- [ ] 2. `my_test.yml` への `ghalint run-action` ステップ追加
  - File: `.github/workflows/my_test.yml`
  - 既存の `Run ghalint` ステップの直後に `Run ghalint run-action` ステップを追加する
  - `ghalint run-action` は `aqua.yaml` の `ghalint@v1.5.5`（v1.5.1 以降でサポート）で実行可能。追加セットアップ不要
  - _Leverage: 既存の `.github/workflows/my_test.yml`（`ghalint run` ステップがすでにある。aqua-installer と PATH 設定も済み）, `aqua.yaml`（`ghalint@v1.5.5` が定義済み）_
  - _Requirements: Requirement 4_
  - _Prompt: Role: GitHub Actions エンジニア | Task: `.github/workflows/my_test.yml` の `Run ghalint` ステップの直後に `Run ghalint run-action` ステップを追加する。\n\n現在の該当箇所:\n```yaml\n      - name: Run ghalint\n        run: ghalint run\n        shell: bash\n\n      - uses: astral-sh/setup-uv@eac588ad8def6316056a12d4907a9d4d84ff7a3b # v7.3.0\n```\n\n変更後:\n```yaml\n      - name: Run ghalint\n        run: ghalint run\n        shell: bash\n\n      - name: Run ghalint run-action\n        run: ghalint run-action\n        shell: bash\n\n      - uses: astral-sh/setup-uv@eac588ad8def6316056a12d4907a9d4d84ff7a3b # v7.3.0\n```\n\n`ghalint run-action` は `.github/composite/` 配下の `action.yml` を含む、カレントディレクトリ配下のすべての `action.yml` に対してセキュリティポリシー（SHA ピン留め等）を検証する。`aqua.yaml` に定義済みの `ghalint@v1.5.5` で実行可能（v1.5.1 以降でサポート）。追加のインストールや PATH 設定は不要（既存の aqua-installer ステップで処理済み）。 | Restrictions: 既存のステップ（`ghalint run`、その前後のステップ）を変更しない。追加するステップは `Run ghalint` の直後、`astral-sh/setup-uv` の前に挿入する。`uses:` の追加は不要（`run:` ステップのみ） | Success: `my_test.yml` に `Run ghalint run-action` ステップが追加されており、PR 実行時に `.github/composite/` 配下の `action.yml` の SHA ピン留め違反を検出できること_

---

## Phase 3: ディレクトリ作成

- [ ] 3. `.github/composite/` ディレクトリの作成（`.gitkeep` 配置）
  - File: `.github/composite/.gitkeep`
  - `.github/composite/` ディレクトリを作成し、`.gitkeep` を配置して Git 管理下に置く
  - ls-lint の `.yml: regex:action` ルールは `.yml` ファイルのみを対象とするため `.gitkeep` への誤検知は発生しない
  - _Leverage: 既存の `.github/` ディレクトリ構造_
  - _Requirements: Requirement 1_
  - _Prompt: Role: リポジトリ管理者 | Task: `.github/composite/` ディレクトリを作成し、`.gitkeep` ファイルを配置する。手順: (1) `.github/composite/` ディレクトリを作成する, (2) `.github/composite/.gitkeep` を空ファイルとして作成する。\n\nGit は空ディレクトリを追跡しないため `.gitkeep` が必要。ls-lint の設定（`.yml: regex:action`）は `.yml` 拡張子のファイルのみを対象とするため、`.gitkeep` ファイルは ls-lint の検証対象にならない（エラーは発生しない）。\n\n将来 Composite Action を追加する際は `.github/composite/{action-name}/action.yml` の構造でファイルを作成する（`{action-name}` は kebab-case で命名すること）。 | Restrictions: `.gitkeep` の内容は空でよい。`.github/composite/` 直下にサブディレクトリは作成しない（Composite Action の実装は本タスクのスコープ外）| Success: `.github/composite/.gitkeep` が存在し、`git status` で追跡されていること_

---

## Phase 4: ドキュメント更新

- [ ] 4. `README.md` への Composite Actions セクション追加
  - File: `README.md`
  - 既存の `## Usage` セクションと `## Available Workflows` セクションの構造を維持したまま、Composite Actions に関するサブセクションを追加する
  - _Leverage: 既存の `README.md`（現在の構造: `## Overview`, `## Usage`, `## Available Workflows`, `## Development`, `## Manual Setup Required`）_
  - _Requirements: Requirement 8_
  - _Prompt: Role: テクニカルライター | Task: `README.md` に Composite Actions に関するサブセクションを追加する。既存の構造（セクション名・順序）は変更しない。以下の2箇所にサブセクションを追加する。\n\n**追加箇所 1: `## Usage` セクションの末尾**\n\n既存の `## Usage` セクション（Reusable Workflow の参照方法）の末尾に以下を追加する:\n\n```markdown\n### Composite Actions\n\n他のリポジトリから Composite Action を参照する場合は以下の形式を使用します:\n\n```yaml\nsteps:\n  - uses: kryota-dev/actions/.github/composite/{action-name}@vX\n    with:\n      # inputs\n```\n\nバージョンはメジャータグ（例: `v1`）または完全なバージョンタグ（例: `v1.0.0`）で指定してください。\n\n> **Reusable Workflows との違い**: Reusable Workflows は `jobs:` レベルで呼び出すのに対し、Composite Actions は `steps:` レベルで呼び出します。Composite Actions は呼び出し元ジョブ内でステップとして実行されるため、より細粒度な再利用が可能です。\n```\n\n**追加箇所 2: `## Available Workflows` セクション内**\n\n`### Reusable Workflows` の後、`### Internal CI Workflows` の前に以下を追加する:\n\n```markdown\n### Composite Actions\n\nComing soon.\n```\n\n**注意事項:**\n- `## Usage` のセクション名は変更しない（`## Usage` のまま）\n- `## Available Workflows` のセクション名は変更しない\n- 既存の Reusable Workflows の説明（`jobs:` 構文のサンプル等）は変更しない\n- `### Internal CI Workflows` の表は変更しない | Restrictions: 既存のセクション名・構造・内容を変更しない。サブセクションの追加のみを行う | Success: `README.md` に `### Composite Actions` サブセクションが `## Usage` と `## Available Workflows` の両方に追加されており、Composite Action の参照方法サンプルが含まれていること_

---

## 実装完了チェックリスト

以下の変更がすべて完了していることを確認する:

| ファイル | 変更内容 | タスク | 確認 |
|---|---|---|---|
| `.ls-lint.yml` | `ls-lint:` → `ls:` キー修正 + `.github/composite/` ルール追加 | 1 | |
| `.github/workflows/my_test.yml` | `ghalint run-action` ステップ追加 | 2 | |
| `.github/composite/.gitkeep` | 新規作成（空ファイル） | 3 | |
| `README.md` | Composite Actions サブセクション追加（Usage + Available Workflows） | 4 | |

## 実装後の動作確認項目

実装完了後、以下の動作を PR 上で確認する:

1. **ls-lint の動作確認**
   - `.github/composite/` 配下に kebab-case のサブディレクトリと `action.yml` を持つ PR で CI が通過すること
   - 違反するディレクトリ名（例: `setupNode`）を含む PR で ls-lint がエラーを報告すること

2. **ghalint run-action の動作確認**
   - SHA ピン留め済みの `action.yml` を含む PR で CI が通過すること
   - ミュータブルタグ（`@v4`）を含む `action.yml` を追加した PR で `ghalint run-action` がエラーを報告すること

3. **zizmor の自動検出確認**
   - `action.yml` を追加した PR で zizmor が `.github/composite/` 配下もスキャン対象に含めることを CI ログで確認すること

4. **actionlint の誤検知なし確認**
   - `action.yml` を追加した PR で actionlint がエラーを報告しないこと（`.github/composite/` は actionlint のスキャン対象外）
