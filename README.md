# todo-portfolio

React・TypeScript、FastAPI、PostgreSQLを使用するポートフォリオ用Todoアプリです。
現在は開発基盤のみ実装しています。ユーザー登録・認証・Todo操作・業務テーブルは未実装です。
要件は[REQUIREMENTS.md](REQUIREMENTS.md)、内部設計は[DESIGN.md](DESIGN.md)を参照してください。

## 前提ソフトウェアとバージョン

Docker EngineとDocker Compose（`docker compose`コマンドを使用できる環境。WindowsではLinuxコンテナ対応のDocker Desktop等）、Gitが必要です。
Dockerの導入や起動は別途行ってください。ホストで品質チェックを実行する場合はNode.jsとuvも使用します。

| 対象 | 採用バージョン | 理由 |
| --- | --- | --- |
| Node.js | 24.21.0 | LTS系列で、Vite・Vitest・jsdomの実行条件を満たす |
| React / React DOM | 19.3.0 | 同一バージョンの安定版を使用 |
| TypeScript | 6.0.3 | typescript-eslintの対応範囲を優先（7系は未採用） |
| Vite / React plugin | 8.3.2 / 6.1.1 | 開発サーバー、Proxy、ビルド、Reactの再読み込み |
| ESLint / typescript-eslint | 10.12.0 / 8.71.0 | TypeScriptと互換性のあるlint構成 |
| Vitest / React Testing Library / jsdom | 5.0.3 / 16.3.3 / 30.1.1 | ブラウザ相当のDOMで最小画面を検証 |
| Python | 3.13.15 | 保守中の3.13系列に固定し、DockerとCIで統一 |
| FastAPI / Uvicorn | 0.142.2 / 0.54.0 | APIと開発サーバーの最小構成 |
| SQLAlchemy / psycopg | 2.1.3 / 3.3.6 | 設計に従う同期PostgreSQL接続。binary配布でビルド環境差を抑える |
| pytest / HTTPX2 | 9.1.1 / 2.13.0 | health APIの単体・PostgreSQL結合テスト |
| Ruff / mypy | 0.16.10 / 2.4.0 | lint・整形確認とstrict型検査 |
| uv | 0.12.23 | Pythonと依存環境を管理し、uv.lockから復元 |
| PostgreSQL | 17.11 | 保守中の17系列を開発・テスト・CIで統一 |

Frontendは`package-lock.json`と`npm ci`、Backendは`uv.lock`と`uv sync --locked`で推移的依存も固定します。
直接依存は`frontend/package.json`と`backend/pyproject.toml`に記録しています。
バージョン更新時はlockファイルも更新し、Docker・CI・ランタイム指定の整合を確認してください。
Alembicは業務モデルを追加する次段階で導入・初期化します。空のMigrationは作成していません。

## 初回セットアップと起動

以下はリポジトリのルートで実行します。`.env`が既にある場合は上書きせず必要な設定を確認してください。

```powershell
Copy-Item .env.example .env
```

macOS/Linuxでは`cp .env.example .env`を使用できます。
`.env`の`POSTGRES_PASSWORD`を自分のローカル開発用の値へ変更してください。
サンプルは本番用の認証情報ではありません。`.env`はGit管理・Docker build contextから除外しています。

```sh
docker compose config --quiet
docker compose up --build -d --wait
docker compose ps
```

初回はイメージ・依存の取得にネットワーク接続が必要です。
`frontend`は起動時にも`npm ci`を実行し、依存Volumeをlockファイルに揃えます。
Frontendのソース変更はVite、BackendのPython変更はUvicornの`--reload`で反映されます。
Docker Desktopでファイル変更が通知されない場合はコンテナを再起動してください。
依存やDockerfileを変更した場合は`docker compose up --build -d --wait`を再実行します。

| サービス | 内容 | ホストからのアクセス |
| --- | --- | --- |
| frontend | React開発サーバー | http://localhost:5173 |
| backend | FastAPI開発サーバー | http://localhost:8000 |
| db | 開発用PostgreSQL、名前付きVolume `dev_db_data` | ホストへ公開しない |
| db-test | test profile専用PostgreSQL、使い捨てtmpfs | 127.0.0.1:5433 |

開発DBとテストDBは別コンテナ・別ストレージです。通常起動で`db-test`は起動しません。
DBのhealthcheckによる起動待ちに加え、Backendのreadinessは毎回DBへ問い合わせます。
アプリ起動時にテーブル作成やMigrationは実行しません。

## 動作確認と停止

ブラウザで http://localhost:5173 を開き、初期画面を確認します。
HTTPの確認例（Windowsでは`curl`の代わりに`curl.exe`を使用）：

```sh
curl -i http://localhost:8000/health/live
curl -i http://localhost:8000/health/ready
curl -i http://localhost:5173/api/v1/not-implemented
docker compose exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1"'
docker compose logs --tail=50 frontend backend db
```

