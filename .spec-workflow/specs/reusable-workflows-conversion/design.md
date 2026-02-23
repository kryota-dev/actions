# Design Document

## Overview

本ドキュメントは、`kryota-dev/actions` リポジトリの4つの内部 CI ワークフローに対応する Reusable Workflows を新規作成し、既存の内部 CI ワークフローをそれらの Reusable Workflows を呼び出す薄いラッパーにリファクタリングするための技術設計を定義する。

変更の全体像:

1. **`codeql-analysis.yml`** — CodeQL セキュリティスキャンの Reusable Workflow を新規作成
2. **`tagpr-release.yml`** — tagpr リリース管理 + メジャータグ更新の Reusable Workflow を新規作成
3. **`auto-assign-pr.yml`** — PR assignee 自動設定の Reusable Workflow を新規作成
4. **`actions-lint.yml`** — 品質ゲート（actionlint / ls-lint / ghalint / zizmor）の Reusable Workflow を新規作成
5. **`my-codeql.yml`** — Reusable Workflow `codeql-analysis.yml` を呼び出すラッパーにリファクタリング
6. **`my-release.yml`** — Reusable Workflow `tagpr-release.yml` を呼び出すラッパーにリファクタリング
7. **`my-setup-pr.yml`** — Reusable Workflow `auto-assign-pr.yml` を呼び出すラッパーにリファクタリング
8. **`my-test.yml`** — Reusable Workflow `actions-lint.yml` を呼び出すラッパーにリファクタリング
9. **`README.md`** — Reusable Workflows セクションを更新

### 命名方針

外部リポジトリから参照した際に何をしているワークフローなのかが一目で分かるよう、具体的な名称を採用する:

| 旧名称（抽象的） | 新名称（具体的） | 理由 |
|---|---|---|
| `codeql.yml` | `codeql-analysis.yml` | CodeQL による「解析」であることを明示 |
| `release.yml` | `tagpr-release.yml` | tagpr を使用した「リリース管理」であることを明示 |
| `setup-pr.yml` | `auto-assign-pr.yml` | PR の「自動アサイン」であることを明示 |
| `test.yml` | `actions-lint.yml` | GitHub Actions の「Lint」であることを明示 |

## Steering Document Alignment

### 技術基準（既存コーディング規約）

- `uses:` は full commit SHA（40文字）でピン留め（`ghalint` / `zizmor` で CI 検証）
- Renovate Bot により SHA を自動更新
- `permissions: {}` をトップレベルに設定し、各 job で最小権限のみ付与
- `timeout-minutes` を全 job に設定

### プロジェクト構造規約

- Reusable Workflows: `.github/workflows/` 配下、kebab-case、`my-` プレフィックスなし
- 内部 CI: `.github/workflows/` 配下、kebab-case、`my-` プレフィックス付き
- ls-lint で命名規則を自動検証

## Code Reuse Analysis

### 既存コンポーネントの活用

| コンポーネント | 活用方法 |
|---|---|
| `my-codeql.yml` | ロジックを Reusable Workflow に移植し、内部 CI は Reusable Workflow を呼び出す薄いラッパーに変換 |
| `my-release.yml` | ロジックを Reusable Workflow に移植し、内部 CI は Reusable Workflow を呼び出す薄いラッパーに変換 |
| `my-setup-pr.yml` | ロジックを Reusable Workflow に移植し、内部 CI は Reusable Workflow を呼び出す薄いラッパーに変換 |
| `my-test.yml` | ロジックを Reusable Workflow に移植し、内部 CI は Reusable Workflow を呼び出す薄いラッパーに変換 |
| `renovate.json5` | Reusable Workflow 内の `uses:` も `.github/workflows/` 配下にあるため、Renovate の自動更新対象となる。**追加設定不要** |

### Reusable Workflow 内での github コンテキストの動作

Reusable Workflow では、`github` コンテキストは呼び出し元（caller）のコンテキストを継承する。つまり:

