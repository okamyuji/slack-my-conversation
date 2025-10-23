"""config.pyのテスト."""

import os
from unittest.mock import patch

import pytest

from app.config import SlackConfig, validate_environment_variables


def test_slack_config_initialization() -> None:
    """SlackConfigの初期化テスト."""
    config = SlackConfig(
        token="xoxp-test-token", channel_id="C123456", user_id="U123456"
    )
    assert config.token == "xoxp-test-token"
    assert config.channel_id == "C123456"
    assert config.user_id == "U123456"


def test_validate_environment_variables_success() -> None:
    """環境変数の検証が成功するテスト."""
    with patch.dict(
        os.environ,
        {
            "SLACK_TOKEN": "xoxp-test-token",
            "SLACK_CHANNEL_ID": "C123456",
            "SLACK_USER_ID": "U123456",
        },
    ):
        config = validate_environment_variables()
        assert config.token == "xoxp-test-token"
        assert config.channel_id == "C123456"
        assert config.user_id == "U123456"


def test_validate_environment_variables_missing() -> None:
    """必要な環境変数が欠けている場合のテスト."""
    with (
        patch("app.config.load_dotenv"),  # .envファイルの読み込みをモック
        patch.dict(os.environ, {}, clear=True),
        pytest.raises(SystemExit),
    ):
        validate_environment_variables()


def test_validate_environment_variables_partial() -> None:
    """一部の環境変数のみ設定されている場合のテスト."""
    with (
        patch("app.config.load_dotenv"),  # .envファイルの読み込みをモック
        patch.dict(
            os.environ,
            {"SLACK_TOKEN": "xoxp-test-token"},
            clear=True,
        ),
        pytest.raises(SystemExit),
    ):
        validate_environment_variables()

