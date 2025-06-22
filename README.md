# Slack メッセージ取得ツール

特定のユーザーのSlackメッセージを効率的に取得・保存するPythonツールです。

## 🚀 機能

- 特定ユーザーのメッセージ抽出: 指定したユーザーのメッセージのみを取得
- 日付範囲指定: 2025-04-01以降など、期間を指定して取得
- 2つの取得方法:
    - 直接検索（推奨）: search.messages APIで効率的に取得
    - 全取得後フィルタ: 全メッセージ取得後にフィルタリング
- 大量データ対応: ページネーション機能で制限なく取得
- JSONファイル保存: 取得したメッセージをファイルに保存
- 環境変数管理: セキュアな設定管理

## 📋 前提条件

- Python 3.7以上
- Slack App（APIトークンが必要）

## 🛠️ セットアップ

### 1. 仮想環境の作成と有効化

```bash
python -m venv venv
source venv/bin/activate
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 3. 環境変数の設定

`.env.sample`をコピーして`.env`ファイルを作成し、実際の値を設定してください：

```bash
cp .env.sample .env
```

`.env`ファイルを編集：

```env
SLACK_TOKEN=xoxp-your-actual-token-here
SLACK_CHANNEL_ID=C1234567890
SLACK_USER_ID=U1234567890
```

### 4. Slack Appの設定

以下のスコープをSlack Appに追加してください：

方法1（推奨）を使用する場合:
    - `search:read`

方法2を使用する場合:
    - `channels:history`
    - `groups:history`
    - `im:history`
    - `mpim:history`

## 🎯 使用方法

### 基本的な実行

```bash
python app.py
```

### 実行時の選択肢

1. 取得方法の選択:
   - 方法1: 直接検索（推奨）- 最大1,000件
   - 方法2: 全取得後フィルタ - 無制限（ページネーション）

2. 詳細設定:
   - 取得件数の指定
   - 日付範囲の指定（例: 2025-04-01）

3. 保存オプション:
   - JSONファイルへの保存

## 📊 API制限

| API | 最大取得件数 | 特徴 |
|-----|-------------|------|
| search.messages | 1,000件 | 効率的、直接検索 |
| conversations.history | 無制限 | ページネーション対応 |

## 📁 ファイル構成

```text
slack-my-conversation/
├── app.py              # メインアプリケーション
├── .env                # 環境変数（実際の値）
├── .env.sample         # 環境変数サンプル
├── requirements.txt    # 依存関係
└── README.md          # このファイル
```

## 🔧 設定値の取得方法

### Slack APIトークン

1. [Slack API Dashboard](https://api.slack.com/apps)にアクセス
2. 該当のアプリを選択
3. 「OAuth & Permissions」から「OAuth Tokens」をコピー

### チャンネルID

- ブラウザ版Slackでチャンネルを開き、URLから取得
- 例: `https://app.slack.com/client/T.../C07S2BXUBV4` → `C07S2BXUBV4`

### ユーザーID

- Slackでユーザープロフィールを開く
- 「その他」→「メンバーIDをコピー」

## ⚠️ 注意事項

- `.env`ファイルは機密情報を含むため、Gitにコミットしないでください
- APIレート制限に注意してください
- 大量データ取得時は時間がかかる場合があります

## 🐛 トラブルシューティング

### 「missing_scope」エラー

- Slack App管理画面で必要なスコープを追加
- ワークスペースに再インストール

### 「channel_not_found」エラー

- チャンネルIDが正しいか確認
- Botがチャンネルのメンバーか確認

### 環境変数エラー

- `.env`ファイルが存在するか確認
- 必要な環境変数が全て設定されているか確認
