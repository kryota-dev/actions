# Design Review: composite-actions-creation

## 総合評価

**APPROVED_WITH_COMMENTS**

## 評価サマリー

4つの Composite Actions 実装設計は全体として高品質であり、要件のほぼ全てをカバーしている。テンプレートインジェクション対策（`env:` 経由の環境変数渡し）、SHA ピン留め、エラーハンドリングなどのセキュリティ要件が適切に設計されている。ただし、Slack API レスポンスの成否検証、シェルスクリプトの JSON インジェクションリスク、`pnpm-setup` のキャッシュ二重管理に関する軽微〜中程度の問題があり、これらへの対応を推奨する。

---

## 詳細フィードバック

### [must] 必須修正事項

#### M1: slack-notify-success / slack-notify-failure - Slack API レスポンスの成否を検証していない

**問題:**
`curl --fail` オプションなし、かつ Slack API はエラー時も HTTP 200 を返しながら `"ok": false` を含む JSON を返す仕様である。設計の `|| { echo "::error::..."; exit 1; }` パターンは HTTP レベルの失敗しか検出できず、Slack API の論理エラー（トークン無効、チャンネル不存在等）を見逃す。

**影響:** 通知が届いていないにもかかわらず CI ステップが成功になる。

**推奨修正:**
```bash
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

Webhook 版（`slack-notify-failure`）は成功時に `"ok"` ではなく `"ok"` の文字列を返すため、HTTP ステータスに `--fail` を使う方式で十分：
```bash
curl --max-time 30 --fail -sS -X POST \
  -H "Content-Type: application/json" \
  -d "${SLACK_DATA}" \
  "${SLACK_WEBHOOK_URL}" \
  || { echo "::error::Failed to post message to Slack"; exit 1; }
```

---

#### M2: Slack の run ステップ - シェル変数展開による JSON インジェクションリスク

**問題:**
`SLACK_DATA=$(cat <<EOF ... "${SLACK_TITLE}" ... "${SLACK_MESSAGE}" ... EOF)` のように環境変数を heredoc 内でダブルクォートで囲んで JSON に展開しているが、これらの変数値にダブルクォート（`"`）やバックスラッシュが含まれると JSON が破損する。`inputs.mention-user`、`inputs.title`、`inputs.message` は呼び出し元が自由に指定できるため、任意の値が入り得る。

**影響:** JSON のパース失敗による curl エラー、または予期しないペイロードの送信。

**推奨修正:** `jq` を使用してJSONを安全に構築する：
```bash
SLACK_DATA=$(jq -n \
  --arg channel "${SLACK_CHANNEL_ID}" \
  --arg color "${SLACK_COLOR}" \
  --arg title "${SLACK_TITLE}" \
  --arg author_name "${GITHUB_REPOSITORY#${GITHUB_REPOSITORY_OWNER}/}" \
  --arg author_link "${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}" \
  --arg text "${SLACK_MESSAGE}" \
  '{
    channel: $channel,
    attachments: [{
      fallback: $title,
      pretext: $title,
      color: $color,
      author_name: $author_name,
      author_link: $author_link,
      text: $text
    }]
  }')
```

ただし `jq` が GitHub Actions の ubuntu-latest に標準搭載されているか確認が必要（標準搭載済みのはずだが、設計文書に明示することを推奨）。代替として Python を使う方法もある。

---

### [imo] 推奨改善事項

#### I1: pnpm-setup - `actions/setup-node` の pnpm キャッシュと `actions/cache` の二重管理

**問題:**
設計では `actions/setup-node`（`cache: 'pnpm'` オプション）と `actions/cache`（pnpm ストアパスを手動キャッシュ）の両方を使用している。`actions/setup-node` の `cache: 'pnpm'` 自体がすでに pnpm ストアのキャッシュを管理するため、これらが二重に機能する可能性がある。