- `github.event` — 呼び出し元のトリガーイベントのペイロード
- `github.actor` — 呼び出し元ワークフローをトリガーしたユーザー
- `github.repository` — 呼び出し元リポジトリ
- `github.token` / `secrets.GITHUB_TOKEN` — 呼び出し元の自動トークン（自動付与）

この性質により、`auto-assign-pr.yml` では `github.event.pull_request.html_url` や `github.actor` を入力パラメータとせずに直接参照できる。

### Reusable Workflow のパーミッション継承ルール

Reusable Workflow では、呼び出し元（caller）のジョブレベルの `permissions` が上限境界として機能する。Reusable Workflow 内のジョブは、この境界を超えるパーミッションを取得できない。

したがって、内部 CI ワークフロー（`my-*`）のラッパーでは、呼び出す Reusable Workflow が必要とするパーミッションをジョブレベルで明示的に宣言する必要がある。

### 変更が必要なファイル

| ファイル | 変更種別 | 変更内容 |
|---|---|---|
| `.github/workflows/codeql-analysis.yml` | 新規作成 | CodeQL Reusable Workflow |
| `.github/workflows/tagpr-release.yml` | 新規作成 | Release Reusable Workflow |
| `.github/workflows/auto-assign-pr.yml` | 新規作成 | Auto Assign PR Reusable Workflow |
| `.github/workflows/actions-lint.yml` | 新規作成 | Actions Lint Reusable Workflow |
| `.github/workflows/my-codeql.yml` | 修正 | Reusable Workflow を呼び出すラッパーに変換 |
| `.github/workflows/my-release.yml` | 修正 | Reusable Workflow を呼び出すラッパーに変換 |
| `.github/workflows/my-setup-pr.yml` | 修正 | Reusable Workflow を呼び出すラッパーに変換 |
| `.github/workflows/my-test.yml` | 修正 | Reusable Workflow を呼び出すラッパーに変換 |
| `README.md` | 修正 | Reusable Workflows セクションの更新 |

### 変更が不要なファイル

| ファイル | 理由 |
|---|---|
| `.ls-lint.yml` | 新ファイルは kebab-case に準拠しており変更不要 |
| `renovate.json5` | `.github/workflows/` 配下の `uses:` は自動検出対象 |

## Architecture

### ディレクトリ構造（To-Be）

```
.github/
  workflows/
    codeql-analysis.yml     # 新規: CodeQL Reusable Workflow
    tagpr-release.yml       # 新規: Release Reusable Workflow
    auto-assign-pr.yml      # 新規: Auto Assign PR Reusable Workflow
    actions-lint.yml        # 新規: Actions Lint Reusable Workflow
    my-codeql.yml           # 既存: → codeql-analysis.yml を呼び出すラッパーに変換
    my-release.yml          # 既存: → tagpr-release.yml を呼び出すラッパーに変換
    my-setup-pr.yml         # 既存: → auto-assign-pr.yml を呼び出すラッパーに変換
    my-test.yml             # 既存: → actions-lint.yml を呼び出すラッパーに変換
  composite/                # 既存: 変更なし
    pnpm-setup/
    playwright-setup/
    slack-notify-success/
    slack-notify-failure/
README.md                   # 既存: Reusable Workflows セクション更新
```

### 全体アーキテクチャ

