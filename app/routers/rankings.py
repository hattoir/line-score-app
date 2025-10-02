from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ..db import get_db

router = APIRouter(prefix="", tags=["rankings"])

class RankItem(BaseModel):
    account_id: str
    total_score: int
    last_message_at: datetime | None = None

@router.get("/rankings", response_model=list[RankItem])
async def get_rankings(limit: int = 50, db: AsyncSession = Depends(get_db)):
    rows = await db.execute(
        text("""
            SELECT a.account_id, a.total_score,
                   MAX(m.created_at) AS last_message_at
              FROM accounts a
              LEFT JOIN messages m ON m.account_id = a.account_id
             GROUP BY a.account_id, a.total_score
             ORDER BY a.total_score DESC, last_message_at DESC NULLS LAST
             LIMIT :lim
        """),
        {"lim": limit},
    )
    res: list[RankItem] = []
    for r in rows.mappings():
        res.append(
            RankItem(
                account_id=r["account_id"],
                total_score=r["total_score"],
                last_message_at=r["last_message_at"],
            )
        )
    return res
