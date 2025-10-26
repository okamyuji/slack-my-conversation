"""pytest設定とフィクスチャ."""

import pytest

from app.config import SlackConfig
from app.types import SlackMessage


@pytest.fixture
def slack_config() -> SlackConfig:
    """テスト用のSlack設定."""
    return SlackConfig(
        token="xoxp-test-token-123456",
        channel_id="C1234567890",
        user_id="U1234567890",
    )


@pytest.fixture
def sample_messages() -> list[SlackMessage]:
    """テスト用のサンプルメッセージ."""
    return [
        {
            "user": "U1234567890",
            "text": "テストメッセージ1",
            "ts": "1609459200.000000",
            "type": "message",
        },
        {
            "user": "U9876543210",
            "text": "別のユーザーのメッセージ",
            "ts": "1609459201.000000",
            "type": "message",
        },
        {
            "user": "U1234567890",
            "text": "テストメッセージ2",
            "ts": "1609459202.000000",
            "type": "message",
        },
    ]


@pytest.fixture
def target_user_id() -> str:
    """テスト用のターゲットユーザーID."""
    return "U1234567890"
