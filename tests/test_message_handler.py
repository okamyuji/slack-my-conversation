"""message_handler.pyのテスト."""

from unittest.mock import mock_open, patch

import pytest

from app.message_handler import (
    display_messages,
    display_statistics,
    filter_messages_by_user,
    save_messages_to_file,
)
from app.types import SlackMessage


def test_filter_messages_by_user(
    sample_messages: list[SlackMessage], target_user_id: str
) -> None:
    """ユーザーによるメッセージフィルタリングのテスト."""
    filtered = filter_messages_by_user(sample_messages, target_user_id)
    assert len(filtered) == 2
    assert all(msg["user"] == target_user_id for msg in filtered)


def test_filter_messages_by_user_no_match(sample_messages: list[SlackMessage]) -> None:
    """マッチするユーザーがいない場合のテスト."""
    filtered = filter_messages_by_user(sample_messages, "U0000000000")
    assert len(filtered) == 0


def test_display_messages_with_messages(
    sample_messages: list[SlackMessage], target_user_id: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """メッセージ表示のテスト."""
    display_messages(sample_messages, target_user_id)
    captured = capsys.readouterr()
    assert f"ユーザー {target_user_id} のメッセージ" in captured.out
    assert "テストメッセージ1" in captured.out


def test_display_messages_empty(
    target_user_id: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """空のメッセージリストの表示テスト."""
    display_messages([], target_user_id)
    captured = capsys.readouterr()
    assert "見つかりませんでした" in captured.out


def test_save_messages_to_file(sample_messages: list[SlackMessage]) -> None:
    """メッセージのファイル保存テスト."""
    with patch("app.message_handler.Path.open", mock_open()) as mock_file:
        save_messages_to_file(sample_messages, "test.json", "U1234567890")
        # openが呼ばれたことを確認
        mock_file.assert_called_once_with("w", encoding="utf-8")


def test_save_messages_to_file_empty(capsys: pytest.CaptureFixture[str]) -> None:
    """空のメッセージリストの保存テスト."""
    save_messages_to_file([], "test.json")
    captured = capsys.readouterr()
    assert "保存するメッセージがありません" in captured.out


def test_display_statistics(
    sample_messages: list[SlackMessage], target_user_id: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """統計情報表示のテスト."""
    display_statistics(sample_messages, target_user_id)
    captured = capsys.readouterr()
    assert "統計情報" in captured.out
    assert "各ユーザーのメッセージ数" in captured.out
    assert "抽出対象" in captured.out