```mermaid
graph TD
    subgraph "External Repository (Caller)"
        EXT_PR[PR / push / etc.] -->|workflow_call| CALL[Reusable Workflow 呼び出し]
    end

    subgraph "kryota-dev/actions (Reusable Workflows)"
        CALL --> CODEQL[codeql-analysis.yml<br/>CodeQL セキュリティ解析]
        CALL --> RELEASE[tagpr-release.yml<br/>tagpr リリース管理 +<br/>メジャータグ更新]
        CALL --> ASSIGN[auto-assign-pr.yml<br/>PR assignee 自動設定]
        CALL --> LINT[actions-lint.yml<br/>actionlint / ls-lint /<br/>ghalint / zizmor]
    end

    subgraph "kryota-dev/actions (Internal CI — thin wrappers)"
        INT_TRIGGER[PR / push / merge_group] --> MY_CODEQL[my-codeql.yml]
        INT_TRIGGER --> MY_RELEASE[my-release.yml]
        INT_TRIGGER --> MY_SETUP_PR[my-setup-pr.yml]
        INT_TRIGGER --> MY_TEST[my-test.yml]

        MY_CODEQL -->|"uses: ./.github/workflows/<br/>codeql-analysis.yml"| CODEQL
        MY_RELEASE -->|"uses: ./.github/workflows/<br/>tagpr-release.yml"| RELEASE
        MY_SETUP_PR -->|"uses: ./.github/workflows/<br/>auto-assign-pr.yml"| ASSIGN
        MY_TEST -->|"uses: ./.github/workflows/<br/>actions-lint.yml"| LINT
    end

    subgraph "Quality Tools"
        LINT --> ACTIONLINT[actionlint<br/>構文チェック]
        LINT --> LSLINT[ls-lint<br/>命名規則チェック]
        LINT --> GHALINT_RUN[ghalint run<br/>Workflow セキュリティ]
        LINT --> GHALINT_ACTION[ghalint run-action<br/>Action セキュリティ]
        LINT --> ZIZMOR[zizmor<br/>静的セキュリティ分析]
    end
```

### Reusable Workflow のインターフェース設計方針

1. **入力の最小化**: `github` コンテキストが継承されるため、コンテキストから取得可能な値は入力パラメータにしない
2. **デフォルト値の提供**: 全ての任意入力にデフォルト値を設定し、最小構成での呼び出しを可能にする
3. **シークレットの明示的定義**: `secrets: inherit` は使用せず、必要なシークレットを `secrets:` で明示的に定義する
4. **出力の提供**: 後続処理に必要な値（リリースタグ等）は `outputs` で公開する

### 内部 CI ワークフロー（`my-*`）のラッパー設計方針

1. **薄いラッパー**: トリガー定義、concurrency 制御、パーミッション宣言のみを記述し、実際のロジックは Reusable Workflow に委譲する
2. **パーミッション境界の明示**: Reusable Workflow が必要とするパーミッションをジョブレベルで宣言する
3. **concurrency は呼び出し元で管理**: 実行制御は呼び出し元の関心事であるため、ラッパー側で定義する
4. **ローカル参照**: 同一リポジトリ内の参照は `uses: ./.github/workflows/xxx.yml` 形式を使用する

---

## Components and Interfaces

### Component 1: `codeql-analysis.yml` — CodeQL Reusable Workflow

- **Purpose:** CodeQL セキュリティスキャンを外部リポジトリから呼び出し可能にする
- **トリガー:** `workflow_call`

**インターフェース:**

| 種別 | 名前 | 型 | 必須 | デフォルト | 説明 |
|---|---|---|---|---|---|
| input | `languages` | string | No | `'["actions"]'` | スキャン対象言語の JSON 配列 |

**設計詳細:**

```yaml
name: CodeQL Analysis

on:
  workflow_call:
    inputs:
      languages:
        description: "JSON array of languages to analyze (e.g., '[\"javascript\", \"typescript\"]')"
        type: string
        required: false
        default: '["actions"]'

permissions: {}

jobs:
  analyze:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    permissions:
      actions: read
      contents: read
      security-events: write
    strategy:
      matrix:
        language: ${{ fromJSON(inputs.languages) }}
    steps:
      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6
        with:
          persist-credentials: false

      - uses: github/codeql-action/init@89a39a4e59826350b863aa6b6252a07ad50cf83e # v4.32.4
        with:
          languages: ${{ matrix.language }}

      - uses: github/codeql-action/analyze@89a39a4e59826350b863aa6b6252a07ad50cf83e # v4.32.4
```

- **Dependencies**: `actions/checkout`, `github/codeql-action/init`, `github/codeql-action/analyze`
- **呼び出し元の前提条件**: なし

**呼び出し例（外部リポジトリ）:**

