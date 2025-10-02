import os
from fastapi import APIRouter, Request, Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ..db import get_db
from ..ai_scoring import score_with_ai
from ..utils.line_verify import verify_line_signature

router = APIRouter(tags=["webhook"])

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")

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
        if ev.get("type") != "message":
            continue
        msg = ev.get("message") or {}
        if msg.get("type") != "text":
            continue

        message_text = msg.get("text", "")
        source = ev.get("source") or {}
        account_id = source.get("userId") or "unknown"

        # 採点
        score = score_with_ai(message_text)

        # トランザクション：アカウント作成（なければ）→メッセージ保存→合計点更新
        async with db.begin():
            # upsert 的に INSERT（重複なら何もしない）
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
