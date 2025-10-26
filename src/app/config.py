"""環境変数とアプリケーション設定の管理."""

import os
import sys
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class SlackConfig:
    """Slack API設定を保持するデータクラス."""

    token: str
    channel_id: str
    user_id: str


def validate_environment_variables() -> SlackConfig:
    """
    環境変数を検証し、必要な値を取得する.

    Returns:
        SlackConfig: 検証済みのSlack設定

    Raises:
        SystemExit: 必要な環境変数が設定されていない場合
    """
    # .envファイルを読み込み
    load_dotenv()

    required_vars = {
        "SLACK_TOKEN": "Slack APIトークン",
        "SLACK_CHANNEL_ID": "Slackチャンネル ID",
        "SLACK_USER_ID": "Slack ユーザー ID",
    }

    config_values = {}
    missing_vars = []

    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if not value:
            missing_vars.append(f"  {var_name}: {description}")
        else:
            config_values[var_name] = value

    if missing_vars:
        print("❌ エラー: 必要な環境変数が設定されていません。")
        print("\n設定が必要な環境変数:")
        for var in missing_vars:
            print(var)
        print("\n解決方法:")
        print("1. .envファイルを作成し、必要な値を設定してください")
        print("2. または、環境変数を直接設定してください")
        print("\n例 (.envファイル):")
        print("SLACK_TOKEN=xoxp-your-token-here")
        print("SLACK_CHANNEL_ID=C1234567890")
        print("SLACK_USER_ID=U1234567890")
        sys.exit(1)

    print("✅ 環境変数の設定を確認しました。")
    return SlackConfig(
        token=config_values["SLACK_TOKEN"],
        channel_id=config_values["SLACK_CHANNEL_ID"],
        user_id=config_values["SLACK_USER_ID"],
    )
