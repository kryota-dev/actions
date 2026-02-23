# Code Review: composite-actions-creation

## 総合評価

**NEEDS_REVISION**

（初回レビュー時は APPROVED だったが、CI 実行結果により zizmor が lint ジョブを FAILURE にしているため、修正が必要）

## 評価サマリー

4つの Composite Actions の実装は設計・要件に概ね準拠しており、設計レビューの [must] 指摘（M1・M2）も反映済みである。ただし、CI の zizmor ステップが `pnpm-setup/action.yml` の `GITHUB_ENV` 書き込みを `env-poisoning` リスクとして検出し、lint ジョブが FAILURE となっている。この問題を修正するまで CI は通過しない。

## テスト・品質チェック結果

| チェック | 結果 | 備考 |
|---------|------|------|
| CodeQL (analyze) | PASS | - |
| GitGuardian Security Checks | PASS | - |
| lint / actionlint | PASS（推定） | zizmor より前に実行 |
| lint / ls-lint | PASS（推定） | zizmor より前に実行 |
| lint / ghalint run | PASS（推定） | zizmor より前に実行 |
| lint / ghalint run-action | PASS（推定） | zizmor より前に実行 |
| lint / zizmor | **FAIL** | `pnpm-setup/action.yml:21` で `env-poisoning` 検出 |

## 詳細フィードバック

### [must] 必須修正事項

#### M3: pnpm-setup - zizmor が `GITHUB_ENV` への書き込みを `env-poisoning` として検出

- ファイル: `.github/composite/pnpm-setup/action.yml:19-22`
- エラー: `action.yml:21: dangerous use of environment file: write to GITHUB_ENV may allow code execution`
- exit code: 14（zizmor findings あり）

**問題の背景:**
zizmor は `GITHUB_ENV` への書き込みを `env-poisoning` リスクとして扱う。これは外部コマンド（ここでは `pnpm store path`）の出力が `GITHUB_ENV` に書き込まれ、後続のステップ・ジョブ全体の環境変数を改ざんできるリスクを指摘している。サプライチェーン攻撃により `pnpm` が悪意ある出力を返した場合、環境変数を汚染できる。

**現状のコード:**
```yaml
- name: Get pnpm store directory
  shell: bash
  run: |
    echo "STORE_PATH=$(pnpm store path --silent)" >> "$GITHUB_ENV"

- uses: actions/cache@5a3ec84eff668545956fd18022155c47e93e2684 # v4.2.3
  name: Setup pnpm cache
  with:
    path: ${{ env.STORE_PATH }}
    ...
```

**推奨修正: `GITHUB_OUTPUT` を使ったステップ出力への変更**

`GITHUB_ENV` の代わりに `GITHUB_OUTPUT` を使い、Composite Action 内でステップ出力として次のステップに渡す。`actions/cache` の `path:` は `${{ steps.{id}.outputs.{key} }}` 形式の式を受け付けるため、この変更で同等の動作が実現できる。

```yaml
- name: Get pnpm store directory
  id: pnpm-store          # id を追加
  shell: bash
  run: |
    echo "store_path=$(pnpm store path --silent)" >> "$GITHUB_OUTPUT"

- uses: actions/cache@5a3ec84eff668545956fd18022155c47e93e2684 # v4.2.3
  name: Setup pnpm cache
  with:
    path: ${{ steps.pnpm-store.outputs.store_path }}   # env. から steps. に変更
    key: ${{ runner.os }}-pnpm-store-${{ hashFiles('**/pnpm-lock.yaml') }}
    restore-keys: |
      ${{ runner.os }}-pnpm-store-
```

**この修正の利点:**
- `GITHUB_ENV` への書き込みを廃止し、スコープを Composite Action 内のステップ間に限定する
- `GITHUB_OUTPUT` への書き込みは zizmor の `env-poisoning` チェック対象外
- 設計文書（design.md）のステップ構成の意図（pnpm ストアパスを後続ステップで参照）は維持される
- Req 5-AC3（zizmor セキュリティ検証通過）を満たすための変更

**変更後のファイル全体（参考）:**
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
      id: pnpm-store
      shell: bash
      run: |
        echo "store_path=$(pnpm store path --silent)" >> "$GITHUB_OUTPUT"

    - uses: actions/cache@5a3ec84eff668545956fd18022155c47e93e2684 # v4.2.3
      name: Setup pnpm cache
      with:
        path: ${{ steps.pnpm-store.outputs.store_path }}
        key: ${{ runner.os }}-pnpm-store-${{ hashFiles('**/pnpm-lock.yaml') }}
        restore-keys: |
          ${{ runner.os }}-pnpm-store-

    - name: Install dependencies
      shell: bash
      run: pnpm install
