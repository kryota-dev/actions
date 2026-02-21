# Requirements Document

## Introduction

本ドキュメントは、`kryota-dev/actions` リポジトリに **Composite Actions の実装** を追加するための要件を定義する。

**As-Is（現状）:**
- `.github/composite/` ディレクトリが作成済みで、Composite Actions を配置するための基盤が整備されている
- ls-lint による命名規則チェック、ghalint run-action によるセキュリティポリシー検証、zizmor による静的セキュリティ分析が CI 上で稼働中
- 現時点では `.github/composite/` 配下には `.gitkeep` のみが存在し、実際の Composite Actions は存在しない

**To-Be（目標）:**
- 以下の Composite Actions を `.github/composite/` 配下に実装する:
  1. **pnpm-setup**: Node.js と pnpm のセットアップ（依存関係インストール含む）
  2. **playwright-setup**: Playwright ブラウザのキャッシュ付きセットアップ
  3. **slack-notify-success**: ワークフロー成功時の Slack 通知（Bot OAuth Token 経由）
  4. **slack-notify-failure**: ワークフロー失敗時の Slack 通知（Incoming Webhook 経由）
- 各 Composite Action に対応した使用方法のドキュメントを README に追記する

**スコープの明確化:**
- 対象: 上記 4 つの Composite Actions の実装と README 更新
- 対象外: 基盤設定（ls-lint、ghalint、zizmor の設定変更）、Reusable Workflows の変更

## Alignment with Product Vision

本リポジトリの目的は「再利用可能な GitHub Actions を一元管理・公開し、各リポジトリの CI/CD 設定の重複を排除する」ことである。本実装は以下の価値を提供する:

- **CI/CD 設定の重複排除**: pnpm・Playwright のセットアップ手順を各リポジトリで重複定義する必要がなくなる
- **Slack 通知の標準化**: 成功/失敗の通知フォーマットを組織全体で統一できる
- **セキュリティの一元管理**: SHA ピン留めや env 経由の入力値渡し等のセキュリティプラクティスを Composite Actions 内に閉じ込め、利用者が意識せずに安全な実装を享受できる

---

## Requirements

### Requirement 1: pnpm-setup Composite Action の実装

**User Story:** As a 利用者リポジトリの開発者, I want `pnpm-setup` Composite Action を `steps:` から呼び出したい, so that Node.js と pnpm のセットアップ・依存関係インストールを数行で完結できる

**概要:**
- `.node-version` ファイルに記載されたバージョンで Node.js をセットアップする
- pnpm のストアキャッシュを利用して `pnpm install` を高速化する
- 入力なし（`package.json` / `.node-version` / `pnpm-lock.yaml` はリポジトリルートに存在する前提）

#### Acceptance Criteria

1. WHEN `pnpm-setup` Action が呼び出されるとき THEN Action SHALL `pnpm/action-setup` を使用して pnpm をインストールする
2. WHEN `pnpm-setup` Action が呼び出されるとき THEN Action SHALL `actions/setup-node` を使用してリポジトリルートの `.node-version` ファイルに記載されたバージョンの Node.js をインストールし、pnpm キャッシュを有効化する
3. WHEN `pnpm-setup` Action が呼び出されるとき THEN Action SHALL `actions/cache` を使用して pnpm ストアをキャッシュし、`pnpm-lock.yaml` のハッシュをキャッシュキーに含める
4. WHEN `pnpm-setup` Action が呼び出されるとき THEN Action SHALL `pnpm install` を実行して依存関係をインストールする
5. WHEN `action.yml` 内に `uses:` ステップが存在する THEN 全ての `uses:` は full commit SHA（40文字）でピン留めされ、コメントにタグ名を記載する
6. IF `run` ステップが存在する THEN そのステップには `shell: bash` フィールドを必ず明記する

---

### Requirement 2: playwright-setup Composite Action の実装

**User Story:** As a 利用者リポジトリの開発者, I want `playwright-setup` Composite Action を `steps:` から呼び出したい, so that Playwright ブラウザをキャッシュ付きでインストールでき、CI の実行時間を短縮できる

