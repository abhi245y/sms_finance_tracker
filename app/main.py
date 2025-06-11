from fastapi import FastAPI
from app.core.config import settings

# from app.db.session import engine
# from app.db.base_class import Base

from app.api.v1.endpoints import transactions as transactions_v1
from app.api.v1.endpoints import categories as categories_v1
from app.api.v1.endpoints import accounts as accounts_v1
from app.api.v1.endpoints import telegram_webhook as telegram_webhook_v1


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

app.include_router(
    transactions_v1.router, 
    prefix=f"{settings.API_V1_STR}/transactions", 
    tags=["transactions"]
)

app.include_router(
    categories_v1.router,
    prefix=f"{settings.API_V1_STR}/categories",
    tags=["Categories"]
)

app.include_router(
    accounts_v1.router,
    prefix=f"{settings.API_V1_STR}/accounts",
    tags=["Accounts"]
)

app.include_router(
    telegram_webhook_v1.router,
    prefix=f"{settings.API_V1_STR}/telegram",
    tags=["Telegram"],
)

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}!"}

# Optional: Add startup event to ensure DB tables are created if not using Alembic for local dev
# @app.on_event("startup")
# async def startup_event():
#      Base.metadata.create_all(bind=engine)