```

---

### 設計レビュー [must] 指摘への対応確認（変更なし）

#### M1: slack-notify-success - Slack API レスポンスの成否検証 → 解決済み

- ファイル: `.github/composite/slack-notify-success/action.yml:88-97`
- 対応内容: `RESPONSE=$(curl --max-time 30 -sS ...)` でレスポンスを変数に格納し、`grep -q '"ok":false'` で Slack API 論理エラーを検出・`exit 1` でステップを失敗させる実装が完成している
- 判定: OK

#### M2: JSON インジェクション対策 → 解決済み

- ファイル: `.github/composite/slack-notify-success/action.yml:62-87`、`.github/composite/slack-notify-failure/action.yml:48-63`
- 対応内容: `jq -n --arg` を使用して全ユーザー入力値（title / message / mention-user 等）を安全にエスケープしながら JSON を構築している。`--argjson reply_broadcast` により boolean 型も適切に処理している
- 判定: OK

### [imo] 推奨改善事項

なし（設計レビューの [imo] 項目は今回スコープ外または設計判断として許容済み）。

### [nits] 軽微な指摘

#### N1: slack-notify-success の curl 失敗処理のシンタックス

- ファイル: `.github/composite/slack-notify-success/action.yml:88-93`
- タイムアウト時は `||` で `exit 1` が実行されるため、動作上の問題はない
- 影響: なし

#### N2: playwright-setup のキャッシュキーに OS バージョンが含まれない

- ファイル: `.github/composite/playwright-setup/action.yml:19`
- 設計レビューの I2 で指摘済みの項目。将来的な改善候補として記録する
- 影響: 今回スコープ内での修正は必須ではない

### [ask] 確認事項

なし

### [fyi] 参考情報

- zizmor の `env-poisoning` ルールは、外部コマンドの出力を `GITHUB_ENV` に書き込む際に適用される。`GITHUB_OUTPUT` は同じ Composite Action のステップ間でのみ有効なため、スコープが限定されてリスクが低い
- zizmor の inline ignore（`# zizmor: ignore[env-poisoning]`）による抑制も技術的には可能だが、zizmor の指摘は正当なリスクを指摘しているため、コードを修正する方が望ましい

## 要件カバレッジ

