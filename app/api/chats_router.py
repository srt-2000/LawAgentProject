from fastapi import APIRouter, Response, HTTPException
from sqlalchemy import ScalarResult

from app.dao.chats_dao import ChatDAO
from app.dependencies.users_dependencies import CurrentUserDep
from app.models.models import Chat
from app.schemas.chats_schema import ChatListDTO, ChatDTO, ChatCreateDTO
from app.schemas.users_schema import ResponseMessageDTO

router = APIRouter(prefix="/user", tags=["Chats"])


@router.get("/chats", response_model=ChatListDTO)
async def get_user_chats_list(current_user: CurrentUserDep) -> ChatListDTO:
    chats_scalar: ScalarResult[Chat] = await ChatDAO.get_user_chat_list(user_id=current_user.id)
    chats: ChatListDTO = ChatListDTO(
        chat_list=[ChatDTO.model_validate(scalar_chat) for scalar_chat in chats_scalar]
    )

    return chats

@router.post("/new_chat")
async def create_new_chat(current_user: CurrentUserDep) -> ResponseMessageDTO | None:
    data_to_create_new_chat: dict[str, str | int] = {
        "title": f"new_chat of {current_user.id}",
        "user_id": current_user.id
    }

    await ChatDAO.add(**data_to_create_new_chat)
    message = {"message": f"Chat {data_to_create_new_chat["title"]} created successfully"}
    return ResponseMessageDTO.model_validate(message)


@router.get("/chats/{chat_id}", response_model=ChatDTO)
async def get_chat_with_id(chat_id: int, current_user: CurrentUserDep) -> ChatDTO:
    chat = await ChatDAO.find_one_or_none_by_id(id=chat_id, user_id=current_user.id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    return ChatDTO.model_validate(chat)


@router.post("/chats/{chat_id}/delete")
async def delete_chat(chat_id: int, current_user: CurrentUserDep) -> ResponseMessageDTO:
    deleted_chats_count: int = await ChatDAO.delete(filter_by={"id": chat_id, "user_id": current_user.id})
    message: dict[str, str] = {"message": f"{deleted_chats_count} chats deleted"}
    return ResponseMessageDTO.model_validate(message)

# GET /chats — список чатов текущего пользователя (например id, title, updated_at). Для сайдбара «история чатов».
# POST /chats — создать новый чат (тело пустое или title опционально). Ответ: { "id": int, "title": str | null }. Фронт потом переключается на этот чат.
# GET /chats/{chat_id} — один чат с сообщениями (только свой). Для «открыть сохранённый чат» — загрузка истории.
# DELETE /chats/{chat_id} — удалить чат (и сообщения). Проверка user_id по текущему пользователю.
# Все эндпоинты — с зависимостью CurrentUserDep (как в users_router), чтобы работать только с чатами текущего пользователя.