**概要:**
- `pnpm exec playwright --version` でインストール済みの Playwright バージョンを取得する
- Playwright のブラウザキャッシュを Playwright バージョンとランナー OS をキーに管理する
- キャッシュヒット時はブラウザのダウンロードをスキップし、ミス時にインストールを実行する

**前提条件:**
- 本 Action の呼び出し前に `pnpm-setup` Action（または同等のセットアップ）が完了していること

#### Acceptance Criteria

1. WHEN `playwright-setup` Action が呼び出されるとき THEN Action SHALL `pnpm exec playwright --version` でバージョンを取得し、ステップ出力（`$GITHUB_OUTPUT`）に `version` として書き出す
2. WHEN `playwright-setup` Action が呼び出されるとき THEN Action SHALL `actions/cache` を使用して `~/.cache/ms-playwright` をキャッシュし、キャッシュキーには `{runner.os}-playwright-{playwright-version}` を使用する
3. WHEN キャッシュが存在しないとき THEN Action SHALL `pnpm exec playwright install --with-deps` を実行して Playwright ブラウザをインストールする
4. WHEN キャッシュが存在するとき THEN Action SHALL ブラウザのダウンロードをスキップする（`actions/cache` の標準動作に委ねる）
5. WHEN `action.yml` 内に `uses:` ステップが存在する THEN 全ての `uses:` は full commit SHA（40文字）でピン留めされ、コメントにタグ名を記載する
6. IF `run` ステップが存在する THEN そのステップには `shell: bash` フィールドを必ず明記する

---

### Requirement 3: slack-notify-success Composite Action の実装

**User Story:** As a 利用者リポジトリの開発者, I want ワークフロー成功時に `slack-notify-success` Composite Action を呼び出したい, so that Slack の特定チャンネルに成功通知（緑色）を投稿できる

**概要:**
- Slack の `chat.postMessage` API（Bot OAuth Token 認証）を使用してメッセージを投稿する
- `attachments` 形式を使用し、カラーバー付きのリッチメッセージを送信する
- スレッドへの返信（`thread_ts`）もサポートする

**インターフェース（inputs）:**

| 入力名 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|
| `channel-id` | 必須 | - | Slack チャンネル ID |
| `bot-oauth-token` | 必須 | - | Slack Bot OAuth Token |
| `color` | 任意 | `good` | メッセージのカラーバー色 |
| `mention-user` | 任意 | `''` | メンション対象ユーザー（空の場合はメンションなし） |
| `title` | 任意 | `'workflow execution completed'` | メッセージタイトル |
| `message` | 任意 | 実行ログ URL | メッセージ本文 |
| `thread-ts` | 任意 | `'null'` | スレッド返信先の timestamp |
| `reply-broadcast` | 任意 | `'false'` | スレッド返信をチャンネルにもブロードキャストするか |

**メッセージ形式:**
- `mention-user` が指定された場合: `*SUCCESS - {mention-user} {title}*`
- `mention-user` が空の場合: `*SUCCESS - {title}*`
- `author_name` にはリポジトリ名（オーナー名なし）を表示する
- `author_link` にはリポジトリの URL を設定する

#### Acceptance Criteria

1. WHEN `slack-notify-success` Action が呼び出されるとき THEN Action SHALL Slack の `chat.postMessage` API へ `curl` でリクエストを送信する
2. WHEN `inputs.channel-id` および `inputs.bot-oauth-token` が提供されるとき THEN Action SHALL これらの値を `env:` 経由で環境変数として `run` ステップに渡す（`${{ inputs.xxx }}` を直接 `run:` に埋め込まない）
3. WHEN `inputs.mention-user` が空でないとき THEN Action SHALL タイトルに `{mention-user}` を含めて Slack に投稿する
4. WHEN `inputs.thread-ts` が `'null'` 以外のとき THEN Action SHALL `thread_ts` フィールドを JSON ペイロードに含めてスレッドに返信する
5. WHEN `curl` リクエストが失敗したとき THEN Action SHALL `echo "::error::Failed to post message to Slack"` を出力し、ステップを失敗させる（`exit 1`）
6. WHEN `runner.debug` が `1` のとき THEN Action SHALL `set -x` でデバッグ出力を有効化する
7. WHEN `inputs.message` が指定されない場合 THEN Action SHALL デフォルト値として GitHub Actions の実行ログ URL（`${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}`）を使用する

