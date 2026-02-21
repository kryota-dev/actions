# Design Review: reusable-workflow-repo-setup

## 総合評価

**APPROVE WITH COMMENTS**

## 評価サマリー

設計全体は要件をほぼ網羅しており、SHA ピン留めポリシー、権限最小化、Renovate + Dependabot Alerts の役割分担など、セキュリティ設計の方針は適切である。一方、いくつかの技術的な不整合・曖昧さが存在するため、実装前に修正・確認を推奨する。特に `my_release.yml` の `bump_major_tag` における未サニタイズのシェル変数展開はスクリプトインジェクションリスクとなるため必須修正が必要である。

---

## 詳細フィードバック

### [must] 必須修正事項

#### M-1: `bump_major_tag` ジョブのシェルインジェクションリスク

**該当箇所**: `my_release.yml` の `bump_major_tag` ジョブ

```yaml
- name: Update major tag
  run: |
    VERSION=${{ needs.tagpr.outputs.tag }}
    MAJOR=${VERSION%%.*}
    git tag -f "$MAJOR"
    git push origin "$MAJOR" --force
```

`${{ needs.tagpr.outputs.tag }}` は GitHub Actions の式展開であり、ワークフロー式が `run:` ブロック内でシェルスクリプトに直接展開される。これは zizmor が検出するテンプレートインジェクション脆弱性（expression injection）に該当する。

`tagpr.outputs.tag` の値が外部から操作可能な場合（例: PR タイトルや ref 経由）、任意シェルコマンドの実行につながる可能性がある。

**修正方法**: 環境変数経由でサニタイズする。

```yaml
- name: Update major tag
  env:
    TAG: ${{ needs.tagpr.outputs.tag }}
  run: |
    MAJOR="${TAG%%.*}"
    git tag -f "$MAJOR"
    git push origin "$MAJOR" --force
```

---

#### M-2: `my_release.yml` の `permissions` 設計と PAT 利用の不整合

**該当箇所**: `my_release.yml` の `tagpr` ジョブ

```yaml
jobs:
  tagpr:
    permissions:
      contents: write
      pull-requests: write
```

設計では `GITHUB_TOKEN` の代わりに `APP_TOKEN`（PAT）を使用する方針だが、PAT を使う場合でも `permissions` ブロックは Job レベルで宣言する必要がある（ghalint の `job_permissions` ポリシーチェックが `permissions` 未宣言をエラーとするため）。

ただし、PAT は `GITHUB_TOKEN` とは異なる認証コンテキストを持つため、`permissions` ブロックは `GITHUB_TOKEN` のスコープを制御するものであり、PAT のスコープとは無関係である。

設計上は PAT（`APP_TOKEN`）を `GITHUB_TOKEN` として `env:` や `with: token:` で渡しているため、`GITHUB_TOKEN` の `permissions` を `contents: write` / `pull-requests: write` に設定することは問題ないが、設計ドキュメントにこの点の説明が不足している。

**修正方法**: 設計ドキュメントに以下の注記を追加する。

> `permissions` ブロックは `GITHUB_TOKEN` のスコープを制御する。PAT（`APP_TOKEN`）は `GITHUB_TOKEN` と独立した認証であり、PAT のスコープは PAT 発行時に設定する（`repo` および `workflow` スコープが必要）。ghalint の `job_permissions` ポリシーを通過させるために `permissions` 宣言は引き続き必要。

---

#### M-3: `my_setup_pr.yml` の `checkout` ステップの不要性明記が曖昧

**該当箇所**: `my_setup_pr.yml` の設計

```yaml
- uses: actions/checkout@<sha> # v4  # 不要な場合は省略可
- name: Add assignee
  run: gh pr edit "$PR_URL" --add-assignee "$ACTOR"
```

設計では「不要な場合は省略可」とコメントしているが、`gh pr edit` コマンドは `checkout` を必要としない。SHA ピン留めポリシーや ghalint の観点から、不要な Action は含めるべきでない。

実装段階で `checkout` を省略した場合、設計と実装が乖離する。設計段階で明確に省略する旨を記載すべきである。

**修正方法**: 設計を以下のように明確化する。

