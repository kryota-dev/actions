# Design Review: branch-ruleset

## 総合評価

**APPROVE_WITH_COMMENTS**

## 評価サマリー

個人リポジトリという制約を正確に把握し、バイパスアクター不可の制限に対して現実的な設計（方針 C）を採用している点は適切である。JSON スキーマの基本構造は正しいが、glob パターンに関して重大な問題が 1 件存在し、`protect-version-tags` の include パターン `refs/tags/v*.*.*` が GitHub Rulesets の fnmatch 仕様に準拠しているか要検証が必要である。また `v[0-9]` による v10 以上の対応漏れは設計上の欠陥として修正を要する。

---

## 詳細フィードバック

### [must] 必須修正事項

#### must-1: `protect-major-tags` の include パターン `v[0-9]` が v10 以上に対応不可

**問題箇所**: `design.md` Ruleset 3: protect-major-tags、JSON スキーマの `conditions.ref_name.include`

```json
"include": ["refs/tags/v[0-9]"]
```

**問題**: `[0-9]` は 1 文字の数字のみにマッチするため、`v10`, `v11`, ..., `v99` 等のメジャータグには一切マッチしない。現状のリリースフローは v0.x.x から始まるため直近の影響は限定的だが、v10 以降でリリースが進んだ際に `bump_major_tag` が作成する `v10` タグが保護されない状態になる。

**修正案**:

```json
"include": ["refs/tags/v[0-9]*"]
```

ただし `refs/tags/v[0-9]*` は `v1`, `v2`, ..., `v99` に加えて `v1.2.3` 形式（`protect-version-tags` 対象）にもマッチする可能性がある。より精密なパターンとして以下も検討する:

```json
"include": ["refs/tags/v[0-9]+"]
```

ただし GitHub Rulesets が正規表現ではなく fnmatch（シェル glob）を使用する場合、`+` は使用不可。GitHub Rulesets の ref パターンは fnmatch ベースであるため、`v[0-9]*` が現実的な選択肢となる。

**対応方針**: パターンを `refs/tags/v[0-9]*` に変更し、`protect-version-tags`（`refs/tags/v*.*.*`）との重複適用の挙動を GitHub UI で実際に確認する。なお、重複適用自体は許容範囲（両ルールの効果が合算される）。

---

#### must-2: `protect-version-tags` の include パターン `refs/tags/v*.*.*` の動作確認必須

**問題箇所**: `design.md` Ruleset 2: protect-version-tags、JSON スキーマの `conditions.ref_name.include`

```json
"include": ["refs/tags/v*.*.*"]
```

**問題**: GitHub Rulesets の ref_name include パターンは fnmatch（glob）を使用する。`*` は多くの glob 実装でスラッシュ以外の任意の文字列にマッチするが、`.` を含む文字列にマッチするかは実装依存である。

具体的には、`v*.*.*` が `v1.2.3` にマッチするかは、GitHub の fnmatch 実装が `.` を `*` でマッチさせるかにかかっている。通常の fnmatch では `*` は `.` を含む任意の文字にマッチするため問題ないが、`v1.2.3` が `refs/tags/v*.*.*` にマッチするかは実際に検証が必要。

**確認方法**:
1. テスト用タグ `v0.0.99-test` を作成してルールセット適用後に削除操作を試み、保護されているか確認する
2. GitHub の公式ドキュメント（Repository Rulesets の ref_name patterns）を参照する

**代替パターン（より明確）**:

```json
"include": ["refs/tags/v*"]
```

この場合 `protect-major-tags` との重複が生じるが、削除禁止ルールの重複適用は問題ない。ただし `protect-version-tags` の意図（バージョンタグのみ保護）が失われるため、`refs/tags/v*.*.*` の動作確認を優先する。

---

### [should] 推奨改善事項

#### should-1: `protect-main` の `non_fast_forward` ルールが tagpr をブロックするリスクの明示

**問題箇所**: `design.md` Ruleset 1: protect-main、Error Handling セクション

設計では「tagpr が main ブランチに push する際は fast-forward のはず」と前提しているが、tagpr の push が non-fast-forward になるケースが存在する。

