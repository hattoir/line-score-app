import os
from fastapi import APIRouter, Request, Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ..db import get_db
from ..ai_scoring import score_with_ai
from ..utils.line_verify import verify_line_signature
from ..utils.line_messaging import send_line_reply_message, create_terms_message, create_ranking_message 

router = APIRouter(tags=["webhook"])

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000") # 修正済みのBASE_URLを使用

@router.post("/webhook/line")
async def line_webhook(
    request: Request,
    x_line_signature: str | None = Header(None, alias="X-Line-Signature"),
    db: AsyncSession = Depends(get_db),
):
    if not LINE_CHANNEL_SECRET:
        raise HTTPException(500, "LINE_CHANNEL_SECRET not configured")

    body_bytes = await request.body()

    if not verify_line_signature(LINE_CHANNEL_SECRET, body_bytes, x_line_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    events = payload.get("events", [])
    if not events:
        return {"ok": True, "processed": 0}

    processed = 0
    for ev in events:
        event_type = ev.get("type")
        reply_token = ev.get("replyToken")
        source = ev.get("source") or {}
        source_type = source.get("type", "unknown")
        
        # 1. account_id の決定 (グループ/ルーム/ユーザー対応)
        account_id = None
        is_group_or_room = source_type in ["group", "room"]

        if source_type == "group":
            account_id = source.get("groupId")
        elif source_type == "room":
            account_id = source.get("roomId")
        else:
            account_id = source.get("userId")
        
        if not account_id:
            continue
        
        # =======================================================
        # 2. 【ご要望1】グループ/ルーム参加時 ('join') の処理 (利用規約の送信)
        # =======================================================
        if event_type == "join" and is_group_or_room and reply_token:
            reply_message = create_terms_message(BASE_URL)
            send_line_reply_message(reply_token, reply_message)
            processed += 1
            continue

        # =======================================================
        # 3. メッセージイベントの処理
        # =======================================================
        if event_type == "message":
            msg = ev.get("message") or {}
            if msg.get("type") != "text":
                continue

            message_text = msg.get("text", "")
            
            # 【ご要望2】 特定のワード ("ランキング") への返信処理
            if message_text == "ランキング" and reply_token:
                ranking_url = f"{BASE_URL}/accounts/{account_id}"
                reply_message = create_ranking_message(ranking_url, is_group=is_group_or_room)
                send_line_reply_message(reply_token, reply_message)
                processed += 1
                # ランキング返信の場合、以降の採点・DB保存は行わない
                continue 

            # メッセージ採点・DB保存のメインロジック (上記ランキングワードに一致しない場合のみ実行)
            
            # 採点
            score = score_with_ai(message_text)

            # トランザクション：アカウント作成（なければ）→メッセージ保存→合計点更新
            async with db.begin():
                # account_id (グループIDまたはユーザーID) でアカウントをUPSERT的に作成・更新
                await db.execute(
                    text("""
                        INSERT INTO accounts (account_id, total_score)
                        VALUES (:aid, 0)
                        ON CONFLICT (account_id) DO NOTHING
                    """),
                    {"aid": account_id},
                )
                await db.execute(
                    text("""
                        INSERT INTO messages (account_id, message, score)
                        VALUES (:aid, :msg, :score)
                    """),
                    {"aid": account_id, "msg": message_text, "score": score},
                )
                await db.execute(
                    text("""
                        UPDATE accounts
                           SET total_score = total_score + :delta
                         WHERE account_id = :aid
                    """),
                    {"delta": score, "aid": account_id},
                )

            processed += 1

    return {"ok": True, "processed": processed}