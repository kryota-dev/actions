# Code Review: branch-ruleset

## 総合評価

**APPROVE_WITH_COMMENTS**

## 評価サマリー

実装された 3 つの JSON ファイルは design.md のスキーマ定義と正確に合致しており、設計レビュー (design-review.md) の [must] 指摘事項（`v[0-9]*` パターン・fnmatch 仕様の注記）はいずれも適切に反映されている。ADR 003 は英語で記述され、既存 ADR（001, 002）のフォーマットに準拠している。ただし、PR に `.spec-workflow/` ディレクトリの変更が含まれている点は運用ルール上の懸念事項として指摘する。タスク 1〜4 は完了（[x]）、タスク 5〜6 は手動手順のため未完了（[ ]）の状態は適切である。

## テスト・品質チェック結果

- quality:check: 対象外（JSON ファイルと Markdown のみの変更）
- test: 対象外（Workflow ファイルの変更なし）
- build:next: 対象外

## 詳細フィードバック

### [must] 必須修正事項

なし

design-review.md の [must] 指摘事項は以下のとおり対応済みであることを確認した:

- **must-1** (`v[0-9]` → `v[0-9]*`): `protect-major-tags.json` の `conditions.ref_name.include` が `["refs/tags/v[0-9]*"]` となっており、v10 以上に対応している。対応済み。
- **must-2** (`refs/tags/v*.*.*` の fnmatch 仕様確認): `protect-version-tags.json` は `["refs/tags/v*.*.*"]` を維持しつつ、design.md にて fnmatch 仕様（`*` が `.` にマッチすること）の根拠を明記し対応済みとしている。

---

### [should] 推奨改善事項

#### should-1: PR に `.spec-workflow/` ディレクトリの変更が含まれている

**問題箇所**: PR #15 の変更ファイル一覧

以下の `.spec-workflow/` 配下ファイルが実装ブランチに含まれている:

```
.spec-workflow/approvals/branch-ruleset/.snapshots/requirements.md/metadata.json
.spec-workflow/approvals/branch-ruleset/.snapshots/requirements.md/snapshot-001.json
.spec-workflow/approvals/branch-ruleset/.snapshots/requirements.md/snapshot-002.json
.spec-workflow/approvals/branch-ruleset/.snapshots/requirements.md/snapshot-003.json
.spec-workflow/approvals/branch-ruleset/.snapshots/tasks.md/metadata.json
.spec-workflow/approvals/branch-ruleset/.snapshots/tasks.md/snapshot-001.json
.spec-workflow/approvals/branch-ruleset/.snapshots/tasks.md/snapshot-002.json
.spec-workflow/specs/branch-ruleset/design-review.md
.spec-workflow/specs/branch-ruleset/design.md
.spec-workflow/specs/branch-ruleset/requirements.md
.spec-workflow/specs/branch-ruleset/tasks.md
```

これらは SDD ワークフロー内部の管理ファイルであり、リポジトリの実際の成果物（`.github/rulesets/`、`docs/adr/`）とは別の性質を持つ。プロジェクトとして `.spec-workflow/` を main にマージすることを意図しているか確認が必要。

**推奨**: プロジェクト運用上 `.spec-workflow/` を main に含める方針であれば問題ない。含めない方針の場合は PR から除外するか、`.gitignore` への追加を検討する。

#### should-2: `docs/adr/README.md` への ADR 002 エントリの追加

**問題箇所**: `docs/adr/README.md`（差分）

```markdown
* [2. replace-pat-with-github-token-for-release](002-replace-pat-with-github-token-for-release.md)
* [3. branch-ruleset](003-branch-ruleset.md)
```

本 PR で ADR 003 を追加する際に、既存の ADR 002 のエントリも同時に追加されている。ADR 002 の追加は本 PR のスコープ外であり、別 PR で追加されるべき変更である。ただし、実害はなく README としての整合性は向上するため、運用方針次第で許容できる。

---

### [nit] 軽微な指摘

#### nit-1: JSON ファイルのフォーマット統一

3 つの JSON ファイルはいずれも 2 スペースインデントで統一されており、問題なし。

#### nit-2: ADR 003 の日付

`Date: 2026-02-21` は現在日（2026-02-21）と一致しており、正確である。

---

### [ask] 確認事項

#### ask-1: `.spec-workflow/` の main ブランチへの混入方針

本 PR には `.spec-workflow/` 配下の設計ドキュメント・スナップショットが含まれている。これは意図的な運用方針か、それとも実装ブランチへの混入として除外すべきか、プロジェクトオーナーに確認が必要。

---

## 要件カバレッジ

| 要件 | 実装状況 | 判定 |
|------|---------|------|
| Req 1: main への直接 push 制限 | `protect-main.json`（deletion + non_fast_forward） | OK（個人リポジトリ制約により PR 必須化なし、設計書に明記） |
| Req 2: PR の必須化 | 個人リポジトリ制約により未実装（design.md に明記） | OK（制約による意図的未実装） |
| Req 3: 必須ステータスチェック | 個人リポジトリ制約により未実装（design.md に明記） | OK（制約による意図的未実装） |
| Req 4: vX.Y.Z タグの保護 | `protect-version-tags.json`（deletion + non_fast_forward、refs/tags/v*.*.*） | OK |
| Req 5: vX タグの保護と force push 許可 | `protect-major-tags.json`（deletion のみ、refs/tags/v[0-9]*） | OK（v[0-9]* で v10 以上に対応） |
| Req 6: JSON によるバージョン管理 | `.github/rulesets/` 配下に 3 JSON ファイル | OK |
| Req 7: ADR の作成 | `docs/adr/003-branch-ruleset.md` | OK |

## ファイルごとの所見

| ファイル | 変更行数 | 所見 |
|---------|---------|------|
| `.github/rulesets/protect-main.json` | +20 | design.md のスキーマと完全一致。target, conditions, rules, bypass_actors すべて正確 |
| `.github/rulesets/protect-version-tags.json` | +20 | refs/tags/v*.*.* パターン正確。deletion + non_fast_forward 両ルール含む |
| `.github/rulesets/protect-major-tags.json` | +17 | refs/tags/v[0-9]* パターン正確（must-1 対応済み）。deletion のみで non_fast_forward 除外 |
| `docs/adr/003-branch-ruleset.md` | +57 | 英語記述、既存 ADR フォーマット準拠。Context/Decision/Consequences 構造完備 |
| `docs/adr/README.md` | +2 | ADR 002 エントリの追加は本 PR スコープ外だが実害なし |
| `.spec-workflow/specs/branch-ruleset/` | +707 | SDD 管理ファイル群。main への混入が運用方針と合致しているか要確認 |
| `.spec-workflow/approvals/branch-ruleset/` | +116 | 同上 |

## レビュー結論

JSON ファイル・ADR ともに設計書のスキーマ・骨子に正確に準拠しており、設計レビュー [must] 指摘事項はすべて反映済みである。`.spec-workflow/` ディレクトリの混入については運用方針の確認が必要だが、実際の成果物品質には問題がない。

**APPROVE_WITH_COMMENTS** — [should-1] の確認後、問題なければ APPROVE 可能。
