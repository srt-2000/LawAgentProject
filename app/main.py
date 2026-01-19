"""
Main application entry point.

This module initializes the FastAPI application and includes all routers
for chat, pages, and users functionality.
"""

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from app.api.chat_router import router as router_chat
from app.api.pages_router import router as router_pages
from app.api.users_router import router as router_users


app = FastAPI(title="Agent Chat", description="Law Agent Chat", version="1.0.0")

app.mount("/static", StaticFiles(directory="app/static"), "static")

app.include_router(router_chat)
app.include_router(router_pages)
app.include_router(router_users)
