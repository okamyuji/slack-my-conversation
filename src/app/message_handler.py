"""メッセージ処理とフィルタリング."""

import json
from pathlib import Path

from app.types import SlackMessage
from app.utils import timestamp_to_readable


def filter_messages_by_user(
    messages: list[SlackMessage], target_user_id: str
) -> list[SlackMessage]:
    """
    特定のユーザーのメッセージのみを抽出.

    Args:
        messages: 全メッセージのリスト
        target_user_id: 抽出したいユーザーのID

    Returns:
        フィルタリングされたメッセージのリスト
    """
    return [message for message in messages if message.get("user") == target_user_id]


def display_messages(messages: list[SlackMessage], user_id: str | None = None) -> None:
    """
    メッセージを見やすい形式で表示.

    Args:
        messages: 表示するメッセージのリスト
        user_id: フィルタリング対象のユーザーID（表示用）
    """
    if not messages:
        if user_id:
            print(f"ユーザー {user_id} のメッセージが見つかりませんでした。")
        else:
            print("メッセージが見つかりませんでした。")
        return

    if user_id:
        print(f"ユーザー {user_id} のメッセージ ({len(messages)}件):\n")
    else:
        print(f"{len(messages)}件のメッセージを取得しました:\n")

    for i, message in enumerate(messages, 1):
        user = message.get("user", "Unknown")
        text = message.get("text", "")
        timestamp = message.get("ts", "")

        # タイムスタンプを人間が読める形式に変換
        readable_time = timestamp_to_readable(timestamp)

        print(f"{i}. User: {user}")
        print(f"   Time: {readable_time} ({timestamp})")
        print(f"   Text: {text}")
        print("-" * 70)


def save_messages_to_file(
    messages: list[SlackMessage], filename: str, user_id: str | None = None
) -> None:
    """
    メッセージをJSONファイルに保存.

    Args:
        messages: 保存するメッセージのリスト
        filename: 保存するファイル名
        user_id: フィルタリング対象のユーザーID（ファイル名に使用）
    """
    if not messages:
        print("保存するメッセージがありません。")
        return

    # ファイル名の生成
    if user_id:
        filename = f"{user_id}_{filename}"

    try:
        filepath = Path(filename)
        with filepath.open("w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        print(f"メッセージを {filename} に保存しました。")
    except OSError as e:
        print(f"ファイル保存エラー: {e}")


def display_statistics(messages: list[SlackMessage], target_user_id: str) -> None:
    """
    メッセージの統計情報を表示.

    Args:
        messages: 全メッセージのリスト
        target_user_id: 抽出対象のユーザーID
    """
    print("\n=== 統計情報 ===")
    user_counts: dict[str, int] = {}
    for message in messages:
        user = message.get("user", "Unknown")
        user_counts[user] = user_counts.get(user, 0) + 1

    print("各ユーザーのメッセージ数:")
    for user, count in sorted(user_counts.items(), key=lambda x: x[1], reverse=True):
        if user == target_user_id:
            print(f"  {user}: {count}件 ← 抽出対象")
        else:
            print(f"  {user}: {count}件")