```yaml
jobs:
  codeql:
    uses: kryota-dev/actions/.github/workflows/codeql-analysis.yml@v1

  codeql-js:
    uses: kryota-dev/actions/.github/workflows/codeql-analysis.yml@v1
    with:
      languages: '["javascript", "typescript"]'
```

---

### Component 2: `tagpr-release.yml` — Release Reusable Workflow

- **Purpose:** tagpr によるリリース管理とメジャータグ更新を外部リポジトリから呼び出し可能にする
- **トリガー:** `workflow_call`

**インターフェース:**

| 種別 | 名前 | 型 | 必須 | デフォルト | 説明 |
|---|---|---|---|---|---|
| secret | `app-token` | secret | Yes | - | tagpr 用 PAT（`repo` + `workflow` スコープ必要） |
| output | `tag` | string | - | - | tagpr が生成したバージョンタグ（リリースなしの場合は空文字列） |

**設計詳細:**

```yaml
name: tagpr Release

on:
  workflow_call:
    secrets:
      app-token:
        description: "Personal Access Token for tagpr (requires 'repo' and 'workflow' scopes)"
        required: true
    outputs:
      tag:
        description: "The version tag created by tagpr (empty if no release)"
        value: ${{ jobs.tagpr.outputs.tag }}

concurrency:
  group: ${{ github.workflow }}-release
  cancel-in-progress: false

permissions: {}

jobs:
  tagpr:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    permissions:
      contents: write
      pull-requests: write
    outputs:
      tag: ${{ steps.tagpr.outputs.tag }}
    steps:
      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6
        with:
          token: ${{ secrets.app-token }}
          persist-credentials: false

      - uses: Songmu/tagpr@da82ed6743aec90049892070edd5561335904a9e # v1.17.0
        id: tagpr
        env:
          GITHUB_TOKEN: ${{ secrets.app-token }}

  bump_major_tag:
    needs: tagpr
    if: needs.tagpr.outputs.tag != ''
    runs-on: ubuntu-latest
    timeout-minutes: 5
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6
        with:
          token: ${{ secrets.app-token }}
          persist-credentials: false

      - name: Update major tag
        env:
          TAG: ${{ needs.tagpr.outputs.tag }}
          GITHUB_TOKEN: ${{ secrets.app-token }}
          REPO: ${{ github.repository }}
        run: |
          git remote set-url origin "https://x-access-token:${GITHUB_TOKEN}@github.com/${REPO}.git"
          MAJOR="${TAG%%.*}"
          git tag -f "$MAJOR"
          git push origin "$MAJOR" --force
```

- **Dependencies**: `actions/checkout`, `Songmu/tagpr`
- **Secrets**: `app-token`（PAT: Branch Protection をバイパスするために `GITHUB_TOKEN` ではなく PAT が必要）
- **呼び出し元の前提条件**: `.tagpr` 設定ファイルが存在すること、`APP_TOKEN` シークレットが設定されていること

**concurrency 設計:**

- `group: ${{ github.workflow }}-release` — 呼び出し元ワークフロー名 + `-release` サフィックスでグループ化
- `cancel-in-progress: false` — リリース処理は中断せず完了を待つ
- Reusable Workflow の concurrency は呼び出し元とは独立してスコープされるため、呼び出し元の他のジョブに影響しない

**呼び出し例（外部リポジトリ）:**

```yaml
jobs:
  release:
    uses: kryota-dev/actions/.github/workflows/tagpr-release.yml@v1
    secrets:
      app-token: ${{ secrets.APP_TOKEN }}
```

---

### Component 3: `auto-assign-pr.yml` — Auto Assign PR Reusable Workflow

- **Purpose:** PR 作成時に作成者を自動的に assignee に設定する処理を外部リポジトリから呼び出し可能にする
- **トリガー:** `workflow_call`

**インターフェース:**

| 種別 | 名前 | 型 | 必須 | デフォルト | 説明 |
|---|---|---|---|---|---|
| (なし) | - | - | - | - | `github` コンテキストから全ての情報を取得 |

