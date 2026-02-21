# Tasks Document

## SHA ピン留めポリシー（全タスク共通）

全ての `uses:` 指定は **実際の full commit SHA**（40文字）を使用すること。プレースホルダー `<sha>` は使用禁止。

```yaml
# 正しい例
uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4

# 禁止
uses: actions/checkout@v4
uses: actions/checkout@<sha>
```

各 Action の最新リリースタグに対応する SHA は、GitHub リリースページまたは以下の方法で取得する:
```bash
gh api repos/{owner}/{repo}/git/ref/tags/{tag} --jq '.object.sha'
# タグが別オブジェクトを指す場合（annotated tag）:
gh api repos/{owner}/{repo}/git/tags/{sha} --jq '.object.sha'
```

---

## Phase 1: 基盤設定ファイル群

- [ ] 1. .gitignore の更新
  - File: `.gitignore`
  - `node_modules/` の除外エントリを追加
  - 既存の direnv 用 `.envrc` の除外設定は保持
  - _Leverage: 既存の `.gitignore`（現在は `.envrc` のみ記載）_
  - _Requirements: Requirement 7（ADR 管理のための npm 利用）_
  - _Prompt: Role: リポジトリ管理者 | Task: `.gitignore` に `node_modules/` を追加する。現在のファイルには direnv 用の `.envrc` 除外のみが記載されている。`node_modules/` を追記して保存する。既存の記述は変更しないこと | Restrictions: 既存の `.envrc` エントリを削除しない | Success: `node_modules/` が `.gitignore` に追加されており、既存エントリが保持されている_

- [ ] 2. .ls-lint.yml の作成
  - File: `.ls-lint.yml`
  - `.github/workflows/` 配下の `.yml` ファイルに `snake_case` 命名規則を適用
  - _Leverage: なし（新規作成）_
  - _Requirements: Requirement 1_
  - _Prompt: Role: リポジトリ管理者 | Task: `.ls-lint.yml` をリポジトリルートに作成する。内容は以下の通り: `ls-lint:` セクションに `.github/workflows:` キーを定義し、`.yml: snake_case` を設定する。これにより `.github/workflows/` 配下の全 `.yml` ファイルが snake_case 命名規則に強制される | Restrictions: 設定はこの1ディレクトリのみ対象とする | Success: `.ls-lint.yml` が正しい YAML 構造で作成されており、`ls-lint` コマンドがエラーなく実行できる_

- [ ] 3. .tagpr の作成
  - File: `.tagpr`
  - tagpr のリリース設定ファイルを作成
  - 設定値: `vPrefix=true`、`releaseBranch=main`、`versionFile=-`
  - _Leverage: なし（新規作成）_
  - _Requirements: Requirement 4_
  - _Prompt: Role: リポジトリ管理者 | Task: `.tagpr` をリポジトリルートに作成する。INI 形式で以下の内容を記述する: `[tagpr]` セクションに `vPrefix = true`、`releaseBranch = main`、`versionFile = -` を設定する。`versionFile = -` はバージョンファイルを使用しないことを意味する | Restrictions: 設定値を変更しない | Success: `.tagpr` が正しい INI 形式で作成されており、3つの設定値が正確に記述されている_

- [ ] 4. .adr.json の作成
  - File: `.adr.json`
  - ADR 管理ツール（adr npm パッケージ）の設定ファイルを作成
  - 設定: `path: "docs/adr/"`, `digits: 3`, `language: "en"`
  - _Leverage: なし（新規作成）_
  - _Requirements: Requirement 7_
  - _Prompt: Role: リポジトリ管理者 | Task: `.adr.json` をリポジトリルートに作成する。JSON 形式で以下の内容を記述する: `path` に `"docs/adr/"`, `digits` に `3`, `language` に `"en"` を設定する。これにより ADR ファイルは `docs/adr/` 配下に3桁ゼロ埋め番号で英語テンプレートとして生成される | Restrictions: 設定値を変更しない | Success: `.adr.json` が正しい JSON 形式で作成されており、3つのフィールドが正確に記述されている_

