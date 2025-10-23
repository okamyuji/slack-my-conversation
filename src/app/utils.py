"""ユーティリティ関数."""

from datetime import UTC, datetime


def date_to_timestamp(date_str: str) -> float | None:
    """
    日付文字列をUNIXタイムスタンプに変換.

    Args:
        date_str: 日付文字列 (例: "2025-04-01", "2025-04-01 10:30:00")

    Returns:
        UNIXタイムスタンプ（浮動小数点数）、エラー時はNone
    """
    try:
        # 時刻が指定されていない場合は00:00:00を補完
        if len(date_str) == 10:  # YYYY-MM-DD
            date_str += " 00:00:00"

        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        # タイムゾーンをUTCとして扱う
        dt = dt.replace(tzinfo=UTC)
        return dt.timestamp()
    except ValueError as e:
        print(f"日付形式エラー: {e}")
        print("正しい形式: YYYY-MM-DD または YYYY-MM-DD HH:MM:SS")
        return None


def timestamp_to_readable(timestamp: str | float) -> str:
    """
    UNIXタイムスタンプを人間が読める形式に変換.

    Args:
        timestamp: UNIXタイムスタンプ（文字列または浮動小数点数）

    Returns:
        人間が読める形式の日時文字列
    """
    try:
        return datetime.fromtimestamp(float(timestamp)).strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return str(timestamp)

