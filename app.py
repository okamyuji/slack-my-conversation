"""
Slack メッセージ取得ツール

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

import json
import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv


def validate_environment_variables() -> Dict[str, str]:
    """
    環境変数を検証し、必要な値を取得する
    
    Returns:
        環境変数の辞書
        
    Raises:
        SystemExit: 必要な環境変数が設定されていない場合
    """
    # .envファイルを読み込み
    load_dotenv()
    
    required_vars = {
        'SLACK_TOKEN': 'Slack APIトークン',
        'SLACK_CHANNEL_ID': 'Slackチャンネル ID',
        'SLACK_USER_ID': 'Slack ユーザー ID'
    }
    
    config = {}
    missing_vars = []
    
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if not value:
            missing_vars.append(f"  {var_name}: {description}")
        else:
            config[var_name] = value
    
    if missing_vars:
        print("❌ エラー: 必要な環境変数が設定されていません。")
        print("\\n設定が必要な環境変数:")
        for var in missing_vars:
            print(var)
        print("\\n解決方法:")
        print("1. .envファイルを作成し、必要な値を設定してください")
        print("2. または、環境変数を直接設定してください")
        print("\\n例 (.envファイル):")
        print("SLACK_TOKEN=xoxp-your-token-here")
        print("SLACK_CHANNEL_ID=C1234567890")
        print("SLACK_USER_ID=U1234567890")
        sys.exit(1)
    
    print("✅ 環境変数の設定を確認しました。")
    return config


def date_to_timestamp(date_str: str) -> Optional[float]:
    """
    日付文字列をUNIXタイムスタンプに変換
    
    Args:
        date_str: 日付文字列 (例: "2025-04-01", "2025-04-01 10:30:00")
    
    Returns:
        UNIXタイムスタンプ（浮動小数点数）
    """
    try:
        # 時刻が指定されていない場合は00:00:00を補完
        if len(date_str) == 10:  # YYYY-MM-DD
            date_str += " 00:00:00"
        
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        # タイムゾーンを日本時間として扱う
        dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except ValueError as e:
        print(f"日付形式エラー: {e}")
        print("正しい形式: YYYY-MM-DD または YYYY-MM-DD HH:MM:SS")
        return None


def get_conversation_history(
    channel_id: str, 
    token: str, 
    limit: int = 100, 
    oldest: str = None, 
    latest: str = None,
    get_all: bool = False
) -> Optional[List[Dict]]:
    """
    Slackチャンネルの会話履歴を取得する
    
    必要なスコープ:
    - channels:history (パブリックチャンネル用)
    - groups:history (プライベートチャンネル用)
    - im:history (DM用)
    - mpim:history (グループDM用)
    
    Args:
        channel_id: チャンネルID
        token: Slack APIトークン
        limit: 一度に取得する最大件数（最大200件）
        oldest: 開始日時 (例: "2025-04-01" または "2025-04-01 10:30:00")
        latest: 終了日時 (例: "2025-04-30" または "2025-04-30 23:59:59")
        get_all: Trueの場合、ページネーションで全件取得
    
    Returns:
        メッセージのリスト
    """
    url = "https://slack.com/api/conversations.history"
    headers = {"Authorization": f"Bearer {token}"}
    
    # パラメータの設定
    params = {
        "channel": channel_id, 
        "limit": min(limit, 200)  # 最大200件
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
    
    all_messages = []
    
    try:
        while True:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['ok']:
                messages = data['messages']
                all_messages.extend(messages)
                
                # ページネーション処理
                if get_all and data.get('has_more') and data.get('response_metadata', {}).get('next_cursor'):
                    params['cursor'] = data['response_metadata']['next_cursor']
                    print(f"取得中... 現在 {len(all_messages)} 件")
                else:
                    break
            else:
                error_msg = data.get('error', 'Unknown error')
                print(f"Slack API Error: {error_msg}")
                
                # エラーの詳細な説明を提供
                if error_msg == 'missing_scope':
                    print("\n=== 解決方法 ===")
                    print("Slack APIトークンに以下のスコープが必要です:")
                    print("- channels:history (パブリックチャンネル用)")
                    print("- groups:history (プライベートチャンネル用)")
                    print("- im:history (ダイレクトメッセージ用)")
                    print("- mpim:history (グループDM用)")
                    print("\nSlack App管理画面でこれらのスコープを追加し、")
                    print("ワークスペースに再インストールしてください。")
                elif error_msg == 'channel_not_found':
                    print(f"チャンネルID '{channel_id}' が見つかりません。")
                elif error_msg == 'not_in_channel':
                    print("Botがこのチャンネルのメンバーではありません。")
                
                return None
        
        print(f"取得完了: 合計 {len(all_messages)} 件のメッセージを取得しました")
        return all_messages
            
    except requests.RequestException as e:
        print(f"HTTP Error: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        return None


def search_user_messages(
    channel_id: str, 
    user_id: str, 
    token: str, 
    count: int = 100, 
    after: str = None, 
    before: str = None
) -> Optional[List[Dict]]:
    """
    search.messages APIを使用して特定のユーザーのメッセージを直接取得する
    
    必要なスコープ:
    - search:read (メッセージ検索用)
    
    Args:
        channel_id: チャンネルID
        user_id: 検索したいユーザーID
        token: Slack APIトークン
        count: 取得するメッセージ数（最大1000）
        after: 開始日時 (例: "2025-04-01" または "2025-04-01")
        before: 終了日時 (例: "2025-04-30" または "2025-04-30")
    
    Returns:
        検索結果のメッセージリスト
    """
    url = "https://slack.com/api/search.messages"
    headers = {"Authorization": f"Bearer {token}"}
    
    # 検索クエリを構築: 特定のチャンネルで特定のユーザーからのメッセージ
    query_parts = [f"in:<#{channel_id}>", f"from:<@{user_id}>"]
    
    # 日付範囲の指定
    if after:
        query_parts.append(f"after:{after}")
    if before:
        query_parts.append(f"before:{before}")
    
    query = " ".join(query_parts)
    
    params = {
        "query": query,
        "count": min(count, 1000),  # 最大1000件
        "sort": "timestamp",
        "sort_dir": "desc"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data['ok']:
            messages = data.get('messages', {}).get('matches', [])
            print(f"検索クエリ: {query}")
            print(f"検索結果: {len(messages)}件のメッセージが見つかりました")
            return messages
        else:
            error_msg = data.get('error', 'Unknown error')
            print(f"Slack Search API Error: {error_msg}")
            
            # エラーの詳細な説明を提供
            if error_msg == 'missing_scope':
                print("\n=== 解決方法 ===")
                print("Slack APIトークンに以下のスコープが必要です:")
                print("- search:read (メッセージ検索用)")
                print("\nSlack App管理画面でこのスコープを追加し、")
                print("ワークスペースに再インストールしてください。")
            elif error_msg == 'invalid_arguments':
                print("検索クエリが無効です。チャンネルIDやユーザーIDを確認してください。")
            
            return None
            
    except requests.RequestException as e:
        print(f"HTTP Error: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        return None


def filter_messages_by_user(messages: List[Dict], target_user_id: str) -> List[Dict]:
    """
    特定のユーザーのメッセージのみを抽出
    
    Args:
        messages: 全メッセージのリスト
        target_user_id: 抽出したいユーザーのID
    
    Returns:
        フィルタリングされたメッセージのリスト
    """
    return [message for message in messages if message.get('user') == target_user_id]


def display_messages(messages: List[Dict], user_id: str = None):
    """
    メッセージを見やすい形式で表示
    
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
        user = message.get('user', 'Unknown')
        text = message.get('text', '')
        timestamp = message.get('ts', '')
        
        # タイムスタンプを人間が読める形式に変換
        try:
            from datetime import datetime
            readable_time = datetime.fromtimestamp(float(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
            readable_time = timestamp
        
        print(f"{i}. User: {user}")
        print(f"   Time: {readable_time} ({timestamp})")
        print(f"   Text: {text}")
        print("-" * 70)


def save_messages_to_file(messages: List[Dict], filename: str, user_id: str = None):
    """
    メッセージをJSONファイルに保存
    
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
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        print(f"メッセージを {filename} に保存しました。")
    except Exception as e:
        print(f"ファイル保存エラー: {e}")


def main():
    # 環境変数の検証と取得
    config = validate_environment_variables()
    
    token = config['SLACK_TOKEN']
    channel_id = config['SLACK_CHANNEL_ID']
    target_user_id = config['SLACK_USER_ID']
    
    print(f"🔧 設定情報:")
    print(f"  チャンネルID: {channel_id}")
    print(f"  ユーザーID: {target_user_id}")
    print(f"  トークン: {token[:20]}... (一部のみ表示)")
    
    print("=== 取得方法を選択してください ===")
    print("1. 直接検索（推奨）: search.messages APIで特定ユーザーのメッセージのみを取得")
    print("2. 全取得後フィルタ: 全メッセージを取得してからフィルタリング")
    
    choice = input("選択してください (1/2): ").strip()
    
    # 共通設定の取得
    print("\n=== 詳細設定（オプション）===")
    
    # 取得件数の設定
    limit_input = input("取得件数を指定してください（デフォルト: 100、最大値はAPI次第）: ").strip()
    limit = int(limit_input) if limit_input.isdigit() else 100
    
    # 日付範囲の設定
    print("\n日付範囲を指定できます（例: 2025-04-01）:")
    start_date = input("開始日（省略可）: ").strip() or None
    end_date = input("終了日（省略可）: ").strip() or None
    
    if choice == "1":
        # 方法1: search.messages APIを使用して直接特定ユーザーのメッセージを取得
        print(f"\n[方法1] 検索APIでユーザー {target_user_id} のメッセージを直接取得中...")
        print(f"設定: 件数={limit}, 開始={start_date or '制限なし'}, 終了={end_date or '制限なし'}")
        
        user_messages = search_user_messages(
            channel_id, 
            target_user_id, 
            token, 
            count=limit,
            after=start_date,
            before=end_date
        )
        
        if user_messages:
            display_messages(user_messages, target_user_id)
            
            # ファイル保存の確認
            save_choice = input("\nメッセージをJSONファイルに保存しますか？ (y/n): ").strip().lower()
            if save_choice == 'y':
                filename = f"slack_messages_{channel_id}.json"
                save_messages_to_file(user_messages, filename, target_user_id)
        else:
            print("メッセージの取得に失敗しました。")
            print("注意: search:read スコープが必要です。")
    
    elif choice == "2":
        # 方法2: 従来の方法（全メッセージ取得後フィルタリング）
        print(f"\n[方法2] チャンネル {channel_id} の全メッセージを取得してからフィルタリング...")
        print(f"設定: 件数={limit}, 開始={start_date or '制限なし'}, 終了={end_date or '制限なし'}")
        
        # 全件取得の確認
        get_all_input = input("\n全メッセージを取得しますか？（y/n、デフォルト: n）: ").strip().lower()
        get_all = get_all_input == 'y'
        
        messages = get_conversation_history(
            channel_id, 
            token,
            limit=limit,
            oldest=start_date,
            latest=end_date,
            get_all=get_all
        )
        
        if messages:
            print(f"全体で{len(messages)}件のメッセージを取得しました。")
            
            # 特定のユーザーのメッセージのみを抽出
            user_messages = filter_messages_by_user(messages, target_user_id)
            
            # フィルタリング結果を表示
            display_messages(user_messages, target_user_id)
            
            # ファイル保存の確認
            save_choice = input("\nメッセージをJSONファイルに保存しますか？ (y/n): ").strip().lower()
            if save_choice == 'y':
                filename = f"slack_messages_{channel_id}.json"
                save_messages_to_file(user_messages, filename, target_user_id)
            
            # 全ユーザーの統計情報も表示
            print("\n=== 統計情報 ===")
            user_counts = {}
            for message in messages:
                user = message.get('user', 'Unknown')
                user_counts[user] = user_counts.get(user, 0) + 1
            
            print("各ユーザーのメッセージ数:")
            for user, count in sorted(user_counts.items(), key=lambda x: x[1], reverse=True):
                if user == target_user_id:
                    print(f"  {user}: {count}件 ← 抽出対象")
                else:
                    print(f"  {user}: {count}件")
                    
        else:
            print("メッセージの取得に失敗しました。")
    
    else:
        print("無効な選択です。プログラムを終了します。")


if __name__ == "__main__":
    main()