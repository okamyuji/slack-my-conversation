"""
Slack メッセージ取得ツール メインモジュール.

機能:
- 特定ユーザーのメッセージを効率的に取得
- 日付範囲による絞り込み（例: 2025-04-01 以降）
- 取得件数の指定（最大値はAPIに依存）
- ページネーション対応で大量データ取得
- JSONファイルへの保存機能

Slack API上限:
- search.messages API: 最大1000件まで
- conversations.history API: 最大200件/回（ページネーション可能）

必要なスコープ:
- search:read（検索API用）
- channels:history, groups:history, im:history, mpim:history（履歴API用）
"""

from app.config import validate_environment_variables
from app.message_handler import (
    display_messages,
    display_statistics,
    filter_messages_by_user,
    save_messages_to_file,
)
from app.slack_client import SlackAPIError, SlackClient


def get_user_input(prompt: str, default: str | None = None) -> str:
    """
    ユーザー入力を取得する.

    Args:
        prompt: 入力プロンプト
        default: デフォルト値

    Returns:
        ユーザーの入力値
    """
    user_input = input(prompt).strip()
    if not user_input and default is not None:
        return default
    return user_input


def main() -> None:
    """メインエントリーポイント."""
    # 環境変数の検証と取得
    config = validate_environment_variables()

    print("🔧 設定情報:")
    print(f"  チャンネルID: {config.channel_id}")
    print(f"  ユーザーID: {config.user_id}")
    print(f"  トークン: {config.token[:20]}... (一部のみ表示)")

    # Slackクライアントの初期化
    client = SlackClient(config.token)

    print("\n=== 取得方法を選択してください ===")
    print("1. 直接検索（推奨）: search.messages APIで特定ユーザーのメッセージのみを取得")
    print("2. 全取得後フィルタ: 全メッセージを取得してからフィルタリング")

    choice = get_user_input("選択してください (1/2): ")

    # 共通設定の取得
    print("\n=== 詳細設定（オプション）===")

    # 取得件数の設定
    limit_input = get_user_input("取得件数を指定してください（デフォルト: 100）: ")
    limit = int(limit_input) if limit_input.isdigit() else 100

    # 日付範囲の設定
    print("\n日付範囲を指定できます（例: 2025-04-01）:")
    start_date = get_user_input("開始日（省略可）: ") or None
    end_date = get_user_input("終了日（省略可）: ") or None

    try:
        if choice == "1":
            # 方法1: search.messages APIを使用して直接特定ユーザーのメッセージを取得
            print(f"\n[方法1] 検索APIでユーザー {config.user_id} のメッセージを直接取得中...")
            print(
                f"設定: 件数={limit}, 開始={start_date or '制限なし'}, 終了={end_date or '制限なし'}"
            )

            user_messages = client.search_user_messages(
                config.channel_id,
                config.user_id,
                count=limit,
                after=start_date,
                before=end_date,
            )

            if user_messages:
                display_messages(user_messages, config.user_id)

                # ファイル保存の確認
                save_choice = get_user_input("\nメッセージをJSONファイルに保存しますか？ (y/n): ")
                if save_choice.lower() == "y":
                    filename = f"slack_messages_{config.channel_id}.json"
                    save_messages_to_file(user_messages, filename, config.user_id)
            else:
                print("メッセージの取得に失敗しました。")
                print("注意: search:read スコープが必要です。")

        elif choice == "2":
            # 方法2: 従来の方法（全メッセージ取得後フィルタリング）
            print(
                f"\n[方法2] チャンネル {config.channel_id} の全メッセージを取得してからフィルタリング..."
            )
            print(
                f"設定: 件数={limit}, 開始={start_date or '制限なし'}, 終了={end_date or '制限なし'}"
            )

            # 全件取得の確認
            get_all_input = get_user_input("\n全メッセージを取得しますか？（y/n、デフォルト: n）: ")
            get_all = get_all_input.lower() == "y"

            messages = client.get_conversation_history(
                config.channel_id,
                limit=limit,
                oldest=start_date,
                latest=end_date,
                get_all=get_all,
            )

            if messages:
                print(f"全体で{len(messages)}件のメッセージを取得しました。")

                # 特定のユーザーのメッセージのみを抽出
                user_messages = filter_messages_by_user(messages, config.user_id)

                # フィルタリング結果を表示
                display_messages(user_messages, config.user_id)

                # ファイル保存の確認
                save_choice = get_user_input("\nメッセージをJSONファイルに保存しますか？ (y/n): ")
                if save_choice.lower() == "y":
                    filename = f"slack_messages_{config.channel_id}.json"
                    save_messages_to_file(user_messages, filename, config.user_id)

                # 全ユーザーの統計情報も表示
                display_statistics(messages, config.user_id)

            else:
                print("メッセージの取得に失敗しました。")

        else:
            print("無効な選択です。プログラムを終了します。")

    except SlackAPIError as e:
        print(f"\n❌ エラーが発生しました: {e}")
    except KeyboardInterrupt:
        print("\n\n⚠️ ユーザーによって中断されました。")
    except Exception as e:
        print(f"\n❌ 予期しないエラーが発生しました: {e}")


if __name__ == "__main__":
    main()
