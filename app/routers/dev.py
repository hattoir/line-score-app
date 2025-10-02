# app/routers/dev.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ..db import get_db
from ..ai_scoring import score_with_ai

router = APIRouter(prefix="/dev", tags=["dev"])

class DevIngestReq(BaseModel):
    account_id: str
    message: str

@router.post("/ingest")
async def dev_ingest(body: DevIngestReq, db: AsyncSession = Depends(get_db)):
    if not body.account_id or not body.message:
        raise HTTPException(400, "account_id and message are required")

    score = score_with_ai(body.message)
    async with db.begin():
        await db.execute(
            text("""
                INSERT INTO accounts (account_id, total_score)
                VALUES (:aid, 0)
                ON CONFLICT (account_id) DO NOTHING
            """),
            {"aid": body.account_id},
        )
        await db.execute(
            text("""
                INSERT INTO messages (account_id, message, score)
                VALUES (:aid, :msg, :score)
            """),
            {"aid": body.account_id, "msg": body.message, "score": score},
        )
        await db.execute(
            text("""
                UPDATE accounts SET total_score = total_score + :delta
                WHERE account_id = :aid
            """),
            {"delta": score, "aid": body.account_id},
        )
    return {"ok": True, "account_id": body.account_id, "score": score}
