# Design Review: pat-branch-ruleset

## 総合評価

条件付き承認

## 評価サマリー

設計全体の方向性は適切であり、PAT（オーナー）バイパスを前提とした保護強化の設計判断は妥当である。ただし、`required_approving_review_count: 0` への変更根拠の記載方法、fnmatch パターンの潜在的な曖昧性、ステータスチェック名の検証手順など、実装時のリスクを低減するためのいくつかの必須修正事項がある。

---

## 詳細フィードバック

### [must] 必須修正事項

#### M-1: `required_approving_review_count` の要件差異に関する明示的な合意が必要

**問題:** requirements.md の Requirement 1-5 では `required_approving_review_count: 1` と明示されているが、design.md では `0` に変更している。design.md 内に設計判断の説明はあるが、要件変更として requirements.md に反映されていない（または要件側に明示的な「変更承認」の記録がない）。

**リスク:** 将来のメンテナー（または自分自身）が要件と設計の乖離を見たとき、どちらが正しいか判断できない。

**対応案:**
- requirements.md の Requirement 1-5 を修正して `0` に更新する（コメントで理由を追記）、または
- design.md に「要件からの意図的な逸脱（Intentional Deviation from Requirements）」セクションを設け、PM/オーナーの承認があった旨を明記する

---

#### M-2: `protect-version-tags.json` と `protect-major-tags.json` のパターン重複による意図しないルール競合の確認

**問題:** `refs/tags/v*.*.*`（バージョンタグ）と `refs/tags/v[0-9]*`（メジャータグ）は、GitHub Rulesets において**両方が同一タグにマッチしない**ことを確認する必要がある。

具体的には：
- `v1.0.0` は `refs/tags/v*.*.*` にマッチ → `deletion` + `non_fast_forward` が適用
- `v1` は `refs/tags/v[0-9]*` にマッチ → `deletion` のみ適用
- 問題は `v1.0.0` が `refs/tags/v[0-9]*` にも**マッチする可能性**があること

`refs/tags/v[0-9]*` の `*` は、fnmatch では `.`（ドット）を含む任意の文字列にマッチする。したがって `v1.0.0` は `v[0-9]*` にもマッチし、**両方のルールセットが適用される**可能性がある。

複数ルールセットが同一 ref にマッチする場合、GitHub は**すべてのルールの論理 OR（最も厳しい方）**を適用する。この場合：
- `v1.0.0` には `protect-major-tags` の `deletion` も適用される（`protect-version-tags` と同じ効果）
- `protect-version-tags` の `non_fast_forward` も適用されるため、`v1.0.0` への force push はブロックされる（これは意図通り）

ただし、`v1` に `protect-version-tags`（`refs/tags/v*.*.*`）がマッチするかは仕様確認が必要：
- `v*.*.*` は `.` が 2 つ必要なパターンのため、`v1` はマッチしない → これは OK

**対応案:** design.md に「パターン重複時の GitHub Rulesets 動作（複数ルールセットの論理 OR 適用）」についての注記を追加し、`v1.0.0` が両ルールセットにマッチすることを意図的に許容する旨を明記する。

---

#### M-3: ステータスチェック名 `lint` の検証 - ジョブ名とステータスチェック名の一致確認

**問題:** `my_test.yml` の検証で、ジョブ名は `lint`（line 13）であることを確認した。しかし、`strategy.matrix` を使用するジョブでは、ステータスチェック名が `jobName (matrixValue)` 形式になる点に注意が必要。

`my_test.yml` の `lint` ジョブは `strategy.matrix` を使用していないため `lint` で正しい。
`my_codeql.yml` の `analyze` ジョブは `strategy.matrix: {language: [actions]}` を使用しているため、実際のステータスチェック名は **`analyze (actions)`** となる可能性がある。

**リスク:** `required_status_checks` に `{ "context": "analyze" }` を設定した場合、実際のチェック名が `analyze (actions)` であれば永遠に pending のままとなり、**すべての PR がマージ不可**になる。

