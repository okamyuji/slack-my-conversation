# マルチステージビルドによる効率的なDockerイメージ構築
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder

# 作業ディレクトリの設定
WORKDIR /app

# 環境変数の設定
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# 依存関係ファイルとREADMEのコピー
COPY pyproject.toml uv.lock* README.md ./

# 依存関係のインストール
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# ソースコードのコピー
COPY src ./src

# プロジェクトのインストール
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# 実行ステージ
FROM python:3.14-slim-bookworm

# 非rootユーザーの作成
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

# 作業ディレクトリの設定
WORKDIR /app

# ビルドステージから仮想環境をコピー
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# ソースコードをコピー
COPY --from=builder --chown=appuser:appuser /app/src /app/src
COPY --from=builder --chown=appuser:appuser /app/pyproject.toml /app/

# パスの設定
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 非rootユーザーに切り替え
USER appuser

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import app; print('OK')" || exit 1

# エントリーポイント
ENTRYPOINT ["python", "-m", "app.main"]