**設計詳細:**

```yaml
name: Auto Assign PR

on:
  workflow_call: {}

permissions: {}

jobs:
  add_assignee:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    permissions:
      pull-requests: write
    steps:
      - name: Add assignee
        run: gh pr edit "$PR_URL" --add-assignee "$ACTOR"
        env:
          GH_TOKEN: ${{ github.token }}
          PR_URL: ${{ github.event.pull_request.html_url }}
          ACTOR: ${{ github.actor }}
```

- **Dependencies**: GitHub CLI（`ubuntu-latest` にプリインストール、`checkout` 不要）
- **呼び出し元の前提条件**: `pull_request: types: [opened]` でトリガーされること（`github.event.pull_request` が存在する必要がある）

**呼び出し例（外部リポジトリ）:**

```yaml
on:
  pull_request:
    types: [opened]

jobs:
  auto-assign:
    uses: kryota-dev/actions/.github/workflows/auto-assign-pr.yml@v1
```

---

### Component 4: `actions-lint.yml` — Actions Lint Reusable Workflow

- **Purpose:** GitHub Actions ワークフローの品質ゲート（actionlint / ls-lint / ghalint / zizmor）を外部リポジトリから呼び出し可能にする
- **トリガー:** `workflow_call`

**インターフェース:**

| 種別 | 名前 | 型 | 必須 | デフォルト | 説明 |
|---|---|---|---|---|---|
| input | `aqua-version` | string | No | `v2.56.6` | aqua のバージョン |
| input | `reviewdog-reporter` | string | No | `github-pr-review` | reviewdog のレポーター種別 |

**設計詳細:**

```yaml
name: Actions Lint

on:
  workflow_call:
    inputs:
      aqua-version:
        description: "Version of aqua to install for ghalint"
        type: string
        required: false
        default: "v2.56.6"
      reviewdog-reporter:
        description: "Reporter type for reviewdog/actionlint (github-pr-review, github-check, etc.)"
        type: string
        required: false
        default: "github-pr-review"

permissions: {}

jobs:
  lint:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6
        with:
          persist-credentials: false

      - uses: reviewdog/action-actionlint@0d952c597ef8459f634d7145b0b044a9699e5e43 # v1.71.0
        with:
          reporter: ${{ inputs.reviewdog-reporter }}

      - uses: ls-lint/action@02e380fe8733d499cbfc9e22276de5085508a5bd # v2.3.1

      - uses: aquaproj/aqua-installer@11dd79b4e498d471a9385aa9fb7f62bb5f52a73c # v4.0.4
        with:
          aqua_version: ${{ inputs.aqua-version }}

      - run: echo "${AQUA_ROOT_DIR:-${HOME}/.local/share/aquaproj-aqua}/bin" >> "$GITHUB_PATH"
        shell: bash

      - name: Run ghalint
        run: ghalint run
        shell: bash

      - name: Run ghalint run-action
        run: ghalint run-action
        shell: bash

      - uses: astral-sh/setup-uv@eac588ad8def6316056a12d4907a9d4d84ff7a3b # v7.3.0

      - name: Run zizmor
        run: uvx zizmor --format=github .
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

- **Dependencies**: `actions/checkout`, `reviewdog/action-actionlint`, `ls-lint/action`, `aquaproj/aqua-installer`, `astral-sh/setup-uv`
- **呼び出し元の前提条件:**
  - `.ls-lint.yml` が存在すること（ls-lint の設定）
  - `aqua.yaml` が存在し、`ghalint` が定義されていること（ghalint のインストール）
  - `.github/workflows/` にワークフローファイルが存在すること（actionlint / ghalint の検証対象）

**呼び出し例（外部リポジトリ）:**

```yaml
jobs:
  lint:
    uses: kryota-dev/actions/.github/workflows/actions-lint.yml@v1

  lint-custom:
    uses: kryota-dev/actions/.github/workflows/actions-lint.yml@v1
    with:
      aqua-version: "v2.60.0"
      reviewdog-reporter: "github-check"
