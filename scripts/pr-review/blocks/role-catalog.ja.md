# レビュアーロールカタログ（Claude 用の Single Source of Truth）

> 参照用の日本語訳です。ランタイムでは英語版（[`role-catalog.md`](role-catalog.md)）が埋め込まれて使用されます。

各 `trigger` を PR の変更ファイルに対して評価してロールを選択します。マッチしたロールのみ（および下表で未カバーの PR 固有観点があれば ad-hoc ロールを1つ追加）を、設定された上限の範囲で起動します。各ロールは1つの並列サブエージェントになります。

| role | trigger | 一次責任 |
|------|---------|----------|
| `correctness` | `always` | ロジック／ランタイム／データ整合性のバグ |
| `security` | `always` | 脆弱性、機密情報漏洩、認可、安全でないデフォルト |
| `performance` | `extensions=.ts,.tsx,.js,.jsx,.go,.rb,.py,.rs,.java,.kt,.sql` | ホットパス、N+1、アロケーション、ブロッキング I/O |
| `tests` | `paths=**/*test*,**/*spec*,**/tests/**,**/__tests__/**` | 新規パスのカバレッジ、エッジ／エラーケース、flaky |
| `api-interface` | `paths=**/api/**,**/*.proto,**/*.graphql,**/openapi*; extensions=.d.ts` | 破壊的変更、契約／後方互換性 |
| `docs` | `paths=**/*.md,**/*.mdx; exclude_paths=**/CHANGELOG.md` | ドキュメントとコードの整合性 |
| `github-actions` | `paths=.github/workflows/**,.github/actions/**` | SHA ピン、最小権限、テンプレートインジェクション |

trigger 構文: `always` ｜ `paths=<glob,...>` ｜ `extensions=<.ext,...>`、任意で `; exclude_paths=<glob,...>` を付与。`paths`/`extensions` トリガーは、いずれかの変更ファイルがマッチし、かつ `exclude_paths` にマッチしないときに発火する。

新しい観点を追加するには、この表に行を1つ足す（ロール選定が定義される唯一の場所）。