- [ ] 5. .github/CODEOWNERS の作成
  - File: `.github/CODEOWNERS`
  - `@kryota-dev` をデフォルトのコードオーナーとして設定
  - `.github/` ディレクトリが存在しない場合は作成する
  - _Leverage: なし（新規作成）_
  - _Requirements: Requirement 8_
  - _Prompt: Role: リポジトリ管理者 | Task: `.github/CODEOWNERS` を作成する。内容は `* @kryota-dev` の1行のみ。これにより全ファイルのデフォルトオーナーが `@kryota-dev` に設定され、PR 作成時に自動でレビュアーとしてアサインされる。`.github/` ディレクトリが存在しない場合は先に作成する | Restrictions: ユーザー名は必ず `@kryota-dev` を使用する（`@ryota` 等の別名不可）| Success: `.github/CODEOWNERS` が作成されており、`* @kryota-dev` が正しく記述されている_

- [ ] 6. .github/release.yml の作成
  - File: `.github/release.yml`
  - GitHub 自動リリースノートのカテゴリ設定を作成
  - カテゴリ: Breaking Changes / New Features / Fix bug / Maintenance / Other Changes
  - _Leverage: なし（新規作成）_
  - _Requirements: Requirement 5_
  - _Prompt: Role: リポジトリ管理者 | Task: `.github/release.yml` を作成する。`changelog.categories` 配下に以下の5カテゴリを定義する: (1) `Breaking Changes` - labels: `[breaking-change]`, (2) `New Features` - labels: `[enhancement]`, (3) `Fix bug` - labels: `[bug]`, (4) `Maintenance` - labels: `[maintenance, dependencies]`, (5) `Other Changes` - labels: `["*"]`。YAML 形式で記述する | Restrictions: カテゴリ名とラベルは指定通りに記述する | Success: `.github/release.yml` が正しい YAML 形式で作成されており、5カテゴリが定義されている_

---

## Phase 2: npm セットアップ

- [ ] 7. package.json の作成と npm install
  - Files: `package.json`, `package-lock.json`
  - `adr` を devDependency として追加し、`adr:new` スクリプトを定義
  - `npm install` を実行して `package-lock.json` を生成
  - _Leverage: なし（新規作成）_
  - _Requirements: Requirement 7_
  - _Prompt: Role: リポジトリ管理者 | Task: `package.json` をリポジトリルートに作成し、`npm install` を実行する。`package.json` の内容: `scripts` に `"adr:new": "adr new"` を定義し、`devDependencies` に `"adr": "^x.x.x"`（最新バージョンに置き換え）を追加する。作成後 `npm install` を実行して `package-lock.json` を生成すること。`node_modules/` は `.gitignore` に追加済みのためコミット不要 | Restrictions: `dependencies`（非 dev）に adr を追加しない。`npm install` は必ず実行して `package-lock.json` を生成すること | Success: `package.json` が作成されており、`npm run adr:new -- "Test ADR"` が実行できる。`package-lock.json` がリポジトリに存在する_

---

## Phase 3: Renovate Bot 設定

- [ ] 8. renovate.json5 の作成
  - File: `renovate.json5`
  - Renovate Bot の設定ファイルを作成
  - `helpers:pinGitHubActionDigests` プリセットで Actions を自動 SHA ピン留め
  - Dependabot Alerts 連携（`[SECURITY]` ラベル付き即時 PR）
  - _Leverage: なし（新規作成）_
  - _Requirements: Requirement 6_
  - _Prompt: Role: リポジトリ管理者 | Task: `renovate.json5` をリポジトリルートに作成する。内容は JSON5 形式で以下を含む: (1) `"$schema": "https://docs.renovatebot.com/renovate-schema.json"`, (2) `"extends": ["config:recommended", "helpers:pinGitHubActionDigests"]` - Actions を自動 SHA ピン留め, (3) `"schedule": ["every weekend"]` - 定期更新は週末に集約, (4) `"labels": ["Maintenance"]` - 通常更新 PR のラベル, (5) `"vulnerabilityAlerts": { "labels": ["[SECURITY]"], "schedule": ["at any time"] }` - Dependabot Alerts 連携でセキュリティ脆弱性は即時 PR 作成。なお Renovate Bot 自体は GitHub App としてリポジトリにインストールする必要があり、そのインストール作業はこのタスクのスコープ外（ユーザーが別途対応） | Restrictions: `.github/dependabot.yml` は作成しない（Dependabot Version Updates は使用しない） | Success: `renovate.json5` が正しい JSON5 形式で作成されている。Renovate Bot がリポジトリをスキャンした際に設定が正しく読み込まれる_

