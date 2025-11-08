from enum import Enum
from fastapi import APIRouter, Query
from typing import Literal
from pydantic import BaseModel
from services.user_service import remove_user
from store.users import USERS

router = APIRouter(prefix="/users", tags=["Users"])

# ---- Коди помилок (на рівні контракту)
class Err(str, Enum):
    USER_NOT_FOUND = "USER_NOT_FOUND"
    ADMIN_NOT_FOUND = "ADMIN_NOT_FOUND"
    NOT_ADMIN = "NOT_ADMIN"
    DIFFERENT_ROOMS = "DIFFERENT_ROOMS"
    CANNOT_DELETE_SELF = "CANNOT_DELETE_SELF"
    ROOM_CLOSED_OR_LOCKED = "ROOM_CLOSED_OR_LOCKED"

# ---- Схеми відповідей
class RemoveUserResponse(BaseModel):
    removedUserId: str
    roomId: str
    participantsCount: int
    message: Literal["USER_REMOVED"] = "USER_REMOVED"

class ApiError(BaseModel):
    detail: str

# --- GET: список учасників кімнати ---
@router.get("/participants")
def list_participants(roomId: str = Query(..., min_length=1)):
    """
    Повертає список учасників кімнати roomId.
    Зараз name = id для простоти.
    """
    return [
        {
            "id": u["id"],
            "name": u["id"],
            "role": u["role"],
            "roomId": u["room_id"],
        }
        for u in USERS.values()
        if u["room_id"] == roomId
    ]

# --- DELETE: видалення учасника адміністратором ---
@router.delete(
    "/{user_id}",
    response_model=RemoveUserResponse,
    responses={
        400: {"model": ApiError, "description": Err.CANNOT_DELETE_SELF},
        403: {"model": ApiError, "description": Err.NOT_ADMIN},
        404: {"model": ApiError, "description": f"{Err.USER_NOT_FOUND} | {Err.ADMIN_NOT_FOUND}"},
        409: {"model": ApiError, "description": f"{Err.DIFFERENT_ROOMS} | {Err.ROOM_CLOSED_OR_LOCKED}"},
    },
    summary="Remove participant by admin before randomization starts",
)
def delete_user(
    user_id: str,
    userCode: str = Query(..., min_length=2, description="Admin user code"),
):
    """
    Видаляє користувача user_id, якщо userCode належить адміністратору тієї ж кімнати.
    """
    return remove_user(user_id=user_id, admin_code=userCode)