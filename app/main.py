from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# from app.db.session import engine
# from app.db.base_class import Base

from app.api.v1.endpoints import (
    transactions as transactions_v1,
    categories as categories_v1,
    accounts as accounts_v1,
    telegram_webhook as telegram_webhook_v1,
    budget as budget_v1_router
)

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
    budget_v1_router.router,
    prefix=f"{settings.API_V1_STR}/budget",
    tags=["Budget Management"]
)


app.include_router(
    telegram_webhook_v1.router,
    prefix=f"{settings.API_V1_STR}/telegram",
    tags=["Telegram"],
)


if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/mini-app/{page_name}", response_class=HTMLResponse)
async def read_mini_app(request: Request, page_name: str):
    """
    Serves the HTML file for the Telegram Mini App.
    e.g., /mini-app/edit-transaction will serve templates/mini-app/edit-transaction.html
    """
    return templates.TemplateResponse(
        f"mini-app/{page_name}.html", {"request": request}
    )

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}!"}

# Optional: Add startup event to ensure DB tables are created if not using Alembic for local dev
# @app.on_event("startup")
# async def startup_event():
#      Base.metadata.create_all(bind=engine)