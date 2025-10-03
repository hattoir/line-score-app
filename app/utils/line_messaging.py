import os
import httpx
from typing import Dict, Any

LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN", "")

def send_line_reply_message(reply_token: str, message: Dict[str, Any]):
    """
    LINE Messaging API にリプライメッセージを送信する
    """
    if not LINE_ACCESS_TOKEN:
        print("LINE_ACCESS_TOKEN is not configured. Cannot send reply.")
        return

    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}",
    }
    
    # 送信ボディの構築
    body = {
        "replyToken": reply_token,
        "messages": [message]
    }

    try:
        # httpx.Client を使用して同期的にリクエストを送信
        with httpx.Client(timeout=5.0) as client:
            response = client.post(url, headers=headers, json=body)
            response.raise_for_status()
            print(f"LINE reply sent successfully. Status: {response.status_code}")
    except httpx.HTTPStatusError as e:
        print(f"Failed to send LINE reply. HTTP error: {e.response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def create_terms_message(base_url: str) -> Dict[str, Any]:
    """
    グループ追加時の利用規約と同意ボタンを含むメッセージボディを生成する
    """
    terms_url = f"{base_url}/terms" 
    
    # Quick Reply（簡易的なボタン）メッセージの構造
    return {
        "type": "text",
        "text": (
            "【性格診断Botへようこそ！】\n\n"
            "メッセージを採点し、グループの総合スコアを算出します。\n"
            "詳細は以下の利用規約をご確認ください。\n"
            f"利用規約: {terms_url}\n\n"
            "同意いただける場合は「同意する」を押して、Botの利用を開始してください。"
        ),
        "quickReply": {
            "items": [
                {
                    "type": "action",
                    "action": {
                        "type": "message",
                        "label": "同意する",
                        "text": "Bot利用に同意しました。"
                    }
                }
            ]
        }
    }

def create_ranking_message(ranking_url: str, is_group: bool) -> Dict[str, Any]:
    """
    ランキングURLを提示するメッセージボディを生成する
    """
    if is_group:
        text_message = (
            "グループの最新スコアランキングURLが発行されました。\n"
            "このURLにアクセスすると、グループ全体の合計スコアとメッセージ履歴を確認できます。\n\n"
        )
    else:
        text_message = (
            "あなたの個人スコア詳細URLが発行されました。\n"
            "このURLにアクセスすると、あなたの合計スコアとメッセージ履歴を確認できます。\n\n"
        )

    return {
        "type": "text",
        "text": f"{text_message}ランキングURL: {ranking_url}"
    }