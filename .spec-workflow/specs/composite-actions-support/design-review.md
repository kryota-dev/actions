# Design Review: composite-actions-support

**レビュー日:** 2026-02-21
**レビュアー:** Design Reviewer (テクニカルリードアーキテクト)
**対象バージョン:** design.md (初版)

---

## 総合評価

**APPROVE_WITH_COMMENTS**

設計の全体的な方向性は正しく、要件との対応も概ね良好です。ただし、技術的実現可能性に関して確認が必要な事項（ls-lint の設定キー問題、ghalint run-action の導入バージョン）と、実装時に注意が必要な点が複数あります。[must] 項目を修正のうえ実装に進むことを推奨します。

---

## 詳細フィードバック

### [must] 必須修正事項

#### M-1: ls-lint の設定キーが ls-lint v2 の仕様と不一致

**問題箇所:** `design.md` Component 2 の「変更後の設定」

設計ドキュメントは以下の設定を提案している:

```yaml
ls-lint:
  .github/workflows:
    .yml: snake_case
  .github/composite:
    .dir: kebab-case
    .yml: regex:action
```

しかし、ls-lint v2.x の公式仕様（[ソースコード](https://github.com/loeffel-io/ls-lint/blob/v2.3.1/internal/config/config.go#L22)）では、設定キーは `ls:` であり、`ls-lint:` ではない。ls-lint リポジトリ自身の `.ls-lint.yml` および全サンプルも `ls:` を使用している。

現行の `.ls-lint.yml` が `ls-lint:` キーを使用しているにも関わらず CI が通過しているとすれば、**ls-lint が不明なキーを無視してチェックを実行していない（常に通過）** という危険な状態の可能性がある。

**検証必須事項:**
1. 現行の `ls-lint:` キーで ls-lint が実際にチェックを実行しているか確認する（例: `snake_case` に違反するファイル名で CI が失敗するか）
2. ls-lint v2 の正式キー `ls:` を使用すべきか検討する

**修正案:**
```yaml
ls:
  .github/workflows:
    .yml: snake_case
  .github/composite:
    .dir: kebab-case
    .yml: regex:action
```

または、現行の `ls-lint:` キーが実際に機能していることを確認し、その根拠を設計ドキュメントに明記する。

---

#### M-2: ghalint run-action コマンドの導入バージョン確認が不十分

**問題箇所:** `design.md` Component 3、`Code Reuse Analysis`

設計は `aqua.yaml` の `ghalint@v1.5.5` で `ghalint run-action` が使用可能と述べている。調査の結果、`run-action` コマンドは **v1.5.0 で追加されており**、v1.5.5 は最新版であるため要件を満たしている。

ただし、設計ドキュメントには以下の記述が欠けている:
- `run-action` コマンドが追加されたバージョン（v1.5.0 以降）の明示
- v1.5.0 にはバグが存在し、v1.5.1 以降の使用が推奨されるという注意事項

**修正案:** 設計ドキュメントに「`ghalint run-action` は v1.5.1 以降でサポート（v1.5.5 で確認済み）」と明記する。

---

### [should] 修正推奨事項

#### S-1: ghalint run-action のパスパターン解析に誤りの可能性

**問題箇所:** `design.md` 「ghalint run vs run-action の使い分け」

設計は以下のように述べている:
> `.github/composite/{action-name}/action.yml` は `.github/composite/action-name/action.yml` と展開され、3階層（`.github` / `composite` / `action-name`）となるため、`ghalint run-action` の正規表現パターン `^([^/]+/){0,3}action\.ya?ml$` に合致する。

正規表現 `^([^/]+/){0,3}action\.ya?ml$` の解析:
- `([^/]+/)` は「スラッシュ以外の文字列 + スラッシュ」を表す
- `{0,3}` は 0〜3 回の繰り返し
- `.github/composite/action-name/action.yml` はスラッシュ区切りで **4セグメント** に分解される: `.github/`, `composite/`, `action-name/`, `action.yml`
- つまり `([^/]+/)` が **3回** マッチした後に `action.yml` が続く構造であり、パターンに合致する

この解析は正しいが、設計の「3階層」という表現が「3つのディレクトリ」を指すのか「スラッシュの数」を指すのか曖昧。より正確には「ファイルパスが `action.yml` を含む4セグメント以内」と表現すべき。

**修正案:** 「`.github/composite/{action-name}/action.yml` は `([^/]+/)` が3回マッチする構造であり、上限の `{0,3}` に収まるため検証対象となる」と明記する。

---

#### S-2: actionlint が .github/composite/ を検証対象外とすることの根拠が不確実

**問題箇所:** `design.md` 「actionlint が `.github/composite/` を誤検知しない仕組み」

設計は「`reviewdog/action-actionlint` は内部的に actionlint を `.github/workflows/` ディレクトリに対してのみ実行する」と述べているが、その根拠（具体的な actionlint のデフォルト動作や reviewdog/action-actionlint の実装）が引用されていない。

actionlint のデフォルトは `.github/workflows/` のみをスキャン対象とするが、将来バージョンで `action.yml` もスキャン対象に含まれた場合のフォールバック手順（`reviewdog/action-actionlint` の `filter_mode` や `workdir` 設定）が Error Handling に記載されているのは評価できる。

**修正案:** actionlint の公式ドキュメントまたはソースコードへの参照を追加し、「デフォルトで `.github/workflows/` のみをスキャン対象とする」という事実の根拠を明示する。

---

#### S-3: zizmor の自動検出根拠の明示不足

**問題箇所:** `design.md` Code Reuse Analysis の zizmor 行

設計は「zizmor v1.0.0 以降はディレクトリスキャン時に `action.yml` を自動発見する」と述べているが、現行の `my_test.yml` で使用している zizmor のバージョンが明示されていない。`uvx zizmor` は最新版を使用するため実質的に問題ないが、バージョン固定がされていない点は潜在的なリスク。

また、zizmor が `.github/composite/` 配下の `action.yml` を自動発見するという動作の根拠（公式ドキュメント・リリースノートへの参照）も不足している。

**修正案:**
1. zizmor の対応バージョン（v1.0.0 以降）を明記し、現行の `uvx zizmor` が最新版を使用するため問題ないことを補足する
2. 公式ドキュメントへの参照を追加する

---

#### S-4: Renovate の github-actions マネージャーがデフォルトで .github/composite/ をカバーするかの根拠不足

**問題箇所:** `design.md` Code Reuse Analysis の Renovate 行

設計は「Renovate の `github-actions` マネージャーはデフォルトで `/(^|/)action\.ya?ml$/` パターンに一致するファイルをスキャンする」と述べている。このパターンで `.github/composite/{name}/action.yml` がカバーされることは論理的に正しい。

ただし、現行の `renovate.json5` には `"extends": ["config:recommended", "helpers:pinGitHubActionDigests"]` しか設定されておらず、`github-actions` マネージャーが明示的に有効化されているわけではない。`config:recommended` プリセットに `github-actions` マネージャーが含まれているかどうかの根拠が設計に欠けている。

**修正案:** `config:recommended` に `github-actions` マネージャーが含まれることを Renovate 公式ドキュメントへの参照とともに明記する。

---

### [nit] 軽微な指摘

#### N-1: README 変更案の構造変更は大きすぎる可能性

**問題箇所:** `design.md` Component 4

設計は `## Available Workflows` セクションを `## Usage` と `## Available Actions` に分割するという大きな構造変更を提案している。これは Req 8 の要件（Composite Actions サブセクションの追加）を超えた変更であり、既存の README 構造への影響が大きい。既存の `## Available Workflows` 構造を維持しつつサブセクションを追加するだけで要件を満たせる。

#### N-2: action.yml テンプレートで `outputs` の `value` フィールドに関する説明不足

**問題箇所:** `design.md` Data Models の action.yml 構造テンプレート

```yaml
outputs:
  {output-name}:
    description: "{出力の説明}"
    value: ${{ steps.{step-id}.outputs.{output} }}
```

Composite Actions の `outputs` は `value` フィールドが必須だが、outputs を定義しない場合の省略可否について言及がない。テンプレートに「（outputs が不要な場合は省略可）」を追記することで実装者の混乱を防げる。

#### N-3: .github/composite/ の初期状態（空ディレクトリ）の扱い

**問題箇所:** `design.md` Architecture ディレクトリ構造

「初期は空」とされているが、Git は空ディレクトリを追跡しないため `.gitkeep` の配置が必要。初期コミットに `.gitkeep` を含めることを明記すべき。ただし、ls-lint の `regex:action` ルールが `.gitkeep` ファイルに対してエラーを出す可能性があるため、`ignore` 設定か、サンプル `action.yml` の配置を検討する。

#### N-4: my_test.yml の `shell: bash` 明記

**問題箇所:** `design.md` Component 3 の変更後ステップ

```yaml
- name: Run ghalint run-action
  run: ghalint run-action
  shell: bash
```

`shell: bash` が明記されており、既存の `Run ghalint` ステップと統一されている点は良い。この設計通りに実装することを確認する。

---

### [ask] 確認事項

#### A-1: 現行の ls-lint が実際に機能しているかの確認

`ls-lint:` キー（vs 公式仕様の `ls:` キー）で現行 CI が正しく lint を実行しているかを確認してほしい。確認方法: `snake_case` に違反するファイル名（例: `.github/workflows/myTest.yml`）を一時的に作成し、CI が失敗するかを検証する。

#### A-2: ghalint run-action がカレントディレクトリを参照することの確認

`ghalint run-action` はカレントディレクトリ配下の `action.yml` を再帰的に検索する。`my_test.yml` のステップは `actions/checkout` 後に実行されるため、ワーキングディレクトリはリポジトリルートとなり、`.github/composite/{name}/action.yml` が検出されるはず。ただし、aqua-installer で PATH を設定した後にコマンドを実行する順序が現行の `Run ghalint` ステップと同様であることを確認する。

#### A-3: ls-lint の `regex:action` は `action.yaml` にも対応が必要か

要件 Req 1.1 では `action.yml` のみ言及しているが、GitHub は `action.yml` と `action.yaml` の両方をサポートする。設計の `regex:action` は `action.yml` のみ許可する意図だが、`action.yaml` を意図的に除外しているかを確認してほしい。

---

### [fyi] 参考情報

#### F-1: ghalint run-action の検証内容

`ghalint run-action` は以下のポリシーを検証する（ghalint 公式ドキュメントより）:
- Action 内の `uses:` が full commit SHA でピン留めされているか
- credential 漏洩パターンがないか
- `GITHUB_TOKEN` の不適切な使用がないか

#### F-2: zizmor の Composite Actions 検証

zizmor は Composite Actions（`action.yml`）の以下を検証する:
- template-injection: `${{ inputs.xxx }}` の直接 `run:` 埋め込み
- unpinned-uses: mutable tag の使用
- excessive-permissions: 過剰な権限設定

#### F-3: ls-lint v2 と v1 の設定キーの違い

- ls-lint v1: `ls-lint:` キーを使用
- ls-lint v2: `ls:` キーに変更

現行の `.ls-lint.yml` が `ls-lint:` を使用しているのは v1 時代の設定を引き継いでいる可能性がある。ls-lint v2 では `ls-lint:` キーは無視され、チェックが実行されない可能性があるため、**緊急の検証が必要**。

---

## 要件カバレッジマトリクス

| 要件 | design.md での対応箇所 | 判定 |
|------|----------------------|------|
| Req 1: Composite Actions のディレクトリ構造 | Architecture / Component 1 | OK |
| Req 1.1: `.github/composite/{action-name}/action.yml` 構造 | Architecture ディレクトリ図 / Component 1 | OK |
| Req 1.2: `using: "composite"` の必須化 | Component 1 必須フィールド / Data Models | OK |
| Req 1.3: 外部参照形式 | Component 1 外部参照形式 | OK |
| Req 1.4: ディレクトリ名 kebab-case | Component 2 / ls-lint 設定 | OK (M-1 の確認待ち) |
| Req 1.5: `shell` フィールドの必須化 | Component 1 必須フィールド / Data Models | OK |
| Req 2: ls-lint への Composite Actions 追加 | Component 2 | OK (M-1 の確認待ち) |
| Req 2.1: `.ls-lint.yml` 更新 | Component 2 変更後設定 | OK |
| Req 2.2: kebab-case 違反時の CI 失敗 | Testing Strategy 手動検証 | OK |
| Req 2.3: `action.yml` の命名チェック通過 | Component 2 `regex:action` ルール | OK |
| Req 2.4: CI での全対象ディレクトリ検証 | Testing Strategy CI 自動検証 | OK |
| Req 3: actionlint の誤検知回避 | Architecture / actionlint セクション / Error Handling | OK (S-2 の根拠強化推奨) |
| Req 3.1: `.github/workflows/` のみを検証対象 | actionlint セクション | OK |
| Req 3.2: `.github/composite/` を検証対象外 | actionlint セクション | OK |
| Req 3.3: actionlint エラーなしの CI 通過 | Testing Strategy | OK |
| Req 4: ghalint による Composite Actions 検証 | Component 3 / Code Reuse Analysis | OK (M-2 の確認推奨) |
| Req 4.1: `ghalint run-action` の CI 追加 | Component 3 変更後ステップ | OK |
| Req 4.2: ミュータブルタグのエラー検出 | Error Handling / Testing Strategy | OK |
| Req 4.3: credential 漏洩のエラー検出 | Error Handling | OK |
| Req 4.4: `my_test.yml` への追加 | Component 3 | OK |
| Req 5: zizmor による静的セキュリティ分析 | Code Reuse Analysis / Testing Strategy | OK (S-3 の確認推奨) |
| Req 5.1: 追加設定不要での自動スキャン | Code Reuse Analysis | OK |
| Req 5.2: テンプレートインジェクションの検出 | Error Handling / Data Models | OK |
| Req 5.3: サプライチェーンリスクの警告 | Error Handling | OK |
| Req 5.4: スキャン対象外の場合のフォールバック | Error Handling (actionlint 想定外ケース参照) | 一部不足 (S-3) |
| Req 6: full commit SHA ピン留め | Component 1 / Data Models / Steering Document | OK |
| Req 6.1: full commit SHA でのピン留め | Data Models テンプレート（`uses:` なし）| 間接的 OK |
| Req 6.2: Renovate による自動更新 | Code Reuse Analysis | OK (S-4 の根拠強化推奨) |
| Req 6.3: 違反時の CI エラー | Error Handling | OK |
| Req 7: タグベースリリース管理との整合 | Code Reuse Analysis (.tagpr 行) | OK |
| Req 7.1: タグの Composite Actions への適用 | Code Reuse Analysis | OK |
| Req 7.2: メジャータグの自動追従 | Code Reuse Analysis | OK |
| Req 7.3: 外部参照形式 | Component 1 外部参照形式 | OK |
| Req 7.4: 既存設定変更不要 | Code Reuse Analysis / Architecture 変更ファイル一覧 | OK |
| Req 8: README の更新 | Component 4 | OK (N-1 の軽微な指摘あり) |
| Req 8.1: Composite Actions サブセクションの追加 | Component 4 変更後構造 | OK |
| Req 8.2: 外部参照サンプルの記載 | Component 4 変更後構造 | OK |
| Req 8.3: Coming soon. プレースホルダー | Component 4 変更後構造 | OK |
| Req 8.4: Reusable Workflows との違いの明記 | Component 4 補足説明 | OK |

---

## まとめ

| 分類 | 件数 |
|------|------|
| [must] 必須修正 | 2件 |
| [should] 修正推奨 | 4件 |
| [nit] 軽微な指摘 | 4件 |
| [ask] 確認事項 | 3件 |
| [fyi] 参考情報 | 3件 |

**最優先事項:** M-1（ls-lint 設定キーの検証）は既存 CI の健全性に関わる問題のため、最初に確認・解決することを強く推奨する。
