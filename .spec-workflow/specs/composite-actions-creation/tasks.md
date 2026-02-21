# Tasks Document

## Phase 1: pnpm-setup Composite Action の実装

- [x] 1. `.github/composite/pnpm-setup/action.yml` を作成する
  - File: `.github/composite/pnpm-setup/action.yml`
  - Node.js・pnpm のセットアップ、pnpm ストアキャッシュ、依存関係インストールを一括実行する Composite Action を実装する
  - Purpose: 利用者リポジトリが `steps:` から1行で pnpm 環境を構築できるようにする
  - _Leverage: `.github/composite/.gitkeep`（ディレクトリ構造の確認）、`composite-actions-support` spec の design.md（ディレクトリ規約）_
  - _Requirements: 1, 5_
  - _Prompt: Role: GitHub Actions エンジニア | Task: `.github/composite/pnpm-setup/action.yml` を以下の完全な YAML 内容で作成してください。ファイルが存在しない場合は新規作成し、`.github/composite/` ディレクトリに配置します。

    ```yaml
    name: Setup pnpm
    description: Setup Node.js and pnpm, and install dependencies

    runs:
      using: 'composite'
      steps:
        - uses: pnpm/action-setup@a7487c7e89a18df4991f7f222e4898a00d66ddda # v4.1.0
          name: Install pnpm
          with:
            package_json_file: package.json
            run_install: false

        - name: Install Node.js
          uses: actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020 # v4.4.0
          with:
            node-version-file: .node-version
            cache: 'pnpm'

        - name: Get pnpm store directory
          shell: bash
          run: |
            echo "STORE_PATH=$(pnpm store path --silent)" >> "$GITHUB_ENV"

        - uses: actions/cache@5a3ec84eff668545956fd18022155c47e93e2684 # v4.2.3
          name: Setup pnpm cache
          with:
            path: ${{ env.STORE_PATH }}
            key: ${{ runner.os }}-pnpm-store-${{ hashFiles('**/pnpm-lock.yaml') }}
            restore-keys: |
              ${{ runner.os }}-pnpm-store-

        - name: Install dependencies
          shell: bash
          run: pnpm install
    ```

    注意事項:
    - `uses:` は全て full commit SHA（40文字）でピン留め済み（変更しないこと）
    - `run` ステップには `shell: bash` を必ず明記すること
    - `inputs:` フィールドはなし（入力なし設計）
    - ファイル名は `action.yml`（`action.yaml` は不可）_

---

## Phase 2: playwright-setup Composite Action の実装

- [x] 2. `.github/composite/playwright-setup/action.yml` を作成する
  - File: `.github/composite/playwright-setup/action.yml`
  - Playwright ブラウザをキャッシュ付きでインストールする Composite Action を実装する
  - Purpose: 利用者リポジトリが CI の Playwright ブラウザインストール時間を短縮できるようにする
  - _Leverage: `composite-actions-support` spec の design.md（セキュリティポリシー）_
  - _Requirements: 2, 5_
  - _Prompt: Role: GitHub Actions エンジニア | Task: `.github/composite/playwright-setup/action.yml` を以下の完全な YAML 内容で作成してください。`pnpm-setup` Action（または同等のセットアップ）が前提条件です。

    ```yaml
    name: Setup Playwright
    description: Setup Playwright browsers with caching

    runs:
      using: 'composite'
      steps:
        - name: Get Playwright version
          id: playwright-version
          shell: bash
          run: |
            PLAYWRIGHT_VERSION=$(pnpm exec playwright --version | sed 's/Version //')
            echo "version=$PLAYWRIGHT_VERSION" >> "$GITHUB_OUTPUT"

        - name: Cache Playwright browsers
          id: cache-playwright
          uses: actions/cache@5a3ec84eff668545956fd18022155c47e93e2684 # v4.2.3
          with:
            path: ~/.cache/ms-playwright
            key: ${{ runner.os }}-playwright-${{ steps.playwright-version.outputs.version }}

        - name: Install Playwright browsers
          if: steps.cache-playwright.outputs.cache-hit != 'true'
          shell: bash
          run: pnpm exec playwright install --with-deps
    ```

    注意事項:
    - `uses:` は full commit SHA（40文字）でピン留め済み（変更しないこと）
    - `run` ステップには `shell: bash` を必ず明記すること
    - `if: steps.cache-playwright.outputs.cache-hit != 'true'` によりキャッシュヒット時はインストールをスキップする（明示的な条件指定）
    - `inputs:` フィールドはなし（入力なし設計）_

---

## Phase 3: slack-notify-success Composite Action の実装

