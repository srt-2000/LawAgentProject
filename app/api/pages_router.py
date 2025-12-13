from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Request
from starlette.templating import Jinja2Templates

from app.dependencies.users_dependencies import CurrentUserDep

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(tags=["Pages"])

@router.get("/", response_class=HTMLResponse)
async def get_main_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html", context={"request": request})

@router.get("/profile")
async def get_profile(request: Request, current_user: CurrentUserDep) -> HTMLResponse:
    return templates.TemplateResponse(name="profile.html", context={"request": request, "profile": current_user})