```yaml
jobs:
  add_assignee:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    steps:
      - name: Add assignee
        run: gh pr edit "$PR_URL" --add-assignee "$ACTOR"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          PR_URL: ${{ github.event.pull_request.html_url }}
          ACTOR: ${{ github.actor }}
```

`checkout` は省略すると明記し、設計の曖昧さを排除する。

---

### [imo] 推奨改善事項

#### I-1: `ghalint` の `job_timeout_minutes_is_required` ポリシー対応の検討

**該当箇所**: 設計文書の「ghalint によるポリシー強制」セクション

設計では `job_timeout_minutes_is_required` ポリシーについて「必要に応じて適用」と記載しているが、ghalint のデフォルト設定では このポリシーが有効である場合、全 Job に `timeout-minutes` が必要になる。

内部 CI ワークフロー自体が ghalint の検証対象となるため、`my_test.yml`, `my_release.yml` 等に `timeout-minutes` を追加しないとself-check が失敗する可能性がある。

**推奨**: 各 Job に適切な `timeout-minutes` を設定する（例: lint job は 10分、release job は 15分）か、`ghalint.yaml` で当該ポリシーを明示的に除外する。設計に方針を明記する。

---

#### I-2: `renovate.json5` の `groupName` 設定の欠如

**該当箇所**: `renovate.json5` 設計

現在の設計では `config:recommended` の `patch` グルーピング設定のみで、GitHub Actions 依存関係のグルーピングが明示されていない。GitHub Actions の依存関係が毎週多数の個別 PR として作成される可能性がある。

**推奨**: 以下のようなグルーピング設定を追加する検討をする。

```json5
{
  "packageRules": [
    {
      "matchManagers": ["github-actions"],
      "groupName": "GitHub Actions"
    }
  ]
}
```

---

#### I-3: `my_codeql.yml` のトリガー設計の確認

**該当箇所**: `my_codeql.yml` のトリガー設定と Requirement 3-4

要件（Req 3-4）では「メインブランチでコードが変更されたとき」とあるが、設計では `pull_request` および `merge_group` トリガーも追加している。CodeQL を PR 上でも実行することは品質上は良いが、要件には記載がない。

この設計判断を「要件を超えた品質向上として意図的に追加した」と設計書に明記することを推奨する。

---

#### I-4: `aqua_version: v2.x.x` の具体的バージョン未定

**該当箇所**: `my_test.yml` の ghalint ステップ

```yaml
- uses: aquaproj/aqua-installer@<sha> # v3
  with:
    aqua_version: v2.x.x
```

`v2.x.x` はプレースホルダーであり、設計段階でバージョンを確定しておくか、Renovate Bot による自動更新の対象であることを明記する必要がある。aqua を使う場合、`aqua.yaml` による tool バージョン管理も必要になるが、設計に `aqua.yaml` の記載がない。

**推奨**: `aqua.yaml` ファイルの作成と ghalint バージョン固定を設計に追記する。

---

#### I-5: `my_release.yml` の `bump_major_tag` 実行条件の精度

**該当箇所**: `my_release.yml` の `bump_major_tag` ジョブ

```yaml
if: needs.tagpr.outputs.tag != ''
```

この条件は tagpr がタグを出力した場合に限定しているが、tagpr がリリース PR を作成するフェーズ（タグなし）と、リリース PR がマージされてタグが付与されるフェーズの両方で `my_release.yml` が実行される。設計通りの動作をするが、条件式の意図を設計ドキュメントに明記することを推奨する。

---

### [nits] 軽微な指摘

#### N-1: `zizmor` の実行コマンドの Action 選択

設計の Code Reuse Analysis テーブルでは `zizmorcore/zizmor-action` または `uvx zizmor` と記載しているが、実際の設計詳細では `astral-sh/setup-uv` + `uvx zizmor` の組み合わせを採用している。

`zizmorcore/zizmor-action` を使わない理由（例: SHA ピン留めの柔軟性、バージョン管理のしやすさ等）を設計書に追記するとより明確になる。

---

#### N-2: `release.yml` の `Other Changes` ラベル記法

**該当箇所**: `.github/release.yml`

```yaml
- title: Other Changes
  labels: ["*"]
```

