"""slack_client.pyのテスト."""

from unittest.mock import Mock, patch

import pytest
import requests

from app.config import SlackConfig
from app.slack_client import SlackAPIError, SlackClient


@pytest.fixture
def slack_client(slack_config: SlackConfig) -> SlackClient:
    """テスト用のSlackClient."""
    return SlackClient(slack_config.token)


def test_slack_client_initialization(slack_config: SlackConfig) -> None:
    """SlackClientの初期化テスト."""
    client = SlackClient(slack_config.token)
    assert client.token == slack_config.token
    assert client.headers == {"Authorization": f"Bearer {slack_config.token}"}


def test_get_conversation_history_success(
    slack_client: SlackClient, slack_config: SlackConfig
) -> None:
    """会話履歴取得成功のテスト."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "ok": True,
        "messages": [{"user": "U123", "text": "test message", "ts": "1609459200.000000"}],
        "has_more": False,
    }
    mock_response.raise_for_status = Mock()

    with patch("requests.get", return_value=mock_response):
        messages = slack_client.get_conversation_history(slack_config.channel_id)
        assert len(messages) == 1
        assert messages[0]["user"] == "U123"


def test_get_conversation_history_pagination(
    slack_client: SlackClient, slack_config: SlackConfig
) -> None:
    """ページネーション処理のテスト."""
    # 1回目のレスポンス
    mock_response1 = Mock()
    mock_response1.json.return_value = {
        "ok": True,
        "messages": [{"user": "U123", "text": "message 1", "ts": "1609459200.000000"}],
        "has_more": True,
        "response_metadata": {"next_cursor": "cursor123"},
    }
    mock_response1.raise_for_status = Mock()

    # 2回目のレスポンス
    mock_response2 = Mock()
    mock_response2.json.return_value = {
        "ok": True,
        "messages": [{"user": "U456", "text": "message 2", "ts": "1609459201.000000"}],
        "has_more": False,
    }
    mock_response2.raise_for_status = Mock()

    with patch("requests.get", side_effect=[mock_response1, mock_response2]):
        messages = slack_client.get_conversation_history(slack_config.channel_id, get_all=True)
        assert len(messages) == 2


def test_get_conversation_history_api_error(
    slack_client: SlackClient, slack_config: SlackConfig
) -> None:
    """APIエラーのテスト."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "ok": False,
        "error": "missing_scope",
    }
    mock_response.raise_for_status = Mock()

    with (
        patch("requests.get", return_value=mock_response),
        pytest.raises(SlackAPIError),
    ):
        slack_client.get_conversation_history(slack_config.channel_id)


def test_search_user_messages_success(slack_client: SlackClient, slack_config: SlackConfig) -> None:
    """メッセージ検索成功のテスト."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "ok": True,
        "messages": {
            "matches": [{"user": "U123", "text": "search result", "ts": "1609459200.000000"}]
        },
    }
    mock_response.raise_for_status = Mock()

    with patch("requests.get", return_value=mock_response):
        messages = slack_client.search_user_messages(slack_config.channel_id, slack_config.user_id)
        assert len(messages) == 1
        assert messages[0]["user"] == "U123"


def test_search_user_messages_api_error(
    slack_client: SlackClient, slack_config: SlackConfig
) -> None:
    """検索APIエラーのテスト."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "ok": False,
        "error": "invalid_arguments",
    }
    mock_response.raise_for_status = Mock()

    with (
        patch("requests.get", return_value=mock_response),
        pytest.raises(SlackAPIError),
    ):
        slack_client.search_user_messages(slack_config.channel_id, slack_config.user_id)


def test_get_conversation_history_http_error(
    slack_client: SlackClient, slack_config: SlackConfig
) -> None:
    """HTTPエラーのテスト."""
    with (
        patch("requests.get", side_effect=requests.RequestException("Network error")),
        pytest.raises(SlackAPIError, match="HTTP Error"),
    ):
        slack_client.get_conversation_history(slack_config.channel_id)


def test_search_user_messages_with_date_range(
    slack_client: SlackClient, slack_config: SlackConfig
) -> None:
    """日付範囲指定の検索テスト."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "ok": True,
        "messages": {"matches": []},
    }
    mock_response.raise_for_status = Mock()

    with patch("requests.get", return_value=mock_response) as mock_get:
        slack_client.search_user_messages(
            slack_config.channel_id,
            slack_config.user_id,
            after="2025-04-01",
            before="2025-04-30",
        )
        # クエリパラメータに日付が含まれることを確認
        call_args = mock_get.call_args
        assert "after:2025-04-01" in call_args[1]["params"]["query"]
        assert "before:2025-04-30" in call_args[1]["params"]["query"]