tagpr は `my_release.yml` の `tagpr` ジョブ内で `Songmu/tagpr` を実行しており、このアクションは Release PR マージ後に `contents: write` 権限の `GITHUB_TOKEN` で main へ直接 push する。通常は fast-forward だが、タイミング次第で non-fast-forward になる可能性を完全には排除できない。

**推奨**: Error Handling セクションの must-1 対応として、`non_fast_forward` ルールが tagpr をブロックした際の明確な対処手順（ルールセットを `disabled` に変更して調査 → 再有効化）を設計書に記載する。

#### should-2: ADR に個人リポジトリ制約の根拠ソースを明記

**問題箇所**: `design.md` ADR 骨子の Context セクション

`"Personal repository constraint: bypass actors cannot be added to ruleset bypass lists."` の記述は正確だが、ADR の Consequences に「この制約を発見した経緯・検証方法」を記録することを推奨する。将来のメンテナーが Organization への移行を検討した場合に、バイパスアクター追加が可能になることを参照できる。

**推奨追記内容**:
```markdown
- If the repository is transferred to an organization, bypass actors (github-actions[bot])
  can be added to ruleset bypass lists, enabling PR requirement enforcement for main.
```

#### should-3: 個人リポジトリオーナーのルールセットバイパスが tagpr に適用されるか要確認

**問題箇所**: `design.md` 個人リポジトリにおけるバイパスアクターの制約 > 注記

設計書の注記:
> 個人リポジトリでは管理者（リポジトリオーナー）は常にルールセットをバイパスできる。

この記述は管理者（人間のアカウント）には適用されるが、`GITHUB_TOKEN` を使用する `github-actions[bot]` がオーナーと同等の権限を持つかは別の問題である。

**実際の動作**:
- `GITHUB_TOKEN` は `github-actions[bot]` として動作するが、これはリポジトリオーナー（人間）とは異なるアクターである
- tagpr が `non_fast_forward` ルールに引っかかる可能性は低い（fast-forward push が前提）が、設計書の注記は「管理者バイパス = tagpr に適用される」と誤解を招く可能性がある

**推奨**: 注記を以下のように修正する:
```
注記: 個人リポジトリでは管理者（リポジトリオーナーである人間のアカウント）は常にルールセットをバイパスできる。
ただし GITHUB_TOKEN で動作する github-actions[bot] は管理者権限を持たない別のアクターであるため、
tagpr・bump_major_tag ジョブはルールセットの制限を受ける。protect-main の non_fast_forward ルールは
tagpr の通常の fast-forward push には影響しないが、異常時にブロックされる可能性がある点に注意する。
```

---

### [nit] 軽微な指摘

#### nit-1: JSON スキーマに `source_type` フィールドの欠落

GitHub Rulesets API の Export JSON には通常 `"source_type": "Repository"` および `"source": "kryota-dev/actions"` フィールドが含まれる。`gh api --method POST` でインポートする場合、これらのフィールドは API 側で無視されるが、Export 機能で出力した JSON と手動作成 JSON の差異として混乱を招く可能性がある。

**推奨**: コメントとして「Export した JSON には `id`, `source`, `source_type`, `created_at`, `updated_at` 等のフィールドが付加されるが、`POST/PUT` 時は省略可能」と設計書に記載する。

#### nit-2: Testing Strategy の検証項目に「tagpr の実際の動作確認」が不足

現状の統合検証は「確認できること」の列挙だが、どのブランチ・タグ状態で検証するかが不明確。テスト用リポジトリでの事前検証を推奨する記述を追加するとよい。

#### nit-3: ADR のファイル番号確認

`docs/adr/` に既存の ADR は `001-repository-environment-setup.md`、`002-replace-pat-with-github-token-for-release.md` の 2 件が確認できた。`003-branch-ruleset.md` の採番は正しい。

---

### [ask] 確認事項

#### ask-1: `bump_major_tag` ジョブの `persist-credentials: false` との整合性

`my_release.yml` の `bump_major_tag` ジョブ（line 39-40）では `persist-credentials: false` で checkout した後、`git remote set-url origin` で `GITHUB_TOKEN` をリモート URL に埋め込んで force push している。

このパターンは `non_fast_forward` ルールの対象となる force push を実行しているが、`protect-major-tags` に `non_fast_forward` ルールを含めていないため意図通りに動作する。この理解は設計意図と合致しているか確認する。

