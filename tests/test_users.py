import pytest
from fastapi.testclient import TestClient
from app import app
from store.users import USERS, _reset_users
from store.rooms import ROOMS, _reset_rooms, RoomStatus

client = TestClient(app)

@pytest.fixture(autouse=True)
def _reset_state():
    _reset_users()
    _reset_rooms()
    yield
    _reset_users()
    _reset_rooms()

# ---- Позитивний кейс
def test_delete_user_success():
    res = client.delete("/users/u2", params={"userCode": "u1"})
    assert res.status_code == 200
    body = res.json()
    assert body["removedUserId"] == "u2"
    assert body["roomId"] == "r1"
    assert body["participantsCount"] == 1
    assert "u2" not in USERS

# ---- Негативні кейси
def test_user_id_not_found():
    res = client.delete("/users/unknown", params={"userCode": "u1"})
    assert res.status_code == 404
    assert res.json()["detail"] == "USER_NOT_FOUND"

def test_admin_code_not_found():
    res = client.delete("/users/u2", params={"userCode": "nope"})
    assert res.status_code == 404
    assert res.json()["detail"] == "ADMIN_NOT_FOUND"

def test_user_code_not_admin():
    res = client.delete("/users/u1", params={"userCode": "u2"})  # u2 — member
    assert res.status_code == 403
    assert res.json()["detail"] == "NOT_ADMIN"

def test_different_rooms():
    res = client.delete("/users/u2", params={"userCode": "u3"})  # u3 в іншій кімнаті
    assert res.status_code == 409
    assert res.json()["detail"] == "DIFFERENT_ROOMS"

def test_cannot_delete_self():
    res = client.delete("/users/u1", params={"userCode": "u1"})
    assert res.status_code == 400
    assert res.json()["detail"] == "CANNOT_DELETE_SELF"

@pytest.mark.parametrize("locked", [
    RoomStatus.RANDOMIZATION_IN_PROGRESS.value,
    RoomStatus.COMPLETED.value,
    RoomStatus.CLOSED.value
])

def test_room_locked(locked):
    ROOMS["r1"]["status"] = locked
    res = client.delete("/users/u2", params={"userCode": "u1"})
    assert res.status_code == 409
    assert res.json()["detail"] == "ROOM_CLOSED_OR_LOCKED"