```

---

### Component 5: 内部 CI ワークフロー（`my-*`）のラッパー化

既存の4つの内部 CI ワークフローを Reusable Workflow を呼び出す薄いラッパーにリファクタリングする。これによりロジックの重複を排除する。

#### `my-codeql.yml`（リファクタリング後）

```yaml
name: codeql
on:
  push:
    branches: [main]
  pull_request:
  merge_group:

permissions: {}

jobs:
  analyze:
    permissions:
      actions: read
      contents: read
      security-events: write
    uses: ./.github/workflows/codeql-analysis.yml
```

- トリガー定義とパーミッション宣言のみ
- デフォルト言語（`actions`）で実行

#### `my-release.yml`（リファクタリング後）

```yaml
name: release
on:
  push:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}
  cancel-in-progress: false

permissions: {}

jobs:
  release:
    permissions:
      contents: write
      pull-requests: write
    uses: ./.github/workflows/tagpr-release.yml
    secrets:
      app-token: ${{ secrets.APP_TOKEN }}
```

- concurrency 制御は呼び出し元で管理（Reusable Workflow 側にも安全装置として存在）
- `APP_TOKEN` シークレットを明示的に渡す
- `permissions` はジョブレベルで宣言（Reusable Workflow 内のジョブが必要とするパーミッションの上限を設定）

#### `my-setup-pr.yml`（リファクタリング後）

```yaml
name: setup_pr
on:
  pull_request:
    types: [opened]

permissions: {}

jobs:
  auto-assign:
    permissions:
      pull-requests: write
    uses: ./.github/workflows/auto-assign-pr.yml
```

#### `my-test.yml`（リファクタリング後）

```yaml
name: test
on:
  pull_request:
  merge_group:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions: {}

jobs:
  lint:
    permissions:
      contents: read
      pull-requests: write
    uses: ./.github/workflows/actions-lint.yml
```

- concurrency 制御は呼び出し元で管理（同一 PR 上の古い実行をキャンセル）
- デフォルトパラメータで実行

---

### Component 6: `README.md` の更新

- **Purpose:** Reusable Workflows セクションの "Coming soon." を実際のワークフロー一覧に置き換える
- **変更箇所:** `## Available Workflows` → `### Reusable Workflows` セクション

**更新後の構造:**

各 Reusable Workflow について以下を記載:
- ワークフロー名と説明
- 入力パラメータ / シークレット / 出力のテーブル
- 前提条件（該当する場合）
- 呼び出し例（YAML コードブロック）

## Data Models

### Reusable Workflow のインターフェースマトリクス

| ワークフロー | inputs | secrets | outputs |
|---|---|---|---|
| `codeql-analysis.yml` | `languages` (任意) | なし | なし |
| `tagpr-release.yml` | なし | `app-token` (必須) | `tag` |
| `auto-assign-pr.yml` | なし | なし | なし |
| `actions-lint.yml` | `aqua-version` (任意), `reviewdog-reporter` (任意) | なし | なし |

### 呼び出し元の前提条件マトリクス

| ワークフロー | 必須設定ファイル | 必須シークレット | 推奨トリガー |
|---|---|---|---|
| `codeql-analysis.yml` | なし | なし | `push` (main), `pull_request`, `merge_group` |
| `tagpr-release.yml` | `.tagpr` | `APP_TOKEN` | `push` (main) |
| `auto-assign-pr.yml` | なし | なし | `pull_request: types: [opened]` |
| `actions-lint.yml` | `.ls-lint.yml`, `aqua.yaml` (ghalint 定義含む) | なし | `pull_request`, `merge_group` |

### 内部 CI ワークフロー → Reusable Workflow 対応表