- [x] 3. `.github/composite/slack-notify-success/action.yml` を作成する
  - File: `.github/composite/slack-notify-success/action.yml`
  - ワークフロー成功時に Slack の `chat.postMessage` API へ通知する Composite Action を実装する
  - Purpose: 利用者リポジトリが成功通知を標準フォーマットで Slack に投稿できるようにする
  - _Leverage: `composite-actions-support` spec の design.md（セキュリティポリシー：env 経由の入力値渡し）_
  - _Requirements: 3, 5_
  - _Prompt: Role: GitHub Actions エンジニア | Task: `.github/composite/slack-notify-success/action.yml` を以下の完全な YAML 内容で作成してください。

    ```yaml
    name: Post Message to Slack - Success
    description: Post a message to Slack when the workflow succeeds

    inputs:
      channel-id:
        description: Slack Channel ID
        required: true
      bot-oauth-token:
        description: Slack Bot OAuth Token
        required: true
      color:
        description: Color of the message
        required: false
        default: good
      mention-user:
        description: Mention user
        required: false
        default: ''
      title:
        description: Message title
        required: false
        default: 'workflow execution completed'
      message:
        description: Message body
        required: false
        default: 'Execution log: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}'
      thread-ts:
        description: Thread timestamp for reply
        required: false
        default: 'null'
      reply-broadcast:
        description: Whether to broadcast the reply to the channel
        required: false
        default: 'false'

    runs:
      using: 'composite'
      steps:
        - id: post-message-success
          shell: bash
          env:
            SLACK_CHANNEL_ID: ${{ inputs.channel-id }}
            SLACK_BOT_OAUTH_TOKEN: ${{ inputs.bot-oauth-token }}
            SLACK_COLOR: ${{ inputs.color }}
            SLACK_MENTION_USER: ${{ inputs.mention-user }}
            SLACK_TITLE_TEXT: ${{ inputs.title }}
            SLACK_MESSAGE: ${{ inputs.message }}
            SLACK_THREAD_TS: ${{ inputs.thread-ts }}
            SLACK_REPLY_BROADCAST: ${{ inputs.reply-broadcast }}
            RUNNER_DEBUG: ${{ runner.debug }}
          run: |
            if [ "${RUNNER_DEBUG}" == "1" ]; then
              set -x
            fi
            if [ -n "${SLACK_MENTION_USER}" ]; then
              SLACK_TITLE="*SUCCESS - ${SLACK_MENTION_USER} ${SLACK_TITLE_TEXT}*"
            else
              SLACK_TITLE="*SUCCESS - ${SLACK_TITLE_TEXT}*"
            fi
            REPO_NAME="${GITHUB_REPOSITORY#${GITHUB_REPOSITORY_OWNER}/}"
            REPO_URL="${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}"
            SLACK_DATA=$(jq -n \
              --arg channel "${SLACK_CHANNEL_ID}" \
              --arg color "${SLACK_COLOR}" \
              --arg title "${SLACK_TITLE}" \
              --arg author_name "${REPO_NAME}" \
              --arg author_link "${REPO_URL}" \
              --arg text "${SLACK_MESSAGE}" \
              --arg thread_ts "${SLACK_THREAD_TS}" \
              --argjson reply_broadcast "${SLACK_REPLY_BROADCAST}" \
              'def base:
                {
                  channel: $channel,
                  attachments: [{
                    fallback: $title,
                    pretext: $title,
                    color: $color,
                    author_name: $author_name,
                    author_link: $author_link,
                    text: $text
                  }]
                };
              if $thread_ts != "null" then
                base + {thread_ts: $thread_ts, reply_broadcast: $reply_broadcast}
              else
                base
              end')
            RESPONSE=$(curl --max-time 30 -sS -X POST \
              -H "Content-Type: application/json" \
              -H "Authorization: Bearer ${SLACK_BOT_OAUTH_TOKEN}" \
              -d "${SLACK_DATA}" \
              "https://slack.com/api/chat.postMessage") \
              || { echo "::error::Failed to post message to Slack (network error)"; exit 1; }
            if echo "${RESPONSE}" | grep -q '"ok":false'; then
              echo "::error::Slack API returned error: ${RESPONSE}"
              exit 1
            fi
    ```

    注意事項:
    - `${{ inputs.xxx }}` を `run:` に直接埋め込まず、全て `env:` 経由で渡すこと（テンプレートインジェクション対策）
    - `runner.debug` も `RUNNER_DEBUG` として `env:` 経由で渡すこと
    - `jq` で JSON を構築すること（`ubuntu-latest` に標準搭載）
    - Slack API は HTTP 200 でも `"ok":false` を返す場合があるため、`grep '"ok":false'` でレスポンスを検証すること
    - `curl --max-time 30 -sS` でタイムアウト設定とレスポンス格納を行うこと
    - `uses:` フィールドはなし（`curl` と `jq` のみ使用）_

