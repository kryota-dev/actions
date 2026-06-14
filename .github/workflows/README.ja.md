[English](README.md) | **日本語**

# Reusable Workflows

## 品質ゲート

| Workflow | Description |
|----------|-------------|
| [actions-lint](docs/actions-lint.ja.md) | GitHub Actions の品質ゲート（actionlint / ls-lint / ghalint / zizmor） |
| [codeql-analysis](docs/codeql-analysis.ja.md) | CodeQL セキュリティスキャン |

## PR 管理

| Workflow | Description |
|----------|-------------|
| [auto-assign-pr](docs/auto-assign-pr.ja.md) | PR 作成者の自動 assignee 設定 |

## コードレビュー

| Workflow | Description |
|----------|-------------|
| [claude-pr-review](docs/claude-pr-review.ja.md) | Claude Code（並列ロールサブエージェント）で PR をレビュー |
| [codex-pr-review](docs/codex-pr-review.ja.md) | Codex（単一の包括的パス）で PR をレビュー |

## リリース

| Workflow | Description |
|----------|-------------|
| [tagpr-release](docs/tagpr-release.ja.md) | tagpr リリース管理とメジャータグ更新 |

## デプロイ

| Workflow | Description |
|----------|-------------|
| [deploy-web-hosting](docs/deploy-web-hosting.ja.md) | FTP / rsync で Web ホスティングサーバーにデプロイ |
| [undeploy-web-hosting](docs/undeploy-web-hosting.ja.md) | FTP / rsync で Web ホスティングサーバーからフィーチャー環境を削除 |

## Usage

他のリポジトリから Reusable Workflow を呼び出す場合:

```yaml
jobs:
  example:
    uses: kryota-dev/actions/.github/workflows/{workflow}.yml@v0
    with:
      # inputs
    secrets:
      # secrets
```

各ワークフローの inputs / secrets / permissions の詳細は上記リンク先のドキュメントを参照してください。

## Internal CI Workflows

このリポジトリ自身の品質管理に使用する内部 CI ワークフロー（`my-` プレフィックス）です。各 Reusable Workflow を呼び出す薄いラッパーとして実装されています。

| Workflow | Trigger | Calls | Description |
|----------|---------|-------|-------------|
| my-test.yml | PR, merge_group | actions-lint.yml | 品質ゲート |
| my-setup-pr.yml | PR opened | auto-assign-pr.yml | 自動 assignee |
| my-release.yml | push (main) | tagpr-release.yml | リリース管理 |
| my-codeql.yml | PR, push (main), merge_group | codeql-analysis.yml | セキュリティスキャン |
| my-update-release-pr.yml | PR labeled (tagpr:major/minor) | tagpr-release.yml | リリース PR バージョン更新 |
| my-claude-pr-review.yml | PR | claude-pr-review.yml | Claude Code によるドッグフード PR レビュー |
