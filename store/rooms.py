from enum import Enum
from typing import Dict

class RoomStatus(str, Enum):
    OPEN = "open"
    RANDOMIZATION_IN_PROGRESS = "randomization_in_progress"
    COMPLETED = "completed"
    CLOSED = "closed"

# Короткий псевдонім (зручно імпортувати в сервіс)
RANDOMIZATION = RoomStatus.RANDOMIZATION_IN_PROGRESS

ROOMS: Dict[str, dict] = {
    "r1": {"id": "r1", "status": RoomStatus.OPEN.value},
    "r2": {"id": "r2", "status": RoomStatus.CLOSED.value},
}

def get_room_status(room_id: str) -> RoomStatus:
    room = ROOMS.get(room_id)
    if not room:
        return RoomStatus.CLOSED
    return RoomStatus(room["status"])

def _reset_rooms():
    ROOMS.clear()
    ROOMS.update({
        "r1": {"id": "r1", "status": RoomStatus.OPEN.value},
        "r2": {"id": "r2", "status": RoomStatus.CLOSED.value},
    })
