"""
Application entry point.

Creates the FastAPI app, mounts static files, and registers routers for
WebSocket chat, HTTP pages, user auth, and chat CRUD.
"""

from fastapi import FastAPI, HTTPException, Request
from starlette import status
from starlette.responses import RedirectResponse, JSONResponse
from starlette.staticfiles import StaticFiles

from app.api.routers.ws import router as router_ws_chat
from app.api.routers.pages import router as router_pages
from app.api.routers.users import router as router_users
from app.api.routers.chats import router as router_chats
from app.constants import FieldNames, FieldValues
from app.storage.redis import lifespan

app = FastAPI(
    title="Agent Chat",
    description="Law Agent Chat",
    version="1.0.0",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="app/static"), "static")

app.include_router(router_ws_chat)
app.include_router(router_pages)
app.include_router(router_users)
app.include_router(router_chats)


@app.exception_handler(HTTPException)
async def auth_http_exception_for_html(
        request: Request,
        handling_exception: HTTPException
) -> JSONResponse | RedirectResponse:
    protected_paths: set[str] = {FieldValues.MAIN_PATH_NAME, FieldValues.PROFILE_PATH_NAME}

    if (
        request.method == FieldValues.GET_HTTP_METHOD_NAME
        and request.url.path in protected_paths
        and handling_exception.status_code in {
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN
        }
    ):
        return RedirectResponse(
            url=FieldValues.LOGIN_PATH_NAME,
            status_code=status.HTTP_303_SEE_OTHER
        )

    return JSONResponse(
        status_code=handling_exception.status_code,
        content={FieldNames.DETAIL: handling_exception.detail}
    )