#### ask-2: `protect-version-tags` が tagpr の push をブロックしないという前提の根拠

tagpr は以下の 2 種類の push を行う:
1. main ブランチへの直接 push（リリース PR 作成のため）
2. vX.Y.Z タグの新規作成

設計書では「新規タグ作成はルールの対象外」と明記されており、`deletion` および `non_fast_forward` ルールは既存 ref への操作のみを対象とする。この理解は GitHub Rulesets の仕様に基づいており正確と判断するが、tagpr が既存タグを上書きするケース（同一バージョンの再タグ付け等）があるか確認する。

---

### [fyi] 参考情報

#### fyi-1: GitHub Rulesets の ref_name パターン仕様

GitHub Rulesets の ref_name include/exclude パターンは `fnmatch` ベースであり、以下の特性を持つ:
- `*` は `/` 以外の任意の文字列にマッチ（`.` を含む）
- `?` は任意の 1 文字にマッチ
- `[0-9]` は 1 文字の文字クラスにマッチ
- `**` はサポートされない（ref パターンでは不要）

したがって `refs/tags/v*.*.*` は `refs/tags/v1.2.3` にマッチし、`refs/tags/v[0-9]` は `refs/tags/v1` にマッチするが `refs/tags/v10` にはマッチしない。

#### fyi-2: Organization 移行時のバイパスアクター設定

将来的に Organization に移行した場合、GitHub Rulesets のバイパスリストに以下のアクターを追加できる:
- `github-actions[bot]`（Integration として追加）
- Renovate Bot（GitHub App として追加）

これにより PR 必須化と自動化ボットの共存が可能になる。

#### fyi-3: tagpr が main に push するケース

`my_release.yml` の `tagpr` ジョブ（`Songmu/tagpr@da82ed6...`）は以下の動作をする:
1. リリース PR がマージされると、tagpr がバージョンタグを作成する
2. 次の開発サイクルのために CHANGELOG や設定ファイルを更新して main に直接 push することがある

このうち 2 のケースが fast-forward でない場合、`protect-main` の `non_fast_forward` ルールに引っかかる可能性がある点は、設計書の Error Handling セクションで既に言及されており適切。

---

## 要件カバレッジマトリクス

| 要件 | design.md での対応箇所 | 判定 |
|------|----------------------|------|
| Req 1: main への直接 push 制限 | 方針 C 採用・バイパスアクター不可のため PR 必須化なし、代わり `non_fast_forward` / `deletion` ルール適用 | OK（制約あり、設計書に明記済み） |
| Req 2: PR の必須化 | 個人リポジトリ制約により断念、設計書に理由明記 | OK（制約による未実装、文書化済み） |
| Req 3: 必須ステータスチェック | 個人リポジトリ制約により PR 必須化なしでは効果限定的として未設定 | OK（制約による未実装、文書化済み） |
| Req 4: vX.Y.Z タグの保護 | `protect-version-tags` ルールセット設計（`deletion` + `non_fast_forward`） | OK（ただし glob パターン要検証: must-2） |
| Req 5: vX タグの保護と force push 許可 | `protect-major-tags` ルールセット（`deletion` のみ） | **PARTIAL**（`v[0-9]` が v10 以上に対応不可: must-1） |
| Req 6: JSON によるバージョン管理 | `.github/rulesets/` ディレクトリ設計、`gh api` コマンド手順 | OK |
| Req 7: ADR の作成 | ADR 骨子の設計、`003-branch-ruleset.md` の命名 | OK |

---

## レビュー結論

**APPROVE_WITH_COMMENTS**

[must] 項目 2 件の修正が推奨される:

1. **must-1**: `protect-major-tags` の include パターンを `refs/tags/v[0-9]*` に変更し、v10 以上のメジャータグに対応する
2. **must-2**: `protect-version-tags` の `refs/tags/v*.*.*` パターンが GitHub fnmatch 仕様で期待通り動作することを実際に検証（または代替パターンへの変更）する

これら 2 点は実装前に解決が必要だが、全体的な設計方針（個人リポジトリ制約への適切な対応、JSON IaC 管理、ADR 記録）は妥当であり、[should] / [nit] 項目は実装品質を高めるための推奨事項として対応を判断されたい。
