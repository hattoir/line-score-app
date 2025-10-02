from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ..db import get_db

router = APIRouter(prefix="/accounts", tags=["accounts"])

class MessageItem(BaseModel):
    id: int
    message: str
    score: int
    created_at: datetime

class AccountDetail(BaseModel):
    account_id: str
    total_score: int
    messages: list[MessageItem]

@router.get("/{account_id}", response_model=AccountDetail)
async def get_account_detail(account_id: str, db: AsyncSession = Depends(get_db)):
    acct = await db.execute(
        text("SELECT account_id, total_score FROM accounts WHERE account_id = :aid"),
        {"aid": account_id},
    )
    arow = acct.mappings().first()
    if not arow:
        raise HTTPException(404, "Account not found")

    msgs = await db.execute(
        text("""
            SELECT id, message, score, created_at
              FROM messages
             WHERE account_id = :aid
             ORDER BY created_at DESC
             LIMIT 100
        """),
        {"aid": account_id},
    )
    messages = [
        MessageItem(
            id=m["id"],
            message=m["message"],
            score=m["score"],
            created_at=m["created_at"],
        )
        for m in msgs.mappings()
    ]
    return AccountDetail(
        account_id=arow["account_id"], total_score=arow["total_score"], messages=messages
    )
