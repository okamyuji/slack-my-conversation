"""utils.pyのテスト."""

from datetime import UTC, datetime

from app.utils import date_to_timestamp, timestamp_to_readable


def test_date_to_timestamp_with_date_only() -> None:
    """日付のみの場合のタイムスタンプ変換テスト."""
    result = date_to_timestamp("2025-04-01")
    expected = datetime(2025, 4, 1, 0, 0, 0, tzinfo=UTC).timestamp()
    assert result == expected


def test_date_to_timestamp_with_datetime() -> None:
    """日時を含む場合のタイムスタンプ変換テスト."""
    result = date_to_timestamp("2025-04-01 10:30:00")
    expected = datetime(2025, 4, 1, 10, 30, 0, tzinfo=UTC).timestamp()
    assert result == expected


def test_date_to_timestamp_invalid_format() -> None:
    """無効な日付形式のテスト."""
    result = date_to_timestamp("invalid-date")
    assert result is None


def test_timestamp_to_readable_with_float() -> None:
    """浮動小数点数のタイムスタンプを読める形式に変換するテスト."""
    timestamp = 1609459200.0  # 2021-01-01 00:00:00 UTC
    result = timestamp_to_readable(timestamp)
    # タイムゾーンによって異なる可能性があるため、形式のみ確認
    assert len(result) == 19  # YYYY-MM-DD HH:MM:SS
    assert "-" in result
    assert ":" in result


def test_timestamp_to_readable_with_string() -> None:
    """文字列のタイムスタンプを読める形式に変換するテスト."""
    timestamp = "1609459200.0"
    result = timestamp_to_readable(timestamp)
    assert len(result) == 19


def test_timestamp_to_readable_invalid() -> None:
    """無効なタイムスタンプの処理テスト."""
    result = timestamp_to_readable("invalid")
    assert result == "invalid"