**対応案:**
1. 既存 PR またはコミットの GitHub Actions の実際のステータスチェック名を確認する（GitHub Web UI または `gh pr checks` コマンド）
2. 確認した名前を design.md に記載し、JSON の `context` フィールドを正確な名前に修正する
3. 必要に応じて `{ "context": "analyze (actions)" }` に修正する

---

### [imo] 推奨改善事項

#### I-1: `strict_required_status_checks_policy: false` の運用上のリスクを追記

design.md では運用負荷軽減のため `false` としているが、この設定では**古い base ブランチの状態でパスしたステータスチェックを有効と判定する**。

競合する変更が main にマージされた後、以前のチェック結果を持つ Renovate Bot の PR がマージ可能な状態のままになるリスクがある。Renovate Bot の PR は通常自動マージ設定を使用しないため影響は限定的だが、design.md にこのトレードオフを明記することを推奨する。

---

#### I-2: `do_not_enforce_on_create: false` の意図の説明追加

`do_not_enforce_on_create: false`（デフォルト）は、新しいブランチまたはタグ作成時にもステータスチェックを適用することを意味する。タグ作成のトリガーでは `required_status_checks` は通常意味をなさない（ブランチ保護にのみ適用される）が、`protect-main.json` における意図を明確にする注記があると良い。

---

#### I-3: ADR 003 の作成で `docs/adr/README.md` の更新を明示

requirements.md の Requirement 5-4 で `docs/adr/README.md` への ADR 003 追加が要求されている。design.md の Component 4 では ADR 003 の作成のみに触れており、`README.md` の更新が成果物リストに明示されていない。実装時の見落としを防ぐため、Component 4 または成果物リストに `docs/adr/README.md` の更新を追記することを推奨する。

---

### [nits] 軽微な指摘

#### N-1: design.md の「Existing Components to Leverage」における `actions/checkout` バージョン

design.md の Code Reuse Analysis で `my_test.yml` の SHA が古いコメント（`v6`）として記載されている可能性があるが、実際のファイルでは `v6`（`de0fac2e...`）が使用されている。コードベースとの整合性は問題ないが、design.md 内のワークフロー参照が最新の状態を反映しているか確認する。

---

#### N-2: Error Handling の Error 2 でコンテキスト名不一致のリスクを「pending 状態」と表記しているが、M-3 の問題が未解決の場合はより深刻

N-2 は M-3 が解決されることを前提とした軽微な表現の問題として分類する。M-3 解決後は Error Handling の説明が実態と一致する。

---

### [ask] 確認事項

#### Q-1: tagpr が main に「直接 push」するケースの具体的な挙動確認

design.md では「tagpr の main への直接 push（リリース PR 作成）」と記載されているが、実際の `my_release.yml` を確認すると、tagpr は main への直接 push ではなく**リリース PR を作成**するワークフローである。

- tagpr がリリース PR を作成する際: `pull_request` ルールの対象外（PR を作成するのは tagpr であり、main への push ではない）
- tagpr がリリース PR マージ後に `vX.Y.Z` タグを付与する際: タグ作成の操作であり、`protect-version-tags.json` の対象

実際に tagpr が main へ直接 push するケースがあるか確認し、あれば具体的なシナリオを design.md に明記することを推奨する。（現状のコードを見る限り、tagpr は PR 経由でのマージのみを行い、main への直接 push は行っていない可能性がある。）

---

#### Q-2: メジャータグ force push の管理者バイパス依存について

Requirement 3-3 では「PAT（オーナー）バイパスにより操作を妨げない」とあり、design.md では `protect-major-tags.json` に `non_fast_forward` を含めないことで対応している。

しかし `non_fast_forward` を含めない場合、**オーナー以外のユーザーも** `v1` 等のメジャータグを force push できる状態になる。個人リポジトリで外部コントリビューターが存在しない場合は問題ないが、将来的な Collaborator 追加時のリスクとして design.md に明記することを推奨する。この点についての設計者の意図を確認したい。

---

