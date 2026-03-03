# compute-web-hosting-deploy-path

GitHub コンテキストと inputs からデプロイパスと本番フラグを計算する Composite Action。

> Source: [`.github/actions/compute-web-hosting-deploy-path/action.yml`](../compute-web-hosting-deploy-path/action.yml)

## Usage

```yaml
- uses: kryota-dev/actions/.github/actions/compute-web-hosting-deploy-path@v1
  with:
    # base-path-prefix - プロジェクト固有のパスプレフィックス（例: /<your-project>）
    # Optional (default: '')
    base-path-prefix: ''

    # production-branch - 本番ブランチ名
    # Optional (default: 'main')
    production-branch: 'main'

    # ref-name - ブランチ名の上書き（空の場合は github context から自動導出）
    # Optional (default: '')
    ref-name: ''
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `base-path-prefix` | プロジェクト固有のパスプレフィックス（例: /&lt;your-project&gt;） | No | `''` |
| `production-branch` | 本番ブランチ名 | No | `'main'` |
| `ref-name` | ブランチ名の上書き（空の場合は github context から自動導出） | No | `''` |

## Outputs

| Name | Description | Example |
|------|-------------|---------|
| `deploy-path` | 完全なデプロイパス | `/my-project`（main ブランチ）、`/my-project/_feature/feat-awesome`（feature ブランチ `feat/awesome`） |
| `is-production` | 本番デプロイかどうか | `true` or `false` |
| `ref-name` | 解決済みの ref 名（導出または上書き） | `main`、`feat/awesome` |

## Examples

### 基本的な使い方

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/compute-web-hosting-deploy-path@v1
    id: compute-path
    with:
      base-path-prefix: '/my-project'
```

### 本番ブランチ名をカスタマイズ

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/compute-web-hosting-deploy-path@v1
    id: compute-path
    with:
      base-path-prefix: '/my-project'
      production-branch: 'master'
```

### ref-name を明示的に指定

```yaml
steps:
  - uses: kryota-dev/actions/.github/actions/compute-web-hosting-deploy-path@v1
    id: compute-path
    with:
      base-path-prefix: '/my-project'
      ref-name: 'feat/awesome'
```

## Behavior

1. ref-name を決定する: `ref-name` input が指定されていればそれを使用する。未指定の場合は `github.event_name` に応じて自動導出する:
   - `pull_request` の場合: `github.head_ref`
   - `repository_dispatch` の場合: `production-branch` の値
   - その他の場合: `github.ref_name`
2. ref-name が空の場合、エラーで終了する
3. ブランチ名をサニタイズする: `/` を `-` に置換する
4. production を判定する: ref-name が `production-branch` と一致すれば `is-production=true` とし、feature suffix は付与しない。一致しなければ `is-production=false` とし、`/_feature/{sanitized-ref}` を feature suffix とする
5. デプロイパスを計算する: `{base-path-prefix}{feature-suffix}`
6. 結果を output に設定する

<!-- ## Migration Guide -->

<!-- Breaking Changes がある場合にコメントアウトを解除して記載する -->