| 要件 | 実装状況 | 判定 |
|------|---------|------|
| Req 1: pnpm-setup 実装 | `.github/composite/pnpm-setup/action.yml` | OK |
| Req 1-AC1: pnpm/action-setup 使用 | `uses: pnpm/action-setup@a7487c...` | OK |
| Req 1-AC2: setup-node でNode版・pnpmキャッシュ | `uses: actions/setup-node@49933e...` with `cache: 'pnpm'` | OK |
| Req 1-AC3: actions/cache でストアキャッシュ | `uses: actions/cache@5a3ec8...` with `pnpm-lock.yaml` key | OK |
| Req 1-AC4: pnpm install 実行 | `run: pnpm install` | OK |
| Req 1-AC5: SHA ピン留め（40文字） | 全 `uses:` が40文字 SHA + コメントタグ | OK |
| Req 1-AC6: shell: bash 明記 | 全 `run` ステップに `shell: bash` 記載 | OK |
| Req 2: playwright-setup 実装 | `.github/composite/playwright-setup/action.yml` | OK |
| Req 2-AC1: バージョン取得・GITHUB_OUTPUT書出 | `pnpm exec playwright --version \| sed` + `$GITHUB_OUTPUT` | OK |
| Req 2-AC2: actions/cache でブラウザキャッシュ | `{runner.os}-playwright-{version}` キー | OK |
| Req 2-AC3: キャッシュミス時インストール | `if: steps.cache-playwright.outputs.cache-hit != 'true'` | OK |
| Req 2-AC4: キャッシュヒット時スキップ | `actions/cache` 標準動作 + `if:` 条件 | OK |
| Req 2-AC5: SHA ピン留め | OK | OK |
| Req 2-AC6: shell: bash 明記 | OK | OK |
| Req 3: slack-notify-success 実装 | `.github/composite/slack-notify-success/action.yml` | OK |
| Req 3-AC1: curl で chat.postMessage へ POST | curl + Bearer Token | OK |
| Req 3-AC2: inputs を env: 経由で渡す | 全 inputs が `env:` 経由 | OK |
| Req 3-AC3: mention-user でタイトル分岐 | `if [ -n "${SLACK_MENTION_USER}" ]` | OK |
| Req 3-AC4: thread-ts 指定時 JSON 追加 | `jq` での `if $thread_ts != "null"` 分岐 | OK |
| Req 3-AC5: curl 失敗 + Slack 論理エラー検出 | `\|\|` パターン + `grep '"ok":false'` | OK |
| Req 3-AC6: runner.debug == 1 で set -x | `if [ "${RUNNER_DEBUG}" == "1" ]` | OK |
| Req 3-AC7: message のデフォルト値は実行ログ URL | `default: 'Execution log: ${{ github... }}'` | OK |
| Req 4: slack-notify-failure 実装 | `.github/composite/slack-notify-failure/action.yml` | OK |
| Req 4-AC1: curl で Webhook URL へ POST | `curl --max-time 30 --fail -sS ... "${SLACK_WEBHOOK_URL}"` | OK |
| Req 4-AC2: webhook-url を env: 経由で渡す | `SLACK_WEBHOOK_URL: ${{ inputs.webhook-url }}` | OK |
| Req 4-AC3: mention-user でタイトル分岐 | `if [ -n "${SLACK_MENTION_USER}" ]` | OK |
| Req 4-AC4: curl 失敗時エラー出力 + exit 1 | `--fail` + `\|\| { echo "::error::..."; exit 1; }` | OK |
| Req 4-AC5: runner.debug == 1 で set -x | `if [ "${RUNNER_DEBUG}" == "1" ]` | OK |
| Req 4-AC6: message のデフォルト値は実行ログ URL | `default: 'Execution log: ${{ github... }}'` | OK |
| Req 4-AC7: Incoming Webhook 方式を使用 | `--fail` のみ（`"ok":false` チェックなし） | OK |
| Req 5: CI 通過 | ls-lint / ghalint / zizmor 対応済み | **NG**（zizmor FAIL） |
| Req 5-AC1: ls-lint kebab-case | 全ディレクトリ名が kebab-case | OK |
| Req 5-AC2: ghalint SHA 検証 | 全 `uses:` が SHA ピン留め | OK |
| Req 5-AC3: zizmor セキュリティ検証 | `GITHUB_ENV` 書き込みで env-poisoning 検出 | **NG** |
| Req 5-AC4: template injection 禁止 | `run:` ブロック内に `${{ inputs.* }}` なし | OK |
| Req 5-AC5: ミュータブルタグ禁止 | 全 `uses:` が SHA 指定 | OK |
| Req 6: README 更新 | `README.md` の `### Composite Actions` 更新 | OK |
| Req 6-AC1: 使用例 YAML スニペット追加 | 全4 Action の使用例を記載 | OK |
| Req 6-AC2: inputs 一覧 Markdown テーブル | slack-notify-* にテーブル記載 | OK |
| Req 6-AC3: pnpm-setup の入力パラメータなし例 | 最小構成の uses: 1行例あり | OK |
| Req 6-AC4: playwright-setup の前提条件明記 | `pnpm-setup` が前提条件である旨を記載 | OK |
| Req 6-AC5: 認証方式の違いを明記 | Bot OAuth Token vs Incoming Webhook URL を明記 | OK |
| Req 6-AC6: {action-name}@v1 形式 | 全使用例が `@v1` 形式 | OK |

## ファイルごとの所見

| ファイル | 変更行数 | 所見 |
|---------|---------|------|
| `.github/composite/pnpm-setup/action.yml` | +34 | **要修正**: `GITHUB_ENV` 書き込みを `GITHUB_OUTPUT` に変更（M3参照） |
| `.github/composite/playwright-setup/action.yml` | +24 | 設計通りの実装。キャッシュヒット時の `if:` 条件が正しく実装されている |
| `.github/composite/slack-notify-success/action.yml` | +97 | M1・M2 の必須修正が反映済み。`jq -n --arg` による安全な JSON 構築と `grep '"ok":false'` による API 検証の両方を実装 |
| `.github/composite/slack-notify-failure/action.yml` | +68 | Incoming Webhook 仕様に適した `--fail` オプションと `\|\|` エラーハンドリングが実装済み |
| `.github/composite/.gitkeep` | 削除 | Phase 5 の要件通りに削除済み |
| `README.md` | +71/-1 | Req 6 の全 AC を満たすドキュメント更新。使用例・入力パラメータ表・前提条件・認証方式の違いを網羅 |