---

## Phase 4: 内部 CI ワークフロー群

- [ ] 9. .github/workflows/my_test.yml の作成
  - File: `.github/workflows/my_test.yml`
  - PR・merge_group トリガーで actionlint / ls-lint / ghalint / zizmor を実行する品質ゲート
  - **全 `uses:` に実際の full commit SHA を使用すること**
  - _Leverage: design.md の Component 1 設計詳細_
  - _Requirements: Requirement 1, Requirement 2, Requirement 3_
  - _Prompt: Role: GitHub Actions エンジニア | Task: `.github/workflows/my_test.yml` を作成する。以下の仕様に従う: (1) トリガー: `pull_request` および `merge_group`, (2) concurrency: `${{ github.workflow }}-${{ github.ref }}` でグループ化し `cancel-in-progress: true`, (3) トップレベル `permissions: {}`, (4) `lint` job: `ubuntu-latest`, `contents: read` + `pull-requests: write` permissions, (5) ステップ構成: Step1: `actions/checkout` (SHA ピン留め), Step2: `reviewdog/action-actionlint` (SHA ピン留め) with `reporter: github-pr-review`, Step3: `ls-lint/action` (SHA ピン留め), Step4: `aquaproj/aqua-installer` (SHA ピン留め) with `aqua_version` 指定後に `run: ghalint run`, Step5: `astral-sh/setup-uv` (SHA ピン留め) 後に `run: uvx zizmor --format=github .` with `GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}`。**重要: 全ての `uses:` は必ず実際の full commit SHA（40文字）を使用すること。各 Action の最新リリースに対応する SHA を GitHub で確認して記述する。コメントにバージョンタグを付与すること（例: `actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4`）** | Restrictions: `<sha>` プレースホルダーを使用しない。SHA はコミット時点の実際の値を使用する | Success: actionlint / ls-lint / ghalint / zizmor の4ツールが全て実行され、ghalint が SHA ピン留めを検証できる状態になっている_

- [ ] 10. .github/workflows/my_setup_pr.yml の作成
  - File: `.github/workflows/my_setup_pr.yml`
  - PR opened トリガーで作成者を assignee に自動設定
  - `checkout` ステップは不要（`gh pr edit` は checkout 不要）
  - _Leverage: design.md の Component 3 設計詳細_
  - _Requirements: Requirement 3_
  - _Prompt: Role: GitHub Actions エンジニア | Task: `.github/workflows/my_setup_pr.yml` を作成する。以下の仕様に従う: (1) name: `setup_pr`, (2) トリガー: `pull_request` の `types: [opened]`, (3) トップレベル `permissions: {}`, (4) `add_assignee` job: `ubuntu-latest`, `pull-requests: write` permission のみ, (5) ステップ: `actions/checkout` は不要。`gh pr edit "$PR_URL" --add-assignee "$ACTOR"` を実行する `run` ステップのみ。env に `GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}`、`PR_URL: ${{ github.event.pull_request.html_url }}`、`ACTOR: ${{ github.actor }}` を設定する。GitHub CLI (`gh`) は `ubuntu-latest` にプリインストール済みのため追加インストール不要 | Restrictions: `checkout` ステップを追加しない。`uses:` を使う場合は SHA ピン留めを行うこと | Success: PR が作成された際に作成者が自動で assignee に追加される_

