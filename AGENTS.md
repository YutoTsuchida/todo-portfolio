# Portfolio Todo Application

## Project Goal

このプロジェクトは、転職・就職活動で使用するポートフォリオ用の
フルスタックTodoアプリケーションです。

単に動作するコードを作るだけではなく、
設計理由・保守性・テスト・セキュリティを説明できることを重視します。

## Tech Stack

Frontend:

- React
- TypeScript

Backend:

- Python
- FastAPI

Database:

- PostgreSQL

Infrastructure:

- Docker
- GitHub Actions

## Development Principles

- 実装前に既存コードとプロジェクト構成を確認する
- 大きな変更を行う場合は、先に実装計画を提示する
- 不明な仕様を勝手に決めない
- 必要以上に複雑な設計にしない
- 初心者でも理解できる構成を優先する
- 変更理由を説明できるコードを書く
- 既存機能を壊さない

## Frontend Rules

- TypeScriptを使用する
- anyは原則使用しない
- コンポーネントを必要以上に巨大化させない
- API通信処理とUIロジックを可能な範囲で分離する
- エラー処理を省略しない

## Backend Rules

- Pythonには型ヒントを付ける
- FastAPIのrouterにビジネスロジックを集中させない
- DBアクセス処理を適切に分離する
- 入力値のバリデーションを行う
- エラー処理を省略しない

## Database Rules

- PostgreSQLを使用する
- テーブル・カラムの役割を明確にする
- PRIMARY KEY、FOREIGN KEY、NOT NULLなどの制約を適切に使用する
- DB設計を変更するときは変更理由を説明する

## Testing

実装を変更した場合は、関連するテストを追加または更新する。

最低限以下を考慮する。

- 正常系
- 入力値エラー
- 存在しないデータ
- 権限エラー

変更後は可能な限りテストを実行する。

## Security

- APIキー、パスワード、秘密鍵をソースコードに直接書かない
- .envなどの秘密情報をGitへcommitしない
- 認証・認可を実装するときは他ユーザーのデータへアクセスできないようにする
- 依存ライブラリを不必要に追加しない

## Codex Working Rules

Codexは以下の順番で作業する。

1. 関連ファイルを確認する
2. 要件を確認する
3. 必要に応じて実装計画を提示する
4. 最小限の変更を行う
5. テストを実行する
6. 変更内容を説明する

ユーザーから「実装しないでください」と指示された場合、
ファイル変更やコマンド実行を行わず、調査・設計・提案のみを行う。

## Git Commit Rules

- Commit messages must follow Conventional Commits 1.0.0.
- When generating a commit message, use the `conventional-commit` skill.
- Generate commit messages primarily from staged changes.
- Do not execute `git commit` unless explicitly requested by the user.