- `/health/live`はDBに接続せず200と`{"status":"ok"}`を返します。
- `/health/ready`はDBへの`SELECT 1`成功時200、接続不能時503と`{"status":"unavailable"}`を返します。接続先・例外詳細は返しません。
- `/api/v1/not-implemented`はBackend由来の404 JSON `{"detail":"Not Found"}`が期待値です。`/api`のPathは書き換えずProxyします。確認のための仮APIは追加していません。
- DB停止時の確認は`docker compose stop db`後にreadyが503、liveが200となることを確認し、`docker compose start db`後にreadyが200へ戻ることを確認します。

```sh
docker compose --profile test down
```

通常停止では開発DBの名前付きVolumeは残ります。`down -v`は開発データも削除するため通常の停止には使いません。
PostgreSQLの初期ユーザー・パスワード・DB名は空のVolumeの初期化時に使用されます。既存Volumeがある状態で`.env`を書き換えてもDB内の認証情報は変更されません。

## 環境変数

| 変数 | 用途 |
| --- | --- |
| POSTGRES_USER / POSTGRES_PASSWORD / POSTGRES_DB | 開発DB初期化とBackend接続。`.env`で設定 |
| DB_HOST / DB_PORT | Backend接続先。Compose内は`db:5432`へ明示的に設定 |
| API_PROXY_TARGET | Viteのサーバー側Proxy先。Compose内は`http://backend:8000`。ホスト起動ではルートの`.env`を読む |
| TEST_DATABASE_URL | pytest結合テスト専用。開発用設定へのフォールバックはしない |

接続パスワードはURL文字列へ連結せずSQLAlchemyのURLオブジェクトで扱います。
Backendはプロセス環境変数を読み、`.env`を直接読みません（Composeが設定を渡します）。
DB設定を`VITE_*`変数へ入れないでください。Proxy設定もブラウザへ埋め込みません。
テストはDB名・ユーザー名が`todo_test`、ホストがlocalhost・127.0.0.1・db-testの場合のみ許可します。
本番DBへのポート転送をテストの接続先に使わないでください。

## Docker内での品質チェック

開発サービスを起動した状態で実行します。

```sh
docker compose exec frontend npm run typecheck
docker compose exec frontend npm run lint
docker compose exec frontend npm test
docker compose exec frontend npm run build
docker compose exec backend uv run --locked ruff check .
docker compose exec backend uv run --locked ruff format --check .
docker compose exec backend uv run --locked mypy
docker compose --profile test up -d --wait db-test
docker compose exec -e TEST_DATABASE_URL=postgresql+psycopg://todo_test:local_test_only@db-test:5432/todo_test backend uv run --locked pytest
```

テストはDBを必要としないlive・ready失敗の単体テストと、実PostgreSQLでready成功を確認する結合テストです。
DB設定がない場合に結合テストを黙ってskipせず失敗させます。SQLiteは使いません。

## ホストでの品質チェック

Node.jsは`frontend/.node-version`と同じバージョンを使用します。

```sh
cd frontend
npm ci
npm run typecheck
npm run lint
npm test
npm run build
npm run dev
```

ホストの`npm run dev`はルートの`.env`にある`API_PROXY_TARGET`を使います。ComposeのFrontendと同時に5173番を使用しないでください。

Backendはuv 0.12.23を用意し、以下を実行します。uvは指定されたPythonを必要に応じて取得します。

```sh
cd backend
uv sync --locked
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy
uv run --locked pytest -m "not integration"
```

全テストには、ルートで`docker compose --profile test up -d --wait db-test`を実行してから、Backendディレクトリで次を実行します。

```powershell
$env:TEST_DATABASE_URL = "postgresql+psycopg://todo_test:local_test_only@127.0.0.1:5433/todo_test"
uv run --locked pytest
```

macOS/Linuxでは`TEST_DATABASE_URL=postgresql+psycopg://todo_test:local_test_only@127.0.0.1:5433/todo_test uv run --locked pytest`を使用します。

## 初期CIとmain保護

`.github/workflows/ci.yml`はPRとmainへのpushで実行します。Linux（Ubuntu 24.04）の単一環境で、path filterはありません。

| Required Status Checkに設定するJob名 | 内容 |
| --- | --- |
| frontend-ci | npm ci、TypeScript、ESLint、Vitest、production build |
| backend-ci | uv sync --locked、Ruff、整形確認、mypy、専用PostgreSQLを使ったpytest |

GitHub側の設定はユーザーが行います。初回CI実行後、上記2つを必須にし、PR経由・最新mainとの検証を要求し、mainへの直接push・通常のバイパスを禁止してください。
利用プランで無料の保護設定が使えるかも確認してください。Workflowの追加だけではmain保護は有効になりません。
E2E・Container build test・本番デプロイ・CDは後続段階です。

## 今回の要件との対応

REQ-NF-001・REQ-NF-003・REQ-NF-004・REQ-NF-007（構成・型・再現性）、REQ-SEC-005・REQ-SEC-010（秘密情報の除外）、REQ-T-008～REQ-T-011（テスト基盤・CI・追跡）、REQ-OPS-006・REQ-OPS-007（手順・health確認）を対象としています。
機能ごとの受入テストや公開環境の運用まで完了したことを意味しません。
