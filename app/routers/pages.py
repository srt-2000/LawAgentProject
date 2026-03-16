"""
HTML page routes: landing (/) and profile (/profile). Profile requires auth.
"""

from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Request
from starlette.templating import Jinja2Templates

from app.routers.constants import RouterFieldNames, FieldValues

from app.dependencies.users import CurrentUserDep

templates = Jinja2Templates(directory=FieldValues.TEMPLATES_PATH)
router = APIRouter(tags=[FieldValues.PAGES_TAG])


@router.get("/", response_class=HTMLResponse)
async def get_main_page(request: Request) -> HTMLResponse:
    """Render the main landing page.

    Args:
        request: FastAPI request object.

    Returns:
        HTMLResponse: Rendered index.html template.
    """
    return templates.TemplateResponse(
        request, FieldValues.INDEX_HTML,
        context={RouterFieldNames.REQUEST: request}
    )


@router.get("/profile")
async def get_profile(request: Request, current_user: CurrentUserDep) -> HTMLResponse:
    """Render the user profile page.

    Args:
        request: FastAPI request object.
        current_user: Authenticated current user.

    Returns:
        HTMLResponse: Rendered profile.html template with user data.
    """
    return templates.TemplateResponse(
        name=FieldValues.PROFILE_HTML,
        context={RouterFieldNames.REQUEST: request, RouterFieldNames.PROFILE: current_user}
    )
