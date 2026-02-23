# Tasks Document

- [x] 1. `auto-assign-pr.yml` に Bot 判定と分岐ロジックを実装
  - File: `.github/workflows/auto-assign-pr.yml`
  - `workflow_call.inputs` に `bot-assignees` パラメータ（string, optional, default: ''）を追加
  - Bot 判定ステップ（`github.actor` が `[bot]` で終わるかチェック）を追加
  - Human ユーザー: 従来通り `gh pr edit --add-assignee` で PR 作成者をアサイン
  - Bot + `bot-assignees` 指定あり: 指定ユーザーをカンマ区切りでアサイン
  - Bot + `bot-assignees` 未指定: スキップしてログ出力
  - Purpose: Bot PR でのワークフロー失敗を防止し、代替アサイン先を指定可能にする
  - _Leverage: 既存の `auto-assign-pr.yml` の構造、`gh pr edit --add-assignee` パターン_
  - _Requirements: 1, 2, 3_
  - _Prompt: Implement the task for spec fix-auto-assign-bot-skip, first run spec-workflow-guide to get the workflow guide then implement the task: Role: GitHub Actions Workflow Developer | Task: Modify `.github/workflows/auto-assign-pr.yml` to add bot detection and conditional assignment logic. Add `bot-assignees` input parameter to `workflow_call`. Add a step to check if `github.actor` ends with `[bot]`. If human, assign PR creator. If bot with `bot-assignees`, assign specified users. If bot without `bot-assignees`, skip and log. Reference the design document at `.spec-workflow/specs/fix-auto-assign-bot-skip/design.md` for the exact YAML implementation. | Restrictions: Do not use `github.actor_type` (it does not exist). Do not add external actions (only `gh` CLI). Maintain `permissions: {}` at top level. Keep `pull-requests: write` at job level. Follow the project's actionlint/ghalint/zizmor CI requirements. | Success: The workflow has `bot-assignees` input, correctly detects bot actors, assigns appropriately based on the input, and skips gracefully when no bot-assignees are specified. After implementation, mark task as in-progress in tasks.md, log the implementation with log-implementation tool, then mark as complete._

- [x] 2. `my-setup-pr.yml` に `bot-assignees` パラメータを追加
  - File: `.github/workflows/my-setup-pr.yml`
  - `uses: ./.github/workflows/auto-assign-pr.yml` の呼び出しに `with: bot-assignees: 'kryota-dev'` を追加
  - Purpose: Bot PR（Renovate Bot 等）で kryota-dev にアサインされるようにする
  - _Leverage: 既存の `my-setup-pr.yml` の構造_
  - _Requirements: 4_
  - _Prompt: Implement the task for spec fix-auto-assign-bot-skip, first run spec-workflow-guide to get the workflow guide then implement the task: Role: GitHub Actions Workflow Developer | Task: Modify `.github/workflows/my-setup-pr.yml` to pass `bot-assignees: 'kryota-dev'` when calling `auto-assign-pr.yml`. Add `with:` block to the existing `uses:` directive. | Restrictions: Keep the thin wrapper pattern (no logic in this file). Do not change the trigger, permissions, or job name. | Success: `my-setup-pr.yml` passes `bot-assignees: 'kryota-dev'` to `auto-assign-pr.yml`. After implementation, mark task as in-progress in tasks.md, log the implementation with log-implementation tool, then mark as complete._

- [x] 3. `auto-assign-pr.md` ドキュメントを更新
  - File: `.github/workflows/docs/auto-assign-pr.md`
  - `bot-assignees` 入力パラメータの説明を Inputs セクションに追加
  - Bot PR 時の動作説明を追加
  - 使用例を更新（`bot-assignees` 指定ありの例を追加）
  - Purpose: ワークフロードキュメントを実装に合わせて更新する
  - _Leverage: 既存の `auto-assign-pr.md` のフォーマット_
  - _Requirements: 1, 4_
  - _Prompt: Implement the task for spec fix-auto-assign-bot-skip, first run spec-workflow-guide to get the workflow guide then implement the task: Role: Technical Writer | Task: Update `.github/workflows/docs/auto-assign-pr.md` to document the new `bot-assignees` input parameter. Add an Inputs table describing the parameter. Add a section explaining bot PR behavior. Update the usage example to show how to pass `bot-assignees`. | Restrictions: Follow the existing documentation format and style. Write in Japanese. Do not change the existing structure unnecessarily. | Success: Documentation accurately describes the new `bot-assignees` parameter, bot detection behavior, and includes a usage example with bot-assignees. After implementation, mark task as in-progress in tasks.md, log the implementation with log-implementation tool, then mark as complete._

- [x] 4. actionlint による構文チェック
  - Run: `aqua exec -- actionlint`
  - Purpose: 修正したワークフローファイルが actionlint を通過することを確認する
  - _Requirements: Non-functional (CI quality gate)_
  - _Prompt: Implement the task for spec fix-auto-assign-bot-skip, first run spec-workflow-guide to get the workflow guide then implement the task: Role: CI/CD Engineer | Task: Run `aqua exec -- actionlint` to verify the modified workflow files pass syntax checking. If errors are found, fix them in the relevant workflow files. | Restrictions: Do not disable or skip any lint rules. Fix issues at the source. | Success: `actionlint` exits with no errors for all workflow files. After verification, mark task as in-progress in tasks.md, log the implementation with log-implementation tool, then mark as complete._