GitHub のリリースノート自動生成では `"*"` はワイルドカードとして機能し、上記カテゴリに含まれないすべての PR を対象とする。この動作は意図通りだが、設計書に動作の説明を追記するとわかりやすい。

---

#### N-3: `ghalint.yaml` の設置場所が未定

設計では「必要な場合のみ」`ghalint.yaml` を作成するとしているが、ghalint は設定ファイルのデフォルト探索パスが `ghalint.yaml`（リポジトリルート）である。明示的に空の excludes を持つファイルを作成するかどうかの方針を明記する。

---

### [ask] 確認事項

#### Q-1: `APP_TOKEN`（PAT）のスコープ要件

設計では「`repo` および `workflow` スコープが必要」と記載しているが、PAT の Fine-grained tokens を使用するか Classic tokens を使用するかの方針が記載されていない。

- Classic PAT: `repo` + `workflow` スコープ
- Fine-grained PAT: `contents: write`、`pull-requests: write`、`workflows: write` 権限

セキュリティ観点から Fine-grained PAT の使用を推奨するが、tagpr が Fine-grained PAT に対応しているかの確認が必要。

**確認**: PAT の種別（Classic / Fine-grained）について方針を明確化してください。

---

#### Q-2: `ls-lint/action` のバージョンと設定の互換性

`ls-lint/action@<sha>` で利用する ls-lint のバージョンによって、`.ls-lint.yml` の設定スキーマが異なる可能性がある。設計では v2 系（`ls-lint/action@<sha> # v2`）を想定しているが、ls-lint v2 の `.ls-lint.yml` スキーマ形式（`ls-lint:` キー配下に設定）が正しいか確認が必要。

**確認**: ls-lint v2 の設定スキーマとの互換性を確認してください。

---

#### Q-3: `Renovate Bot` のインストール状態の前提確認

設計では「Renovate Bot がリポジトリにインストール済みであることを前提とする」と記載しているが、個人リポジトリ `kryota-dev/actions` に Renovate GitHub App がインストールされているか確認が必要。インストールされていない場合、`renovate.json5` を配置しても Renovate は動作しない。

**確認**: `kryota-dev` アカウントまたは `kryota-dev/actions` リポジトリへの Renovate Bot インストール状況を確認してください。

---

### [fyi] 参考情報

#### F-1: `tagpr` と Branch Protection Rules の注意点

tagpr は PAT を使用してもリポジトリの Branch Protection Rules の「Require a pull request before merging」設定がある場合、リリース PR のマージ自体は自動化されないことに注意。tagpr が自動化するのは「リリース PR の作成・更新」と「マージ後のタグ付け」であり、PR のマージ自体は人手が必要。

#### F-2: `ghalint` のセルフチェック問題

内部 CI ワークフロー自身が ghalint の検証対象となるため、設計した `my_test.yml` の全 `uses:` を SHA ピン留めしないと、CI が初回から失敗する。実装時は全 Action の SHA を事前に取得してから YAML を作成する必要がある。

#### F-3: `zizmor` の `--format=github` の動作

`zizmor --format=github .` は GitHub Actions の Workflow コンテキスト外（ローカル実行）では出力が見づらい。ローカルデバッグ用に `zizmor .` （デフォルトフォーマット）も案内として設計書に追記することを検討する。

#### F-4: `CHANGELOG.md` の初期化

tagpr は `CHANGELOG.md` を自動生成するが、ファイルが存在しない場合に初回リリース時に生成される。設計ではプロジェクト構造に `CHANGELOG.md`（tagpr が自動生成）と記載があるが、初期状態では存在しないことを実装者が認識する必要がある。

---

## 要件カバレッジマトリクス

