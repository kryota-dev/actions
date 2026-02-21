# Tasks Document

## Phase 1: JSON ファイル作成（IaC）

- [x] 1. `.github/rulesets/` ディレクトリの作成と `protect-main.json` の作成
  - File: `.github/rulesets/protect-main.json`
  - main ブランチの保護ルールセット JSON を作成する
  - _Leverage: design.md の「protect-main.json の完全スキーマ」セクション_
  - _Requirements: Req 1, Req 4_
  - _Prompt: Role: GitHub Actions / Repository Configuration Engineer | Task: `.github/rulesets/` ディレクトリを作成し、design.md の「protect-main.json の完全スキーマ」に従って `.github/rulesets/protect-main.json` を作成する。スキーマは以下の通り: target="branch", enforcement="active", conditions.ref_name.include=["refs/heads/main"], rules=[deletion, non_fast_forward, required_linear_history, pull_request(required_approving_review_count:0), required_status_checks(lint, "analyze (actions)")], bypass_actors=[]。`jq . .github/rulesets/protect-main.json` で JSON 構文エラーがないことを確認する | Restrictions: JSON にコメントは使用不可。`required_status_checks` のコンテキスト名は `lint` と `analyze (actions)` であり `analyze` ではない（my_codeql.yml が matrix を使用するため）。`integration_id` は省略する | Success: `jq` で構文エラーなし、design.md のスキーマと完全一致_

- [x] 2. `protect-version-tags.json` の作成
  - File: `.github/rulesets/protect-version-tags.json`
  - バージョンタグ（vX.Y.Z）の保護ルールセット JSON を作成する
  - _Leverage: design.md の「protect-version-tags.json の完全スキーマ」セクション_
  - _Requirements: Req 2, Req 4_
  - _Prompt: Role: GitHub Actions / Repository Configuration Engineer | Task: design.md の「protect-version-tags.json の完全スキーマ」に従って `.github/rulesets/protect-version-tags.json` を作成する。スキーマは以下の通り: target="tag", enforcement="active", conditions.ref_name.include=["refs/tags/v*.*.*"], rules=[deletion, non_fast_forward], bypass_actors=[]。`jq . .github/rulesets/protect-version-tags.json` で JSON 構文エラーがないことを確認する | Restrictions: パターンは `refs/tags/v*.*.*`（fnmatch 仕様で `*` はドットを含む任意文字列にマッチ）。`refs/tags/v*` と混同しないこと | Success: `jq` で構文エラーなし、design.md のスキーマと完全一致_

- [x] 3. `protect-major-tags.json` の作成
  - File: `.github/rulesets/protect-major-tags.json`
  - メジャータグ（v1, v2 等）の保護ルールセット JSON を作成する
  - _Leverage: design.md の「protect-major-tags.json の完全スキーマ」セクション_
  - _Requirements: Req 3, Req 4_
  - _Prompt: Role: GitHub Actions / Repository Configuration Engineer | Task: design.md の「protect-major-tags.json の完全スキーマ」に従って `.github/rulesets/protect-major-tags.json` を作成する。スキーマは以下の通り: target="tag", enforcement="active", conditions.ref_name.include=["refs/tags/v[0-9]*"], rules=[deletion のみ], bypass_actors=[]。`jq . .github/rulesets/protect-major-tags.json` で JSON 構文エラーがないことを確認する | Restrictions: `non_fast_forward` ルールは**意図的に除外する**（bump_major_tag の `git push --force` を許容するため）。パターンは `refs/tags/v[0-9]*`（v10 以上の 2 桁メジャーバージョンにも対応） | Success: `jq` で構文エラーなし、design.md のスキーマと完全一致、`non_fast_forward` が含まれていないこと_

## Phase 2: ADR 作成

