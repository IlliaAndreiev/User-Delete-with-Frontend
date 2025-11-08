from enum import Enum
from fastapi import HTTPException
from store.users import USERS, find_user_by_code, count_participants_in_room, delete_user_by_id
from store.rooms import get_room_status, RoomStatus, RANDOMIZATION

class Err(str, Enum):
    USER_NOT_FOUND = "USER_NOT_FOUND"
    ADMIN_NOT_FOUND = "ADMIN_NOT_FOUND"
    NOT_ADMIN = "NOT_ADMIN"
    DIFFERENT_ROOMS = "DIFFERENT_ROOMS"
    CANNOT_DELETE_SELF = "CANNOT_DELETE_SELF"
    ROOM_CLOSED_OR_LOCKED = "ROOM_CLOSED_OR_LOCKED"

def remove_user(user_id: str, admin_code: str):
    # 1) жертва існує?
    victim = USERS.get(user_id)
    if not victim:
        raise HTTPException(status_code=404, detail=Err.USER_NOT_FOUND.value)

    # 2) адмін існує?
    admin = find_user_by_code(admin_code)
    if not admin:
        raise HTTPException(status_code=404, detail=Err.ADMIN_NOT_FOUND.value)

    # 3) адмін — адмін?
    if admin["role"] != "admin":
        raise HTTPException(status_code=403, detail=Err.NOT_ADMIN.value)

    # 4) одна кімната?
    if admin["room_id"] != victim["room_id"]:
        raise HTTPException(status_code=409, detail=Err.DIFFERENT_ROOMS.value)

    # 5) не видаляє себе?
    if admin["id"] == victim["id"]:
        raise HTTPException(status_code=400, detail=Err.CANNOT_DELETE_SELF.value)

    # 6) кімната не заблокована?
    status = get_room_status(admin["room_id"])
    if status in (RANDOMIZATION, RoomStatus.COMPLETED, RoomStatus.CLOSED):
        raise HTTPException(status_code=409, detail=Err.ROOM_CLOSED_OR_LOCKED.value)

    # --- виконання ---
    delete_user_by_id(victim["id"])
    remaining = count_participants_in_room(admin["room_id"])

    return {
        "removedUserId": user_id,
        "roomId": admin["room_id"],
        "participantsCount": remaining,
        "message": "USER_REMOVED",
    }
