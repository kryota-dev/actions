---
name: manage-rulesets
description: GitHub Repository Rulesets の管理（作成・更新・削除・差分確認・エクスポート）。「ルールセット」「rulesets」「ブランチ保護」と言及された際に使用。
---

# GitHub Repository Rulesets 管理

`.github/rulesets/*.json` と `gh` CLI を使用して GitHub Rulesets を管理する。

## 前提

- `gh` CLI 認証済み、リポジトリ管理者権限あり
- ルールセット JSON は `.github/rulesets/` に配置

## 引数 → サブコマンド

| 引数 | 動作 |
|------|------|
| `apply` / `適用` / 引数なし | 全 JSON を GitHub に適用（既存は更新、新規は作成） |
| `list` / `一覧` | ルールセット一覧を表示 |
| `delete <name>` / `削除 <name>` | 指定ルールセットを削除 |
| `delete-all` / `全削除` | 全ルールセットを削除 |
| `diff` / `差分` | ローカル JSON と GitHub 設定の差分を表示 |
| `export` / `エクスポート` | GitHub 設定をローカル JSON にエクスポート |

## 実行方法

スクリプトを実行する。プロジェクトルートから:

```bash
bash .claude/skills/manage-rulesets/scripts/manage-rulesets.sh <subcommand> [args]
```

`delete` と `delete-all` は実行前にユーザーへ確認を求めること。

## API の注意点

- `evaluate` enforcement は Enterprise プラン限定（free/pro では 422 エラー）。`active` / `disabled` のみ使用可能
- 同名ルールセットの作成は 422 `Name must be unique` エラー。スクリプトの `apply` は名前で既存を検索し自動で更新に切り替える
- `diff` で差分が出る場合、GitHub API がデフォルト値（`allowed_merge_methods` 等）を付加するため。`enforcement`, `rules[].type`, `conditions` の差分に着目すること

## 出力形式

操作完了後、結果をテーブルで報告する:

```
| ルールセット | 操作 | 結果 |
|------------|------|------|
| protect-main | 作成 | OK |
```