- [x] 4. `docs/adr/003-pat-branch-ruleset.md` の作成
  - File: `docs/adr/003-pat-branch-ruleset.md`
  - PAT 前提でのブランチルールセット設計の意思決定を英語で記録する
  - _Leverage: `docs/adr/001-repository-environment-setup.md`（フォーマット参照）_
  - _Requirements: Req 5_
  - _Prompt: Role: Technical Writer / Architect | Task: `docs/adr/003-pat-branch-ruleset.md` を英語で作成する。`docs/adr/001-repository-environment-setup.md` のフォーマット（Date / Status / Context / Decision / Consequences）に従うこと。内容に含めるべき事項: (1) PR #13 で GITHUB_TOKEN 化を試みたが PR #16 で revert された背景、(2) GITHUB_TOKEN（github-actions[bot]）前提では個人リポジトリでバイパスアクター設定ができず PR 必須化・ステータスチェック必須化が実現できなかった制約、(3) PAT（APP_TOKEN）はリポジトリオーナーとして認証され個人リポジトリでは管理者バイパスが機能するため強力な保護が可能になった決定、(4) 3 つのルールセット（protect-main, protect-version-tags, protect-major-tags）の設計概要、(5) required_approving_review_count を 0 とした理由（PR 作成者は自分自身を承認できない GitHub 仕様）。Date は 2026-02-21 とする | Restrictions: 英語で記述。コードブロックや箇条書きを活用して読みやすくする | Success: 既存 ADR フォーマットに準拠、英語で記述、設計の意思決定が明確に記録されている_

- [x] 5. `docs/adr/README.md` の更新
  - File: `docs/adr/README.md`
  - ADR 003 のエントリを README に追加する
  - _Leverage: `docs/adr/README.md`（既存エントリの形式）_
  - _Requirements: Req 5_
  - _Prompt: Role: Technical Writer | Task: `docs/adr/README.md` に ADR 003 のエントリを追加する。既存の `* [1. repository-environment-setup](001-repository-environment-setup.md)` の形式に従い、`* [3. pat-branch-ruleset](003-pat-branch-ruleset.md)` を追加する | Restrictions: 既存エントリの形式を変えないこと | Success: ADR 003 のエントリが追加され、番号順に並んでいる_

## Phase 3: 手動適用手順（非自動化タスク）

- [ ] 6. GitHub Web UI でルールセットを適用する（手動）
  - File: なし（GitHub Web UI での操作）
  - 3 つの JSON ファイルを GitHub の Rulesets 設定に適用する
  - _Leverage: `.github/rulesets/protect-main.json`, `.github/rulesets/protect-version-tags.json`, `.github/rulesets/protect-major-tags.json`_
  - _Requirements: Req 4_
  - _Prompt: Role: Repository Administrator | Task: GitHub Web UI（Settings > Rules > Rulesets）で以下の 3 つのルールセットを適用する。各ルールセットは対応する JSON ファイルを参照してパラメータを手動入力する。(1) protect-main: `.github/rulesets/protect-main.json` の内容を適用。(2) protect-version-tags: `.github/rulesets/protect-version-tags.json` の内容を適用。(3) protect-major-tags: `.github/rulesets/protect-major-tags.json` の内容を適用。`required_status_checks` の設定時、`analyze (actions)` のコンテキスト名が正確であることを確認する（`analyze` や `analyze(actions)` ではない）。適用後、設定が正しく反映されていることを Rulesets 画面で確認する | Restrictions: GitHub CLI でのインポート（`gh api --input`）を使用しても可。ただし JSON の `name` フィールドが既存ルールセットと重複しないよう注意 | Success: 3 つのルールセットが `active` 状態で適用されている_

- [ ] 7. ルールセット動作確認（手動）
  - File: なし（動作確認）
  - ルールセット適用後の動作を design.md の Testing Strategy に従って確認する
  - _Leverage: design.md の「Testing Strategy」セクション_
  - _Requirements: Req 1, Req 2, Req 3_
  - _Prompt: Role: Repository Administrator / QA | Task: design.md の「Testing Strategy」セクションに記載された確認手順（確認 1〜6）を実施する。(確認 1) テスト用ブランチを作成し、main への直接 push がブロックされることを確認。(確認 2) PR 作成後、`lint` と `analyze (actions)` のステータスチェックが必須となることを確認。(確認 3) tagpr が main への push・リリース PR 作成を継続できることを確認（管理者バイパスが機能していること）。(確認 4) bump_major_tag の force push が成功することを確認。(確認 5) バージョンタグ（vX.Y.Z）の削除・force push がブロックされることを確認。(確認 6) メジャータグ（v1 等）の削除がブロックされ、force push は成功することを確認 | Restrictions: 確認用に作成したテストブランチや不要なタグは確認後に削除する | Success: 全確認項目が期待通りの動作となる_