**推奨:** 参考リポジトリ（nextjs-static-export-boilerplate）の実装を確認し、どちらか一方に統一するか、両者の役割分担（例：`setup-node` の cache でキャッシュ復元、`actions/cache` で追加のstore path管理）を設計文書に明記すること。

#### I2: playwright-setup - キャッシュキーに OS バージョンが含まれない

**問題:**
キャッシュキーを `{runner.os}-playwright-{version}` としているが、`runner.os` は `Linux` のような OS 名であり、OS のバージョンやディストリビューションは含まれない。Playwright の `--with-deps` でインストールされるシステム依存パッケージはOS バージョンに依存するため、ランナーイメージが更新された場合にキャッシュが古い依存パッケージを持ち込む可能性がある。

**推奨（参考）:**
```yaml
key: ${{ runner.os }}-${{ runner.arch }}-playwright-${{ steps.playwright-version.outputs.version }}
```
または `hashFiles('pnpm-lock.yaml')` をキーに含めることも検討。

#### I3: slack-notify-success - `set -x` 時に Bot OAuth Token がログに露出する

**問題:**
`RUNNER_DEBUG == '1'` 時に `set -x` を実行すると、`env:` で設定した全環境変数（`SLACK_BOT_OAUTH_TOKEN` を含む）が curl コマンドのヘッダ引数としてランナーログに出力される可能性がある。GitHub Actions は `${{ secrets.XXX }}` の値をマスクするが、環境変数経由でシェルに渡された値のデバッグ出力は完全にマスクされない場合がある。

**推奨:** 設計文書に「`runner.debug` は信頼できる環境のみで有効化すること」の注意書きを追加する、または `set -x` の代わりにステップ単位のデバッグを使用する。

#### I4: my-test.yml - `actions/checkout` が `v6` を指している

**問題（コードベース検証で発見）:**
既存の `my-test.yml` の `actions/checkout` が `# v6` とコメントされているが、2026年2月時点での最新メジャーバージョンは `v4` である。SHA 自体はピン留めされているため実害はないが、コメントのバージョン表記が誤解を招く（Renovate が正しく追跡しているか確認が必要）。

**補足:** これは今回の設計スコープ外だが、気づいた点として共有する。

---

### [nits] 軽微な指摘

#### N1: design.md のmermaid図 - 外部 Actions のバージョンがタグ表記

design.md の Architecture セクション（mermaid図）に `pnpm/action-setup@v4.1.0` 等のタグ表記が使用されているが、実装では SHA ピン留めを使用する。図はあくまで概念的な表現だが、設計文書の正確性のため SHA 形式または「（SHA ピン留め）」の注記を追加することが望ましい。

#### N2: slack-notify-success - `reply-broadcast` の型が文字列

`reply-broadcast` の `default: 'false'` は文字列型であり、シェルスクリプト内で `if [ "${SLACK_REPLY_BROADCAST}" == 'true' ]` と比較している。Composite Actions の inputs は全て文字列として扱われるため動作は正しいが、`description` に「文字列 `'true'` または `'false'` を指定」と明記すると利用者の混乱を防げる。

#### N3: README の `### Composite Actions` - 個別 Action の入力パラメータ表が `pnpm-setup` と `playwright-setup` に存在しない

`pnpm-setup` と `playwright-setup` は inputs なしのため表は不要だが、「入力パラメータ: なし」と明示するか、前提条件（`.node-version` 等のファイル存在）を Requirements に沿って記載するとよい。設計では前提条件の記述がある点は評価できる。

---

### [ask] 確認事項

#### A1: `pnpm-setup` の `package_json_file: package.json` の意図

`pnpm/action-setup` の `package_json_file` を `package.json` に明示的に設定している（デフォルトと同じ）。これはモノレポ対応のために将来的に変更可能にする意図か、または単なる明示的な記述か？デフォルトと同じであれば省略するのがシンプルだが、意図がある場合は設計文書にコメントを追加してほしい。

#### A2: `playwright-setup` の outputs を `なし` としている点

