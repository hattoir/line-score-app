from fastapi import FastAPI
from .routers import webhook, rankings, accounts
import os

app = FastAPI(title="LINE Scoring Backend")

app.include_router(webhook.router)
app.include_router(rankings.router)
app.include_router(accounts.router)

# 開発用エンドポイント（本番では無効にしたい）
if os.getenv("APP_ENV", "dev") == "dev":
    from .routers import dev
    app.include_router(dev.router)

@app.get("/health")
async def health():
    return {"ok": True}
