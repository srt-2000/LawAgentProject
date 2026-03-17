"""
Application entry point.

Creates the FastAPI app, mounts static files, and registers routers for
WebSocket chat, HTTP pages, user auth, and chat CRUD.
"""

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from app.api.routers.ws import router as router_ws_chat
from app.api.routers.pages import router as router_pages
from app.api.routers.users import router as router_users
from app.api.routers.chats import router as router_chats


app = FastAPI(title="Agent Chat", description="Law Agent Chat", version="1.0.0")

app.mount("/static", StaticFiles(directory="app/static"), "static")

app.include_router(router_ws_chat)
app.include_router(router_pages)
app.include_router(router_users)
app.include_router(router_chats)
