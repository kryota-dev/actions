# Requirements Document

## Introduction

`auto-assign-pr.yml` Reusable Workflow は PR 作成者を自動的にアサインするワークフローだが、Bot ユーザー（Renovate Bot 等）が作成した PR で `gh pr edit --add-assignee` が失敗する。Bot ユーザーは GitHub 上でアサインできないため、Bot による PR の場合は代替のアサイン先を指定可能にし、指定がない場合はアサイン処理をスキップする必要がある。

関連 Issue: [#28](https://github.com/kryota-dev/actions/issues/28)

## Alignment with Product Vision

このリポジトリは再利用可能な GitHub Actions を一元管理・公開するもの。外部リポジトリから呼び出される Reusable Workflow が Bot PR で失敗すると、呼び出し元の CI 全体に悪影響を与える。Bot PR での柔軟なアサイン対応は、ワークフローの堅牢性と利便性の向上に直結する。

## Requirements

### Requirement 1: Bot ユーザーの PR で代替アサイン先を指定可能にする

**User Story:** リポジトリの管理者として、Bot ユーザーが作成した PR に対して特定のユーザーまたは Organization のチームをアサインできるようにしたい。Bot PR のレビュー担当者を明確にするためである。

#### Acceptance Criteria

1. WHEN `auto-assign-pr.yml` が `workflow_call` で呼び出される THEN 呼び出し元は `bot-assignees` 入力パラメータ（カンマ区切りのユーザー名/チーム名）を指定できること
2. WHEN Bot ユーザーの PR で `bot-assignees` が指定されている THEN `auto-assign-pr.yml` SHALL 指定されたユーザー/チームを PR にアサインすること
3. WHEN Bot ユーザーの PR で `bot-assignees` が未指定（空文字列）の場合 THEN `auto-assign-pr.yml` SHALL アサイン処理をスキップし、正常終了すること
4. WHEN Bot ユーザーの PR でアサインがスキップまたは代替アサインされた場合 THEN ワークフローのログに SHALL その旨が出力されること

### Requirement 2: Bot ユーザーの判定

**User Story:** リポジトリの管理者として、Bot ユーザーが確実に判定されるようにしたい。誤判定による不具合を防ぐためである。

#### Acceptance Criteria

1. WHEN `github.actor_type` が `Bot` の場合 THEN `auto-assign-pr.yml` SHALL 当該 PR を Bot PR として扱うこと
2. IF `github.actor` が `[bot]` で終わる場合 THEN `auto-assign-pr.yml` SHALL 当該 PR を Bot PR として扱うこと

### Requirement 3: 通常ユーザーの PR でのアサイン動作を維持

**User Story:** リポジトリの管理者として、通常ユーザーが作成した PR では引き続き自動アサインが動作してほしい。PR レビュープロセスを効率化するためである。

#### Acceptance Criteria

1. WHEN 通常ユーザー（Human）が PR を作成する THEN `auto-assign-pr.yml` SHALL 従来通り PR 作成者をアサインすること
2. IF `github.actor_type` が `User` の場合 THEN `auto-assign-pr.yml` SHALL `gh pr edit --add-assignee` を実行すること
3. WHEN 通常ユーザーの PR の場合 THEN `bot-assignees` パラメータは無視されること

### Requirement 4: 内部 CI での利用例

**User Story:** このリポジトリの管理者として、`my-setup-pr.yml` で Bot PR が作成された場合に自分（kryota-dev）にアサインされるようにしたい。Bot PR のレビューを漏れなく行うためである。

#### Acceptance Criteria

1. WHEN `my-setup-pr.yml` が `auto-assign-pr.yml` を呼び出す THEN `bot-assignees` に `kryota-dev` を指定すること
2. WHEN Renovate Bot 等が PR を作成した場合 THEN `kryota-dev` が PR にアサインされること

## Non-Functional Requirements

### Code Architecture and Modularity
- **Single Responsibility Principle**: Bot 判定ロジックはワークフロー内のステップとして完結させる
- **Modular Design**: `auto-assign-pr.yml` 内で完結し、他のワークフローに影響を与えない
- **Clear Interfaces**: `workflow_call` に `bot-assignees` 入力パラメータを追加する。既存の動作には影響しない（デフォルト値は空文字列）

### Performance
- Bot 判定は `github.actor_type` のコンテキスト変数で行い、追加の API 呼び出しを避ける

### Security
- 既存の permissions（`pull-requests: write`）の範囲内で実装する。新たな権限は不要
- SHA ピン留めルールは引き続き遵守する

### Reliability
- Bot 判定に `github.actor_type == 'Bot'` を使用し、確実にスキップする
- 判定ロジックの誤りで通常ユーザーの PR がスキップされないようにする
- `bot-assignees` に無効なユーザー名が指定された場合でもワークフローが失敗しないようにする

### Usability
- `bot-assignees` パラメータはオプション（デフォルト: 空文字列）。既存の呼び出し元は変更不要
- 呼び出し元はカンマ区切りで複数のアサイン先を指定可能