---

## Phase 4: slack-notify-failure Composite Action の実装

- [x] 4. `.github/composite/slack-notify-failure/action.yml` を作成する
  - File: `.github/composite/slack-notify-failure/action.yml`
  - ワークフロー失敗時に Slack の Incoming Webhook URL へ通知する Composite Action を実装する
  - Purpose: 利用者リポジトリが失敗通知を標準フォーマットで Slack に投稿できるようにする
  - _Leverage: `composite-actions-support` spec の design.md（セキュリティポリシー：env 経由の入力値渡し）_
  - _Requirements: 4, 5_
  - _Prompt: Role: GitHub Actions エンジニア | Task: `.github/composite/slack-notify-failure/action.yml` を以下の完全な YAML 内容で作成してください。`slack-notify-success` と異なり、Incoming Webhook URL を使用するため `channel-id` / `bot-oauth-token` / `thread-ts` / `reply-broadcast` は不要です。

    ```yaml
    name: Post Message to Slack - Failure
    description: Post a message to Slack when the workflow fails

    inputs:
      webhook-url:
        description: Slack Incoming Webhook URL
        required: true
      color:
        description: Color of the message
        required: false
        default: danger
      mention-user:
        description: Mention user
        required: false
        default: ''
      title:
        description: Message title
        required: false
        default: 'workflow failed'
      message:
        description: Message body
        required: false
        default: 'Execution log: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}'

    runs:
      using: 'composite'
      steps:
        - id: post-message-failure
          shell: bash
          env:
            SLACK_WEBHOOK_URL: ${{ inputs.webhook-url }}
            SLACK_COLOR: ${{ inputs.color }}
            SLACK_MENTION_USER: ${{ inputs.mention-user }}
            SLACK_TITLE_TEXT: ${{ inputs.title }}
            SLACK_MESSAGE: ${{ inputs.message }}
            RUNNER_DEBUG: ${{ runner.debug }}
          run: |
            if [ "${RUNNER_DEBUG}" == "1" ]; then
              set -x
            fi
            if [ -n "${SLACK_MENTION_USER}" ]; then
              SLACK_TITLE="*FAILURE - ${SLACK_MENTION_USER} ${SLACK_TITLE_TEXT}*"
            else
              SLACK_TITLE="*FAILURE - ${SLACK_TITLE_TEXT}*"
            fi
            REPO_NAME="${GITHUB_REPOSITORY#${GITHUB_REPOSITORY_OWNER}/}"
            REPO_URL="${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}"
            SLACK_DATA=$(jq -n \
              --arg color "${SLACK_COLOR}" \
              --arg title "${SLACK_TITLE}" \
              --arg author_name "${REPO_NAME}" \
              --arg author_link "${REPO_URL}" \
              --arg text "${SLACK_MESSAGE}" \
              '{
                attachments: [{
                  fallback: $title,
                  pretext: $title,
                  color: $color,
                  author_name: $author_name,
                  author_link: $author_link,
                  text: $text
                }]
              }')
            curl --max-time 30 --fail -sS -X POST \
              -H "Content-Type: application/json" \
              -d "${SLACK_DATA}" \
              "${SLACK_WEBHOOK_URL}" \
              || { echo "::error::Failed to post message to Slack"; exit 1; }
    ```

    注意事項:
    - `${{ inputs.xxx }}` を `run:` に直接埋め込まず、全て `env:` 経由で渡すこと（テンプレートインジェクション対策）
    - `runner.debug` も `RUNNER_DEBUG` として `env:` 経由で渡すこと
    - `jq` で JSON を構築すること（`ubuntu-latest` に標準搭載）
    - Incoming Webhook は HTTP ステータスでエラーを返すため `--fail` オプションで十分（`"ok":false` チェック不要）
    - `slack-notify-success` と異なり `channel` フィールドは JSON に含めない（Webhook URL にチャンネルが埋め込まれているため）
    - `uses:` フィールドはなし（`curl` と `jq` のみ使用）_

---

## Phase 5: .gitkeep の削除

- [x] 5. `.github/composite/.gitkeep` を削除する
  - File: `.github/composite/.gitkeep`（削除）
  - Purpose: 実際の Composite Actions が追加されたため、ディレクトリを Git 管理するための `.gitkeep` は不要になる
  - _Leverage: なし_
  - _Requirements: 1, 2, 3, 4（ディレクトリに実ファイルが追加されたため）_
  - _Prompt: Role: GitHub Actions エンジニア | Task: `.github/composite/.gitkeep` ファイルを削除してください。Phase 1〜4 で実際の `action.yml` ファイルが配置されたため、このファイルは不要です。`git rm .github/composite/.gitkeep` または通常のファイル削除で対応してください。削除後に `.github/composite/` ディレクトリが以下の構造になっていることを確認してください:

    ```
    .github/composite/
      pnpm-setup/
        action.yml
      playwright-setup/
        action.yml
      slack-notify-success/
        action.yml
      slack-notify-failure/
        action.yml
    ```

    注意事項:
    - `.gitkeep` 以外のファイルは削除しないこと
    - `.github/composite/` ディレクトリ自体は残すこと_