### [fyi] 参考情報

#### F-1: GitHub Rulesets API における `integration_id` の省略について

design.md で「`integration_id` は省略可能」と記載されており、正しい。ただし GitHub Actions の統合 ID は `15368` ではなく、`github-actions` App の ID は環境によって異なる場合がある。Web UI からのインポートでは省略が推奨される。省略時はジョブ名が一致する任意のチェックを受け付けるため、`integration_id` 省略方針は適切。

---

#### F-2: `refs/tags/v[0-9]*` と `refs/tags/v*.*.*` のマッチ順序について

GitHub Rulesets は複数のルールセットが同一 ref にマッチした場合、それぞれのルールを**独立して適用**し、より制限的なルールが優先される。`v1.0.0` には両ルールセットが適用されるが、最終的な保護レベルは `protect-version-tags.json`（`deletion` + `non_fast_forward`）の方が強いため、期待通りの動作となる。

---

## 要件カバレッジマトリクス

| 要件 | design.md での対応箇所 | 判定 |
|------|----------------------|------|
| Req 1-1: deletion（main） | Component 1, protect-main.json | OK |
| Req 1-2: non_fast_forward（main） | Component 1, protect-main.json | OK |
| Req 1-3: required_linear_history | Component 1, protect-main.json | OK |
| Req 1-4: pull_request 必須化 | Component 1, protect-main.json | OK |
| Req 1-5: required_approving_review_count: 1 | 設計で 0 に変更（要件との乖離） | **要確認** |
| Req 1-6: required_status_checks 必須化 | Component 1, protect-main.json | OK |
| Req 1-7: lint + analyze チェック | protect-main.json の context | OK（M-3 要確認） |
| Req 1-8: PAT バイパス | 管理者バイパスの仕組みセクション | OK |
| Req 1-9: Renovate Bot の CI 通過 | Integration Points | OK |
| Req 2-1: deletion（version-tags） | Component 2, protect-version-tags.json | OK |
| Req 2-2: non_fast_forward（version-tags） | Component 2, protect-version-tags.json | OK |
| Req 2-3: tagpr のバイパス | Integration Points | OK |
| Req 2-4: fnmatch パターン確認 | Data Models の注記 | OK |
| Req 3-1: deletion（major-tags） | Component 3, protect-major-tags.json | OK |
| Req 3-2: non_fast_forward 除外 | Component 3（意図的に除外） | OK |
| Req 3-3: bump_major_tag のバイパス | Integration Points | OK |
| Req 3-4: v[0-9]* パターン確認 | Component 3 の注記 | OK |
| Req 4-1: .github/rulesets/ 配置 | Project Structure | OK |
| Req 4-2: protect-main.json | Component 1 | OK |
| Req 4-3: protect-version-tags.json | Component 2 | OK |
| Req 4-4: protect-major-tags.json | Component 3 | OK |
| Req 4-5: GitHub API スキーマ準拠 | Data Models | OK |
| Req 4-6: 手動適用手順 | Error Handling / Testing Strategy | 部分的（Testing Strategy に記載あり） |
| Req 5-1: docs/adr/003-pat-branch-ruleset.md | Component 4 | OK |
| Req 5-2: ADR 003 の内容 | Component 4 | OK（詳細は実装時確認） |
| Req 5-3: ADR フォーマット準拠 | Component 4 | OK |
| Req 5-4: docs/adr/README.md 更新 | Component 4（明示なし） | **要確認** |

---

## 総括

本設計は PAT 前提での保護強化という方針が明確で、技術的根拠も適切に文書化されている。

**承認のブロッカーとなる必須対応（[must]）:**
1. `required_approving_review_count` の要件乖離の明示的な処理（M-1）
2. `analyze (actions)` のステータスチェック名の実名確認（M-3）

M-1 と M-3 が解決されれば、設計は実装可能な状態となる。M-2（パターン重複の明記）は安全性の観点から必須扱いとしたが、設計への注記追加のみで対応可能であり、実装をブロックするものではない。
