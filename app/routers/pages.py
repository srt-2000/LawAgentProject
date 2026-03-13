"""
HTML page routes: landing (/) and profile (/profile). Profile requires auth.
"""

from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Request
from starlette.templating import Jinja2Templates

from app.dependencies.users import CurrentUserDep

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(tags=["Pages"])


@router.get("/", response_class=HTMLResponse)
async def get_main_page(request: Request) -> HTMLResponse:
    """Render the main landing page.

    Args:
        request: FastAPI request object.

    Returns:
        HTMLResponse: Rendered index.html template.
    """
    return templates.TemplateResponse(
        request, "index.html", context={"request": request}
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
        name="profile.html", context={"request": request, "profile": current_user}
    )
