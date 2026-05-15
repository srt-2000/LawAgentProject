"""
HTML page routes: landing (/) and profile (/profile). Profile requires auth.
"""

from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Request
from starlette.templating import Jinja2Templates

from app.api.constants import (
    Fields,
    Values,
    TEMPLATES_PATH,
    INDEX_HTML,
    LOGIN_HTML,
    PROFILE_HTML,
)

from app.api.dependencies.users import CurrentUserDep

templates = Jinja2Templates(directory=TEMPLATES_PATH)
router = APIRouter(tags=[Values.PAGES_TAG])


@router.get("/", response_class=HTMLResponse)
async def main_page(request: Request, current_user: CurrentUserDep) -> HTMLResponse:
    """Render the main landing page for authenticated user.

    Args:
        request: FastAPI request object.
        current_user: Authenticated current user.

    Returns:
        HTMLResponse: Rendered index.html template.
    """
    return templates.TemplateResponse(
        name=INDEX_HTML,
        context={
            Fields.REQUEST: request,
            Fields.PROFILE: current_user,
        },
    )


@router.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, current_user: CurrentUserDep) -> HTMLResponse:
    """Render the user profile page.

    Args:
        request: FastAPI request object.
        current_user: Authenticated current user.

    Returns:
        HTMLResponse: Rendered profile.html template with user data.
    """
    return templates.TemplateResponse(
        name=PROFILE_HTML,
        context={
            Fields.REQUEST: request,
            Fields.PROFILE: current_user,
        },
    )


@router.get("/login", response_class=HTMLResponse)
async def login(request: Request) -> HTMLResponse:
    """Render the login/register page."""
    return templates.TemplateResponse(
        name=LOGIN_HTML, context={Fields.REQUEST: request}
    )