設計では「Outputs: なし（内部ステップ出力 `version` は ... `actions/cache` の key に使用）」としているが、`playwright-version` ステップの output は `$GITHUB_OUTPUT` に書き出されている。これは Composite Action 全体の output として外部には公開しない（`outputs:` セクションなし）という理解で正しいか？もし呼び出し元でバージョンを確認したいユースケースがあれば、output として公開することも検討できる。

#### A3: Slack の curl レスポンスの `ok` フィールド検証の意図的な省略か

M1で指摘した Slack API のレスポンス検証について、意図的に省略したか、または考慮漏れか確認したい。参考リポジトリ（nextjs-static-export-boilerplate）での実装はどのようになっているか？

---

### [fyi] 参考情報

#### F1: ghalint run-action のパスセグメント制限

`ghalint run-action` はデフォルトで Composite Actions の `uses:` パスのセグメント数に制限を設けている（v1.5.1以降）。設計で採用している `.github/composite/{action-name}/action.yml` の構造（3セグメント）は標準的であり問題ない。ただし、将来的にネスト構造（例: `.github/composite/slack/notify-success/action.yml`）を採用する場合は制限に注意が必要。

#### F2: zizmor の `template-injection` 検出について

zizmor は `env:` 経由での環境変数渡しを適切なパターンとして認識し、直接埋め込みのみをエラーとして報告する。設計で採用した `env:` パターンは zizmor の検出を回避するための正しいアプローチである。

#### F3: Renovate Bot の `helpers:pinGitHubActionDigests` の動作

`.github/composite/` 配下の `action.yml` 内の `uses:` は、`helpers:pinGitHubActionDigests` により Renovate Bot の自動更新対象となる。これは `renovate.json5` の追加設定なしで機能する（Renovate は `.github/` 配下を自動スキャンするため）。設計の記載は正確。

---

## 要件カバレッジマトリクス