| 内部 CI | 呼び出す Reusable Workflow | 渡すパーミッション | 渡すシークレット |
|---|---|---|---|
| `my-codeql.yml` | `codeql-analysis.yml` | `actions: read`, `contents: read`, `security-events: write` | なし |
| `my-release.yml` | `tagpr-release.yml` | `contents: write`, `pull-requests: write` | `app-token: ${{ secrets.APP_TOKEN }}` |
| `my-setup-pr.yml` | `auto-assign-pr.yml` | `pull-requests: write` | なし |
| `my-test.yml` | `actions-lint.yml` | `contents: read`, `pull-requests: write` | なし |

## Error Handling

### Error Scenarios

1. **呼び出し元のトリガーと Reusable Workflow の不整合**
   - **Handling:** `auto-assign-pr.yml` を `pull_request` 以外のトリガーから呼び出すと、`github.event.pull_request` が存在せず失敗する
   - **User Impact:** ワークフロー実行が失敗し、エラーログに null reference が表示される
   - **対処:** README に推奨トリガーを明記し、利用者の設定ミスを防止する

2. **tagpr-release.yml の `app-token` シークレット未設定**
   - **Handling:** tagpr が認証エラーで失敗する
   - **User Impact:** リリースジョブが失敗し、PR 作成やタグ付けができない
   - **対処:** `required: true` を設定し、呼び出し時にシークレット未指定で即エラーにする

3. **actions-lint.yml の呼び出し元に `aqua.yaml` が存在しない場合**
   - **Handling:** `aqua-installer` は正常に動作するが、ghalint がインストールされず `ghalint run` でコマンド未発見エラーになる
   - **User Impact:** lint ジョブが失敗する
   - **対処:** README に前提条件を明記する

4. **actions-lint.yml の呼び出し元に `.ls-lint.yml` が存在しない場合**
   - **Handling:** ls-lint が設定ファイル未発見で失敗する
   - **User Impact:** lint ジョブが失敗する
   - **対処:** README に前提条件を明記する

5. **内部 CI ラッパーのパーミッション不足**
   - **Handling:** ラッパーのジョブレベル `permissions` が Reusable Workflow の要求を下回ると、Reusable Workflow 内で権限エラーが発生する
   - **User Impact:** CI が失敗する
   - **対処:** 本設計書の「内部 CI ワークフロー → Reusable Workflow 対応表」に従いパーミッションを設定する

6. **SHA ピン留め違反（Renovate 更新前）**
   - **Handling:** ghalint / zizmor が CI でエラーを報告する
   - **User Impact:** Reusable Workflow 自体の CI が失敗する
   - **対処:** 全ての `uses:` を既存の内部 CI と同一の SHA で記述する。Renovate が自動で更新を管理する

## Testing Strategy

### CI による自動検証（主要テスト手段）

Reusable Workflow ファイル自体は `.github/workflows/` 配下に配置されるため、`my-test.yml`（→ `actions-lint.yml`）CI パイプラインが自動的に以下を検証する:

| ツール | 検証内容 |
|---|---|
| actionlint | Reusable Workflow の構文チェック（`workflow_call` トリガーをサポート） |
| ls-lint | ファイル名が kebab-case であること |
| ghalint run | `uses:` が full commit SHA でピン留めされていること、`permissions` が適切であること |
| zizmor | テンプレートインジェクション等のセキュリティ問題がないこと |

### 内部 CI のセルフテスト

リファクタリング後の `my-*` ワークフローは、PR 作成時に自動実行される。これにより、Reusable Workflow の呼び出しが正常に機能することを PR マージ前に自動検証できる。

### 手動検証項目

1. **各 Reusable Workflow の外部呼び出しテスト**
   - 別リポジトリから各 Reusable Workflow を `workflow_call` で呼び出し、正常に動作することを確認

2. **`tagpr-release.yml` の concurrency 検証**
   - 同時に複数のプッシュが発生した場合に、リリース処理が競合しないことを確認

3. **`auto-assign-pr.yml` の github コンテキスト継承検証**
   - 呼び出し元の `pull_request` イベントから `github.event.pull_request.html_url` と `github.actor` が正しく取得できることを確認

4. **Renovate の自動更新確認**
   - 新しい Reusable Workflow ファイル内の `uses:` が Renovate の更新対象として認識されることを確認