- [ ] 11. .github/workflows/my_release.yml の作成
  - File: `.github/workflows/my_release.yml`
  - main ブランチへの push トリガーで tagpr によるリリース管理とメジャータグ更新を行う
  - 2 job 構成: `tagpr` → `bump_major_tag`
  - PAT（`APP_TOKEN`）を使用。`run:` ブロック内での直接テンプレート展開は禁止（環境変数経由）
  - **全 `uses:` に実際の full commit SHA を使用すること**
  - _Leverage: design.md の Component 2 設計詳細_
  - _Requirements: Requirement 3, Requirement 4_
  - _Prompt: Role: GitHub Actions エンジニア | Task: `.github/workflows/my_release.yml` を作成する。以下の仕様に従う: (1) name: `release`, (2) トリガー: `push` branches: `[main]`, (3) トップレベル `permissions: {}`, (4) `tagpr` job: `ubuntu-latest`, permissions: `contents: write` + `pull-requests: write`, outputs: `tag: ${{ steps.tagpr.outputs.tag }}`, ステップ: `actions/checkout` (SHA ピン留め) with `token: ${{ secrets.APP_TOKEN }}`, `Songmu/tagpr` (SHA ピン留め) with id: `tagpr` env: `GITHUB_TOKEN: ${{ secrets.APP_TOKEN }}`, (5) `bump_major_tag` job: `needs: tagpr`, `if: needs.tagpr.outputs.tag != ''`, `ubuntu-latest`, permissions: `contents: write`, ステップ: `actions/checkout` (SHA ピン留め) with `token: ${{ secrets.APP_TOKEN }}`, `Update major tag` run ステップ（env に `TAG: ${{ needs.tagpr.outputs.tag }}` と `GITHUB_TOKEN: ${{ secrets.APP_TOKEN }}` を設定し、run ブロックで `MAJOR="${TAG%%.*}"` / `git tag -f "$MAJOR"` / `git push origin "$MAJOR" --force` を実行）。**セキュリティ注意: `${{ needs.tagpr.outputs.tag }}` を `run:` ブロック内で直接展開しない。必ず `env:` 経由で渡すこと（テンプレートインジェクション防止）。全 `uses:` は full commit SHA を使用すること** | Restrictions: `run:` 内でのテンプレート直接展開禁止。`APP_TOKEN` はリポジトリシークレットとして事前設定が必要（設定はスコープ外）| Success: main への push で tagpr が起動し、タグ付け後にメジャータグ（v1 等）が更新される。ghalint の SHA ピン留め検証を通過する_

- [ ] 12. .github/workflows/my_codeql.yml の作成
  - File: `.github/workflows/my_codeql.yml`
  - push(main) / pull_request / merge_group トリガーで CodeQL セキュリティスキャンを実行
  - **全 `uses:` に実際の full commit SHA を使用すること**
  - _Leverage: design.md の Component 4 設計詳細_
  - _Requirements: Requirement 3_
  - _Prompt: Role: GitHub Actions エンジニア | Task: `.github/workflows/my_codeql.yml` を作成する。以下の仕様に従う: (1) name: `codeql`, (2) トリガー: `push` branches: `[main]`, `pull_request`, `merge_group`, (3) トップレベル `permissions: {}`, (4) `analyze` job: `ubuntu-latest`, permissions: `actions: read` + `contents: read` + `security-events: write`, strategy matrix: `language: [actions]`, ステップ: `actions/checkout` (SHA ピン留め), `github/codeql-action/init` (SHA ピン留め) with `languages: ${{ matrix.language }}`, `github/codeql-action/analyze` (SHA ピン留め)。**全 `uses:` は必ず実際の full commit SHA（40文字）を使用すること。`github/codeql-action` は composite action のため `init` と `analyze` それぞれの SHA が必要** | Restrictions: SHA プレースホルダー使用禁止 | Success: CodeQL スキャンが実行され、セキュリティ結果が GitHub の Security タブに表示される_

---

## Phase 5: ADR ディレクトリの初期化

