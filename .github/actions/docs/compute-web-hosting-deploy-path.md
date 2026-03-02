# compute-web-hosting-deploy-path

> ソースファイル: [`.github/actions/compute-web-hosting-deploy-path/action.yml`](../compute-web-hosting-deploy-path/action.yml)

`github` コンテキストからブランチ名を自動導出し、デプロイパスと本番判定を計算する Composite Action です。チェックアウト不要で利用できます。

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `base-path-prefix` | プロジェクト固有パスプレフィックス（例: `/<your-project>`） | No | `''` |
| `production-branch` | 本番ブランチ名 | No | `'main'` |
| `ref-name` | ブランチ名オーバーライド（未指定時は `github` コンテキストから自動導出） | No | `''` |

## Outputs

| Name | Description | Example |
|------|-------------|---------|
| `deploy-path` | 完全なデプロイパス | `/<your-project>/_feature/feature-something` or `/<your-project>` |
| `is-production` | 本番デプロイかどうか | `true` or `false` |
| `ref-name` | 実際に使用されたブランチ名（導出値またはオーバーライド値） | `feature-branch` or `main` |

## 動作

### ref-name の導出

`ref-name` 入力が空の場合、`github` コンテキストから自動的にブランチ名を導出します:

| Event | 導出元 | 説明 |
|-------|--------|------|
| `pull_request` | `github.head_ref` | PR のソースブランチ名 |
| `push` | `github.ref_name` | プッシュ先ブランチ名 |
| `repository_dispatch` | `github.ref_name` | デフォルトブランチ名（注意: 本番ブランチとは限らない） |
| `workflow_dispatch` | `github.ref_name` | 実行元ブランチ名 |

### パス計算ロジック

1. ブランチ名の `/` を `-` に置換してサニタイズ（例: `feature/something` → `feature-something`）
2. ブランチ名が `production-branch` と一致 → `is-production=true`、フィーチャーサフィックスなし
3. それ以外 → `is-production=false`、`/_feature/{sanitized-branch-name}` を付加
4. `deploy-path` = `base-path-prefix` + フィーチャーサフィックス

### バリデーション

- ref-name が空文字の場合、エラー終了します

## 使用例

### PR / push デプロイ（自動導出）

```yaml
steps:
  - name: Compute deploy path
    id: compute-path
    uses: kryota-dev/actions/.github/actions/compute-web-hosting-deploy-path@v1
    with:
      base-path-prefix: '/<your-project>'
      production-branch: 'main'
```

### repository_dispatch（デフォルトブランチ ≠ 本番ブランチの場合）

```yaml
steps:
  - name: Compute deploy path
    id: compute-path
    uses: kryota-dev/actions/.github/actions/compute-web-hosting-deploy-path@v1
    with:
      base-path-prefix: '/<your-project>'
      production-branch: 'main'
      ref-name: ${{ github.event_name == 'repository_dispatch' && 'main' || '' }}
```

### ref-name オーバーライド（手動 undeploy 等）

```yaml
steps:
  - name: Compute deploy path
    id: compute-path
    uses: kryota-dev/actions/.github/actions/compute-web-hosting-deploy-path@v1
    with:
      base-path-prefix: '/<your-project>'
      ref-name: ${{ github.event.inputs.branch_name }}
```

### Outputs の利用

```yaml
steps:
  - name: Compute deploy path
    id: compute-path
    uses: kryota-dev/actions/.github/actions/compute-web-hosting-deploy-path@v1
    with:
      base-path-prefix: '/<your-project>'

  - name: Use computed values
    run: |
      echo "Deploy path: ${{ steps.compute-path.outputs.deploy-path }}"
      echo "Is production: ${{ steps.compute-path.outputs.is-production }}"
      echo "Ref name: ${{ steps.compute-path.outputs.ref-name }}"
```