| 要件 | design.md での対応箇所 | 判定 |
|------|----------------------|------|
| Req 1: pnpm-setup 実装（pnpm/action-setup 使用） | Component 1, Data Models / pnpm-setup | OK |
| Req 1-AC1: pnpm/action-setup 使用 | Data Models の `uses: pnpm/action-setup@...` | OK |
| Req 1-AC2: setup-node でノードバージョン設定・pnpmキャッシュ | Data Models の `uses: actions/setup-node@...` | OK |
| Req 1-AC3: actions/cache でストアキャッシュ | Data Models の `uses: actions/cache@...` | OK |
| Req 1-AC4: pnpm install 実行 | Data Models の `run: pnpm install` | OK |
| Req 1-AC5: SHA ピン留め（40文字） | Steering Document Alignment、Data Models | OK |
| Req 1-AC6: run に shell: bash 明記 | Data Models（全 run ステップに shell: bash あり） | OK |
| Req 2: playwright-setup 実装 | Component 2, Data Models / playwright-setup | OK |
| Req 2-AC1: バージョン取得と GITHUB_OUTPUT 書き出し | ステップ構成 1 | OK |
| Req 2-AC2: actions/cache でブラウザキャッシュ（キー形式） | ステップ構成 2 | OK |
| Req 2-AC3: キャッシュミス時にインストール実行 | ステップ構成 3 | OK |
| Req 2-AC4: キャッシュヒット時はスキップ | `if: steps.cache-playwright.outputs.cache-hit != 'true'` | OK |
| Req 2-AC5: SHA ピン留め | Data Models | OK |
| Req 2-AC6: run に shell: bash 明記 | Data Models | OK |
| Req 3: slack-notify-success 実装（chat.postMessage API） | Component 3, Data Models / slack-notify-success | OK |
| Req 3-AC1: curl で chat.postMessage へ POST | Data Models のシェルスクリプト | OK |
| Req 3-AC2: inputs を env: 経由で渡す | Data Models の `env:` セクション | OK |
| Req 3-AC3: mention-user 指定時にタイトルに含める | シェルの if 分岐 | OK |
| Req 3-AC4: thread-ts 指定時に JSON に含める | シェルの if 分岐 | OK |
| Req 3-AC5: curl 失敗時のエラー出力と exit 1 | `\|\| { echo "::error::..."; exit 1; }` | PARTIAL（Slack APIの論理エラーは未検証 - M1参照） |
| Req 3-AC6: runner.debug == 1 時に set -x | シェルの if 分岐 | OK |
| Req 3-AC7: message のデフォルト値は実行ログ URL | `default: '${{ github.server_url }}/...'` | OK |
| Req 4: slack-notify-failure 実装（Webhook URL） | Component 4, Data Models / slack-notify-failure | OK |
| Req 4-AC1: curl で Webhook URL へ POST | Data Models | OK |
| Req 4-AC2: webhook-url を env: 経由で渡す | Data Models の `env:` セクション | OK |
| Req 4-AC3: mention-user 指定時にタイトルに含める | シェルの if 分岐 | OK |
| Req 4-AC4: curl 失敗時のエラー出力と exit 1 | `\|\| { echo "::error::..."; exit 1; }` | PARTIAL（M1参照） |
| Req 4-AC5: runner.debug == 1 時に set -x | シェルの if 分岐 | OK |
| Req 4-AC6: message のデフォルト値は実行ログ URL | `default: '${{ github.server_url }}/...'` | OK |
| Req 4-AC7: success との認証方式の違いを反映 | Component 4 設計判断 | OK |
| Req 5: CI 通過（ls-lint / ghalint / zizmor） | Steering Document Alignment | OK |
| Req 5-AC1: ls-lint が kebab-case を検証 | ディレクトリ構造が kebab-case 準拠 | OK |
| Req 5-AC2: ghalint run-action が SHA 検証 | 全 uses が SHA ピン留め | OK |
| Req 5-AC3: zizmor がセキュリティ検証 | env: 経由による template injection 回避 | OK |
| Req 5-AC4: template injection 禁止 | env: パターンを明示的に採用 | OK |
| Req 5-AC5: ミュータブルタグ禁止 | 全 uses を SHA 指定 | OK |
| Req 6: README 更新 | Data Models / README セクション | OK |
| Req 6-AC1: Composite Actions セクションに使用例追加 | README セクション | OK |
| Req 6-AC2: inputs 一覧を Markdown テーブルで表示 | slack-notify-* のみ（pnpm-setup/playwright-setup はテーブルなし） | OK（inputs なしのため） |
| Req 6-AC3: pnpm-setup は入力パラメータなしの例 | README セクション | OK |
| Req 6-AC4: playwright-setup は pnpm-setup を前提条件明記 | README セクション | OK |
| Req 6-AC5: slack-notify の認証方式の違いを明記 | README セクション | OK |
| Req 6-AC6: 使用例は {action-name}@v1 形式 | README セクション | OK |

---

## セキュリティ評価

| 項目 | 評価 | 備考 |
|------|------|------|
| テンプレートインジェクション対策（env: 経由） | 適切 | 全 inputs を env: 経由で渡している |
| SHA ピン留め（40文字） | 適切 | 全 uses に SHA + コメントタグ形式 |
| シークレットのハードコード禁止 | 適切 | inputs 経由のみ |
| JSON インジェクション対策 | 不十分 | M2 参照 - ユーザー入力の文字列が JSON 内で展開される |
| Slack API レスポンス検証 | 不十分 | M1 参照 - HTTP レベルのみで Slack 論理エラーを見逃す |
| デバッグ時のシークレット露出 | 要注意 | I3 参照 |

---

## まとめ

設計の方向性は正しく、セキュリティ要件の大半は適切に設計されている。主要な改善点は以下 2 点：

1. **[must] Slack API のレスポンス検証** - HTTP 200 でも Slack 論理エラーが返ることへの対応
2. **[must] JSON インジェクション対策** - ユーザー入力値を直接 heredoc で展開することのリスク

これら 2 点を修正することで、設計は APPROVED に引き上げられる。