---

### Requirement 4: slack-notify-failure Composite Action の実装

**User Story:** As a 利用者リポジトリの開発者, I want ワークフロー失敗時に `slack-notify-failure` Composite Action を呼び出したい, so that Slack の特定チャンネルに失敗通知（赤色）を投稿できる

**概要:**
- Slack の Incoming Webhook URL を使用してメッセージを投稿する（Bot OAuth Token ではなく Webhook URL 方式）
- `attachments` 形式を使用し、カラーバー付きのリッチメッセージを送信する
- `slack-notify-success` との設計の違い: チャンネル指定が不要（Webhook URL に埋め込まれているため）、Bot OAuth Token の代わりに Webhook URL を使用する

**インターフェース（inputs）:**

| 入力名 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|
| `webhook-url` | 必須 | - | Slack Incoming Webhook URL |
| `color` | 任意 | `danger` | メッセージのカラーバー色 |
| `mention-user` | 任意 | `''` | メンション対象ユーザー（空の場合はメンションなし） |
| `title` | 任意 | `'workflow failed'` | メッセージタイトル |
| `message` | 任意 | 実行ログ URL | メッセージ本文 |

**メッセージ形式:**
- `mention-user` が指定された場合: `*FAILURE - {mention-user} {title}*`
- `mention-user` が空の場合: `*FAILURE - {title}*`
- `author_name` にはリポジトリ名（オーナー名なし）を表示する
- `author_link` にはリポジトリの URL を設定する

#### Acceptance Criteria

1. WHEN `slack-notify-failure` Action が呼び出されるとき THEN Action SHALL Slack の Incoming Webhook URL へ `curl` でリクエストを送信する
2. WHEN `inputs.webhook-url` が提供されるとき THEN Action SHALL その値を `env:` 経由で環境変数として `run` ステップに渡す（`${{ inputs.webhook-url }}` を直接 `run:` に埋め込まない）
3. WHEN `inputs.mention-user` が空でないとき THEN Action SHALL タイトルに `{mention-user}` を含めて Slack に投稿する
4. WHEN `curl` リクエストが失敗したとき THEN Action SHALL `echo "::error::Failed to post message to Slack"` を出力し、ステップを失敗させる（`exit 1`）
5. WHEN `runner.debug` が `1` のとき THEN Action SHALL `set -x` でデバッグ出力を有効化する
6. WHEN `inputs.message` が指定されない場合 THEN Action SHALL デフォルト値として GitHub Actions の実行ログ URL（`${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}`）を使用する
7. IF `slack-notify-success` は `chat.postMessage` API を使用するとき THEN `slack-notify-failure` は Incoming Webhook URL を使用する（認証方式・チャンネル指定の違いを反映する）

---

### Requirement 5: 各 Composite Action の CI 通過

**User Story:** As a リポジトリ管理者, I want 追加した Composite Actions が CI パイプラインの全チェックを通過したい, so that コード品質とセキュリティポリシーへの準拠を保証できる

#### Acceptance Criteria

1. WHEN PR が作成・更新されるとき THEN CI SHALL ls-lint が `.github/composite/` 配下の全ディレクトリ名・ファイル名チェックを通過する
2. WHEN PR が作成・更新されるとき THEN CI SHALL `ghalint run-action` が全 `action.yml` の `uses:` に対して SHA ピン留め検証を通過する
3. WHEN PR が作成・更新されるとき THEN CI SHALL zizmor が全 `action.yml` のセキュリティ静的解析を通過する
4. IF `action.yml` 内に `${{ inputs.xxx }}` を直接 `run:` ステップに埋め込む場合 THEN zizmor SHALL テンプレートインジェクション警告を報告するためこの実装を禁止する
5. WHEN `action.yml` 内に `uses:` が存在する THEN ghalint SHALL ミュータブルタグ（例: `@v4`）を検出してエラーを報告するため、全 `uses:` は SHA ピン留めにする

---

### Requirement 6: README への使用方法の追記

**User Story:** As a 利用者リポジトリの開発者, I want README から各 Composite Action の入力パラメータと使用例を参照したい, so that 実装の詳細を `action.yml` まで確認せずに利用を開始できる

