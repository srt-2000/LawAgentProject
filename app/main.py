"""
Application entry point.

Creates the FastAPI app, mounts static files, and registers routers for
WebSocket chat, HTTP pages, user auth, and chat CRUD.
"""

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from app.api.ws_router import router as router_ws_chat
from app.api.pages_router import router as router_pages
from app.api.users_router import router as router_users
from app.api.chats_router import router as router_chats


app = FastAPI(title="Agent Chat", description="Law Agent Chat", version="1.0.0")

app.mount("/static", StaticFiles(directory="app/static"), "static")

app.include_router(router_ws_chat)
app.include_router(router_pages)
app.include_router(router_users)
app.include_router(router_chats)