- [ ] 13. docs/adr/ ディレクトリの作成と初期 ADR
  - Files: `docs/adr/.gitkeep`（または初期 ADR ファイル）
  - `docs/adr/` ディレクトリを作成し Git で追跡できる状態にする
  - `npm run adr:new` コマンドの動作確認を兼ねて初期 ADR を作成することを推奨
  - _Leverage: `.adr.json`（タスク 4 で作成）, `package.json`（タスク 7 で作成）_
  - _Requirements: Requirement 7_
  - _Prompt: Role: リポジトリ管理者 | Task: `docs/adr/` ディレクトリを作成し Git で追跡できる状態にする。手順: (1) `mkdir -p docs/adr` でディレクトリ作成, (2) `npm run adr:new -- "Repository environment setup"` を実行して初期 ADR を生成する（推奨）。または `touch docs/adr/.gitkeep` で空ファイルを置く最小限の対応も可。初期 ADR を作成した場合は内容を適宜編集してリポジトリ環境構築の設計決定を記録すること | Restrictions: `docs/adr/` ディレクトリが Git で追跡されていること（空ディレクトリは Git 管理対象外のため `.gitkeep` 等が必要） | Success: `docs/adr/` ディレクトリが存在し、Git の管理下に入っている_

---

## Phase 6: README 更新

- [ ] 14. README.md の更新
  - File: `README.md`
  - リポジトリの目的・概要と Reusable Workflow 一覧セクションを追加
  - 現時点では Reusable Workflow は未実装のためプレースホルダーで記述
  - _Leverage: 既存の `README.md`（現在は `# actions\nGitHub Actions Reusable Workflow` の2行のみ）_
  - _Requirements: Requirement 9_
  - _Prompt: Role: テクニカルライター | Task: `README.md` を更新する。現在の内容（`# actions\nGitHub Actions Reusable Workflow`）を拡充する。含めるべきセクション: (1) リポジトリの目的・概要（`kryota-dev/actions` は再利用可能な GitHub Actions Reusable Workflow を一元管理するリポジトリである旨）, (2) 利用方法（他リポジトリからの参照方法の基本説明: `uses: kryota-dev/actions/.github/workflows/{workflow}.yml@vX`）, (3) Available Workflows セクション（現時点では内部 CI ワークフロー群のみで Reusable Workflow は「Coming soon」等のプレースホルダー）, (4) Development（`npm run adr:new` コマンドの説明等）。日本語・英語どちらでも可 | Restrictions: 過度な詳細化は不要。将来の Reusable Workflow 追加時に更新しやすい構造にする | Success: README にリポジトリの目的が明記されており、利用者が基本的な使い方を把握できる_

---

## 実装完了チェックリスト

以下のファイルが全て存在することを確認する:

| ファイル | タスク | 確認 |
|---|---|---|
| `.gitignore`（更新済み） | 1 | |
| `.ls-lint.yml` | 2 | |
| `.tagpr` | 3 | |
| `.adr.json` | 4 | |
| `.github/CODEOWNERS` | 5 | |
| `.github/release.yml` | 6 | |
| `package.json` | 7 | |
| `package-lock.json` | 7 | |
| `renovate.json5` | 8 | |
| `.github/workflows/my_test.yml` | 9 | |
| `.github/workflows/my_setup_pr.yml` | 10 | |
| `.github/workflows/my_release.yml` | 11 | |
| `.github/workflows/my_codeql.yml` | 12 | |
| `docs/adr/`（追跡済み） | 13 | |
| `README.md`（更新済み） | 14 | |

## 実装後の手動設定（スコープ外・ユーザー対応）

以下はリポジトリの Web UI または外部サービスで設定が必要な項目:

1. **PAT（`APP_TOKEN`）の設定**: GitHub リポジトリの Settings > Secrets and variables > Actions で `APP_TOKEN` シークレットを追加。PAT には `repo` と `workflow` スコープが必要
2. **Renovate Bot のインストール**: [Renovate GitHub App](https://github.com/apps/renovate) をリポジトリにインストール
3. **Dependabot Alerts の有効化**: GitHub リポジトリの Settings > Security > Dependabot alerts を有効化
