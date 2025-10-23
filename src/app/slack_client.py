"""Slack API クライアント."""

import json
from typing import Any

import requests

from app.types import SearchResponse, SlackMessage, SlackResponse
from app.utils import date_to_timestamp


class SlackAPIError(Exception):
    """Slack API エラー."""

    pass


class SlackClient:
    """Slack API クライアント."""

    def __init__(self, token: str) -> None:
        """
        SlackClientの初期化.

        Args:
            token: Slack APIトークン
        """
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"}

    def get_conversation_history(
        self,
        channel_id: str,
        limit: int = 100,
        oldest: str | None = None,
        latest: str | None = None,
        get_all: bool = False,
    ) -> list[SlackMessage]:
        """
        Slackチャンネルの会話履歴を取得する.

        必要なスコープ:
        - channels:history (パブリックチャンネル用)
        - groups:history (プライベートチャンネル用)
        - im:history (DM用)
        - mpim:history (グループDM用)

        Args:
            channel_id: チャンネルID
            limit: 一度に取得する最大件数（最大200件）
            oldest: 開始日時 (例: "2025-04-01" または "2025-04-01 10:30:00")
            latest: 終了日時 (例: "2025-04-30" または "2025-04-30 23:59:59")
            get_all: Trueの場合、ページネーションで全件取得

        Returns:
            メッセージのリスト

        Raises:
            SlackAPIError: API呼び出しに失敗した場合
        """
        url = "https://slack.com/api/conversations.history"

        # パラメータの設定
        params: dict[str, Any] = {
            "channel": channel_id,
            "limit": min(limit, 200),  # 最大200件
        }

        # 日付範囲の指定
        if oldest:
            oldest_ts = date_to_timestamp(oldest)
            if oldest_ts:
                params["oldest"] = oldest_ts

        if latest:
            latest_ts = date_to_timestamp(latest)
            if latest_ts:
                params["latest"] = latest_ts

        all_messages: list[SlackMessage] = []

        try:
            while True:
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
                response.raise_for_status()
                data: SlackResponse = response.json()

                if data["ok"]:
                    messages = data.get("messages", [])
                    all_messages.extend(messages)

                    # ページネーション処理
                    if (
                        get_all
                        and data.get("has_more")
                        and data.get("response_metadata", {}).get("next_cursor")
                    ):
                        params["cursor"] = data["response_metadata"]["next_cursor"]
                        print(f"取得中... 現在 {len(all_messages)} 件")
                    else:
                        break
                else:
                    error_msg = data.get("error") or "Unknown error"
                    self._handle_api_error(error_msg, channel_id)
                    raise SlackAPIError(f"Slack API Error: {error_msg}")

            print(f"取得完了: 合計 {len(all_messages)} 件のメッセージを取得しました")
            return all_messages

        except requests.RequestException as e:
            raise SlackAPIError(f"HTTP Error: {e}") from e
        except json.JSONDecodeError as e:
            raise SlackAPIError(f"JSON Decode Error: {e}") from e

    def search_user_messages(
        self,
        channel_id: str,
        user_id: str,
        count: int = 100,
        after: str | None = None,
        before: str | None = None,
    ) -> list[SlackMessage]:
        """
        search.messages APIを使用して特定のユーザーのメッセージを直接取得する.

        必要なスコープ:
        - search:read (メッセージ検索用)

        Args:
            channel_id: チャンネルID
            user_id: 検索したいユーザーID
            count: 取得するメッセージ数（最大1000）
            after: 開始日時 (例: "2025-04-01" または "2025-04-01")
            before: 終了日時 (例: "2025-04-30" または "2025-04-30")

        Returns:
            検索結果のメッセージリスト

        Raises:
            SlackAPIError: API呼び出しに失敗した場合
        """
        url = "https://slack.com/api/search.messages"

        # 検索クエリを構築: 特定のチャンネルで特定のユーザーからのメッセージ
        query_parts = [f"in:<#{channel_id}>", f"from:<@{user_id}>"]

        # 日付範囲の指定
        if after:
            query_parts.append(f"after:{after}")
        if before:
            query_parts.append(f"before:{before}")

        query = " ".join(query_parts)

        params: dict[str, str | int] = {
            "query": query,
            "count": min(count, 1000),  # 最大1000件
            "sort": "timestamp",
            "sort_dir": "desc",
        }

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data: SearchResponse = response.json()

            if data["ok"]:
                messages: list[SlackMessage] = data.get("messages", {}).get("matches", [])
                print(f"検索クエリ: {query}")
                print(f"検索結果: {len(messages)}件のメッセージが見つかりました")
                return messages

            error_msg = data.get("error") or "Unknown error"
            self._handle_search_error(error_msg)
            raise SlackAPIError(f"Slack Search API Error: {error_msg}")

        except requests.RequestException as e:
            raise SlackAPIError(f"HTTP Error: {e}") from e
        except json.JSONDecodeError as e:
            raise SlackAPIError(f"JSON Decode Error: {e}") from e

    def _handle_api_error(self, error_msg: str, channel_id: str) -> None:
        """
        API エラーの詳細な説明を提供.

        Args:
            error_msg: エラーメッセージ
            channel_id: チャンネルID
        """
        print(f"Slack API Error: {error_msg}")

        if error_msg == "missing_scope":
            print("\n=== 解決方法 ===")
            print("Slack APIトークンに以下のスコープが必要です:")
            print("- channels:history (パブリックチャンネル用)")
            print("- groups:history (プライベートチャンネル用)")
            print("- im:history (ダイレクトメッセージ用)")
            print("- mpim:history (グループDM用)")
            print("\nSlack App管理画面でこれらのスコープを追加し、")
            print("ワークスペースに再インストールしてください。")
        elif error_msg == "channel_not_found":
            print(f"チャンネルID '{channel_id}' が見つかりません。")
        elif error_msg == "not_in_channel":
            print("Botがこのチャンネルのメンバーではありません。")

    def _handle_search_error(self, error_msg: str) -> None:
        """
        検索API エラーの詳細な説明を提供.

        Args:
            error_msg: エラーメッセージ
        """
        print(f"Slack Search API Error: {error_msg}")

        if error_msg == "missing_scope":
            print("\n=== 解決方法 ===")
            print("Slack APIトークンに以下のスコープが必要です:")
            print("- search:read (メッセージ検索用)")
            print("\nSlack App管理画面でこのスコープを追加し、")
            print("ワークスペースに再インストールしてください。")
        elif error_msg == "invalid_arguments":
            print("検索クエリが無効です。チャンネルIDやユーザーIDを確認してください。")