#### Acceptance Criteria

1. WHEN `README.md` を更新するとき THEN `### Composite Actions` セクションに各 Action の使用例（YAML スニペット）を追加する
2. WHEN 各 Action のセクションを追加するとき THEN 必須 inputs と任意 inputs の一覧を Markdown テーブルで示す
3. WHEN `pnpm-setup` のセクションが追加されるとき THEN 入力パラメータなしの最小構成での呼び出し例を含める
4. WHEN `playwright-setup` のセクションが追加されるとき THEN `pnpm-setup` が前提条件である旨を明記する
5. WHEN `slack-notify-success` と `slack-notify-failure` のセクションが追加されるとき THEN 両者の認証方式の違い（Bot OAuth Token vs Incoming Webhook URL）を明記する
6. WHEN 使用例の YAML スニペットを記載するとき THEN `{action-name}@v1` 形式のバージョン指定を使用する（SHA 指定ではなくタグ指定での例示）

---

## Non-Functional Requirements

### Code Architecture and Modularity

- **Single Responsibility Principle**: 各 Composite Action は単一の目的に特化し、複数の責務を持たせない
  - `pnpm-setup`: Node.js・pnpm のセットアップのみ
  - `playwright-setup`: Playwright ブラウザのキャッシュ付きインストールのみ
  - `slack-notify-success`: 成功通知（Bot OAuth Token 方式）のみ
  - `slack-notify-failure`: 失敗通知（Incoming Webhook 方式）のみ
- **Modular Design**: 各 Action のディレクトリを分離し、`pnpm-setup` と `playwright-setup` は組み合わせて使用できる設計とする
- **Clear Interfaces**: 全 `action.yml` に `name`・`description`・`inputs`（必須/任意、説明、デフォルト値）を明示的に定義する

### Performance

- `pnpm-setup` はキャッシュにより2回目以降の `pnpm install` を高速化する
- `playwright-setup` はブラウザキャッシュにより CI の Playwright インストール時間を削減する
- 不必要な追加ステップを避け、最小限の実装に留める

### Security

- 全 `action.yml` 内の `uses:` は **full commit SHA（40文字）でピン留め**し、コメントにタグ名を記載する（例: `uses: actions/checkout@{SHA} # v4`）
- `inputs` の値を `run` ステップに直接埋め込まず、**`env:` 経由で環境変数として渡す**（テンプレートインジェクション対策）
- `action.yml` にシークレット・トークン・Webhook URL をハードコードしない
- Slack の Bot OAuth Token および Incoming Webhook URL は必ず呼び出し元の `inputs:` 経由で受け取る
- Composite Actions は `secrets:` フィールドをサポートしないため、機密情報は `inputs:` で受け取る設計とする

### Reliability

- `curl` コマンドには `--max-time 30` タイムアウトを設定し、Slack API が応答しない場合に CI がハングしないようにする
- `curl` 失敗時は明示的にエラーメッセージを出力して非ゼロ終了コードで失敗させる
- `pnpm exec playwright --version` の出力から `sed` でバージョン番号のみを抽出し、予期しないフォーマット変化による問題を最小化する

### Usability

- ディレクトリ名は kebab-case で命名し、Action の目的が直感的に分かるようにする（`pnpm-setup`, `playwright-setup`, `slack-notify-success`, `slack-notify-failure`）
- 各 `action.yml` には `name` と `description` を必ず記載し、GitHub UI での視認性を確保する
- `inputs` の `description` には利用者が値を把握できる十分な説明を含める

---

## Out of Scope

以下は今回のスコープ外とする:

- 基盤設定（`.ls-lint.yml`、`my-test.yml` の `ghalint run-action` ステップ、`.github/composite/` ディレクトリ）の変更（既に完了済み）
- Reusable Workflows の新規追加・変更
- pnpm-setup・playwright-setup 以外のパッケージマネージャーやテストフレームワークへの対応
- Slack 以外の通知サービスへの対応
- Docker Action や JavaScript Action のサポート（Composite Actions のみ対象）
- `slack-notify-success` と `slack-notify-failure` のインターフェース統一（認証方式の違いを尊重し、あえて統一しない）
