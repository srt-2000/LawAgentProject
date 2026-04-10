"""
HTML page routes: landing (/) and profile (/profile). Profile requires auth.
"""

from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Request
from starlette.templating import Jinja2Templates

from app.api.routers.constants import RouterFieldNames, FieldValues

from app.api.dependencies.users import CurrentUserDep

templates = Jinja2Templates(directory=FieldValues.TEMPLATES_PATH)
router = APIRouter(tags=[FieldValues.PAGES_TAG])


@router.get("/", response_class=HTMLResponse)
def main_page(request: Request, current_user: CurrentUserDep) -> HTMLResponse:
    """Render the main landing page for authenticated user.

    Args:
        request: FastAPI request object.
        current_user: Authenticated current user.

    Returns:
        HTMLResponse: Rendered index.html template.
    """
    return templates.TemplateResponse(
        name=FieldValues.INDEX_HTML,
        context={
            RouterFieldNames.REQUEST: request,
            RouterFieldNames.PROFILE: current_user,
        },
    )


@router.get("/profile", response_class=HTMLResponse)
def profile(request: Request, current_user: CurrentUserDep) -> HTMLResponse:
    """Render the user profile page.

    Args:
        request: FastAPI request object.
        current_user: Authenticated current user.

    Returns:
        HTMLResponse: Rendered profile.html template with user data.
    """
    return templates.TemplateResponse(
        name=FieldValues.PROFILE_HTML,
        context={
            RouterFieldNames.REQUEST: request,
            RouterFieldNames.PROFILE: current_user,
        },
    )


@router.get("/login", response_class=HTMLResponse)
def login(request: Request) -> HTMLResponse:
    """Render the login/register page."""
    return templates.TemplateResponse(
        name=FieldValues.LOGIN_HTML, context={RouterFieldNames.REQUEST: request}
    )