| 要件 | design.md での対応箇所 | 判定 |
|------|----------------------|------|
| Req 1: ls-lint による命名規則チェック | Component 1 (my_test.yml) + Component 5 (.ls-lint.yml) | OK |
| Req 1-1: .github/workflows/ 配下ファイル変更時にCI実行 | my_test.yml の pull_request トリガー | OK |
| Req 1-2: snake_case 違反時にエラー | ls-lint/action ステップ | OK |
| Req 1-3: .ls-lint.yml で snake_case.yml ルール適用 | .ls-lint.yml 設計 | OK |
| Req 2: actionlint / ghalint / zizmor | Component 1 (my_test.yml) | OK |
| Req 2-1: actionlint 実行 | reviewdog/action-actionlint ステップ | OK |
| Req 2-2: reviewdog 経由でインラインコメント | reporter: github-pr-review | OK |
| Req 2-3: ゼロエラー確認 | CI 失敗による暗黙的な保証 | OK |
| Req 2-4〜6: ghalint 実行 | ghalint run ステップ | OK |
| Req 2-8〜11: zizmor 実行 | uvx zizmor ステップ | OK |
| Req 3: 内部CIワークフロー群 | Component 1〜4 | OK |
| Req 3-1: my_test.yml | Component 1 | OK |
| Req 3-2: my_setup_pr.yml | Component 3 | OK |
| Req 3-3: my_release.yml | Component 2 | OK |
| Req 3-4: my_codeql.yml | Component 4 | OK |
| Req 3-5: my_ プレフィックス | Project Structure | OK |
| Req 4: tagpr によるリリース管理 | Component 2 + .tagpr | OK |
| Req 4-1〜3: タグ自動付与・メジャータグ更新 | bump_major_tag ジョブ | OK |
| Req 4-4: .tagpr 設定 | Component 5 (.tagpr) | OK |
| Req 4-5: APP_TOKEN (PAT) 使用 | Secrets マトリクス + Component 2 | OK |
| Req 5: リリースノートカテゴリ | Component 5 (.github/release.yml) | OK |
| Req 5-1: 5カテゴリの設定 | release.yml 設計 | OK |
| Req 5-2: ラベルによる分類 | release.yml の labels 設定 | OK |
| Req 6: Renovate Bot + Dependabot Alerts | Component 5 (renovate.json5) | OK |
| Req 6-1〜2: github-actions / npm 依存関係更新 | config:recommended | OK |
| Req 6-3: [SECURITY] プレフィックス PR | vulnerabilityAlerts 設定 | OK |
| Req 6-4: renovate.json5 設定 | Component 5 | OK |
| Req 6-5: Dependabot Alerts の有効化 | Integration Points に記載 | OK |
| Req 6-6: Version Updates / Security Updates 無効 | .github/dependabot.yml を作成しない方針 | OK |
| Req 7: ADR 管理 | Component 5 (.adr.json + package.json) | OK |
| Req 7-1: docs/adr/ への保存・命名規則 | .adr.json 設計 | OK |
| Req 7-2: npm run adr:new コマンド | package.json scripts | OK |
| Req 7-3: adr を devDependency 管理 | package.json devDependencies | OK |
| Req 8: CODEOWNERS 設定 | Component 5 (.github/CODEOWNERS) | OK |
| Req 8-1: @kryota-dev をデフォルトオーナーに設定 | CODEOWNERS 設計 | OK |
| Req 8-2: PR 作成時の自動アサイン | GitHub 標準機能による | OK |
| Req 9: README とドキュメント構造 | Project Structure | 条件付きOK |
| Req 9-1: リポジトリ目的の記載 | README 更新（詳細未定義） | 条件付きOK |
| Req 9-2: Workflow 一覧セクション（プレースホルダー） | 設計に明示的な記載なし | 要確認 |
| Req 9-3: docs/adr/ への格納 | Project Structure | OK |

**条件付きOK の補足**: Req 9-2 については、設計書に README の更新方針（プレースホルダー含む）の具体的な記載がない。実装時に考慮が必要。

---

## レビュー結論

本設計は全体的に高品質であり、セキュリティ設計（SHA ピン留め、権限最小化、多層的セキュリティチェック）は適切に設計されている。以下の修正後に実装着手可能と判断する。

### 実装前に必須対応すべき項目

1. **[M-1]** `bump_major_tag` のシェルインジェクション修正（環境変数経由への変更）
2. **[M-2]** PAT と permissions の関係を設計ドキュメントに明記
3. **[M-3]** `my_setup_pr.yml` から `checkout` ステップを明確に除外

### 推奨対応項目（実装中に判断可）

1. **[I-4]** `aqua.yaml` の設計追加（ghalint バージョン管理）
2. **[Q-1]** PAT の種別（Classic / Fine-grained）方針の確定
3. **[Q-3]** Renovate Bot のインストール状況確認