---

## Phase 6: README.md の Composite Actions セクション更新

- [x] 6. `README.md` の `### Composite Actions` セクションを更新する
  - File: `README.md`
  - `### Composite Actions` セクションの `Coming soon.` を各 Action の使用方法・入力パラメータ一覧に置き換える
  - Purpose: 利用者が README から各 Composite Action の使い方をすぐに把握できるようにする
  - _Leverage: 現行の `README.md`（既存の `## Usage` セクション・`### Composite Actions` セクションの構造を維持する）_
  - _Requirements: 6_
  - _Prompt: Role: テクニカルライター | Task: `README.md` の `### Composite Actions` セクションを以下の内容に更新してください。現在は `Coming soon.` のみが記載されているため、各 Action の詳細に置き換えます。

    **現在の `### Composite Actions` セクション（変更前）:**
    ```markdown
    ### Composite Actions

    Coming soon.
    ```

    **更新後の `### Composite Actions` セクション（変更後）:**
    ```markdown
    ### Composite Actions

    #### pnpm-setup

    Node.js と pnpm のセットアップ、pnpm ストアキャッシュ、依存関係インストールを一括実行します。

    **前提条件:** リポジトリルートに `.node-version`・`package.json`・`pnpm-lock.yaml` が存在すること

    ```yaml
    steps:
      - uses: kryota-dev/actions/.github/composite/pnpm-setup@v1
    ```

    ---

    #### playwright-setup

    Playwright ブラウザをキャッシュ付きでインストールします。キャッシュヒット時はダウンロードをスキップします。

    **前提条件:** `pnpm-setup` Action（または同等のセットアップ）が先に完了していること

    ```yaml
    steps:
      - uses: kryota-dev/actions/.github/composite/pnpm-setup@v1
      - uses: kryota-dev/actions/.github/composite/playwright-setup@v1
    ```

    ---

    #### slack-notify-success

    ワークフロー成功時に Slack へ通知します。Slack Bot OAuth Token と `chat.postMessage` API を使用します。

    | 入力名 | 必須 | デフォルト値 | 説明 |
    |---|---|---|---|
    | `channel-id` | 必須 | - | Slack チャンネル ID |
    | `bot-oauth-token` | 必須 | - | Slack Bot OAuth Token |
    | `color` | 任意 | `good` | メッセージのカラーバー色 |
    | `mention-user` | 任意 | `''` | メンション対象ユーザー |
    | `title` | 任意 | `workflow execution completed` | メッセージタイトル |
    | `message` | 任意 | 実行ログ URL | メッセージ本文 |
    | `thread-ts` | 任意 | `'null'` | スレッド返信先 timestamp |
    | `reply-broadcast` | 任意 | `'false'` | スレッド返信をチャンネルにもブロードキャストするか |

    ```yaml
    steps:
      - uses: kryota-dev/actions/.github/composite/slack-notify-success@v1
        with:
          channel-id: ${{ vars.SLACK_CHANNEL_ID }}
          bot-oauth-token: ${{ secrets.SLACK_BOT_OAUTH_TOKEN }}
    ```

    ---

    #### slack-notify-failure

    ワークフロー失敗時に Slack へ通知します。Slack Incoming Webhook URL を使用します（`slack-notify-success` と異なり、チャンネル指定不要）。

    | 入力名 | 必須 | デフォルト値 | 説明 |
    |---|---|---|---|
    | `webhook-url` | 必須 | - | Slack Incoming Webhook URL |
    | `color` | 任意 | `danger` | メッセージのカラーバー色 |
    | `mention-user` | 任意 | `''` | メンション対象ユーザー |
    | `title` | 任意 | `workflow failed` | メッセージタイトル |
    | `message` | 任意 | 実行ログ URL | メッセージ本文 |

    ```yaml
    steps:
      - uses: kryota-dev/actions/.github/composite/slack-notify-failure@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
    ```
    ```

    注意事項:
    - `## Usage` セクションや `### Reusable Workflows` セクション等、他のセクションは変更しないこと
    - `### Internal CI Workflows` セクションより前に `### Composite Actions` セクションが位置していることを確認すること
    - YAML コードブロック内のバッククォートが正しくレンダリングされることを確認すること_
