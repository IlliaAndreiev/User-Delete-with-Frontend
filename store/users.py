from typing import Dict, Optional

# Проста in-memory "БД"
USERS: Dict[str, dict] = {
    # id: {id, room_id, role}
    "u1": {"id": "u1", "room_id": "r1", "role": "admin"},
    "u2": {"id": "u2", "room_id": "r1", "role": "member"},
    "u3": {"id": "u3", "room_id": "r2", "role": "admin"},
}

def find_user_by_code(user_code: str) -> Optional[dict]:
    # У спрощенні: userCode == id користувача-адміністратора
    return USERS.get(user_code)

def delete_user_by_id(user_id: str) -> None:
    USERS.pop(user_id, None)

def count_participants_in_room(room_id: str) -> int:
    return sum(1 for u in USERS.values() if u["room_id"] == room_id)

def _reset_users():
    USERS.clear()
    USERS.update({
        "u1": {"id": "u1", "room_id": "r1", "role": "admin"},
        "u2": {"id": "u2", "room_id": "r1", "role": "member"},
        "u3": {"id": "u3", "room_id": "r2", "role": "admin"},
    })
